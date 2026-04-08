import logging
import time

from app.webpage_image_summarizer import WebpageImageSummarizer
from app.website_crawler import WebsiteCrawler
from utils.file_manager import (
    load_crawl_results_from_json,
    save_crawl_results_as_json,
    save_crawl_results_as_md,
)

logger = logging.getLogger(__name__)


# TODO: 開始時輸出單元測試設定
def test_website_crawler(max_pages: int | None = None):
    max_pages = 10  # test

    logger.info("1. Website Crawling")
    logger.info("-" * 30)

    t0 = time.time()
    crawl_results = WebsiteCrawler.crawl_website(
        url="https://sites.google.com/site/nculab/labintro",
        max_depth=2,
        url_patterns=["*nculab*"],
        allowed_domains=["sites.google.com"],
        exclude_words=(
            "Search this site",
            "Embedded Files",
            "Skip to main content",
            "Skip to navigation",
            "Google Sites",
            "Report abuse",
        ),
        max_pages=max_pages,
    )
    t1 = time.time()

    if crawl_results is None:
        logger.error("Crawling failed.")
        return
    logger.info(f"Crawling completed in {t1 - t0:.2f} seconds.")
    logger.info("=" * 30)

    save_crawl_results_as_json(crawl_results)
    save_crawl_results_as_md(crawl_results, "fit_markdown")


def test_webpage_image_summarizer(skip_website_crawling: bool = True):
    # skip_website_crawling = False

    if not skip_website_crawling:
        test_website_crawler(
            max_pages=10  # test
        )
    crawl_results = load_crawl_results_from_json()

    logger.info("2. Image Summarization")
    logger.info("-" * 30)

    t1 = time.time()
    # TODO: 測試多組初始化參數
    # webpage_image_summarizer = WebpageImageSummarizer()
    webpage_image_summarizer = WebpageImageSummarizer.from_toml(
        download_timeout=30.0
    )  # * 此處可以override
    enhanced_crawl_results = webpage_image_summarizer.summarize_crawl_results_images(
        crawl_results,
    )
    t2 = time.time()

    logger.info(f"Image summarization completed in {t2 - t1:.2f} seconds.")
    logger.info("=" * 30)

    save_crawl_results_as_json(enhanced_crawl_results)
    save_crawl_results_as_md(enhanced_crawl_results, "enhanced_markdown")

    # first_enhanced_crawl_result = enhanced_crawl_results[0]
    # print("first_enhanced_crawl_result:\n", first_enhanced_crawl_result)
    # print("enhanced_markdown:\n", first_enhanced_crawl_result["enhanced_markdown"])
