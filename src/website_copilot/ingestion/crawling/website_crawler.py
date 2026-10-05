import asyncio
import logging
import re
from typing import Any
from urllib.parse import unquote, urlparse

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
)
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.deep_crawling.filters import (
    DomainFilter,
    FilterChain,
    URLFilter,
    URLPatternFilter,
)
from rich.table import Table

from website_copilot.ingestion.crawling.html_date_extractor import (
    extract_date_from_html,
)
from website_copilot.ingestion.crawling.markdown_cleaner import WebpageMarkdownCleaner
from website_copilot.schemas import GenerationResult
from website_copilot.utils.document_rules import DOCUMENT_EXTENSION_PATTERN
from website_copilot.utils.log_helper import log_session, print_log, record_cost
from website_copilot.utils.text_helper import MARKDOWN_IMAGE_PATTERN, clean_description

logger = logging.getLogger(__name__)

# URL sub-path → page_type 映射規則
PAGE_TYPE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"/news"), "announcement"),
    (re.compile(r"/publication|/paper"), "paper"),
    (re.compile(r"/members|/people|/advisor"), "personnel"),
    (re.compile(r"/blog"), "blog"),
    (re.compile(r"/events"), "event"),
]


class WebsiteCrawler:
    def __init__(
        self,
        *,
        max_depth: int | None,
        max_pages: int | None,
        content_threshold: float,
        light_mode: bool,
        wait_for_images: bool,
        cleaner: WebpageMarkdownCleaner,
    ) -> None:
        """參數皆由 WebsiteCrawlerConfig 傳入（預設值見 config），None 代表不限制。"""
        # ===== init args =====
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.content_threshold = content_threshold
        self.light_mode = light_mode
        self.wait_for_images = wait_for_images
        self.cleaner = cleaner

        # ===== crawl args =====
        self.url: str
        self.url_patterns: list[str] | None = None
        self.allowed_domains: list[str] | None = None
        self.path_prefix: str = "/"
        self.document_url_patterns: list[str] = []

        # ===== internal state =====
        self._crawl_stats: dict[str, int] = self._new_crawl_stats()
        self.generation_result: GenerationResult | None = None
        self.raw_pages: dict[str, str] = {}

    def crawl_website(
        self,
        *,
        url: str,
        url_patterns: list[str] | None,
        allowed_domains: list[str] | None,
        path_prefix: str | None,
        document_url_patterns: list[str] | None = None,
    ) -> dict[str, dict] | None:
        """執行完整網站爬取流程並將結果過濾後輸出為 Markdown 檔案。

        url_patterns／allowed_domains 為 None 時不過濾；path_prefix 為 None 時取起始 URL 的父路徑。
        文件 URL（通用副檔名 + document_url_patterns）不進入 BFS：瀏覽器導航會觸發下載而失敗，
        文件改由 augmenter 處理。
        """
        self.url = url
        self.url_patterns = url_patterns
        self.allowed_domains = allowed_domains
        self.document_url_patterns = list(document_url_patterns or [])
        self.generation_result = None
        self._crawl_stats = self._new_crawl_stats()

        # path_prefix: 設定檔指定 > 起始 URL 父路徑 > "/"
        if path_prefix is not None:
            self.path_prefix = path_prefix.rstrip("/")
        else:
            start_path = urlparse(url).path.rstrip("/")
            self.path_prefix = start_path.rsplit("/", 1)[0] or "/"

        crawl_results = self._safe_step(
            lambda: asyncio.run(self._crawl_website_async()), "crawling"
        )
        if crawl_results is None:
            return None

        filtered_results = self._safe_step(
            lambda: self._filter_crawl_results(crawl_results), "filtering crawl results"
        )
        if filtered_results is None:
            return None

        cleaned_results = self._safe_step(
            lambda: self._clean_results(filtered_results), "cleaning crawl results"
        )
        if cleaned_results is None:
            return None

        enriched_results = self._safe_step(
            lambda: self._extract_crawl_results_data(cleaned_results),
            "enriching crawl results",
        )
        if enriched_results is None:
            return None

        self._log_stats(self._crawl_stats)

        return enriched_results

    async def _crawl_website_async(self) -> list:
        """以指定爬蟲設定非同步抓取網站頁面並回傳原始爬取結果。"""
        browser_config = BrowserConfig()

        pruning_content_filter = PruningContentFilter(
            threshold=self.content_threshold,
        )

        filter_chain = self._build_filter_chain()

        strategy_kwargs: dict[str, Any] = {"filter_chain": filter_chain}
        if self.max_depth is not None:
            strategy_kwargs["max_depth"] = self.max_depth
        if self.max_pages is not None:
            strategy_kwargs["max_pages"] = self.max_pages
        bfs_strategy = BFSDeepCrawlStrategy(**strategy_kwargs)

        crawler_run_config = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=pruning_content_filter,
            ),
            deep_crawl_strategy=bfs_strategy,
            wait_for_images=self.wait_for_images,
            verbose=False,  # 關閉 crawl4ai 逐頁 FETCH/SCRAPE/COMPLETE，明細改由 _filter_crawl_results 輸出
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            results = await crawler.arun(self.url, crawler_run_config)
        if not isinstance(results, list):
            results = [results] if results else []

        return results

    def _build_filter_chain(self) -> FilterChain:
        """BFS 的 URL 過濾：先排除文件 URL，再套用站點的 url_patterns／allowed_domains。"""
        # 排除文件 URL（reverse：符合者不通過）；副檔名規則為不分大小寫的 regex
        document_patterns: list[str | re.Pattern] = [
            DOCUMENT_EXTENSION_PATTERN,
            *self.document_url_patterns,
        ]
        filters: list[URLFilter] = [
            URLPatternFilter(patterns=document_patterns, reverse=True)
        ]
        if self.url_patterns is not None:
            # URLPatternFilter 的參數型別為 list[str | Pattern]（list 不變性，需轉型）
            patterns: list[str | re.Pattern] = list(self.url_patterns)
            filters.append(URLPatternFilter(patterns=patterns))
        if self.allowed_domains is not None:
            filters.append(DomainFilter(allowed_domains=self.allowed_domains))
        return FilterChain(filters)

    def _filter_crawl_results(
        self,
        crawl_results: list,
    ) -> dict[str, dict]:
        """過濾爬取結果：排除 404 與重複頁面，回傳中間資料（fit_markdown 為未清理原文）。

        去重鍵：從 URL path 截去 path_prefix 後的相對路徑。
        """
        filtered_results: dict[str, dict] = {}

        for crawl_result in crawl_results:
            if crawl_result.status_code == 404:
                self._crawl_stats["error_404"] += 1
                logger.info(
                    f"Skip {unquote(crawl_result.url)} (error: status code 404)"
                )
                continue

            if not crawl_result.success:
                self._crawl_stats["error_failed"] += 1
                logger.info(
                    f"Skip {unquote(crawl_result.url)} "
                    f"(error: {crawl_result.error_message or 'crawl failed'})"
                )
                continue

            if crawl_result.markdown is None:
                self._crawl_stats["error_no_markdown"] += 1
                logger.info(f"Skip {unquote(crawl_result.url)} (error: no markdown)")
                continue

            dedup_key = self._resolve_dedup_key(crawl_result.url, self.path_prefix)
            if dedup_key in filtered_results:
                self._crawl_stats["repeat_pages"] += 1
                logger.info(
                    f"Skip {unquote(crawl_result.url)} (duplicate of {dedup_key})"
                )
                continue

            filtered_results[dedup_key] = {
                "url": crawl_result.url,
                "fit_markdown": crawl_result.markdown.fit_markdown,
                "crawl_result": crawl_result,
            }
            self._crawl_stats["success_pages"] += 1

        return filtered_results

    def _clean_results(self, filtered_results: dict[str, dict]) -> dict[str, dict]:
        """由 LLM 產生 exclude_words 並逐頁清理 fit_markdown。

        LLM 步驟失敗會拋出例外，由 _safe_step 讓整個爬取失敗。
        """
        self.raw_pages = {k: d["fit_markdown"] for k, d in filtered_results.items()}
        self.generation_result = self.cleaner.generate_exclude_words(self.raw_pages)
        if self.generation_result:
            record_cost(self.generation_result.cost_usd)
        exclude_words = self.generation_result.words if self.generation_result else None
        cleaned = self.cleaner.clean_pages(self.raw_pages, exclude_words)
        for key, fit_markdown in cleaned.items():
            filtered_results[key]["fit_markdown"] = fit_markdown
        return filtered_results

    def _extract_crawl_results_data(
        self, filtered_results: dict[str, dict]
    ) -> dict[str, dict]:
        """從過濾後的中間資料萃取影像、metadata、crawl_info，產出最終結構。"""
        enriched_results = {}
        for page_title, data in filtered_results.items():
            logger.debug("-" * 30)

            fit_markdown = data["fit_markdown"]
            crawl_result = data["crawl_result"]
            url: str = crawl_result.url
            raw_metadata: dict = crawl_result.metadata

            enriched_results[page_title] = {
                "url": url,
                "fit_markdown": fit_markdown,
                "images": self._extract_images(fit_markdown),
                "metadata": self._extract_metadata(
                    url,
                    raw_metadata,
                    html=getattr(crawl_result, "html", None),
                    response_headers=getattr(crawl_result, "response_headers", None),
                ),
                "crawl_info": self._extract_crawl_info(raw_metadata),
            }

            logger.debug(f"Successfully crawled webpage: {page_title}")
            logger.debug(f"*  URL: {url}")
            logger.debug(f"*  Depth: {raw_metadata.get('depth', 0)}")

        return enriched_results

    @staticmethod
    def _resolve_dedup_key(url: str, path_prefix: str) -> str:
        """從 URL 產生去重鍵：截去 path_prefix 後的相對路徑。

        path 與 path_prefix 皆先做百分比解碼，使 `/news/碩論口試` 與
        `/news/%E7%A2%A9...` 得到相同的鍵。
        """
        full_path = unquote(urlparse(url).path)
        base = unquote(path_prefix).rstrip("/")
        relative = full_path[len(base) :].strip("/") if base else full_path.strip("/")
        return relative.replace("/", "_") or "index"

    @staticmethod
    def _extract_metadata(
        url: str,
        raw_metadata: dict,
        html: str | None = None,
        response_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """萃取內容屬性（給 LLM 閱讀 + DB pre-filter 使用）。"""
        path = urlparse(url).path

        metadata: dict[str, Any] = {
            "description": clean_description(
                raw_metadata.get("description") or raw_metadata.get("og:description")
            ),
            "page_type": "general",
        }

        for pattern, label in PAGE_TYPE_PATTERNS:
            if pattern.search(path):
                metadata["page_type"] = label
                break

        if html:
            date_info = extract_date_from_html(html, response_headers)
            if date_info["published_date"]:
                metadata["published_date"] = date_info["published_date"]
            if date_info["modified_date"]:
                metadata["modified_date"] = date_info["modified_date"]

        return metadata

    @staticmethod
    def _extract_images(fit_markdown: str) -> list[dict[str, str]]:
        """萃取 Markdown 內的影像 URL。"""
        image_urls = MARKDOWN_IMAGE_PATTERN.findall(fit_markdown)
        return [{"url": url} for url in image_urls]

    @staticmethod
    def _extract_crawl_info(raw_metadata: dict) -> dict:
        """萃取爬蟲環境資訊（僅供除錯／調度，不進 LLM）。"""
        return {
            "depth": raw_metadata.get("depth"),
            "parent_url": raw_metadata.get("parent_url"),
        }

    @staticmethod
    def _new_crawl_stats() -> dict[str, int]:
        return {
            "success_pages": 0,
            "error_404": 0,
            "error_failed": 0,
            "error_no_markdown": 0,
            "repeat_pages": 0,
        }

    @staticmethod
    def _safe_step(fn, label: str):
        """包裝 pipeline 步驟，失敗時記錄錯誤並回傳 None。"""
        try:
            return fn()
        except Exception:
            logger.exception("Error during %s", label)
            return None

    @staticmethod
    def _log_stats(stats: dict[str, int]) -> None:
        log_session("Website Crawling Stats", style="green")

        table = Table(show_header=True, header_style="bold green")
        table.add_column("Metric", style="green", no_wrap=True)
        table.add_column("Value", style="white")
        for key, value in stats.items():
            table.add_row(key, str(value))

        print_log(table)
