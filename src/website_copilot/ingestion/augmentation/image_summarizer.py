import asyncio
import base64
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, astuple, dataclass, fields
from typing import Any, Literal
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from litellm import acompletion, completion_cost
from rich.table import Table
from rich.text import Text

from website_copilot.utils.llm_provider import get_api_key, resolve_provider
from website_copilot.utils.text_helper import MARKDOWN_IMAGE_PATTERN
from website_copilot.utils.log_helper import (
    TaskCountProgress,
    log_session,
    print_log,
    record_cost,
)

logger = logging.getLogger(__name__)


# VLM（OpenAI）僅支援 png / jpeg / gif / webp，其他格式（如 svg、avif）直接略過
SUPPORTED_IMAGE_CONTENT_TYPES = frozenset(
    {"image/png", "image/jpeg", "image/gif", "image/webp"}
)
UNSUPPORTED_IMAGE_SUFFIXES = (".svg", ".avif", ".bmp", ".ico", ".tif", ".tiff")


@dataclass
class ImageEntry:
    """單張圖片的下載與摘要結果（status 為 "success"／"failed"，尚未進行時為空字串）。"""

    base64_url: str = ""
    download_status: str = ""
    caption: str = ""
    summarize_status: str = ""


@dataclass
class PageStats:
    """單頁統計；欄位順序即 log 表格的欄位順序。"""

    cost_usd: float = 0.0
    success: int = 0
    download_failure: int = 0
    summarize_failure: int = 0
    cache_reuse: int = 0

    @property
    def failure(self) -> int:
        return self.download_failure + self.summarize_failure

    def __add__(self, other: "PageStats") -> "PageStats":
        return PageStats(
            *(a + b for a, b in zip(astuple(self), astuple(other), strict=True))
        )


@dataclass
class RoundStats:
    """所有輪次的累計統計（retries 為已執行的輪數）。"""

    cost_usd: float = 0.0
    success: int = 0
    failure: int = 0
    retries: int = 0


