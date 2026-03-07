import logging
import time

from website_crawler.crawl4ai_crawler import WebsiteCrawler
# from webpage_content_extracter.webpage_image_summarizer import WebpageImageSummarizer
# from webpage_content_extracter.md_file_manager import MdFileManager


logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_main():
    logger.info("1. Website Crawling")
    logger.info("-" * 50)

    t0 = time.time()
    WebsiteCrawler.crawl_website(
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
        # max_pages=10, # test
    )
    t1 = time.time()

    logger.info(f"Crawling completed in {t1 - t0:.2f} seconds.")
    logger.info("-" * 50)
