import logging
import time

from app.webpage_image_summarizer import WebpageImageSummarizer
from app.website_crawler import WebsiteCrawler
from utils.file_manager import FileManager

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main(max_pages: int | None = None) -> None:
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

    logger.info("2. Image Summarization")
    logger.info("-" * 30)

    webpage_image_summarizer = WebpageImageSummarizer()
    enhanced_crawl_results = webpage_image_summarizer.summarize_crawl_results_images(
        crawl_results=crawl_results
    )
    t2 = time.time()

    logger.info(f"Image summarization completed in {t2 - t1:.2f} seconds.")
    logger.info("=" * 30)

    FileManager.save_crawl_results_as_json(enhanced_crawl_results)
    FileManager.save_enhanced_crawl_results_as_md(enhanced_crawl_results)


if __name__ == "__main__":
    main()
