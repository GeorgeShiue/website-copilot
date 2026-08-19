import asyncio
import json
import logging
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any, Pattern
from urllib.parse import urlparse

import mdformat
from bs4 import BeautifulSoup
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
from utils.log_helper import log_session, print_log

logger = logging.getLogger(__name__)


# Markdown 清洗正則規則
UNICODE_WHITESPACE_PATTERN = re.compile(r"[\u200b\xa0\u3000]+")
TRAILING_WHITESPACE_PATTERN = re.compile(r"[ \t]+$", flags=re.MULTILINE)
EMPTY_ANCHOR_LINK_PATTERN = re.compile(r"\[\]\(.*?#h\.[a-z0-9]+\)")
EMPTY_LIST_NOISE_PATTERN = re.compile(r"^\s*\*\s*#{1,6}\s*$", flags=re.MULTILINE)
EMPTY_HEADING_LINE_PATTERN = re.compile(r"^(\s{0,3}#{1,6})\s*$")
SKIP_AS_HEADING_PATTERN = re.compile(r"^\s*!?\[.*?\]\(.*?\)\s*$")
EXCESSIVE_NEWLINES_PATTERN = re.compile(r"\n{3,}")
LIST_ITEM_SPACING_PATTERN = re.compile(
    r"(^[ \t]*(?:[-*+]|\d+\.)[ \t]+.*)\n{2,}(?=[ \t]*(?:[-*+]|\d+\.)[ \t]+)",
    flags=re.MULTILINE,
)
HEADING_BELOW_SPACING_PATTERN = re.compile(
    r"(^[ \t]*#{1,6}[ \t]+.*)\n{2,}", flags=re.MULTILINE
)
HEADING_ABOVE_SPACING_PATTERN = re.compile(
    r"([^\n])\n(?=[ \t]*#{1,6}[ \t]+)", flags=re.MULTILINE
)
IMAGE_ABOVE_SPACING_PATTERN = re.compile(
    r"([^\n])\n(?=[ \t]*!\[.*?\]\()", flags=re.MULTILINE
)
IMAGE_FOLLOW_TEXT_PATTERN = re.compile(r"(!\[.*?\]\(.*?\))\s*(?=\S)")

MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[.*?\]\((https?://[^\s)]+)\)")

# URL sub-path → page_type 映射規則
PAGE_TYPE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"/news"), "announcement"),
    (re.compile(r"/publication|/paper"), "paper"),
    (re.compile(r"/members|/people|/advisor"), "personnel"),
    (re.compile(r"/blog"), "blog"),
    (re.compile(r"/events"), "event"),
]


def _extract_from_jsonld(soup: BeautifulSoup) -> tuple[str | None, str | None]:
    """從 JSON-LD 擷取 datePublished / dateModified。"""
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.string or "")
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict):
                    pub = item.get("datePublished") or item.get("dateCreated")
                    mod = item.get("dateModified")
                    if pub or mod:
                        return pub, mod
        except (json.JSONDecodeError, TypeError):
            continue
    return None, None


def _extract_meta_property(soup: BeautifulSoup, prop: str) -> str | None:
    """從 `<meta property="...">` 擷取 content 屬性。"""
    tag = soup.select_one(f'meta[property="{prop}"]')
    content = tag.get("content") if tag else None
    return str(content) if content is not None else None


def _extract_time_element(soup: BeautifulSoup) -> str | None:
    """從 `<time>` 元素擷取 datetime 屬性。"""
    for selector in (
        'time[itemprop="datePublished"]',
        "time[datetime]",
    ):
        tag = soup.select_one(selector)
        if tag:
            dt = tag.get("datetime")
            if dt is not None:
                return str(dt)
    return None


def _extract_meta_name(soup: BeautifulSoup, names: tuple[str, ...]) -> str | None:
    """從 `<meta name="...">` 擷取 content 屬性（不區分大小寫）。"""
    for name in names:
        tag = soup.select_one(f'meta[name="{name}" i]')
        if tag:
            content = tag.get("content")
            if content is not None:
                return str(content)
    return None


def _parse_http_date(date_str: str | None) -> str | None:
    """解析 HTTP 日期格式（RFC 7231），回傳 ISO 8601。"""
    if not date_str:
        return None
    try:
        return parsedate_to_datetime(date_str).isoformat()
    except (ValueError, TypeError):
        return None