class ImageSummarizer:
    def __init__(
        self,
        *,
        download_timeout: float,
        download_max_workers: int,  # 同時下載圖片的執行緒數
        success_threshold: float,  # 圖片下載成功率低於此值則啟動重試機制
        max_retries: int,  # 最大重試次數，對應指數退避的長度 + 最後一次用 cap
    ) -> None:
        """參數皆由 ImageSummarizerConfig.init 傳入（預設值見 config）。"""
        # ===== init args =====
        self.download_timeout = download_timeout
        self.download_max_workers = download_max_workers
        self.success_threshold = success_threshold
        self.max_retries = max_retries

        # ===== summarize args =====
        self.model: str = ""
        self.prompt: str = ""
        self.summary_max_workers: int = 0
        self.image_source: str = ""
        self.litellm_kwargs: dict[str, Any] = {}
        self._litellm_model: str = ""  # 加上供應商前綴（如 openai/）的模型名稱
        self._api_key: str = ""

        # ===== internal state =====
        # 同一 run 內跨頁共用（同一張圖只下載、摘要一次）；重試時移除失敗的圖
        self._image_cache: dict[str, ImageEntry] = {}
        self._page_stats = PageStats()
        self._page_stats_by_page: list[tuple[str, PageStats]] = []
        self._all_round_stats = RoundStats()
        # 最終仍失敗的圖片：url -> (頁面, 原因)；重試成功時移除
        self._failed_images: dict[str, tuple[str, str]] = {}
        self._download_failure_reasons: dict[str, str] = {}
        self._current_page: str = ""

    # * 下載和摘要拆成兩個模組
    def summarize_crawl_results_images(
        self,
        crawl_results: dict[str, dict[str, Any]],
        *,
        model: str,
        prompt: str,
        summary_max_workers: int,
        image_source: Literal["images", "markdown"],
        **litellm_kwargs: Any,
    ) -> dict[str, dict[str, Any]]:
        """
        使用 VLM 總結所有爬取下的網頁中的圖片。
        若一輪後圖片下載成功率 < 80% 且嘗試數足夠，視為可能被擋，依指數退避自動重試。

        - crawl_results: 爬取結果列表，每個元素為 dict，包含 "fit_markdown"與 "images"。
        """
        self.model = model
        self.prompt = prompt
        self.summary_max_workers = summary_max_workers
        self.image_source = image_source
        self.litellm_kwargs = litellm_kwargs
        # 開始前解析一次：無法判斷供應商或缺 API key 時直接失敗，不逐張圖報錯
        provider = resolve_provider(model)
        self._litellm_model = f"{provider.litellm_prefix}{model}"
        self._api_key = get_api_key(provider)

        self._all_round_stats = RoundStats()
        self._failed_images = {}
        self._download_failure_reasons = {}

        target_urls: set[str] | None = None
        enhanced_crawl_results = crawl_results
        while True:
            self._page_stats_by_page = []
            enhanced_crawl_results = self._summarize_crawl_results_images(
                crawl_results, target_urls
            )

            round_total = self._round_total()
            self._log_page_stats_table("All Image Summarize Stats", round_total)
            self._all_round_stats.cost_usd += round_total.cost_usd
            self._all_round_stats.success += round_total.success
            self._all_round_stats.failure += round_total.failure
            self._all_round_stats.retries += 1

            retry_context = self._retrieve_retry_context(round_total)
            if retry_context is None:
                break

            failed_urls, success_rate = retry_context
            self._prepare_retry_urls(failed_urls, success_rate)
            target_urls = failed_urls

        if self._all_round_stats.retries > 1:
            self._log_stats(
                asdict(self._all_round_stats), "All Rounds Image Summarize Stats"
            )

        self._log_failed_images()

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
                Text.assemble("[", page_title, "]"),
                style="blue",
            )

            fit_markdown, image_urls = crawl_result_content
            self._page_stats = PageStats()
            self._current_page = page_title

            image_uncached_urls, caption_uncached_urls = self._collect_cached_items(
                image_urls
            )
            self._download_images(image_uncached_urls)
            self._generate_image_captions(caption_uncached_urls)
            crawl_result["enhanced_markdown"] = self._enhance_markdown(
                fit_markdown, image_urls
            )
            for image in crawl_result.get("images", []):
                entry = self._image_cache.get(image.get("url", ""))
                if entry is not None and entry.summarize_status:
                    image["caption"] = entry.caption

            self._page_stats_by_page.append((page_title, self._page_stats))
            record_cost(self._page_stats.cost_usd)

        return crawl_results

    def _round_total(self) -> PageStats:
        """本輪所有處理過的頁面統計加總。"""
        return sum((stats for _, stats in self._page_stats_by_page), PageStats())

    def _collect_cached_items(
        self,
        image_urls: list[str],
    ) -> tuple[list[str], list[str]]:
        """回傳需下載與需摘要（快取未命中或先前失敗）的 URL。"""
        image_uncached_urls = []
        caption_uncached_urls = []
        for image_url in image_urls:
            entry = self._image_cache.get(image_url)
            if entry is None:
                image_uncached_urls.append(image_url)
                caption_uncached_urls.append(image_url)
                continue

            download_reused = entry.download_status == "success"
            caption_reused = entry.summarize_status == "success"
            if not download_reused:
                image_uncached_urls.append(image_url)
            if not caption_reused:
                caption_uncached_urls.append(image_url)
            if download_reused or caption_reused:
                self._page_stats.cache_reuse += 1

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

        image_urls = [
            url
            for url in image_urls
            if not urlparse(url).path.lower().endswith(UNSUPPORTED_IMAGE_SUFFIXES)
        ]

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
        with ThreadPoolExecutor(max_workers=self.download_max_workers) as executor:
            future_to_image_url = {
                executor.submit(self._download_image, url): url for url in image_urls
            }
            futures = list(future_to_image_url.keys())

            with TaskCountProgress() as progress:
                task_id = progress.add_task("Downloading images...", total=len(futures))

                for future in as_completed(futures):
                    image_url = future_to_image_url[future]
                    image_base64_url = future.result()

                    if image_base64_url is None:
                        self._page_stats.download_failure += 1
                        self._image_cache[image_url] = ImageEntry(
                            download_status="failed", summarize_status="failed"
                        )
                        self._failed_images[image_url] = (
                            self._current_page,
                            self._download_failure_reasons.pop(
                                image_url, "download failed"
                            ),
                        )
                    else:
                        self._failed_images.pop(image_url, None)
                        self._image_cache[image_url] = ImageEntry(
                            base64_url=image_base64_url, download_status="success"
                        )

                    progress.update(task_id, advance=1)

    def _download_image(
        self,
        url: str,
    ) -> str | None:
        """下載圖片並轉成 image url(base64)，供 VLM 使用；失敗時回傳 None（原因記於 _download_failure_reasons）。"""
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
            logger.warning("Image download failed - %s (url=%s)", str(e), url)
            self._download_failure_reasons[url] = str(e)
            return None

        content_type: str = raw_content_type.split(";")[0].strip()
        if content_type not in SUPPORTED_IMAGE_CONTENT_TYPES:
            logger.warning(
                "Unsupported image content-type (url=%s, content_type=%s)",
                url,
                content_type or "<empty>",
            )
            self._download_failure_reasons[url] = (
                f"unsupported content-type {content_type or '<empty>'}"
            )
            return None

        b64 = base64.standard_b64encode(data).decode("ascii")
        data_url = f"data:{content_type};base64,{b64}"
        logger.debug("Image download succeeded (url=%s)", url)

        return data_url

    def _generate_image_captions(
        self,
        image_urls: list[str],
    ) -> None:
        """為已下載成功的圖片取得 caption。"""
        if not image_urls:
            return

        images = {
            url: self._image_cache[url].base64_url
            for url in image_urls
            if url in self._image_cache and self._image_cache[url].base64_url
        }

        caption_results = asyncio.run(self._agenerate_image_captions(images))
        # logger.debug(
        #     "%s/%s image captions generate succeeded",
        #     len(caption_results),
        #     len(images),
        # )

        for image_url, image_caption, summarize_status, cost_usd in caption_results:
            if summarize_status == "success":
                self._page_stats.success += 1
                self._page_stats.cost_usd += cost_usd
                self._failed_images.pop(image_url, None)
            else:
                self._page_stats.summarize_failure += 1
                self._failed_images[image_url] = (
                    self._current_page,
                    "caption generation failed",
                )

            entry = self._image_cache[image_url]
            entry.caption = image_caption
            entry.summarize_status = summarize_status

    async def _agenerate_image_captions(
        self,
        images: dict[str, str],
    ) -> list[tuple[str, str, str, float]]:
        """對圖片批次平行摘要，回傳 (url, caption, status, cost)。"""
        # 同一批 task 共用一個 semaphore 才能限制並行數；
        # 每頁的 asyncio.run 為新 event loop，故不可存成屬性跨頁共用
        semaphore = asyncio.Semaphore(self.summary_max_workers)
        tasks: list[asyncio.Task[tuple[str, str, str, float]]] = []
        for image_url, image_base64_url in images.items():
            task = asyncio.create_task(
                self._agenerate_image_caption_task(
                    semaphore, image_url, image_base64_url
                )
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
        semaphore: asyncio.Semaphore,
        image_url: str,
        image_base64_url: str,
    ) -> tuple[str, str, str, float]:
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
        litellm_kwargs: dict[str, Any] = {"api_key": self._api_key}  # 避免 api key 洩漏
        litellm_kwargs.update(self.litellm_kwargs)
        image_caption = ""

        try:
            response = await acompletion(
                model=self._litellm_model,
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

    def _enhance_markdown(
        self,
        markdown: str,
        image_urls: list[str],
    ) -> str:
        """將圖片說明以適當格式插入原 markdown 中。"""
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
                entry = self._image_cache.get(url)
                caption = entry.caption if entry is not None else ""
                if caption:
                    enhanced_parts.append(
                        f"> # Image-{index}\n>\n> {caption.replace(chr(10), chr(10) + '> ')}\n"
                    )

        return "".join(enhanced_parts).rstrip()

    def _retrieve_retry_context(
        self,
        round_total: PageStats,
    ) -> tuple[set[str], float] | None:
        """回傳重試所需資料（需重試的 URL 集合、成功率）"""
        if self._all_round_stats.retries >= self.max_retries:
            return None

        success, failure = round_total.success, round_total.failure
        total = success + failure
        if total == 0:
            return None
        success_rate = success / total
        if success_rate >= self.success_threshold:
            return None

        failed_urls = {
            url
            for url, entry in self._image_cache.items()
            if entry.download_status == "failed" or entry.summarize_status == "failed"
        }
        if not failed_urls:
            return None

        for failed_url in failed_urls:
            self._image_cache.pop(failed_url, None)

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
            bases[min(self._all_round_stats.retries, len(bases) - 1)] if bases else 30
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
            self._all_round_stats.retries + 1,
        )
        logger.warning("-" * 30)
        time.sleep(wait_sec)

    def _log_failed_images(self) -> None:
        """彙整最終仍失敗的圖片（頁面 · 原因 · 完整 URL，單行不折行）。"""
        if not self._failed_images:
            return

        log_session(f"Failed Images ({len(self._failed_images)})", style="yellow")
        for url, (page, reason) in self._failed_images.items():
            # soft_wrap：URL 不被 rich 硬折行，方便複製
            # Text 而非 str：避免 "[page]" 被 rich 當成 markup 標籤吞掉
            print_log(Text(f"[{page}] {reason}: {url}"), soft_wrap=True)

    @staticmethod
    def _truncate_page_title(title: str, max_len: int = 20) -> str:
        """裁剪過長的頁面名稱，避免壓縮表格其餘欄位的可讀性。"""
        if len(title) <= max_len:
            return title
        return title[:max_len] + "…"

    def _log_page_stats_table(self, title: str, total: PageStats) -> None:
        """彙整逐頁統計為單一表格（取代逐頁各自的 Rule + 表格）。"""
        log_session(title, style="green")

        def cells(stats: PageStats) -> list[str]:
            return [
                f"${value:.6f}" if key == "cost_usd" else str(value)
                for key, value in asdict(stats).items()
            ]

        table = Table(show_header=True, header_style="bold green")
        table.add_column("Page", style="green", no_wrap=True)
        for f in fields(PageStats):
            table.add_column(f.name, style="white")

        for page_title, stats in self._page_stats_by_page:
            table.add_row(self._truncate_page_title(page_title), *cells(stats))

        table.add_section()
        table.add_row("Total", *cells(total))
        print_log(table)

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
