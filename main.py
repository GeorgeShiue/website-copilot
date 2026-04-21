import logging
import time

from app.webpage_image_summarizer import WebpageImageSummarizer
from app.webpage_image_summarizer_config import (
    WebpageImageSummarizerConfig,
    save_summarizer_config_as_toml,
)
from app.website_crawler import WebsiteCrawler
from app.website_crawler_config import WebsiteCrawlerConfig, save_crawler_config_as_toml
from utils.config_manager import log_config
from utils.exp_manager import ExperimentManager

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main(max_pages: int | None = None) -> None:
    exp_manager = ExperimentManager()

    logger.info("1. Website Crawling")
    logger.info("-" * 30)
    t0 = time.time()

    module_name = "WebsiteCrawler"
    exp_manager.init_module_paths(module_name)
    config = WebsiteCrawlerConfig.from_config()
    log_config("WebsiteCrawler config from toml:", vars(config))

    save_crawler_config_as_toml(config, exp_manager.config_path)

    crawler = WebsiteCrawler(
        max_depth=config.max_depth,
        max_pages=config.max_pages,
        content_threshold=config.content_threshold,
        light_mode=config.light_mode,
        wait_for_images=config.wait_for_images,
    )

    crawl_results = crawler.crawl_website(
        url=config.url,
        url_patterns=config.url_patterns,
        allowed_domains=config.allowed_domains,
        exclude_words=config.exclude_words,
    )
    if crawl_results is None:
        logger.error("Crawling failed.")
        return

    exp_manager.save_crawl_results_as_json(crawl_results)
    exp_manager.save_crawl_results_as_md(crawl_results, "fit_markdown")

    t1 = time.time()
    logger.info(f"Crawling completed in {t1 - t0:.2f} seconds.")
    logger.info("=" * 30)

    logger.info("2. Image Summarization")
    logger.info("-" * 30)
    t2 = time.time()

    module_name = "WebpageImageSummarizer"
    exp_manager.init_module_paths(module_name)
    config = WebpageImageSummarizerConfig.from_toml()
    log_config("WebpageImageSummarizer config from toml:", vars(config))

    webpage_image_summarizer = WebpageImageSummarizer(
        download_timeout=config.download_timeout,
        success_threshold=config.success_threshold,
        max_retries=config.max_retries,
    )

    save_summarizer_config_as_toml(config, exp_manager.config_path)

    enhanced_crawl_results = webpage_image_summarizer.summarize_crawl_results_images(
        crawl_results,
        model=config.model,
        prompt=config.prompt,
        vlm_max_workers=config.vlm_max_workers,
        image_source=config.image_source,
        **config.litellm_kwargs,
    )

    t2 = time.time()
    logger.info(f"Image summarization completed in {t2 - t1:.2f} seconds.")
    logger.info("=" * 30)

    exp_manager.save_crawl_results_as_json(enhanced_crawl_results)
    exp_manager.save_crawl_results_as_md(enhanced_crawl_results, "enhanced_markdown")


if __name__ == "__main__":
    main()
