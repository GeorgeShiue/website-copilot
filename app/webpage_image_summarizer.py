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
from rich.progress import Progress
from rich.table import Table

from app.webpage_image_summarizer_config import (
    DEFAULT_PROMPT,
    get_summarizer_model_api_key,
)
from utils.log_helper import log_session, print_log

logging.getLogger("LiteLLM").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)


MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[.*?\]\((https?://[^\s)]+)\)")


class WebpageImageSummarizer:
    def __init__(
        self,
        download_timeout: float = 10.0,
        success_threshold: float = 0.8,  # 圖片下載成功率低於此值則啟動重試機制
        max_retries: int = 6,  # 最大重試次數，對應指數退避的長度 + 最後一次用 cap
    ) -> None:
        # ===== init args =====
        self.download_timeout = download_timeout
        self.success_threshold = success_threshold
        self.max_retries = max_retries

        # ===== summarize args =====
        self.model: str = ""
        self.prompt: str = ""
        self.vlm_max_workers: int = 0
        self.image_source: str = ""
        self.litellm_kwargs: dict[str, Any] = {}

        # ===== internal state =====
        # url -> {"caption": ..., "download_stats": ..., "summarize_stats": ...}
        self._image_cache: dict[str, dict[str, str]] = {}
        self._image_urls: list[str] = []
        self._image_captions: dict[str, str] = {}
        self._page_stats: dict[str, int | float] = self._new_page_stats()
        self._all_page_stats: dict[str, int | float] = self._new_all_page_stats()
        self._all_round_stats: dict[str, int | float] = self._new_all_round_stats()

    # TODO: 下載和摘要拆成兩個模組
    def summarize_crawl_results_images(
        self,
        crawl_results: list[dict[str, Any]],
        model: str = "gpt-5-mini",
        prompt: str = DEFAULT_PROMPT,
        vlm_max_workers: int = 10,
        image_source: Literal["images", "markdown"] = "markdown",
        **litellm_kwargs: Any,
    ) -> list[dict]:
        """
        使用 VLM 總結所有爬取下的網頁中的圖片。
        若一輪後圖片下載成功率 < 80% 且嘗試數足夠，視為可能被擋，依指數退避自動重試。

        - crawl_results: 爬取結果列表，每個元素為 dict，包含 "fit_markdown"與 "images"。
        """
        self.model = model
        self.prompt = prompt
        self.vlm_max_workers = vlm_max_workers
        self.image_source = image_source
        self.litellm_kwargs = litellm_kwargs

        self._image_cache = {}
        self._image_urls = []
        self._image_captions = {}
        self._all_round_stats = self._new_all_round_stats()

        target_urls: set[str] | None = None
        enhanced_crawl_results = crawl_results
        while True:
            self._all_page_stats = self._new_all_page_stats()
            enhanced_crawl_results = self._summarize_crawl_results_images(
                crawl_results, target_urls
            )

            self._log_stats(self._all_page_stats, "All image summarize stats")
            self._all_round_stats["cost_usd"] += self._all_page_stats["cost_usd"]
            self._all_round_stats["success"] += self._all_page_stats["success"]
            self._all_round_stats["failure"] += self._all_page_stats["failure"]
            self._all_round_stats["retries"] += 1

            retry_context = self._retrieve_retry_context()
            if retry_context is None:
                break

            failed_urls, success_rate = retry_context
            self._prepare_retry_urls(failed_urls, success_rate)
            target_urls = failed_urls

        if self._all_round_stats["retries"] > 1:
            self._log_stats(self._all_round_stats, "All rounds image summarize stats")

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

            log_session(
                f"Summarizing images in {crawl_result.get('md_file_name', '<unknown>')}",
                style="blue",
            )
            fit_markdown, image_urls = crawl_result_content
            self._image_urls = image_urls
            self._page_stats = self._new_page_stats()

            uncached_image_urls = self._collect_cached_captions()
            downloaded_images = self._download_images(uncached_image_urls)
            self._generate_image_captions(downloaded_images)
            enhanced_markdown = self._enhance_markdown(fit_markdown)
            crawl_result["enhanced_markdown"] = enhanced_markdown

            self._log_stats(self._page_stats)
            self._all_page_stats["success"] += self._page_stats["success"]
            self._all_page_stats["failure"] += (
                self._page_stats["download_failure"]
                + self._page_stats["summarize_failure"]
            )
            self._all_page_stats["cost_usd"] += self._page_stats["cost_usd"]

        return crawl_results

    def _collect_cached_captions(
        self,
    ) -> list[str]:
        """收集快取命中的 caption，並回傳未命中的 URL。"""
        cached_urls = set(self._image_cache.keys())
        image_urls = self._image_urls

        for url in image_urls:
            if url in cached_urls:
                self._page_stats["cache_reuse"] += 1
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
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_image_url = {
                executor.submit(self._download_image, url): url for url in image_urls
            }
            futures = list(future_to_image_url.keys())

            # FIXME: 修改進度條顯示機制
            with Progress() as progress:
                task_id = progress.add_task(
                    "[blue]Downloading images...", total=len(futures)
                )

                for future in as_completed(futures):
                    image_url = future_to_image_url[future]
                    image_base64_url, download_status = future.result()

                    if "failure" in download_status:
                        self._page_stats[download_status] += 1
                        self._image_cache[image_url] = {
                            "caption": "",
                            "download_stats": download_status,
                            "summarize_stats": "failed",
                        }
                        self._image_captions[image_url] = ""
                    elif image_base64_url is not None:
                        downloaded_images[image_url] = image_base64_url

                    progress.update(task_id, advance=1)

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

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=download_timeout) as resp:
                data = resp.read()
                raw_content_type: str = resp.headers.get("Content-Type", "")
        except Exception as e:
            logger.warning("Image download failed (url=%s): %s", url, e)
            return None, "download_failure"

        content_type: str = raw_content_type.split(";")[0].strip()
        if not content_type.startswith("image/"):
            logger.warning(
                "Image content-type is not image/* (url=%s, content_type=%s)",
                url,
                content_type or "<empty>",
            )
            return None, "download_failure"

        b64 = base64.standard_b64encode(data).decode("ascii")
        data_url = f"data:{content_type};base64,{b64}"
        logger.debug("Image download succeeded (url=%s)", url)

        return data_url, "success"

    def _generate_image_captions(
        self,
        images: dict[str, str],
    ) -> None:
        """為已下載成功的圖片取得 caption。"""
        if not images:
            return

        caption_results = asyncio.run(self._agenerate_image_captions(images))
        logger.debug(
            "%s/%s image captions generate succeeded",
            len(caption_results),
            len(images),
        )

        for image_url, image_caption, summarize_status, cost_usd in caption_results:
            if summarize_status == "success":
                self._page_stats["success"] += 1
                self._page_stats["cost_usd"] += cost_usd
            else:
                self._page_stats["summarize_failure"] += 1

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

        results: list[tuple[str, str, str, float]] = []

        # ! 以下進度條實作會出錯
        # 建立 task id 到 url 的映射，便於取得完成的 task 對應的 image_url
        # task_id_to_url = {id(task): url for url, task in tasks}
        # with Progress(transient=True) as progress:
        #     task_id = progress.add_task(
        #         "[magenta]Generating captions...", total=len(tasks)
        #     )

        #     for completed_task in asyncio.as_completed([task for _, task in tasks]):
        #         try:
        #             image_caption, summarize_status, cost_usd = await completed_task
        #             image_url = task_id_to_url[id(completed_task)]
        #             results.append(
        #                 (image_url, image_caption, summarize_status, cost_usd)
        #             )
        #         except Exception as e:
        #             logger.warning(
        #                 "Image summarization task failed unexpectedly: %s", e
        #             )
        #         finally:
        #             progress.update(task_id, advance=1)

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
        api_key = get_summarizer_model_api_key(self.model)
        litellm_kwargs: dict[str, Any] = {}
        litellm_kwargs["api_key"] = api_key  # 避免 api key 洩漏
        litellm_kwargs.update(self.litellm_kwargs)
        image_caption = ""

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
        if self._all_round_stats["retries"] >= self.max_retries:
            return None

        success, failure = (
            self._all_page_stats["success"],
            self._all_page_stats["failure"],
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
            if cache_item["download_stats"] == "download_failure"
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
            bases[min(int(self._all_round_stats["retries"]), len(bases) - 1)]
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
            "Image summarization success rate %.0f%% (< %.0f%%). Possible blocking detected; retrying %s URLs in %.1f seconds (attempt %s)",
            success_rate * 100,
            self.success_threshold * 100,
            len(failed_urls),
            wait_sec,
            self._all_round_stats["retries"] + 1,
        )
        logger.warning("-" * 30)
        time.sleep(wait_sec)

    @staticmethod
    def _new_page_stats() -> dict[str, int | float]:
        return {
            "cost_usd": 0.0,
            "success": 0,
            "download_failure": 0,
            "summarize_failure": 0,
            "cache_reuse": 0,
        }

    @staticmethod
    def _new_all_page_stats() -> dict[str, int | float]:
        return {
            "cost_usd": 0.0,
            "success": 0,
            "failure": 0,
        }

    @staticmethod
    def _new_all_round_stats() -> dict[str, int | float]:
        return {
            "cost_usd": 0.0,
            "success": 0,
            "failure": 0,
            "retries": 0,
        }

    @staticmethod
    def _log_stats(stats: dict[str, int | float], title: str = "") -> None:
        if title:
            log_session(title, style="green")

        table = Table(show_header=True, header_style="bold green")
        table.add_column("Metric", style="green", no_wrap=True)
        table.add_column("Value", style="white")

        for key in stats:
            value: int | float | str = stats[key]
            if key == "cost_usd" and isinstance(value, (int, float)):
                value = f"${value:.6f}"
            table.add_row(key, str(value))

        print_log(table)

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

    # ? 會在執行階段動態調整成員變數嗎
    def override_init_config(self, **init_kwargs) -> None:
        """覆寫建構子參數。"""
        self.download_timeout = init_kwargs.get(
            "download_timeout", self.download_timeout
        )
        self.success_threshold = init_kwargs.get(
            "success_threshold", self.success_threshold
        )
        self.max_retries = init_kwargs.get("max_retries", self.max_retries)

    def override_summarize_config(self, **summarize_kwargs) -> None:
        """覆寫 summarize 參數。"""
        self.model = summarize_kwargs.get("model", self.model)
        self.prompt = summarize_kwargs.get("prompt", self.prompt)
        self.vlm_max_workers = summarize_kwargs.get(
            "vlm_max_workers", self.vlm_max_workers
        )
        self.image_source = summarize_kwargs.get("image_source", self.image_source)
        litellm_kwargs = summarize_kwargs.get("litellm_kwargs", {})
        if litellm_kwargs:
            self.litellm_kwargs.update(litellm_kwargs)
