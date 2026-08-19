import asyncio
import logging
import re
from typing import Any, Pattern
from urllib.parse import urlparse

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

from app.configs.website_crawler_config import KEEP_IMAGE_CONTENT_THRESHOLD
from utils.html_date_extractor import extract_date_from_html
from utils.log_helper import log_session, print_log
from utils.markdown_cleaner import clean_markdown

logger = logging.getLogger(__name__)

# URL sub-path → page_type 映射規則
PAGE_TYPE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"/news"), "announcement"),
    (re.compile(r"/publication|/paper"), "paper"),
    (re.compile(r"/members|/people|/advisor"), "personnel"),
    (re.compile(r"/blog"), "blog"),
    (re.compile(r"/events"), "event"),
]

# Markdown 內的影像 URL 擷取
MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[.*?\]\((https?://[^\s)]+)\)")


def resolve_dedup_key(url: str, path_prefix: str) -> str:
    """從 URL 產生去重鍵：截去 path_prefix 後的相對路徑。"""
    full_path = urlparse(url).path
    base = path_prefix.rstrip("/")
    relative = full_path[len(base) :].strip("/") if base else full_path.strip("/")
    return relative.replace("/", "_") or "index"


def _extract_metadata(
    url: str,
    raw_metadata: dict,
    html: str | None = None,
    response_headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """萃取內容屬性（給 LLM 閱讀 + DB pre-filter 使用）。"""
    path = urlparse(url).path

    metadata: dict[str, Any] = {
        "description": raw_metadata.get("description")
        or raw_metadata.get("og:description"),
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


def _extract_images(fit_markdown: str) -> list[dict[str, str]]:
    """萃取 Markdown 內的影像 URL。"""
    image_urls = MARKDOWN_IMAGE_PATTERN.findall(fit_markdown)
    return [{"url": url} for url in image_urls]


def _extract_crawl_info(raw_metadata: dict) -> dict:
    """萃取爬蟲環境資訊（僅供除錯／調度，不進 LLM）。"""
    return {
        "depth": raw_metadata.get("depth"),
        "parent_url": raw_metadata.get("parent_url"),
    }


class WebsiteCrawler:
    def __init__(
        self,
        max_depth: int | None = None,
        max_pages: int | None = None,
        content_threshold: float = KEEP_IMAGE_CONTENT_THRESHOLD,
        light_mode: bool = True,
        wait_for_images: bool = True,
    ) -> None:
        # ===== init args =====
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.content_threshold = content_threshold
        # TODO: light_mode 尚未實作差異化行為，僅保留介面向後相容
        self.light_mode = light_mode
        self.wait_for_images = wait_for_images

        # ===== crawl args =====
        self.url: str
        self.url_patterns: str | Pattern | list[str | Pattern] | None = None
        self.allowed_domains: str | list[str] | None = None
        self.exclude_words: list[str] | None = None
        self.path_prefix: str = "/"

        # ===== internal state =====
        self._crawl_stats: dict[str, int] = self._new_crawl_stats()

    def crawl_website(
        self,
        url: str,
        url_patterns: str | Pattern | list[str | Pattern] | None = None,
        allowed_domains: str | list[str] | None = None,
        exclude_words: list[str] | None = None,
        path_prefix: str | None = None,
    ) -> dict[str, dict] | None:
        """執行完整網站爬取流程並將結果過濾後輸出為 Markdown 檔案。"""
        self.url = url
        self.url_patterns = url_patterns
        self.allowed_domains = allowed_domains
        self.exclude_words = exclude_words
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

        enriched_results = self._safe_step(
            lambda: self._extract_crawl_results_data(filtered_results),
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

        filters: list[URLFilter] = []
        if self.url_patterns is not None:
            filters.append(URLPatternFilter(patterns=self.url_patterns))
        if self.allowed_domains is not None:
            filters.append(DomainFilter(allowed_domains=self.allowed_domains))
        filter_chain = FilterChain(filters)

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
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            results = await crawler.arun(self.url, crawler_run_config)
        if not isinstance(results, list):
            results = [results] if results else []

        return results

    def _filter_crawl_results(
        self,
        crawl_results: list,
    ) -> dict[str, dict]:
        """過濾爬取結果：排除 404 與重複頁面，回傳中間資料。

        去重鍵：從 URL path 截去 path_prefix 後的相對路徑。
        """
        filtered_results: dict[str, dict] = {}
        existed_keys: set[str] = set()

        for crawl_result in crawl_results:
            if crawl_result.status_code == 404:
                self._crawl_stats["error_pages"] += 1
                logger.debug(
                    f"Webpage {crawl_result.url} status code is 404, skipping..."
                )
                logger.debug("-" * 30)
                continue

            fit_markdown = clean_markdown(
                crawl_result.markdown.fit_markdown,
                exclude_words=self.exclude_words,
            )
            dedup_key = resolve_dedup_key(crawl_result.url, self.path_prefix)

            if dedup_key in existed_keys:
                self._crawl_stats["repeat_pages"] += 1
                logger.debug(f"Webpage {dedup_key} already exists, skipping...")
                continue
            existed_keys.add(dedup_key)

            filtered_results[dedup_key] = {
                "url": crawl_result.url,
                "fit_markdown": fit_markdown,
                "crawl_result": crawl_result,
            }
            self._crawl_stats["success_pages"] += 1

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
                "images": _extract_images(fit_markdown),
                "metadata": _extract_metadata(
                    url,
                    raw_metadata,
                    html=getattr(crawl_result, "html", None),
                    response_headers=getattr(crawl_result, "response_headers", None),
                ),
                "crawl_info": _extract_crawl_info(raw_metadata),
            }

            logger.debug(f"Successfully crawled webpage: {page_title}")
            logger.debug(f"*  URL: {url}")
            logger.debug(f"*  Depth: {raw_metadata.get('depth', 0)}")

        return enriched_results

    @staticmethod
    def _new_crawl_stats() -> dict[str, int]:
        return {
            "success_pages": 0,
            "error_pages": 0,
            "repeat_pages": 0,
        }

    @staticmethod
    def _safe_step(fn, label: str):
        """包裝 pipeline 步驟，失敗時記錄錯誤並回傳 None。"""
        try:
            return fn()
        except Exception as e:
            logger.error(f"Error during {label}: {e}")
            return None

    @staticmethod
    def _log_stats(stats: dict[str, int]) -> None:
        log_session("Website Crawling Stats", style="green")

        table = Table(show_header=True, header_style="bold green")
        table.add_column("Metric", style="green", no_wrap=True)
        table.add_column("Value", style="white")
        for key in stats:
            table.add_row(key, str(stats[key]))

        print_log(table)

    def override_init_config(self, **init_kwargs) -> None:
        """覆寫初始化參數。"""
        self.max_depth = init_kwargs.get("max_depth", self.max_depth)
        self.max_pages = init_kwargs.get("max_pages", self.max_pages)
        self.content_threshold = init_kwargs.get(
            "content_threshold", self.content_threshold
        )
        self.light_mode = init_kwargs.get("light_mode", self.light_mode)
        self.wait_for_images = init_kwargs.get("wait_for_images", self.wait_for_images)
