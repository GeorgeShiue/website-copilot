"""Augmenter：篩選 → 下載 → 解析 → 回寫。

首版只處理頁面圖片：ImageCollector 跨頁收集不重複的圖片，共用下載器整批下載，ImageCaptioner
整批呼叫 VLM，描述內嵌回各頁的 enhanced_markdown 與 images[].caption。成功率低於門檻時
（懷疑被封鎖或限流）依指數退避整輪重做可恢復的失敗項目。
"""

import logging
import random
import time
from collections.abc import Callable, Iterable
from dataclasses import asdict, astuple, dataclass, fields
from typing import Any, Literal, Protocol

from rich.table import Table
from rich.text import Text

from website_copilot.ingestion.augmentation.assets import Asset
from website_copilot.ingestion.augmentation.collectors import ImageCollector
from website_copilot.ingestion.augmentation.processors.image_captioner import (
    ImageCaptioner,
    to_image_data_url,
)
from website_copilot.ingestion.augmentation.processors.image_filter import (
    content_sha1,
    image_long_edge,
)
from website_copilot.utils.http_downloader import DownloadResult
from website_copilot.utils.log_helper import (
    TaskCountProgress,
    log_session,
    print_log,
    record_cost,
)
from website_copilot.utils.text_helper import MARKDOWN_IMAGE_PATTERN

logger = logging.getLogger(__name__)

# 403／429 常為封鎖或限流，與逾時、連線錯誤、5xx 同屬可恢復；其餘 4xx 為永久錯誤
RECOVERABLE_STATUS_CODES = frozenset({403, 429})


class Downloader(Protocol):
    """HttpDownloader 的介面（測試以 fake 取代）。"""

    def download(
        self,
        urls: Iterable[str],
        on_complete: Callable[[DownloadResult], None] | None = None,
    ) -> dict[str, DownloadResult]: ...


@dataclass
class ImageEntry:
    """單張圖片的下載與摘要結果（status 為 "success"／"failed"，尚未進行時為空字串）。"""

    base64_url: str = ""
    download_status: str = ""
    caption: str = ""
    summarize_status: str = ""
    failure_reason: str = ""
    # 失敗是否可恢復（逾時、連線錯誤、5xx、429、403、VLM 失敗）
    recoverable: bool = False
    # 已下載但不送 VLM（長邊小於 min_size），不產生描述
    skip_reason: str = ""
    # 內容與此 URL 的圖片相同，共用其描述（本身不送 VLM）
    shared_with: str = ""


@dataclass
class PageStats:
    """單頁統計；欄位順序即 log 表格的欄位順序。"""

    cost_usd: float = 0.0
    success: int = 0
    download_failure: int = 0
    summarize_failure: int = 0
    skipped: int = 0  # 小圖略過
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


