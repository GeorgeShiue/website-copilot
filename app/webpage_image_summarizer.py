import base64
import logging
import os
import random
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from litellm import completion

logging.getLogger("LiteLLM").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

load_dotenv()


@dataclass(frozen=True)
class _ImageSummarizeParameters:
    """VLM 圖片摘要用不可變設定參數，供內部方法共用"""

    model: str | None
    prompt: str | None
    api_key: str | None
    vlm_max_workers: int | None
    litellm_kwargs: dict[str, Any]


@dataclass
class _ImageSummarizeStates:
    """Per-call 可變狀態：快取與下載統計。"""

    cache: dict[str, tuple[str, str]]  # url -> (caption, download_status)
    download_stats: dict[str, int]
    retry_count: int = 0


class WebpageImageSummarizerConstants:
    """VLM 圖片摘要用常數：圖片 URL 正則、預設提示詞、支援的模型對照。"""

    VLM_MODELS: dict[str, tuple[str, str]] = {
        "openai": ("gpt-4.1-mini", "OPENAI_WEBPAGE_SUMMARIZER_VLM_API_KEY"),
        "gemini": ("gemini-2.5-flash", "GEMINI_WEBPAGE_SUMMARIZER_VLM_API_KEY"),
    }
    DEFAULT_VLM_MODEL: str = "openai"
    DEFAULT_VLM_MAX_WORKERS: int = 10

    IMAGE_CAPTION_PROMPT = (
        "請描述這張圖片中的文字與版面內容。"
        "以結構化、易讀的純文字輸出，方便作為網頁內容的補充說明。"
        "若需要列點敘述，統一使用「*」作為 Markdown 列點符號。"
    )

    # 圖片下載配置
    DEFAULT_DOWNLOAD_TIMEOUT: float = 15.0  # 秒
    DEFAULT_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    DEFAULT_CONTENT_TYPE: str = "image/jpeg"  # 當無法判斷圖片類型時的預設值

    # 重試策略配置
    MIN_SUCCESS_RATE_THRESHOLD: float = 0.8
    MIN_DOWNLOAD_ATTEMPTS_TO_CONSIDER_RETRY: int = 10

    # 指數退避秒數：第 1 次 30s、第 2 次 60s、第 3 次 2min，之後 5～10min，上限 15min
    BACKOFF_SECONDS: tuple[float, ...] = (30, 60, 120, 300, 600)
    BACKOFF_CAP_SECONDS: float = 900.0  # 15 分鐘
    BACKOFF_JITTER_FRACTION: float = 0.2  # ±20% 隨機
    MAX_RETRIES: int = 6  # 對應 BACKOFF_SECONDS 長度 + 最後一次用 cap


