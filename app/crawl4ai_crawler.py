import asyncio
import logging
import os
import re
import shutil
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


class WebsiteCrawler:
    KEEP_TITLE_CONTENT_THRESHOLD = 0.45
    KEEP_IMAGE_CONTENT_THRESHOLD = 0.25
    MARKDOWN_FOLDER_PATH = "./data/test/webpage_markdown"
    HEADING_PATTERN = re.compile(r"^#+\s*(.+)", flags=re.MULTILINE)
    SAFE_TITLE_PATTERN = re.compile(r"[\\/:\"\*\?<>\|]|\s+")

    @classmethod
    def crawl_website(
        cls,
        url: str,
        max_depth: int,
        url_patterns: str | Pattern | list[str | Pattern] | None = None,
        allowed_domains: str | list[str] | None = None,
        exclude_words: tuple[str, ...] | None = None,
        max_pages: int | None = None,
        content_threshold: float = KEEP_TITLE_CONTENT_THRESHOLD,
        light_mode: bool = True,
        wait_for_images: bool = True,
    ) -> list[dict] | None:
        """
        執行完整網站爬取流程並將結果過濾後輸出為 Markdown 檔案。

        Args:
            url: 目標網站 URL
            max_depth: 最大爬取深度
            url_patterns: URL 匹配模式列表
            allowed_domains: 允許爬取的域名列表
            exclude_words: 過濾掉包含這些詞的行
            max_pages: 最大頁面數限制，預設無限
            content_threshold: 內容過濾閾值，0.45 可顯示所有標題，0.25可顯示所有圖片，預設 0.45
            light_mode: 是否使用輕量化模式(關閉部分背景資源)，預設 True
            wait_for_images: 是否等待圖片加載，預設 True
        """

        shutil.rmtree(cls.MARKDOWN_FOLDER_PATH, ignore_errors=True)
        os.makedirs(cls.MARKDOWN_FOLDER_PATH, exist_ok=True)

        try:
            crawl_results = asyncio.run(
                cls._crawl_website_async(
                    url=url,
                    max_depth=max_depth,
                    url_patterns=url_patterns,
                    allowed_domains=allowed_domains,
                    max_pages=max_pages,
                    content_threshold=content_threshold,
                    light_mode=light_mode,
                    wait_for_images=wait_for_images,
                )
            )
        except Exception as e:
            logger.error(f"Error during crawling: {e}")
            return None

        try:
            filtered_results = cls._filter_crawl_results(
                crawl_results=crawl_results,
                exclude_words=exclude_words,
            )
        except Exception as e:
            logger.error(f"Error during filteringcrawl results: {e}")
            return None

        try:
            cls._save_crawl_results_as_md(filtered_results)
        except Exception as e:
            logger.error(f"Error during saving crawl results as Markdown: {e}")
            return None

        return filtered_results

    @staticmethod
    async def _crawl_website_async(
        url: str,
        max_depth: int,
        url_patterns: str | Pattern | list[str | Pattern] | None = None,
        allowed_domains: str | list[str] | None = None,
        max_pages: int | None = None,
        content_threshold: float = KEEP_TITLE_CONTENT_THRESHOLD,
        light_mode: bool = True,
        wait_for_images: bool = True,
    ) -> list:
        """以指定爬蟲設定非同步抓取網站頁面並回傳原始爬取結果。"""
        browser_config = BrowserConfig(
            # headless=False, # 是否顯示瀏覽器
            light_mode=light_mode,
        )

        pruning_content_filter = PruningContentFilter(
            threshold=content_threshold,
            # threshold_type="dynamic",
        )

        filters: list[URLFilter] = []
        if url_patterns is not None:
            filters.append(URLPatternFilter(patterns=url_patterns))
        if allowed_domains is not None:
            filters.append(
                DomainFilter(
                    allowed_domains=allowed_domains,
                    # blocked_domains=["old.docs.example.com"],
                )
            )
        filter_chain = FilterChain(filters)

        if max_pages is not None:
            bfs_deep_crawl_strategy = BFSDeepCrawlStrategy(
                max_depth=max_depth,
                filter_chain=filter_chain,
                max_pages=max_pages,
            )
        else:
            bfs_deep_crawl_strategy = BFSDeepCrawlStrategy(
                max_depth=max_depth,
                filter_chain=filter_chain,
            )

        crawler_run_config = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=pruning_content_filter
            ),
            deep_crawl_strategy=bfs_deep_crawl_strategy,
            wait_for_images=wait_for_images,
            # process_iframes=True,
            # cache_mode=CacheMode.ENABLED,
            # stream=True
            # excluded_tags=["header"],
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            results = await crawler.arun(
                url=url,
                config=crawler_run_config,
            )
        if not isinstance(results, list):
            results = [results] if results else []

        return results

    @classmethod
    def _filter_crawl_results(
        cls,
        crawl_results: list,
        exclude_words: tuple[str, ...] | None = None,
    ) -> list[dict]:
        """過濾爬取結果內容並統計資訊後儲存可用頁面資料。"""
        filtered_results = []
        existed_markdown_file_names = set()
        success_unique_count = 0
        error_count = 0
        repeat_count = 0
        image_count = 0

        for crawl_result in crawl_results:
            # 排除 404 頁面
            if crawl_result.status_code == 404:
                error_count += 1
                # results.remove(result)
                logger.debug(
                    f"Webpage {crawl_result.url} status code is 404, skipping..."
                )
                logger.debug("-" * 30)
                continue

            # 過濾網頁多餘文字
            if exclude_words is not None:
                fit_markdown = "".join(
                    line
                    for line in crawl_result.markdown.fit_markdown.splitlines(
                        keepends=True
                    )
                    if not any(word in line for word in exclude_words)
                )
            else:
                fit_markdown = crawl_result.markdown.fit_markdown

            # 取內文的第一個標題作為檔名，若無則使用 URL 的最後一段
            heading_match = cls.HEADING_PATTERN.search(fit_markdown)
            if heading_match:
                title = heading_match.group(1).strip()
                safe_title = re.sub(r"[\\/:\"\*\?<>\|]", "", title)
                safe_title = re.sub(r"\s+", "_", safe_title)
                markdown_file_name = f"{safe_title}.md"
            else:
                markdown_file_name = f"{crawl_result.url.split('/')[-1]}.md"

            # 避免存取相同網頁多次，若網頁已存在則跳過
            if markdown_file_name in existed_markdown_file_names:
                repeat_count += 1
                logger.debug(
                    f"Webpage {markdown_file_name} already exists, skipping..."
                )
                logger.debug("-" * 30)
                continue
            existed_markdown_file_names.add(markdown_file_name)

            # 獲取網頁圖片
            images = crawl_result.media.get("images", [])
            image_count += len(images)

            # 儲存為 Markdown 檔案
            success_unique_count += 1
            filtered_result = {
                "markdown_file_path": os.path.join(
                    cls.MARKDOWN_FOLDER_PATH, markdown_file_name
                ),
                "url": crawl_result.url,
                "fit_markdown": fit_markdown,
                "images": crawl_result.media.get("images", []),
            }
            filtered_results.append(filtered_result)
            # cls._save_crawl_results_as_md(filtered_result)

            logger.debug(f"URL: {crawl_result.url}")
            logger.debug(f"Depth: {crawl_result.metadata.get('depth', 0)}")
            logger.debug("Images:")
            for image in images:
                logger.debug(image)
            logger.debug("-" * 30)

        logger.info("Website crawling stats:")
        logger.info(f"  * Successful unique pages: {success_unique_count}")
        logger.info(f"  * Error pages: {error_count}")
        logger.info(f"  * Repeat pages: {repeat_count}")
        logger.info(f"  * Total images: {image_count}")
        logger.info("-" * 30)

        return filtered_results

    @staticmethod
    def _save_crawl_results_as_md(filtered_results: list[dict]):
        """將單筆過濾後的爬取結果寫入 Markdown 檔案。"""
        for filtered_result in filtered_results:
            markdown_file_path = filtered_result["markdown_file_path"]
            url = filtered_result["url"]
            fit_markdown = filtered_result["fit_markdown"]
            images = filtered_result["images"]

            with open(markdown_file_path, "w", encoding="utf-8") as f:
                f.write("-" * 5 + "\n")
                f.write(f"URL: {url}\n")
                f.write("-" * 5 + "\n")
                f.write(fit_markdown)
                if images:
                    f.write("\n" + "-" * 5 + "\n")
                    f.write("Images:\n\n")
                    for image in images:
                        f.write(f"![]({image['src']})\n")
                    f.write("\n" + "-" * 5 + "\n")
