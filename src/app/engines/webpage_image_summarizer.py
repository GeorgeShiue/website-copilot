import asyncio
import base64
import logging
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Literal
from urllib.error import URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from litellm import acompletion, completion_cost
from rich.table import Table
from rich.text import Text

from app.configs.webpage_image_summarizer_config import (
    DEFAULT_PROMPT,
    VLM_MODEL_TO_API_KEY,
)
from utils.config_helper import EnvironmentVariableError
from utils.log_helper import TaskCountProgress, log_session, print_log

logger = logging.getLogger(__name__)


MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[.*?\]\((https?://[^\s)]+)\)")


class WebpageImageSummarizer:
    def __init__(
        self,
        download_timeout: float = 10.0,
        success_threshold: float = 0.8,  # 圖片下載成功率低於此值則啟動重試機制
        max_retries: int = 6,  # 最大重試次數，對應指數退避的長度 + 最後一次用 cap
        cache_download_images: bool = False,  # 適用於同一批網頁重複實驗的情況
        cache_image_captions: bool = False,  # 適用於同一批網頁重複實驗的情況
    ) -> None:
        # ===== init args =====
        self.download_timeout = download_timeout
        self.success_threshold = success_threshold
        self.max_retries = max_retries
        self.cache_download_image = cache_download_images
        self.cache_image_captions = cache_image_captions

        # ===== summarize args =====
        self.model: str = ""
        self.prompt: str = ""
        self.vlm_max_workers: int = 0
        self.image_source: str = ""
        self.litellm_kwargs: dict[str, Any] = {}

        # ===== internal state =====
        # url -> {"base_64_url": ..., "caption": ..., "download_status": ..., "summarize_status": ...}
        self._image_cache: dict[str, dict[str, str]] = {}
        self._downloaded_images: dict[str, str] = {}
        self._image_captions: dict[str, str] = {}
        self._page_stats: dict[str, int | float] = self._new_page_stats()
        self._all_page_stats: dict[str, int | float] = self._new_all_page_stats()
        self._all_round_stats: dict[str, int | float] = self._new_all_round_stats()

    # * 下載和摘要拆成兩個模組
    def summarize_crawl_results_images(
        self,
        crawl_results: dict[str, dict[str, Any]],
        model: str = "gemini-3-flash-preview",
        prompt: str = DEFAULT_PROMPT,
        vlm_max_workers: int = 10,
        image_source: Literal["images", "markdown"] = "markdown",
        **litellm_kwargs: Any,
    ) -> dict[str, dict[str, Any]]:
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

        if not self.cache_download_image:
            self._downloaded_images = {}
        if not self.cache_image_captions:
            self._image_captions = {}
        if not self.cache_download_image and not self.cache_image_captions:
            self._image_cache = {}

        self._all_round_stats = self._new_all_round_stats()

        target_urls: set[str] | None = None
        enhanced_crawl_results = crawl_results
        while True:
            self._all_page_stats = self._new_all_page_stats()
            enhanced_crawl_results = self._summarize_crawl_results_images(
                crawl_results, target_urls
            )

            self._log_stats(self._all_page_stats, "All Image Summarize Stats")
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
            self._log_stats(self._all_round_stats, "All Rounds Image Summarize Stats")

        return enhanced_crawl_results

    def _summarize_crawl_results_images(
        self,
        crawl_results: dict[str, dict[str, Any]],
        target_urls: set[str] | None = None,
    ) -> dict[str, dict[str, Any]]:
        """摘要爬取的網頁中的所有圖片。"""
        for page_title, crawl_result in crawl_results.items():
            crawl_result_content = self._retrieve_crawl_result_content(
                crawl_result, target_urls
            )
            if crawl_result_content is None:
                continue

            log_session(
                Text.assemble("Summarizing Images in [", page_title, "]"),
                style="blue",
            )
            fit_markdown, image_urls = crawl_result_content
            self._page_stats = self._new_page_stats()

            image_uncached_urls, caption_uncached_urls = self._collect_cached_items(
                image_urls
            )
            self._download_images(image_uncached_urls)
            self._generate_image_captions(caption_uncached_urls)
            crawl_result["enhanced_markdown"] = self._enhance_markdown(
                fit_markdown, image_urls
            )
            for image in crawl_result.get("images", []):
                url = image.get("url", "")
                if url in self._image_captions:
                    image["caption"] = self._image_captions[url]

            self._log_stats(self._page_stats)
            self._all_page_stats["success"] += self._page_stats["success"]
            self._all_page_stats["failure"] += (
                self._page_stats["download_failure"]
                + self._page_stats["summarize_failure"]
            )
            self._all_page_stats["cost_usd"] += self._page_stats["cost_usd"]

        return crawl_results

    def _collect_cached_items(
        self,
        image_urls: list[str],
    ) -> tuple[list[str], list[str]]:
        """收集快取並回傳未命中的 URL。"""
        cached_urls = set(self._image_cache.keys())

        image_uncached_urls = []
        caption_uncached_urls = []
        for image_url in image_urls:
            if image_url in cached_urls:
                cache_reused = False

                if self._image_cache[image_url]["download_status"] == "success":
                    self._downloaded_images[image_url] = self._image_cache[image_url][
                        "base_64_url"
                    ]
                    cache_reused = True
                else:
                    image_uncached_urls.append(image_url)

                if self._image_cache[image_url]["summarize_status"] == "success":
                    self._image_captions[image_url] = self._image_cache[image_url][
                        "caption"
                    ]
                    cache_reused = True
                else:
                    caption_uncached_urls.append(image_url)

                if cache_reused:
                    self._page_stats["cache_reuse"] += 1
            else:
                image_uncached_urls.append(image_url)
                caption_uncached_urls.append(image_url)

        if len(image_urls) - len(image_uncached_urls) > 0:
            logger.debug(
                "Collected download images from cache for %s/%s images",
                len(image_urls) - len(image_uncached_urls),
                len(image_urls),
            )

        if len(image_urls) - len(caption_uncached_urls) > 0:
            logger.debug(
                "Collected image captions from cache for %s/%s images",
                len(image_urls) - len(caption_uncached_urls),
                len(image_urls),
            )

        return image_uncached_urls, caption_uncached_urls

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
            image_urls = [image.get("url", "") for image in images if image.get("url")]

        if target_urls is not None and not (set(image_urls) & target_urls):
            return None

        if not image_urls:
            crawl_result["enhanced_markdown"] = fit_markdown
            return None

        return fit_markdown, image_urls

    def _download_images(
        self,
        image_urls: list[str],
    ) -> None:
        """平行下載圖片，回傳成功下載圖片。"""
        max_workers = self.vlm_max_workers
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_image_url = {
                executor.submit(self._download_image, url): url for url in image_urls
            }
            futures = list(future_to_image_url.keys())

            with TaskCountProgress() as progress:
                task_id = progress.add_task("Downloading images...", total=len(futures))

                for future in as_completed(futures):
                    image_url = future_to_image_url[future]
                    image_base64_url, download_status = future.result()

                    if "failure" in download_status or image_base64_url is None:
                        self._page_stats["download_failure"] += 1
                        self._image_cache[image_url] = {
                            "base_64_url": "",
                            "download_status": download_status,
                            "caption": "",
                            "summarize_status": "failed",
                        }
                        self._downloaded_images[image_url] = ""
                        self._image_captions[image_url] = ""
                    else:
                        self._downloaded_images[image_url] = image_base64_url
                        self._image_cache[image_url] = {
                            "base_64_url": image_base64_url,
                            "download_status": "success",
                            "caption": "",
                            "summarize_status": "",
                        }

                    progress.update(task_id, advance=1)

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
            req = Request(url, headers=headers)
            with urlopen(req, timeout=download_timeout) as resp:
                data = resp.read()
                raw_content_type: str = resp.headers.get("Content-Type", "")
        except (URLError, TimeoutError, OSError) as e:
            logger.warning("Image download failed (url=%s): %s", url, e)
            return None, "failed"

        content_type: str = raw_content_type.split(";")[0].strip()
        if not content_type.startswith("image/"):
            logger.warning(
                "Image content-type is not image/* (url=%s, content_type=%s)",
                url,
                content_type or "<empty>",
            )
            return None, "failed"

        b64 = base64.standard_b64encode(data).decode("ascii")
        data_url = f"data:{content_type};base64,{b64}"
        logger.debug("Image download succeeded (url=%s)", url)

        return data_url, "success"

    def _generate_image_captions(
        self,
        image_urls: list[str],
    ) -> None:
        """為已下載成功的圖片取得 caption。"""
        if not image_urls:
            return

        images = {}
        for url in image_urls:
            if (
                self._downloaded_images.get(url) is not None
                and self._downloaded_images[url] != ""
            ):
                images[url] = self._downloaded_images[url]

        caption_results = asyncio.run(self._agenerate_image_captions(images))
        # logger.debug(
        #     "%s/%s image captions generate succeeded",
        #     len(caption_results),
        #     len(images),
        # )

        for image_url, image_caption, summarize_status, cost_usd in caption_results:
            if summarize_status == "success":
                self._page_stats["success"] += 1
                self._page_stats["cost_usd"] += cost_usd
            else:
                self._page_stats["summarize_failure"] += 1

            self._image_cache[image_url]["caption"] = image_caption
            self._image_cache[image_url]["summarize_status"] = summarize_status
            self._image_captions[image_url] = image_caption

    async def _agenerate_image_captions(
        self,
        images: dict[str, str],
    ) -> list[tuple[str, str, str, float]]:
        """對圖片批次平行摘要，回傳 (url, caption, status, cost)。"""
        tasks: list[asyncio.Task[tuple[str, str, str, float]]] = []
        for image_url, image_base64_url in images.items():
            task = asyncio.create_task(
                self._agenerate_image_caption_task(image_url, image_base64_url)
            )
            tasks.append(task)

        results: list[tuple[str, str, str, float]] = []
        with TaskCountProgress() as progress:
            task_id = progress.add_task("Generating captions...", total=len(tasks))

            for completed_task in asyncio.as_completed(tasks):
                try:
                    (
                        image_url,
                        image_caption,
                        summarize_status,
                        cost_usd,
                    ) = await completed_task
                    results.append(
                        (image_url, image_caption, summarize_status, cost_usd)
                    )
                    # logger.debug(
                    #     "Image summarization %s (url=%s, cost_usd=$%.6f)",
                    #     summarize_status,
                    #     image_url,
                    #     cost_usd,
                    # )
                except Exception as e:
                    logger.warning(
                        "Image summarization task failed unexpectedly: %s",
                        e,
                        exc_info=True,
                    )
                finally:
                    progress.update(task_id, advance=1)

        return results

    async def _agenerate_image_caption_task(
        self,
        image_url: str,
        image_base64_url: str,
    ) -> tuple[str, str, str, float]:
        semaphore = asyncio.Semaphore(max(1, self.vlm_max_workers))
        async with semaphore:
            (
                image_caption,
                summarize_status,
                cost_usd,
            ) = await self._agenerate_image_caption(image_base64_url)
            return image_url, image_caption, summarize_status, cost_usd

    async def _agenerate_image_caption(
        self,
        image_base64_url: str,
    ) -> tuple[str, str, float]:
        """呼叫 VLM 取得圖片描述。"""
        model = self.model
        if (
            "gemini" in self.model.lower()
        ):  # lite llm 使用 gemini 模型要加上 "gemini/" 前綴
            model = f"gemini/{model}"

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
        api_key = self._get_api_key()
        litellm_kwargs: dict[str, Any] = {}
        litellm_kwargs["api_key"] = api_key  # 避免 api key 洩漏
        litellm_kwargs.update(self.litellm_kwargs)
        image_caption = ""

        try:
            response = await acompletion(
                model=model,
                messages=messages,
                stream=False,
                **litellm_kwargs,
            )
        except Exception as e:
            logger.warning("Image summarization failed: %s", e, exc_info=True)
            return image_caption, "failed", 0.0

        cost_usd = completion_cost(completion_response=response)
        self._log_caption_generation(response=response, cost_usd=cost_usd)

        choices = getattr(response, "choices", None)
        if choices and isinstance(choices, (list, tuple)) and len(choices) > 0:
            choice = choices[0]
            message = getattr(choice, "message", None)
            if message:
                msg_content = getattr(message, "content", None)
                if isinstance(msg_content, str):
                    image_caption = msg_content.strip()

        return image_caption, "success", cost_usd

    def _get_api_key(self) -> str:
        """根據模型名稱推斷環境變數，並傳回有效的 API 金鑰。"""
        api_key_name: str | None = None
        for keyword, key_var in VLM_MODEL_TO_API_KEY.items():
            if keyword.lower() in self.model.lower():
                api_key_name = key_var
                break

        if api_key_name is None:
            raise EnvironmentVariableError(
                f"無法根據模型名稱 '{self.model}' 推斷 API key 變數。"
                f"請確保模型名稱包含 {list(VLM_MODEL_TO_API_KEY.keys())}"
            )

        load_dotenv()
        api_key = os.getenv(api_key_name)
        if api_key is None:
            raise EnvironmentVariableError(
                f"環境變數 {api_key_name} 未設定。請檢查 .env 或系統環境變數。"
            )

        return api_key

    def _enhance_markdown(
        self,
        markdown: str,
        image_urls: list[str],
    ) -> str:
        """將圖片說明以適當格式插入原 markdown 中。"""
        if not self._image_captions:
            return markdown

        enhanced_markdown = ""
        lines = markdown.splitlines(keepends=True)
        enhanced_parts: list[str] = []
        index = 0
        for line in lines:
            enhanced_parts.append(line)
            line_image_urls = MARKDOWN_IMAGE_PATTERN.findall(line)
            for _ in line_image_urls:
                if index >= len(image_urls):
                    break

                url = image_urls[index]
                index += 1
                caption = self._image_captions.get(url, "")
                if caption:
                    enhanced_parts.append(
                        f"> # Image-{index}\n>\n> {caption.replace(chr(10), chr(10) + '> ')}\n"
                    )

        enhanced_markdown = "".join(enhanced_parts).rstrip()

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
            if cache_item["download_status"] == "failed"
            or cache_item["summarize_status"] == "failed"
        }
        if not failed_urls:
            return None

        for failed_url in failed_urls:
            self._image_cache.pop(failed_url, None)
            self._downloaded_images.pop(failed_url, None)
            # self._image_captions.pop(failed_url, None)

        return failed_urls, success_rate

    # * 重試機制根據 max retries 動態生成等待時間
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
    def _log_caption_generation(response=None, cost_usd=None) -> None:
        caption_generation_log = "Caption generation succeeded"

        if response is not None and cost_usd is not None:
            usage = getattr(response, "usage", None)
            prompt_tokens = getattr(usage, "prompt_tokens", None) if usage else None
            completion_tokens = (
                getattr(usage, "completion_tokens", None) if usage else None
            )
            total_tokens = getattr(usage, "total_tokens", None) if usage else None
            cost_usd_string = f"${cost_usd:.6f}"
            caption_generation_log += f" (cost_usd={cost_usd_string} prompt_tokens={prompt_tokens} completion_tokens={completion_tokens} total_tokens={total_tokens})"

        logger.debug(caption_generation_log)

    def override_init_config(self, **init_kwargs) -> None:
        """覆寫建構子參數。"""
        self.download_timeout = init_kwargs.get(
            "download_timeout", self.download_timeout
        )
        self.success_threshold = init_kwargs.get(
            "success_threshold", self.success_threshold
        )
        self.max_retries = init_kwargs.get("max_retries", self.max_retries)
        self.cache_download_image = init_kwargs.get(
            "cache_download_images",
            init_kwargs.get("cache_download_image", self.cache_download_image),
        )
        self.cache_image_captions = init_kwargs.get(
            "cache_image_captions", self.cache_image_captions
        )
