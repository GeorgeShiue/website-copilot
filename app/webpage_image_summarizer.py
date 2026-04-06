import asyncio
import base64
import logging
import random
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Literal

from litellm import acompletion, completion_cost

from app.webpage_image_summarizer_config import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_CONFIG_SECTION,
    get_vlm_api_key,
    set_webpage_image_summarizer_args,
)

logging.getLogger("LiteLLM").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)


DEFAULT_PROMPT = """
用繁體中文描述圖片，作為網頁補充說明。

依序輸出：
    - 圖片摘要：1 句（20-40 字）。
    - 可觀察元素：列出 3-5 點可直接看見的內容（物件、顏色、位置、構圖）。
    - 可讀文字：列出圖片中的文字；若沒有請寫「無」。
    - 場景功能：1 句，描述圖片中場景可能的用途或功能。

規則：
    - 只寫可觀察事實，避免主觀形容詞。
    - 不確定就寫「不確定」，不要臆測細節。
    - 若需列點，一律使用「*」作為 Markdown 列點符號。
"""
VLM_MODEL_TO_API_KEY: dict[str, str] = {
    "gpt": "OPENAI_WEBPAGE_SUMMARIZER_VLM_API_KEY",
    "gemini": "GEMINI_WEBPAGE_SUMMARIZER_VLM_API_KEY",
}
MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[.*?\]\((https?://[^\s)]+)\)")


class WebpageImageSummarizer:
    def __init__(
        self,
        download_timeout: float = 10.0,
        model: str = "gpt-5-mini",
        prompt: str = DEFAULT_PROMPT,
        vlm_max_workers: int = 10,
        image_source: Literal["images", "markdown"] = "markdown",
        success_threshold: float = 0.8,  # 圖片下載成功率低於此值則啟動重試機制
        max_retries: int = 6,  # 最大重試次數，對應指數退避的長度 + 最後一次用 cap
        **litellm_kwargs: Any,
    ) -> None:
        self.download_timeout = download_timeout
        self.model = model
        self.prompt = prompt
        self.vlm_max_workers = vlm_max_workers
        self.litellm_kwargs = litellm_kwargs

        self.image_source: Literal["images", "markdown"] = image_source
        self.success_threshold = success_threshold
        self.max_retries = max_retries

        # url -> {"caption": ..., "download_stats": ..., "summarize_stats": ...}
        self._stats: dict[str, int | float] = self._new_stats()
        self._image_cache: dict[str, dict[str, str]] = {}
        self._image_urls: list[str] = []
        self._image_captions: dict[str, str] = {}
        self._final_stats: dict[str, int | float] = self._new_final_stats()

    # TODO: 下載和摘要拆成兩個模組
    def summarize_crawl_results_images(
        self,
        crawl_results: list[dict[str, Any]],
    ) -> list[dict]:
        """
        使用 VLM 總結所有爬取下的網頁中的圖片。
        若一輪後圖片下載成功率 < 80% 且嘗試數足夠，視為可能被擋，依指數退避自動重試。

        - crawl_results: 爬取結果列表，每個元素為 dict，包含 "fit_markdown"與 "images"。
        """
        self._image_cache = {}
        self._image_urls = []
        self._image_captions = {}
        self._final_stats = self._new_final_stats()

        target_urls: set[str] | None = None
        enhanced_crawl_results = crawl_results
        while True:
            enhanced_crawl_results = self._summarize_crawl_results_images(
                crawl_results, target_urls
            )
            retry_context = self._retrieve_retry_context()
            if retry_context is None:
                break

            failed_urls, success_rate = retry_context
            self._prepare_retry_urls(failed_urls, success_rate)
            target_urls = failed_urls
            self._final_stats["retries"] += 1

        logger.info("Final image summarize stats:")
        for k, v in self._final_stats.items():
            if k == "cost_usd":
                v = f"${v:.6f}"
            logger.info("  * %s: %s", k, v)

        return enhanced_crawl_results

    def _summarize_crawl_results_images(
        self,
        crawl_results: list[dict[str, Any]],
        target_urls: set[str] | None = None,
    ) -> list[dict]:
        """摘要爬取的網頁中的所有圖片。"""
        for crawl_result in crawl_results:
            crawl_result_content = self._retrieve_crawl_result_content(
                crawl_result, target_urls
            )
            if crawl_result_content is None:
                continue

            fit_markdown, image_urls = crawl_result_content
            self._image_urls = image_urls
            self._stats = self._new_stats()

            uncached_image_urls = self._collect_cached_captions()
            downloaded_images = self._download_images(uncached_image_urls)
            self._generate_image_captions(downloaded_images)
            enhanced_markdown = self._enhance_markdown(fit_markdown)
            crawl_result["enhanced_markdown"] = enhanced_markdown

            logger.info("-" * 30)
            logger.info("Image summarize stats:")
            for k, v in self._stats.items():
                if k == "cost_usd":
                    v = f"${v:.6f}"
                logger.info("  * %s: %s", k, v)
            logger.info("-" * 30)

            self._final_stats["success"] += self._stats["success"]
            self._final_stats["failure"] += (
                self._stats["network_failure"]
                + self._stats["processing_failure"]
                + self._stats["summarize_failure"]
            )
            self._final_stats["cost_usd"] += self._stats["cost_usd"]

        return crawl_results

    def _collect_cached_captions(
        self,
    ) -> list[str]:
        """收集快取命中的 caption，並回傳未命中的 URL。"""
        cached_urls = set(self._image_cache.keys())
        image_urls = self._image_urls

        for url in image_urls:
            if url in cached_urls:
                self._stats["cache_reuse"] += 1
                self._image_captions[url] = self._image_cache[url]["caption"]

        uncached_urls = [url for url in image_urls if url not in cached_urls]
        if len(image_urls) - len(uncached_urls) > 0:
            logger.info(
                "Collected captions from cache for %s/%s images",
                len(image_urls) - len(uncached_urls),
                len(image_urls),
            )

        return uncached_urls

    def _retrieve_crawl_result_content(
        self,
        crawl_result: dict[str, Any],
        target_urls: set[str] | None = None,
    ) -> tuple[str, list[str]] | None:
        """從爬取結果中提取圖片 URL。"""
        fit_markdown = crawl_result.get("fit_markdown", "")

        image_urls: list[str] = []
        if self.image_source == "markdown":
            image_urls = MARKDOWN_IMAGE_PATTERN.findall(fit_markdown)
        elif self.image_source == "images":
            images = crawl_result.get("images", [])
            image_urls = [img.get("src", "") for img in images if img.get("src")]

        if target_urls is not None and not (set(image_urls) & target_urls):
            return None

        if not image_urls:
            crawl_result["enhanced_markdown"] = fit_markdown
            return None

        return fit_markdown, image_urls

    def _download_images(
        self,
        image_urls: list[str],
    ) -> dict[str, str]:
        """平行下載圖片，回傳成功下載圖片。"""
        downloaded_images: dict[str, str] = {}

        if not image_urls:
            return downloaded_images

        max_workers = self.vlm_max_workers

        def download_image(image_url: str) -> tuple[str, str | None, str]:
            image_base64_url, download_status = self._download_image(image_url)
            return image_url, image_base64_url, download_status

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(download_image, url) for url in image_urls]
            for future in as_completed(futures):
                image_url, image_base64_url, download_status = future.result()

                if "failure" in download_status:
                    self._stats[download_status] += 1
                    self._image_cache[image_url] = {
                        "caption": "",
                        "download_stats": download_status,
                        "summarize_stats": "failed",
                    }
                    self._image_captions[image_url] = ""
                elif image_base64_url is not None:
                    downloaded_images[image_url] = image_base64_url

        return downloaded_images

    def _download_image(
        self,
        url: str,
    ) -> tuple[str | None, str]:
        """下載圖片並轉成 image url(base64)，供 VLM 使用。"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        download_timeout = self.download_timeout
        default_content_type = "image/jpeg"

        # 圖片下載
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=download_timeout) as resp:
                data = resp.read()
                raw_content_type = resp.headers.get(
                    "Content-Type", default_content_type
                )
        except Exception as e:
            logger.warning("Image download failed (url=%s): %s", url, e)
            return None, "network_failure"

        # 圖片後處理
        try:
            content_type = raw_content_type.split(";")[0].strip()
            if not content_type.startswith("image/"):
                content_type = default_content_type
            b64 = base64.standard_b64encode(data).decode("ascii")
            data_url = f"data:{content_type};base64,{b64}"
            logger.info("Image download succeeded (url=%s)", url)
            return data_url, "success"
        except Exception as e:
            logger.warning(
                "Image post-processing failed (url=%s, network fetch succeeded): %s",
                url,
                e,
            )
            return None, "processing_failure"

    def _generate_image_captions(
        self,
        images: dict[str, str],
    ) -> None:
        """為已下載成功的圖片取得 caption。"""
        if not images:
            return

        caption_results = asyncio.run(self._agenerate_image_captions(images))
        logger.info(
            "%s/%s image captions generate succeeded",
            len(caption_results),
            len(images),
        )

        for image_url, image_caption, summarize_status, cost_usd in caption_results:
            if summarize_status == "success":
                self._stats["success"] += 1
                self._stats["cost_usd"] += cost_usd
            else:
                self._stats["summarize_failure"] += 1

            self._image_cache[image_url] = {
                "caption": image_caption,
                "download_stats": "success",
                "summarize_stats": summarize_status,
            }
            self._image_captions[image_url] = image_caption

    async def _agenerate_image_captions(
        self,
        images: dict[str, str],
    ) -> list[tuple[str, str, str, float]]:
        """對圖片批次平行摘要，回傳 (url, caption, status, cost)。"""
        semaphore = asyncio.Semaphore(max(1, self.vlm_max_workers))

        tasks: list[tuple[str, asyncio.Task[tuple[str, str, float]]]] = []
        for image_url, image_base64_url in images.items():
            await semaphore.acquire()
            task = asyncio.create_task(self._agenerate_image_caption(image_base64_url))
            task.add_done_callback(lambda _task: semaphore.release())
            tasks.append((image_url, task))

        if not tasks:
            return []

        gathered_results = await asyncio.gather(
            *(task for _, task in tasks),
            return_exceptions=True,
        )

        results: list[tuple[str, str, str, float]] = []
        for (image_url, _), item in zip(tasks, gathered_results):
            if isinstance(item, BaseException):
                logger.warning("Image summarization task failed unexpectedly: %s", item)
                continue
            image_caption, summarize_status, cost_usd = item
            results.append((image_url, image_caption, summarize_status, cost_usd))

        return results

    async def _agenerate_image_caption(
        self,
        image_base64_url: str,
    ) -> tuple[str, str, float]:
        """呼叫 VLM 取得圖片描述。"""
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": self.prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_base64_url},
                    },
                ],
            }
        ]
        api_key = get_vlm_api_key(self.model)
        litellm_kwargs: dict[str, Any] = {}
        litellm_kwargs["api_key"] = api_key  # 避免 api key 洩漏
        litellm_kwargs.update(self.litellm_kwargs)
        image_caption = ""

        # 圖片說明生成
        try:
            response = await acompletion(
                model=self.model,
                messages=messages,
                stream=False,
                **litellm_kwargs,
            )
        except Exception as e:
            logger.warning("Image summarization failed: %s", e)
            return image_caption, "failed", 0.0

        cost_usd = completion_cost(completion_response=response)
        # self._log_image_summarization(response=response, cost_usd=cost_usd) # debug

        choices = getattr(response, "choices", None)
        if choices and isinstance(choices, (list, tuple)) and len(choices) > 0:
            choice = choices[0]
            message = getattr(choice, "message", None)
            if message:
                msg_content = getattr(message, "content", None)
                if isinstance(msg_content, str):
                    image_caption = msg_content.strip()

        return image_caption, "success", cost_usd

    def _enhance_markdown(
        self,
        markdown: str,
    ) -> str:
        """將圖片說明以適當格式插入原 markdown 中。"""
        if not self._image_captions:
            return markdown

        image_urls = self._image_urls
        enhanced_markdown = ""
        if self.image_source == "markdown":
            lines = markdown.splitlines(keepends=True)
            enhanced_parts: list[str] = []
            occurrence_index = 0

            for line in lines:
                enhanced_parts.append(line)
                line_image_urls = MARKDOWN_IMAGE_PATTERN.findall(line)
                for _ in line_image_urls:
                    if occurrence_index >= len(image_urls):
                        break

                    url = image_urls[occurrence_index]
                    occurrence_index += 1
                    caption = self._image_captions.get(url, "")
                    if caption:
                        enhanced_parts.append(
                            f"> Image-{occurrence_index}:\n>\n> {caption.replace(chr(10), chr(10) + '> ')}\n\n"
                        )

            enhanced_markdown = "".join(enhanced_parts)
        elif self.image_source == "images":
            captions = ["---\n\n# Image\n\n"]
            for i, url in enumerate(image_urls, 1):
                caption = self._image_captions.get(url, "")
                if caption:
                    captions.append(
                        f"## Image-{i}\n> {caption.replace(chr(10), chr(10) + '> ')}\n\n"
                    )
            enhanced_markdown = markdown + "".join(captions)

        return enhanced_markdown

    def _retrieve_retry_context(
        self,
    ) -> tuple[set[str], float] | None:
        """回傳重試所需資料（需重試的 URL 集合、成功率）"""
        if self._final_stats["retries"] >= self.max_retries:
            return None

        success, failure = (
            self._stats["success"],
            self._stats["network_failure"],
        )
        total = success + failure
        if total == 0:
            return None
        success_rate = success / total
        if success_rate >= self.success_threshold:
            return None

        failed_urls = {
            url
            for url, cache_item in self._image_cache.items()
            if cache_item["download_stats"] == "network_failure"
        }
        if not failed_urls:
            return None

        for failed_url in failed_urls:
            self._image_cache.pop(failed_url, None)

        return failed_urls, success_rate

    # TODO: 重試機制根據 max retries 動態生成等待時間
    def _prepare_retry_urls(
        self,
        failed_urls: set[str],
        success_rate: float,
    ) -> None:
        """根據失敗的 URL 集合和成功率計算等待時間，並回傳下一輪要重試的 URL。"""
        # 依重試次數計算等待秒數（含 jitter），不超過 BACKOFF_CAP_SECONDS
        # 指數退避秒數：第 1 次 30s、第 2 次 60s、第 3 次 2min，之後 5～10min，上限 15min
        bases = (30, 60, 120, 300, 600)
        base = (
            bases[min(int(self._final_stats["retries"]), len(bases) - 1)]
            if bases
            else 30
        )
        backoff_cap_seconds = 900.0  # 15 分鐘
        backoff_jitter_fraction = 0.2  # ±20% 隨機
        jitter = 1.0 + random.uniform(
            -backoff_jitter_fraction,
            backoff_jitter_fraction,
        )
        wait_sec = min(base * jitter, backoff_cap_seconds)

        logger.warning(
            "Image download success rate %.0f%% (< %.0f%%). Possible blocking detected; retrying %s URLs in %.1f seconds (attempt %s)",
            success_rate * 100,
            self.success_threshold * 100,
            len(failed_urls),
            wait_sec,
            self._final_stats["retries"] + 1,
        )
        logger.warning("-" * 30)
        time.sleep(wait_sec)

    @classmethod
    def from_toml(
        cls,
        config_path: str = DEFAULT_CONFIG_PATH,
        config_section: str = DEFAULT_CONFIG_SECTION,
        **overrides: dict[str, Any],
    ) -> "WebpageImageSummarizer":
        """從 TOML 設定檔建立 WebpageImageSummarizer。"""
        logger.info("Initializing WebpageImageSummarizer from toml")
        init_kwargs, litellm_kwargs = set_webpage_image_summarizer_args(
            config_path, config_section, **overrides
        )
        return cls(**init_kwargs, **litellm_kwargs)

    @staticmethod
    def _new_stats() -> dict[str, int | float]:
        return {
            "cost_usd": 0.0,
            "success": 0,
            "network_failure": 0,
            "processing_failure": 0,
            "summarize_failure": 0,
            "cache_reuse": 0,
        }

    @staticmethod
    def _new_final_stats() -> dict[str, int | float]:
        return {
            "cost_usd": 0.0,
            "success": 0,
            "failure": 0,
            "retries": 0,
        }

    @staticmethod
    def _log_image_summarization(response=None, cost_usd=None) -> None:
        image_summarization_log = "Image summarization succeeded"

        if response is not None and cost_usd is not None:
            usage = getattr(response, "usage", None)
            prompt_tokens = getattr(usage, "prompt_tokens", None) if usage else None
            completion_tokens = (
                getattr(usage, "completion_tokens", None) if usage else None
            )
            total_tokens = getattr(usage, "total_tokens", None) if usage else None
            cost_usd_string = f"${cost_usd:.6f}"
            image_summarization_log += f" (cost_usd={cost_usd_string} prompt_tokens={prompt_tokens} completion_tokens={completion_tokens} total_tokens={total_tokens})"

        logger.info(image_summarization_log)
