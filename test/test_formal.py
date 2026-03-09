import logging
import time

from app.crawl4ai_crawler import WebsiteCrawler
from app.md_file_manager import MdFileManager

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_main():
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
        max_pages=10,  # test
    )
    t1 = time.time()

    if crawl_results is None:
        logger.error("Crawling failed.")
        return
    logger.info(f"Crawling completed in {t1 - t0:.2f} seconds.")
    logger.info("-" * 30)

    MdFileManager.save_crawl_results_as_md(crawl_results, "fit_markdown")