# TODO: 簡化程式碼
class WebpageImageSummarizer:
    """可初始化的網頁 Markdown 圖片摘要器，統計資訊封裝於實例內。"""

    Constants = WebpageImageSummarizerConstants

    @classmethod
    def summarize_crawl_results_images(
        cls,
        crawl_results: list[dict[str, Any]],
        *,
        model: str | None = None,
        prompt: str | None = None,
        api_key: str | None = None,
        vlm_max_workers: int | None = None,
        **litellm_kwargs: Any,
    ) -> list[dict]:
        """
        對多個 crawl_result 項目做 VLM 圖片摘要，回傳 (更新後的 crawl_results, 重試次數, 下載統計)。
        若一輪後圖片下載成功率 < 80% 且嘗試數足夠，視為可能被擋，依指數退避自動重試（僅重試失敗的 URL）。
        - model: 模型商名稱（WebpageImageSummarizerConstants.VLM_MODELS 的 key），
          傳入後會自動對應模型型號與 .env 中的 API key；未傳則使用 Constants.DEFAULT_VLM_MODEL（'openai'）。
        - prompt: 送給 VLM 的提示詞，未設則用內建 IMAGE_CAPTION_PROMPT。
        - api_key: 若提供則覆寫該次呼叫的 API key，否則依模型商使用 VLM_MODELS 對應的環境變數。
        - vlm_max_workers: VLM 並行數上限，未設則用 Constants.DEFAULT_VLM_MAX_WORKERS，避免觸發 API rate limit。
        - **litellm_kwargs: 其他傳給 litellm.completion 的參數。
        """
        # Per-call states: do not store mutable progress on instance.
        params = _ImageSummarizeParameters(
            model=model,
            prompt=prompt,
            api_key=api_key,
            vlm_max_workers=vlm_max_workers,
            litellm_kwargs=litellm_kwargs,
        )
        states = _ImageSummarizeStates(
            cache={},
            download_stats=cls._new_download_stats(),
        )

        min_success_rate = cls.Constants.MIN_SUCCESS_RATE_THRESHOLD
        target_urls: set[str] | None = None
        enhanced_crawl_results = crawl_results
        while True:
            enhanced_crawl_results = cls._summarize_crawl_results_images(
                crawl_results,
                params,
                states,
                target_urls=target_urls,
            )

            retry_context = cls._retrieve_retry_context(states, min_success_rate)
            if retry_context is None:
                break

            success_rate, failed_urls = retry_context
            target_urls = cls._prepare_retry_urls(
                states=states,
                failed_urls=failed_urls,
                success_rate=success_rate,
                min_success_rate=min_success_rate,
            )

        logger.info("Image download stats:")
        for k, v in states.download_stats.items():
            logger.info("  * %s: %s", k, v)
        logger.info("  * total retries: %s", states.retry_count)
        logger.info("-" * 30)

        return enhanced_crawl_results

    @classmethod
    def _new_download_stats(cls) -> dict[str, int]:
        return {
            "success": 0,
            "network_failure": 0,
            "processing_failure": 0,
            "cache_reuse": 0,
        }

    @classmethod
    def _summarize_crawl_results_images(
        cls,
        crawl_results: list[dict[str, Any]],
        params: _ImageSummarizeParameters,
        states: _ImageSummarizeStates,
        target_urls: set[str] | None = None,
    ) -> list[dict]:
        """通用頁面摘要流程，支援全量模式與重試過濾模式。

        - target_urls 為空（None 或空集合）時：全量處理所有頁面。
          無圖片頁面會寫入 enhanced_markdown = fit_markdown。
        - target_urls 有值時：只處理包含任一 target URL 的頁面（重試模式）。
          未命中的頁面保持原值，不重算不覆寫。
        """
        for crawl_result in crawl_results:
            markdown = crawl_result.get("fit_markdown", "")
            images = crawl_result.get("images", [])

            if target_urls is not None:
                page_urls = {img.get("src", "") for img in images if img.get("src")}
                if not (page_urls & target_urls):
                    continue

            if not images:
                crawl_result["enhanced_markdown"] = markdown
                continue

            enhanced = cls._enhance_markdown_with_image_captions(
                markdown,
                images=images,
                params=params,
                states=states,
            )
            crawl_result["enhanced_markdown"] = enhanced
        return crawl_results

    @classmethod
    def _enhance_markdown_with_image_captions(
        cls,
        markdown: str,
        images: list[dict[str, str]],
        params: _ImageSummarizeParameters,
        states: _ImageSummarizeStates,
    ) -> str:
        """對單一 Markdown 字串：從 images 列表取得圖片 URL，並行呼叫 VLM，並將所有圖片說明附加到 markdown 末尾。"""
        # 從 images 提取所有 src
        image_urls = [img.get("src", "") for img in images if img.get("src")]
        if not image_urls:
            return markdown

        # 取得所有 caption
        url_to_caption = cls._get_image_captions(
            image_urls,
            params=params,
            states=states,
        )

        # 附加所有圖片說明到 markdown 末尾
        captions = ["---\n\n# Image\n\n"]
        for i, url in enumerate(image_urls, 1):
            caption = url_to_caption.get(url, "")
            if caption:
                captions.append(
                    f"## Image-{i}:\n\n> {caption.replace(chr(10), chr(10) + '> ')}"
                )

        if captions:
            return markdown + "".join(captions)
        return markdown

    @classmethod
    def _get_image_captions(
        cls,
        urls: list[str],
        params: _ImageSummarizeParameters,
        states: _ImageSummarizeStates,
    ) -> dict[str, str]:
        """獲取單一網頁所有圖片的caption，已存在 cache 的圖片直接重用。"""
        url_to_caption: dict[str, str] = {}
        cached_urls = set(states.cache.keys())
        uncached = [u for u in urls if u not in cached_urls]
        for url in urls:
            if url in cached_urls:
                states.download_stats["cache_reuse"] += 1
                url_to_caption[url] = states.cache[url][0]
        if not uncached:
            return url_to_caption

        max_workers = (
            params.vlm_max_workers
            if params.vlm_max_workers is not None
            else cls.Constants.DEFAULT_VLM_MAX_WORKERS
        )

        def fetch_caption(image_url: str) -> tuple[str, str, str]:
            prompt = params.prompt or cls.Constants.IMAGE_CAPTION_PROMPT
            image_base64_url, download_status = cls._download_image(image_url)
            if image_base64_url is None:
                return image_url, "", download_status

            return cls._get_image_caption(
                image_url=image_url,
                prompt=prompt,
                image_base64_url=image_base64_url,
                download_status=download_status,
                params=params,
            )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(fetch_caption, url) for url in uncached]
            for future in as_completed(futures):
                image_url, image_caption, download_status = future.result()
                # 根據狀態更新統計
                if download_status == "success":
                    states.download_stats["success"] += 1
                elif download_status == "network_failure":
                    states.download_stats["network_failure"] += 1
                elif download_status == "processing_failure":
                    states.download_stats["processing_failure"] += 1
                states.cache[image_url] = (image_caption, download_status)
                url_to_caption[image_url] = image_caption
        return url_to_caption

    @classmethod
    def _download_image(
        cls,
        url: str,
        timeout: float | None = None,
        referer: str | None = None,
    ) -> tuple[str | None, str]:
        """從 URL 下載圖片並轉成 data URL，供 VLM 使用。
        回傳 (data_url, status)，其中 status 為：
        - "success": 網路下載與後處理皆成功
        - "network_failure": 網路抓取失敗（連線逾時、404 等）
        - "processing_failure": 網路抓取成功但後處理失敗（content-type、base64 編碼等）
        """
        effective_timeout = (
            timeout if timeout is not None else cls.Constants.DEFAULT_DOWNLOAD_TIMEOUT
        )

        headers = {"User-Agent": cls.Constants.DEFAULT_USER_AGENT}
        if referer:
            headers["Referer"] = referer

        # 網路下載圖片
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=effective_timeout) as resp:
                data = resp.read()
                raw_content_type = resp.headers.get(
                    "Content-Type", cls.Constants.DEFAULT_CONTENT_TYPE
                )
        except Exception as e:
            logger.warning("Image download failed (url=%s): %s", url, e)
            return None, "network_failure"

        # 圖片後處理(content-type 解析、base64 編碼)
        try:
            content_type = raw_content_type.split(";")[0].strip()
            if not content_type.startswith("image/"):
                content_type = cls.Constants.DEFAULT_CONTENT_TYPE
            b64 = base64.standard_b64encode(data).decode("ascii")
            data_url = f"data:{content_type};base64,{b64}"
            logger.info("Image download and processing succeeded (url=%s)", url)
            return data_url, "success"
        except Exception as e:
            logger.warning(
                "Image post-processing failed (url=%s, network fetch succeeded): %s",
                url,
                e,
            )
            return None, "processing_failure"

    @classmethod
    def _get_image_caption(
        cls,
        image_url: str,
        prompt: str,
        image_base64_url: str,
        download_status: str,
        params: _ImageSummarizeParameters,
    ) -> tuple[str, str, str]:
        """呼叫支援視覺的模型取得圖片描述，失敗時回傳空字串。
        回傳 (url, caption, download_status)，其中 download_status 為 "success", "network_failure", "processing_failure"。
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_base64_url},
                    },
                ],
            }
        ]

        provider_config = cls.Constants.VLM_MODELS.get(
            params.model
            if params.model is not None
            else cls.Constants.DEFAULT_VLM_MODEL
        )
        if provider_config is None:
            raise ValueError(f"VLM 模型{params.model}名稱錯誤")
        model_name, api_key_name = provider_config

        effective_api_key = (
            params.api_key if params.api_key is not None else os.getenv(api_key_name)
        )
        if effective_api_key is None:
            raise ValueError(f"VLM 模型{model_name}API key錯誤")

        options: dict[str, Any] = {}
        options["api_key"] = effective_api_key
        options.update(params.litellm_kwargs)

        try:
            response = completion(
                model=model_name, messages=messages, stream=False, **options
            )
            image_caption = ""
            choices = getattr(response, "choices", None)
            if choices and isinstance(choices, (list, tuple)) and len(choices) > 0:
                choice = choices[0]
                message = getattr(choice, "message", None)
                if message:
                    msg_content = getattr(message, "content", None)
                    if isinstance(msg_content, str):
                        image_caption = msg_content.strip()
            return image_url, image_caption, download_status
        except Exception as e:
            logger.warning("VLM model %s call failed: %s", model_name, e)
            return image_url, "", download_status

    @classmethod
    def _retrieve_retry_context(
        cls,
        states: _ImageSummarizeStates,
        min_success_rate: float,
    ) -> tuple[float, set[str]] | None:
        """回傳重試所需資料；若不需重試則回傳 None。"""
        if states.retry_count >= cls.Constants.MAX_RETRIES:
            return None

        success, failure = (
            states.download_stats["success"],
            states.download_stats["network_failure"],
        )
        total = success + failure
        success_rate = (
            None
            if total < cls.Constants.MIN_DOWNLOAD_ATTEMPTS_TO_CONSIDER_RETRY
            else success / total
        )
        if success_rate is None or success_rate >= min_success_rate:
            return None

        failed_urls = {
            url
            for url, (_, status) in states.cache.items()
            if status == "network_failure"
        }
        if not failed_urls:
            return None

        for failed_url in failed_urls:
            states.cache.pop(failed_url, None)

        return success_rate, failed_urls

    @classmethod
    def _prepare_retry_urls(
        cls,
        *,
        states: _ImageSummarizeStates,
        failed_urls: set[str],
        success_rate: float,
        min_success_rate: float,
    ) -> set[str]:
        # 依重試次數計算等待秒數（含 jitter），不超過 BACKOFF_CAP_SECONDS
        bases = cls.Constants.BACKOFF_SECONDS
        base = bases[min(states.retry_count, len(bases) - 1)] if bases else 30
        jitter = 1.0 + random.uniform(
            -cls.Constants.BACKOFF_JITTER_FRACTION,
            cls.Constants.BACKOFF_JITTER_FRACTION,
        )
        wait_sec = min(base * jitter, cls.Constants.BACKOFF_CAP_SECONDS)
        logger.warning(
            "Image download success rate %.0f%% (< %.0f%%). Possible blocking detected; retrying %s URLs in %.1f seconds (attempt %s)",
            success_rate * 100,
            min_success_rate * 100,
            len(failed_urls),
            wait_sec,
            states.retry_count + 1,
        )
        logger.warning("-" * 30)
        time.sleep(wait_sec)

        # 重置統計，準備重試
        states.download_stats = cls._new_download_stats()
        states.retry_count += 1
        return failed_urls