class Augmenter:
    def __init__(
        self,
        *,
        downloader: Downloader,  # 共用下載器：並行上限、單一請求重試、大小上限由它負責
        success_threshold: float,  # 成功率低於此值則啟動整輪重試機制
        max_retries: int,  # 最大輪數（含第一輪），對應指數退避的長度 + 最後一次用 cap
    ) -> None:
        """參數皆由 AugmenterConfig 傳入（預設值見 config）。"""
        # ===== init args =====
        self.downloader = downloader
        self.success_threshold = success_threshold
        self.max_retries = max_retries

        # ===== internal state =====
        # 以資源 URL 為鍵，同一 run 內跨頁共用（同一張圖只下載、摘要一次）；重試時重設失敗項目
        self._image_cache: dict[str, ImageEntry] = {}
        # 內容 sha1 → 第一個下載到該內容的 URL（共用描述的代表）
        self._content_reps: dict[str, str] = {}
        self._image_min_size = 0
        self._page_stats_by_page: list[tuple[str, PageStats]] = []
        self._all_round_stats = RoundStats()
        # 最終仍失敗的圖片：url -> (第一個引用頁面, 原因)
        self._failed_images: dict[str, tuple[str, str]] = {}

    def augment(
        self,
        crawl_results: dict[str, dict[str, Any]],
        *,
        model: str,
        prompt: str,
        image_max_concurrency: int,
        image_source: Literal["images", "markdown"],
        image_min_size: int,
        **litellm_kwargs: Any,
    ) -> dict[str, dict[str, Any]]:
        """使用 VLM 描述所有爬取頁面中的圖片，並寫回各頁（就地修改後回傳）。

        送 VLM 前過濾：長邊小於 image_min_size 的圖片略過（不產生描述；0 為不過濾）；
        內容（sha1）相同的圖片只描述一次、共用描述。

        若一輪後成功率 < success_threshold，視為可能被擋，依指數退避重做可恢復的失敗項目。

        - crawl_results: 爬取結果，每個元素為 dict，包含 "fit_markdown"與 "images"。
        """
        # 開始前建立：無法判斷供應商或缺 API key 時直接失敗，不下載任何圖片
        captioner = ImageCaptioner(
            model=model,
            prompt=prompt,
            max_concurrency=image_max_concurrency,
            litellm_kwargs=litellm_kwargs,
        )
        assets = ImageCollector(image_source).collect(crawl_results)

        self._image_cache = {}
        self._content_reps = {}
        self._image_min_size = image_min_size
        self._all_round_stats = RoundStats()

        pending = assets
        while pending:
            round_stats = self._process_round(crawl_results, assets, pending, captioner)
            self._all_round_stats.cost_usd += round_stats.cost_usd
            self._all_round_stats.success += round_stats.success
            self._all_round_stats.failure += round_stats.failure
            self._all_round_stats.retries += 1

            failed_assets = self._retrieve_retry_targets(pending)
            if failed_assets is None:
                break
            pending = failed_assets

        if self._all_round_stats.retries > 1:
            self._log_stats(
                asdict(self._all_round_stats), "All Rounds Image Summarize Stats"
            )

        self._write_back(crawl_results, assets)
        self._failed_images = self._collect_failed_images(assets)
        self._log_failed_images(self._failed_images)

        return crawl_results

    # ===== 一輪：下載 → 解析 =====

    def _process_round(
        self,
        crawl_results: dict[str, dict[str, Any]],
        assets: list[Asset],
        pending: list[Asset],
        captioner: ImageCaptioner,
    ) -> PageStats:
        """處理 pending 資源（下載、摘要）並更新快取；回傳本輪統計加總。"""
        self._download(pending)
        costs = self._caption(pending, captioner)

        self._page_stats_by_page = self._page_stats(
            crawl_results, assets, pending, costs
        )
        round_total = sum((stats for _, stats in self._page_stats_by_page), PageStats())
        self._log_page_stats_table("All Image Summarize Stats", round_total)
        record_cost(round_total.cost_usd)
        return round_total

    def _download(self, pending: list[Asset]) -> None:
        """整批下載尚未成功下載的資源（所有頁面共用並行上限）。"""
        urls = [
            asset.url
            for asset in pending
            if self._image_cache.get(asset.url, ImageEntry()).download_status
            != "success"
        ]
        if not urls:
            return

        with TaskCountProgress() as progress:
            task_id = progress.add_task("Downloading images...", total=len(urls))
            results = self.downloader.download(
                urls, on_complete=lambda _result: progress.update(task_id, advance=1)
            )

        for url in urls:
            result = results[url]
            data_url, reason = None, ""
            if result.ok:
                data_url, reason = to_image_data_url(result)
                recoverable = False
            else:
                reason = result.error or "download failed"
                recoverable = self._is_recoverable(result)
                logger.warning("Image download failed - %s (url=%s)", reason, url)

            if data_url is None:
                # 下載失敗視同摘要失敗：不送 VLM，caption 為空
                self._image_cache[url] = ImageEntry(
                    download_status="failed",
                    summarize_status="failed",
                    failure_reason=reason,
                    recoverable=recoverable,
                )
            else:
                entry = ImageEntry(base64_url=data_url, download_status="success")
                self._apply_image_filters(url, result, entry)
                self._image_cache[url] = entry

        skipped = sum(self._image_cache[url].skip_reason != "" for url in urls)
        shared = sum(self._image_cache[url].shared_with != "" for url in urls)
        if skipped or shared:
            logger.info(
                "Image filter: skipped %s small images, %s images share content with another",
                skipped,
                shared,
            )

    def _apply_image_filters(
        self, url: str, result: DownloadResult, entry: ImageEntry
    ) -> None:
        """小圖略過（長邊 < image_min_size）；內容相同的圖片共用第一張的描述。"""
        assert result.content is not None
        long_edge = image_long_edge(result.content)
        if long_edge is not None and long_edge < self._image_min_size:
            entry.skip_reason = f"too small ({long_edge}px)"
            entry.base64_url = ""
            return

        representative = self._content_reps.setdefault(
            content_sha1(result.content), url
        )
        if representative != url:
            entry.shared_with = representative
            entry.base64_url = ""

    def _resolve(self, url: str) -> ImageEntry | None:
        """圖片的描述記錄：內容相同者指向代表圖片的記錄。"""
        entry = self._image_cache.get(url)
        if entry is not None and entry.shared_with:
            return self._image_cache.get(entry.shared_with, entry)
        return entry

    @staticmethod
    def _is_recoverable(result: DownloadResult) -> bool:
        """失敗是否可能因重試或等待而恢復：逾時、連線錯誤、5xx、429、403。"""
        if result.error is not None and result.error.startswith(
            ("invalid url", "exceeds max_bytes")
        ):
            return False
        status = result.status_code
        if status is None:
            return True
        return status >= 500 or status in RECOVERABLE_STATUS_CODES

    @staticmethod
    def _is_captionable(entry: ImageEntry) -> bool:
        """已下載成功、未被過濾、尚未摘要成功，需要送 VLM。"""
        return (
            entry.download_status == "success"
            and not entry.skip_reason
            and not entry.shared_with
            and entry.summarize_status != "success"
        )

    def _caption(
        self, pending: list[Asset], captioner: ImageCaptioner
    ) -> dict[str, float]:
        """為已下載成功、尚未摘要成功的資源取得 caption；回傳 url → 花費。"""
        images = {
            asset.url: self._image_cache[asset.url].base64_url
            for asset in pending
            if self._is_captionable(self._image_cache[asset.url])
        }

        costs: dict[str, float] = {}
        for image_url, image_caption, summarize_status, cost_usd in captioner.caption(
            images
        ):
            entry = self._image_cache[image_url]
            entry.caption = image_caption
            entry.summarize_status = summarize_status
            if summarize_status == "success":
                costs[image_url] = cost_usd
            else:
                entry.failure_reason = "caption generation failed"
                entry.recoverable = True

        # 呼叫失敗以外未回傳的資源（task 例外）視同摘要失敗
        for url in images:
            entry = self._image_cache[url]
            if not entry.summarize_status:
                entry.summarize_status = "failed"
                entry.failure_reason = "caption generation failed"
                entry.recoverable = True
        return costs

    # ===== 統計 =====

    def _page_stats(
        self,
        crawl_results: dict[str, dict[str, Any]],
        assets: list[Asset],
        pending: list[Asset],
        costs: dict[str, float],
    ) -> list[tuple[str, PageStats]]:
        """依頁面順序彙整本輪統計。

        每個本輪處理的資源只計一次（成功／失敗記在第一個引用頁面），其餘引用記 cache_reuse；
        本輪沒處理、但先前已成功的資源，若所在頁面本輪有處理其他資源，同樣記 cache_reuse。
        """
        pending_urls = {asset.url for asset in pending}
        touched_pages = {ref.page_key for asset in pending for ref in asset.refs}
        stats = {key: PageStats() for key in crawl_results if key in touched_pages}

        for asset in assets:
            entry = self._image_cache[asset.url]
            processed = asset.url in pending_urls
            reusable = not entry.skip_reason and (
                entry.download_status == "success"
                or entry.summarize_status == "success"
            )
            for index, ref in enumerate(asset.refs):
                if ref.page_key not in touched_pages:
                    continue
                page_stats = stats[ref.page_key]
                if not processed:
                    page_stats.cache_reuse += int(reusable)
                elif index > 0 or entry.shared_with:
                    page_stats.cache_reuse += 1
                elif entry.skip_reason:
                    page_stats.skipped += 1
                elif entry.summarize_status == "success":
                    page_stats.success += 1
                    page_stats.cost_usd += costs.get(asset.url, 0.0)
                elif entry.download_status == "failed":
                    page_stats.download_failure += 1
                else:
                    page_stats.summarize_failure += 1

        return list(stats.items())

    # ===== 重試 =====

    def _retrieve_retry_targets(self, pending: list[Asset]) -> list[Asset] | None:
        """成功率過低時回傳下一輪要重做的資源（並重設其失敗狀態）；不需重試回傳 None。

        成功率 = 成功 ÷（成功 + 可恢復失敗），以不重複資源計算；404 等永久錯誤不計入。
        """
        if self._all_round_stats.retries >= self.max_retries:
            return None

        failed_assets = [
            asset
            for asset in pending
            if self._image_cache[asset.url].summarize_status == "failed"
            and self._image_cache[asset.url].recoverable
        ]
        success = sum(
            self._image_cache[asset.url].summarize_status == "success"
            for asset in pending
        )
        total = success + len(failed_assets)
        if total == 0 or not failed_assets:
            return None
        success_rate = success / total
        if success_rate >= self.success_threshold:
            return None

        for asset in failed_assets:
            entry = self._image_cache[asset.url]
            if entry.download_status == "failed":
                del self._image_cache[asset.url]
            else:  # 下載已成功，只重做摘要
                entry.summarize_status = ""
                entry.caption = ""
                entry.failure_reason = ""
                entry.recoverable = False

        self._backoff(len(failed_assets), success_rate)
        return failed_assets

    # * 重試機制根據 max retries 動態生成等待時間
    def _backoff(self, failed_count: int, success_rate: float) -> None:
        """根據成功率與重試次數計算等待時間並等待。"""
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
            failed_count,
            wait_sec,
            self._all_round_stats.retries + 1,
        )
        logger.warning("-" * 30)
        time.sleep(wait_sec)

    # ===== 回寫 =====

    def _write_back(
        self, crawl_results: dict[str, dict[str, Any]], assets: list[Asset]
    ) -> None:
        """圖片描述寫回各頁：enhanced_markdown 與 images[].caption。"""
        pages_with_images = {ref.page_key for asset in assets for ref in asset.refs}
        for page_key, crawl_result in crawl_results.items():
            fit_markdown = crawl_result.get("fit_markdown", "")
            if page_key in pages_with_images:
                crawl_result["enhanced_markdown"] = self._enhance_markdown(fit_markdown)
            else:
                crawl_result["enhanced_markdown"] = fit_markdown

            for image in crawl_result.get("images", []):
                entry = self._resolve(image.get("url", ""))
                if entry is not None and entry.summarize_status:
                    image["caption"] = entry.caption

    def _enhance_markdown(self, markdown: str) -> str:
        """將圖片說明以適當格式插入原 markdown 中（依每張圖片自己的 URL 查描述）。"""
        enhanced_parts: list[str] = []
        index = 0
        for line in markdown.splitlines(keepends=True):
            enhanced_parts.append(line)
            for url in MARKDOWN_IMAGE_PATTERN.findall(line):
                index += 1  # 頁內圖片序號
                entry = self._resolve(url)
                caption = entry.caption if entry is not None else ""
                if caption:
                    enhanced_parts.append(
                        f"> # Image-{index}\n>\n> {caption.replace(chr(10), chr(10) + '> ')}\n"
                    )

        return "".join(enhanced_parts).rstrip()

    # ===== log =====

    def _collect_failed_images(self, assets: list[Asset]) -> dict[str, tuple[str, str]]:
        return {
            asset.url: (asset.first_page, self._image_cache[asset.url].failure_reason)
            for asset in assets
            if self._image_cache[asset.url].summarize_status == "failed"
        }

    @staticmethod
    def _log_failed_images(failed_images: dict[str, tuple[str, str]]) -> None:
        """彙整最終仍失敗的圖片（頁面 · 原因 · 完整 URL，單行不折行）。"""
        if not failed_images:
            return

        log_session(f"Failed Images ({len(failed_images)})", style="yellow")
        for url, (page, reason) in failed_images.items():
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
        """彙整逐頁統計為單一表格。"""
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
