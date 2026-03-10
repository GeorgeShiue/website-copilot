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
    """VLM 圖片摘要用參數，供內部方法共用"""

    model: str | None
    prompt: str | None
    api_key: str | None
    caption_heading: str | None
    vlm_max_workers: int | None
    litellm_kwargs: dict[str, Any]


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
    CAPTION_HEADING = "**圖片說明：**"

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
    def summarize_webpage_markdown_images(
        cls,
        crawl_results: list[dict[str, Any]],
        *,
        model: str | None = None,
        prompt: str | None = None,
        api_key: str | None = None,
        caption_heading: str | None = None,
        caption_cache: dict[str, str] | None = None,
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
        - caption_cache: 可選。若提供則會在此 dict 中累積 url -> 圖片說明，同一次呼叫內跨頁共用；下次呼叫可傳入同一 dict 以跨次重用。
        - vlm_max_workers: VLM 並行數上限，未設則用 Constants.DEFAULT_VLM_MAX_WORKERS，避免觸發 API rate limit。
        - **litellm_kwargs: 其他傳給 litellm.completion 的參數。
        """
        # Per-call state: do not store mutable progress on instance.
        download_stats = {
            "success": 0,
            "network_failure": 0,
            "processing_failure": 0,
            "cache_reuse": 0,
        }
        retry_count = 0

        caption_cache = caption_cache if caption_cache is not None else {}
        params = _ImageSummarizeParameters(
            model=model,
            prompt=prompt,
            api_key=api_key,
            caption_heading=caption_heading,
            vlm_max_workers=vlm_max_workers,
            litellm_kwargs=litellm_kwargs,
        )
        enhanced_crawl_results = cls._summarize_webpages(
            crawl_results,
            caption_cache,
            params,
            download_stats=download_stats,
        )

        # TODO: 以下重試機制獨立成一個方法，並簡化流程
        min_success_rate = cls.Constants.MIN_SUCCESS_RATE_THRESHOLD
        max_retries = cls.Constants.MAX_RETRIES
        while retry_count < max_retries:
            success_rate = cls._success_rate_for_retry(download_stats)
            if success_rate is None or success_rate >= min_success_rate:
                break

            # 找出所有失敗的 URL（caption 為空字串）
            failed_urls = {url for url, cap in caption_cache.items() if cap == ""}
            if not failed_urls:
                break

            # 從 cache 中移除失敗的 URL，以便重試時重新下載
            for url in failed_urls:
                del caption_cache[url]

            wait_sec = cls._backoff_seconds(retry_count)
            logger.warning(
                "Image download success rate %.0f%% (< %.0f%%). Possible blocking detected; retrying %s URLs in %.1f seconds (attempt %s)",
                success_rate * 100,
                min_success_rate * 100,
                len(failed_urls),
                wait_sec,
                retry_count + 1,
            )
            logger.warning("-" * 30)
            time.sleep(wait_sec)

            # 重置統計，準備重試
            download_stats = {
                "success": 0,
                "network_failure": 0,
                "processing_failure": 0,
                "cache_reuse": 0,
            }

            # 只重新處理包含失敗 URL 的頁面（效率優化）
            cls._summarize_webpages(
                crawl_results,
                caption_cache,
                params,
                download_stats,
                target_urls=failed_urls,
            )
            retry_count += 1

        logger.info("Image download stats:")
        for k, v in download_stats.items():
            logger.info("  * %s: %s", k, v)
        logger.info("  * total retries: %s", retry_count)
        logger.info("-" * 30)

        return enhanced_crawl_results

    @classmethod
    def _summarize_webpages(
        cls,
        crawl_results: list[dict[str, Any]],
        caption_cache: dict[str, str],
        params: _ImageSummarizeParameters,
        download_stats: dict[str, int],
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

            enhanced = cls._summarize_markdown_with_captions(
                markdown,
                images=images,
                caption_cache=caption_cache,
                params=params,
                download_stats=download_stats,
            )
            crawl_result["enhanced_markdown"] = enhanced
        return crawl_results

    @classmethod
    def _summarize_markdown_with_captions(
        cls,
        markdown: str,
        images: list[dict[str, str]],
        caption_cache: dict[str, str],
        params: _ImageSummarizeParameters,
        download_stats: dict[str, int],
    ) -> str:
        """對單一 Markdown 字串：從 images 列表取得圖片 URL，並行呼叫 VLM，並將所有圖片說明附加到 markdown 末尾。"""
        # 從 images 提取所有 src
        image_urls = [img.get("src", "") for img in images if img.get("src")]
        if not image_urls:
            return markdown

        # 取得所有 caption
        url_to_caption = cls._get_captions_for_urls(
            image_urls,
            caption_cache=caption_cache,
            params=params,
            download_stats=download_stats,
        )
        heading = params.caption_heading or cls.Constants.CAPTION_HEADING

        # TODO: 修改圖片說明格式
        # 附加所有圖片說明到 markdown 末尾
        captions = []
        for i, url in enumerate(image_urls, 1):
            caption = url_to_caption.get(url, "")
            if caption:
                captions.append(
                    f"\n\n### 圖片 {i}\n\n> {heading}\n>\n> {caption.replace(chr(10), chr(10) + '> ')}"
                )

        if captions:
            return markdown + "".join(captions)
        return markdown

    @classmethod
    def _get_captions_for_urls(
        cls,
        urls: list[str],
        caption_cache: dict[str, str],
        params: _ImageSummarizeParameters,
        download_stats: dict[str, int],
    ) -> dict[str, str]:
        """對一組 URL 並行取得說明（ThreadPoolExecutor）；已存在 caption_cache 的 URL 直接重用。"""
        url_to_caption: dict[str, str] = {}
        cached_urls = set(caption_cache.keys())
        uncached = [u for u in urls if u not in cached_urls]
        for u in urls:
            if u in cached_urls:
                download_stats["cache_reuse"] += 1
                url_to_caption[u] = caption_cache[u]
        if not uncached:
            return url_to_caption

        max_workers = (
            params.vlm_max_workers
            if params.vlm_max_workers is not None
            else cls.Constants.DEFAULT_VLM_MAX_WORKERS
        )

        def fetch_caption(url: str) -> tuple[str, str, str]:
            return cls._get_image_caption(url, params)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(fetch_caption, url) for url in uncached]
            for future in as_completed(futures):
                url, caption, download_status = future.result()
                # 根據狀態更新統計
                if download_status == "success":
                    download_stats["success"] += 1
                elif download_status == "network_failure":
                    download_stats["network_failure"] += 1
                elif download_status == "processing_failure":
                    download_stats["processing_failure"] += 1
                caption_cache[url] = caption
                url_to_caption[url] = caption
        return url_to_caption

    @classmethod
    def _get_image_caption(
        cls,
        image_url: str,
        params: _ImageSummarizeParameters,
    ) -> tuple[str, str, str]:
        """呼叫支援視覺的模型取得圖片描述，失敗時回傳空字串。
        回傳 (url, caption, download_status)，其中 download_status 為 "success", "network_failure", "processing_failure"。
        """
        prompt = params.prompt or cls.Constants.IMAGE_CAPTION_PROMPT
        image_base64_url, download_status = cls._download_image_as_base64_data_url(
            image_url
        )
        if image_base64_url is None:
            return image_url, "", download_status

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
            content = ""
            choices = getattr(response, "choices", None)
            if choices and isinstance(choices, (list, tuple)) and len(choices) > 0:
                choice = choices[0]
                message = getattr(choice, "message", None)
                if message:
                    msg_content = getattr(message, "content", None)
                    if isinstance(msg_content, str):
                        content = msg_content.strip()
            return image_url, content, download_status
        except Exception as e:
            logger.warning("VLM model %s call failed: %s", model_name, e)
            return image_url, "", download_status

    @classmethod
    def _download_image_as_base64_data_url(
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
    def _success_rate_for_retry(cls, download_stats: dict[str, int]) -> float | None:
        """若網路下載嘗試數足夠則回傳網路層成功率（success/(success+network_failure)），否則回傳 None。
        注意：只計算網路層面的成功率，不包括 processing_failure，因為後處理失敗不是網路被封鎖的徵兆。
        """
        s, f = download_stats["success"], download_stats["network_failure"]
        total = s + f
        if total < cls.Constants.MIN_DOWNLOAD_ATTEMPTS_TO_CONSIDER_RETRY:
            return None
        return s / total

    @classmethod
    def _backoff_seconds(cls, retry_index: int) -> float:
        """依重試次數回傳等待秒數（含 jitter），不超過 BACKOFF_CAP_SECONDS。"""
        bases = cls.Constants.BACKOFF_SECONDS
        base = bases[min(retry_index, len(bases) - 1)] if bases else 30
        jitter = 1.0 + random.uniform(
            -cls.Constants.BACKOFF_JITTER_FRACTION,
            cls.Constants.BACKOFF_JITTER_FRACTION,
        )
        return min(base * jitter, cls.Constants.BACKOFF_CAP_SECONDS)