def _normalize_to_iso8601(date_str: str | None) -> str | None:
    """嘗試將各種日期格式標準化為 ISO 8601（YYYY-MM-DD）。"""
    if not date_str:
        return None
    # 已經是 ISO 格式：取 YYYY-MM-DD 部分
    if re.match(r"\d{4}-\d{2}-\d{2}", date_str):
        return date_str[:10]
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _extract_date_from_html(
    html: str,
    response_headers: dict[str, str] | None = None,
) -> dict[str, str | None]:
    """從 HTML 原始碼 + HTTP 標頭擷取發佈/修改日期。

    解析優先級：
      1. JSON-LD datePublished
      2. <meta property="article:published_time">
      3. <time datetime> with itemprop="datePublished"
      4. Generic meta name="date" / "pubdate"
      5. Dublin Core dc.date
      6. HTTP Last-Modified

    回傳 ISO 8601 格式（YYYY-MM-DD）。無法擷取時對應值為 None。
    """
    published_date: str | None = None
    modified_date: str | None = None

    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        logger.debug("BeautifulSoup parsing failed, skipping HTML date extraction")
        return {"published_date": None, "modified_date": None}

    # --- Priority 1: JSON-LD datePublished / dateModified ---
    published_date, modified_date = _extract_from_jsonld(soup)

    # --- Priority 2: <meta property="article:published_time"> ---
    if published_date is None:
        published_date = _extract_meta_property(soup, "article:published_time")

    # --- Priority 3: <time datetime> elements ---
    if published_date is None:
        published_date = _extract_time_element(soup)

    # --- Priority 4: Generic meta date tags ---
    if published_date is None:
        published_date = _extract_meta_name(soup, ("date", "pubdate", "publish_date"))

    # --- Priority 5: Dublin Core dc.date ---
    if published_date is None:
        published_date = _extract_meta_name(soup, ("dc.date", "dc.date.created"))

    # --- Priority 6: HTTP Last-Modified ---
    if published_date is None and response_headers:
        published_date = _parse_http_date(response_headers.get("Last-Modified"))

    # modified_date 從 article:modified_time 補充
    if modified_date is None:
        modified_date = _extract_meta_property(soup, "article:modified_time")

    return {
        "published_date": _normalize_to_iso8601(published_date),
        "modified_date": _normalize_to_iso8601(modified_date),
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

        try:
            crawl_results = asyncio.run(self._crawl_website_async())
        except Exception as e:
            logger.error(f"Error during crawling: {e}")
            return None

        try:
            filtered_results = self._filter_crawl_results(crawl_results)
        except Exception as e:
            logger.error(f"Error during filtering crawl results: {e}")
            return None

        try:
            enriched_results = self._extract_crawl_results_data(filtered_results)
        except Exception as e:
            logger.error(f"Error during enriching crawl results: {e}")
            return None

        self._log_stats(self._crawl_stats)

        return enriched_results

    async def _crawl_website_async(
        self,
    ) -> list:
        """以指定爬蟲設定非同步抓取網站頁面並回傳原始爬取結果。"""
        browser_config = BrowserConfig(
            # headless=False, # 是否顯示瀏覽器
        )

        pruning_content_filter = PruningContentFilter(
            threshold=self.content_threshold,
            # threshold_type="dynamic",
        )

        filters: list[URLFilter] = []
        if self.url_patterns is not None:
            filters.append(URLPatternFilter(patterns=self.url_patterns))
        if self.allowed_domains is not None:
            filters.append(
                DomainFilter(
                    allowed_domains=self.allowed_domains,
                    # blocked_domains=["old.docs.example.com"],
                )
            )
        filter_chain = FilterChain(filters)

        bfs_deep_crawl_strategy_kwargs = {}
        bfs_deep_crawl_strategy_kwargs["filter_chain"] = filter_chain
        if self.max_depth is not None:
            bfs_deep_crawl_strategy_kwargs["max_depth"] = self.max_depth
        if self.max_pages is not None:
            bfs_deep_crawl_strategy_kwargs["max_pages"] = self.max_pages
        bfs_deep_crawl_strategy = BFSDeepCrawlStrategy(**bfs_deep_crawl_strategy_kwargs)

        crawler_run_config = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=pruning_content_filter
            ),
            deep_crawl_strategy=bfs_deep_crawl_strategy,
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

            fit_markdown = crawl_result.markdown.fit_markdown
            fit_markdown = self._clean_markdown(fit_markdown)

            dedup_key = self._resolve_dedup_key(crawl_result.url)

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

    def _resolve_dedup_key(self, url: str) -> str:
        """從 URL 產生去重鍵：截去 path_prefix 後的相對路徑。"""
        full_path = urlparse(url).path
        base = self.path_prefix.rstrip("/")
        relative = full_path[len(base) :].strip("/") if base else full_path.strip("/")
        return relative.replace("/", "_") or "index"

    def _clean_markdown(self, markdown: str) -> str:
        """優化後的 Markdown 清理邏輯：混合 Regex 與 mdformat。"""
        # --- 資料清洗 ---
        if self.exclude_words is not None:
            markdown = "".join(
                line
                for line in markdown.splitlines(keepends=True)
                if not any(word in line for word in self.exclude_words)
            )
        markdown = EMPTY_ANCHOR_LINK_PATTERN.sub("", markdown)
        markdown = EMPTY_LIST_NOISE_PATTERN.sub("", markdown)

        # ----- 結構修復 (前) -----
        markdown = self._promote_empty_heading_line(markdown)
        markdown = IMAGE_ABOVE_SPACING_PATTERN.sub(r"\1\n\n", markdown)

        # ----- 格式化 -----
        try:
            markdown = mdformat.text(
                markdown,
                options={"wrap": "no"},  # 避免強制換行
                extensions={"gfm"},  # 支援表格
            )
        except Exception as e:
            logger.error(f"Error during mdformat formatting: {e}")

        # ----- 結構修復 (後) -----
        markdown = IMAGE_FOLLOW_TEXT_PATTERN.sub(r"\1\n", markdown)
        markdown = IMAGE_ABOVE_SPACING_PATTERN.sub(r"\1\n\n", markdown)

        return markdown

    @staticmethod
    def _promote_empty_heading_line(fit_markdown: str) -> str:
        """將空標題行提升為下一個可用文字標題，並保留中間內容。"""
        lines = fit_markdown.splitlines(keepends=True)
        fixed_lines: list[str] = []
        i = 0

        while i < len(lines):
            current_line = lines[i]
            heading_match = EMPTY_HEADING_LINE_PATTERN.match(
                current_line.rstrip("\r\n")
            )
            if heading_match:
                j = i + 1
                while j < len(lines):
                    candidate = lines[j].strip()
                    if candidate and not SKIP_AS_HEADING_PATTERN.match(candidate):
                        fixed_lines.append(f"{heading_match.group(1)} {candidate}\n")
                        fixed_lines.extend(lines[i + 1 : j])
                        i = j + 1
                        break
                    j += 1
                else:
                    fixed_lines.append(current_line)
                    i += 1
            else:
                fixed_lines.append(current_line)
                i += 1

        return "".join(fixed_lines)

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

        # page_type — 從 URL sub-path 匹配
        for pattern, label in PAGE_TYPE_PATTERNS:
            if pattern.search(path):
                metadata["page_type"] = label
                break

        # HTML 日期擷取
        if html:
            date_info = _extract_date_from_html(html, response_headers)
            if date_info["published_date"]:
                metadata["published_date"] = date_info["published_date"]
            if date_info["modified_date"]:
                metadata["modified_date"] = date_info["modified_date"]

        return metadata

    @staticmethod
    def _extract_images(fit_markdown: str) -> list[dict[str, str]]:
        """萃取 Markdown 內的影像 URL。"""
        image_urls = MARKDOWN_IMAGE_PATTERN.findall(fit_markdown)
        images = [{"url": url} for url in image_urls]
        return images

    @staticmethod
    def _extract_crawl_info(raw_metadata: dict) -> dict:
        """萃取爬蟲環境資訊（僅供除錯／調度，不進 LLM）。"""
        crawl_info = {
            "depth": raw_metadata.get("depth"),
            "parent_url": raw_metadata.get("parent_url"),
        }

        return crawl_info

    @staticmethod
    def _new_crawl_stats() -> dict[str, int]:
        return {
            "success_pages": 0,
            "error_pages": 0,
            "repeat_pages": 0,
            # "image_count": 0,
        }

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
