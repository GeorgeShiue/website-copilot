import asyncio
import logging
import re
from typing import Pattern

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

logger = logging.getLogger(__name__)


KEEP_TITLE_CONTENT_THRESHOLD = 0.45
KEEP_IMAGE_CONTENT_THRESHOLD = 0.25

HEADING_PATTERN = re.compile(r"^#+\s*(.+)", flags=re.MULTILINE)
EMPTY_HEADING_LINE_PATTERN = re.compile(r"^(\s{0,3}#{1,6})\s*$")
SKIP_AS_HEADING_PATTERN = re.compile(r"^\s*!?\[.*?\]\(.*?\)\s*$")

EMPTY_ANCHOR_LINK_PATTERN = re.compile(r"\[\]\(.*?#h\.[a-z0-9]+\)")

INVALID_FILENAME_CHARS_PATTERN = re.compile(r"[\\/:\"*?<>|]")
WHITESPACE_SEQUENCE_PATTERN = re.compile(r"\s+")


# TODO: 加入內部狀態，success_unique_count、error_count、repeat_count、image_count 等統計資訊
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

    def crawl_website(
        self,
        url: str,
        url_patterns: str | Pattern | list[str | Pattern] | None = None,
        allowed_domains: str | list[str] | None = None,
        exclude_words: tuple[str, ...] | None = None,
    ) -> list[dict] | None:
        """
        執行完整網站爬取流程並將結果過濾後輸出為 Markdown 檔案。

        Args:
            url: 目標網址
            url_patterns: URL 匹配模式列表
            allowed_domains: 允許爬取的域名列表
            exclude_words: 過濾掉包含這些詞的行
        """
        self.url = url
        self.url_patterns = url_patterns
        self.allowed_domains = allowed_domains
        self.exclude_words = exclude_words

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

        return filtered_results

    async def _crawl_website_async(
        self,
    ) -> list:
        """以指定爬蟲設定非同步抓取網站頁面並回傳原始爬取結果。"""
        browser_config = BrowserConfig(
            # headless=False, # 是否顯示瀏覽器
            light_mode=self.light_mode,
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
    ) -> list[dict]:
        """過濾爬取結果內容並統計資訊後儲存可用頁面資料。"""
        filtered_results = []
        existed_markdown_file_names = set()
        success_unique_count = 0
        error_count = 0
        repeat_count = 0
        image_count = 0

        for crawl_result in crawl_results:
            if crawl_result.status_code == 404:
                error_count += 1
                # results.remove(result)
                # logger.info(
                #     f"Webpage {crawl_result.url} status code is 404, skipping..."
                # )
                # logger.info("-" * 30)
                continue

            fit_markdown = crawl_result.markdown.fit_markdown

            if self.exclude_words is not None:
                fit_markdown = "".join(
                    line
                    for line in fit_markdown.splitlines(keepends=True)
                    if not any(word in line for word in self.exclude_words)
                )

            # 移除 https://...#h.xxx 這類隱藏錨點空連結
            fit_markdown = EMPTY_ANCHOR_LINK_PATTERN.sub("", fit_markdown)

            fit_markdown = self._promote_empty_heading_line(fit_markdown)

            # 取內文的第一個標題作為檔名，若無則使用 URL 的最後一段
            heading_match = HEADING_PATTERN.search(fit_markdown)
            if heading_match:
                title = heading_match.group(1).strip()
                safe_title = INVALID_FILENAME_CHARS_PATTERN.sub("", title)
                safe_title = WHITESPACE_SEQUENCE_PATTERN.sub("_", safe_title)
                markdown_file_name = f"{safe_title}.md"
            else:
                markdown_file_name = f"{crawl_result.url.split('/')[-1]}.md"

            if markdown_file_name in existed_markdown_file_names:
                repeat_count += 1
                # logger.info(
                #     f"Webpage {markdown_file_name} already exists, skipping..."
                # )
                # logger.info("-" * 30)
                continue
            existed_markdown_file_names.add(markdown_file_name)

            images = crawl_result.media.get("images", [])
            image_count += len(images)

            filtered_result = {
                "markdown_file_name": markdown_file_name,
                "url": crawl_result.url,
                "fit_markdown": fit_markdown,
                "images": crawl_result.media.get("images", []),
            }
            filtered_results.append(filtered_result)
            success_unique_count += 1

            # logger.info(f"URL: {crawl_result.url}")
            # logger.info(f"Depth: {crawl_result.metadata.get('depth', 0)}")
            # logger.info("Images:")
            # for image in images:
            #     logger.info(image)
            # logger.info("-" * 30)

        logger.info("Website crawling stats:")
        logger.info(f"  * Successful unique pages: {success_unique_count}")
        logger.info(f"  * Error pages: {error_count}")
        logger.info(f"  * Repeat pages: {repeat_count}")
        # logger.info(f"  * Total images: {image_count}")
        logger.info("-" * 30)

        return filtered_results

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

    def override_init_config(self, **init_kwargs) -> None:
        """覆寫初始化參數。"""
        self.max_depth = init_kwargs.get("max_depth", self.max_depth)
        self.max_pages = init_kwargs.get("max_pages", self.max_pages)
        self.content_threshold = init_kwargs.get(
            "content_threshold", self.content_threshold
        )
        self.light_mode = init_kwargs.get("light_mode", self.light_mode)
        self.wait_for_images = init_kwargs.get("wait_for_images", self.wait_for_images)
