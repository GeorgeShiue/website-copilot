import logging
import time

from website_crawler.crawl4ai_crawler import WebsiteCrawler
from webpage_content_extracter.webpage_cleaner import WebpageCleaner
from webpage_content_extracter.webpage_image_summarizer import WebpageImageSummarizer
from webpage_content_extracter.md_file_manager import MdFileManager


def test_main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    log = logging.getLogger(__name__)
    t0 = time.perf_counter()

    start_url = "https://sites.google.com/site/nculab/labintro"
    webpage_markdowns = WebsiteCrawler.crawl_website(
        url=start_url,
        max_depth=3,
        include_external=False,
        url_prefix="https://sites.google.com/site/nculab",
        concurrent_requests=15,
        text_mode=False,
        light_mode=True,
        verbose=True,
        max_pages=10,  # test
    )
    t1 = time.perf_counter()
    log.info("爬取%s個網頁, 耗時%.3f秒", len(webpage_markdowns), t1 - t0)
    log.info("-" * 50)

    cleaned_webpage_markdowns = WebpageCleaner.clean_webpage_markdown(
        webpage_markdowns, include_frontmatter=True
    )
    t2 = time.perf_counter()
    log.info(
        "清理後剩餘%s個網頁, 耗時%.3f秒",
        len(cleaned_webpage_markdowns),
        t2 - t1,
    )
    log.info("-" * 50)

    image_summarizer = WebpageImageSummarizer()
    markdown_contents_with_image_summary, retry_count, download_stats = (
        image_summarizer.summarize_webpage_markdown_images(
            cleaned_webpage_markdowns,
            model="openai",
            skip_pages_without_images=True,
        )
    )
    t3 = time.perf_counter()
    log.info(
        "加註%s個網頁的圖片, 重試%s次, 耗時%.3f秒",
        len(markdown_contents_with_image_summary),
        retry_count,
        t3 - t2,
    )
    log.info(
        "- 圖片下載資訊: 成功%s次, 失敗%s次, 跨頁重用快取%s次",
        download_stats["success"],
        download_stats["failure"],
        download_stats["cache_reuse"],
    )
    log.info("-" * 50)

    md_file_paths = MdFileManager.save_md_files(
        directory="./data/test/webpage_markdown_with_image_summary_test",  # test
        markdown_contents=markdown_contents_with_image_summary,
    )
    t4 = time.perf_counter()
    log.info("已存成%s個 .md 檔, 耗時%.3f秒", len(md_file_paths), t4 - t3)
    log.info("-" * 50)

    log.info("總耗時%.3f秒", t4 - t0)


# if __name__ == "__main__":
#     test_website_crawling()
