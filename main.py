import logging
import time

from app.webpage_image_summarizer import WebpageImageSummarizer
from app.webpage_image_summarizer_config import (
    WebpageImageSummarizerConfig,
)
from app.website_crawler import WebsiteCrawler
from app.website_crawler_config import (
    WebsiteCrawlerConfig,
)
from utils.config_helper import log_config, save_config_as_toml
from utils.exp_manager import ExperimentManager

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main(max_pages: int | None = None) -> None:
    logger.info("1. Website Crawling")
    logger.info("-" * 30)
    t0 = time.time()

    exp_manager = ExperimentManager()
    module_name = "website_crawler"
    exp_manager.set_module_path(module_name)

    config = WebsiteCrawlerConfig.from_toml()
    log_config("WebsiteCrawler config from toml:", vars(config))
    config.override_init_config(max_pages=max_pages)
    log_config("WebsiteCrawler config after override:", vars(config))

    exp_manager.set_run_path(config.run_name)
    exp_manager.init_module_run_paths()
    save_config_as_toml(config, exp_manager.config_toml_path)

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

    exp_manager.save_results_as_json(crawl_results)
    exp_manager.save_results_as_md(crawl_results, "fit_markdown")

    t1 = time.time()
    logger.info(f"Crawling completed in {t1 - t0:.2f} seconds.")
    logger.info("=" * 30)

    logger.info("2. Image Summarization")
    logger.info("-" * 30)
    t2 = time.time()

    module_name = "webpage_image_summarizer"
    exp_manager.set_module_path(module_name)

    config = WebpageImageSummarizerConfig.from_toml()
    log_config("WebpageImageSummarizer config from toml:", vars(config))

    exp_manager.set_run_path(config.run_name)
    exp_manager.init_module_run_paths()
    save_config_as_toml(config, exp_manager.config_toml_path)

    webpage_image_summarizer = WebpageImageSummarizer(
        download_timeout=config.download_timeout,
        success_threshold=config.success_threshold,
        max_retries=config.max_retries,
    )

    enhanced_crawl_results = webpage_image_summarizer.summarize_crawl_results_images(
        crawl_results,
        model=config.model,
        prompt=config.prompt,
        vlm_max_workers=config.vlm_max_workers,
        image_source=config.image_source,
        **config.litellm_kwargs,
    )

    exp_manager.save_results_as_json(enhanced_crawl_results)
    exp_manager.save_results_as_md(enhanced_crawl_results, "enhanced_markdown")

    t2 = time.time()
    logger.info(f"Image summarization completed in {t2 - t1:.2f} seconds.")
    logger.info("=" * 30)


if __name__ == "__main__":
    main()
