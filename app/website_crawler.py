import asyncio
import logging
import re
from typing import Pattern

import mdformat
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

from app.website_crawler_config import KEEP_IMAGE_CONTENT_THRESHOLD
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

# 標題正則規則
HEADING_PATTERN = re.compile(r"^#+\s*(.+)", flags=re.MULTILINE)
INVALID_FILENAME_CHARS_PATTERN = re.compile(r"[\\/:\"*?<>|]")
WHITESPACE_SEQUENCE_PATTERN = re.compile(r"\s+")

MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[.*?\]\((https?://[^\s)]+)\)")


class WebsiteCrawler:
    def __init__(
        self,
        max_depth: int,
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
        self.exclude_words: tuple[str, ...] | None = None

        # ===== internal state =====
        self._crawl_stats: dict[str, int] = self._new_crawl_stats()

    def crawl_website(
        self,
        url: str,
        url_patterns: str | Pattern | list[str | Pattern] | None = None,
        allowed_domains: str | list[str] | None = None,
        exclude_words: tuple[str, ...] | None = None,
    ) -> dict[str, dict] | None:
        """執行完整網站爬取流程並將結果過濾後輸出為 Markdown 檔案。"""
        self.url = url
        self.url_patterns = url_patterns
        self.allowed_domains = allowed_domains
        self.exclude_words = exclude_words
        self._crawl_stats = self._new_crawl_stats()

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

        self._log_stats(self._crawl_stats)

        return filtered_results

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

        if self.max_pages is not None:
            bfs_deep_crawl_strategy = BFSDeepCrawlStrategy(
                max_depth=self.max_depth,
                filter_chain=filter_chain,
                max_pages=self.max_pages,
            )
        else:
            bfs_deep_crawl_strategy = BFSDeepCrawlStrategy(
                max_depth=self.max_depth,
                filter_chain=filter_chain,
            )

        crawler_run_config = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=pruning_content_filter
            ),
            deep_crawl_strategy=bfs_deep_crawl_strategy,
            wait_for_images=self.wait_for_images,
            # process_iframes=True,
            # cache_mode=CacheMode.ENABLED,
            # stream=True
            # excluded_tags=["header"],
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
        """過濾爬取結果內容並統計資訊後儲存可用頁面資料。"""
        filtered_results = {}
        existed_page_title = set()

        for crawl_result in crawl_results:
            logger.debug("-" * 30)
            if crawl_result.status_code == 404:
                self._crawl_stats["error_pages"] += 1
                logger.debug(
                    f"Webpage {crawl_result.url} status code is 404, skipping..."
                )
                logger.debug("-" * 30)
                continue

            fit_markdown = crawl_result.markdown.fit_markdown
            fit_markdown = self._clean_markdown(fit_markdown)

            # 取內文的第一個標題作為檔名，若無則使用 URL 的最後一段
            heading_match = HEADING_PATTERN.search(fit_markdown)
            if heading_match:
                title = heading_match.group(1).strip()
                safe_title = INVALID_FILENAME_CHARS_PATTERN.sub("", title)
                safe_title = WHITESPACE_SEQUENCE_PATTERN.sub("_", safe_title)
                page_title = safe_title
            else:
                page_title = crawl_result.url.split("/")[-1]

            if page_title in existed_page_title:
                self._crawl_stats["repeat_pages"] += 1
                logger.debug(f"Webpage {page_title} already exists, skipping...")
                continue
            existed_page_title.add(page_title)

            image_urls = MARKDOWN_IMAGE_PATTERN.findall(fit_markdown)
            images = [{"url": url} for url in image_urls]
            # self._crawl_stats["image_count"] += len(images)

            filtered_result = {
                "url": crawl_result.url,
                "fit_markdown": fit_markdown,
                "images": images,
            }
            filtered_results[page_title] = filtered_result
            self._crawl_stats["success_pages"] += 1

            logger.debug(f"Successfully crawled webpage: {page_title}")
            logger.debug(f"*  URL: {crawl_result.url}")
            logger.debug(f"*  Depth: {crawl_result.metadata.get('depth', 0)}")
            # logger.debug("Images:")
            # for image in images:
            #     logger.debug(image)

        return filtered_results

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
