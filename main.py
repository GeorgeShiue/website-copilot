import logging
import time

from app.webpage_image_summarizer import WebpageImageSummarizer
from app.webpage_image_summarizer_config import WebpageImageSummarizerConfig
from app.website_crawler import WebsiteCrawler
from app.website_crawler_config import WebsiteCrawlerConfig
from utils.config_helper import log_config, save_config_as_toml
from utils.exp_manager import ExperimentManager
from utils.log_helper import log_session, setup_logging

logger = logging.getLogger(__name__)
setup_logging()


def main(max_pages: int | None = None) -> None:
    log_session("Website Crawler", style="purple")
    t0 = time.time()

    exp_manager = ExperimentManager()
    module_name = "website_crawler"
    exp_manager.set_module_path(module_name)

    config = WebsiteCrawlerConfig.from_toml()
    log_config("WebsiteCrawler Config Loaded from toml", config)
    config.override_init_config(max_pages=max_pages)
    log_config("WebsiteCrawler Config after Override", config)

    log_session("Experiment Paths", style="cyan")
    exp_manager.set_run_path(config.run_name)
    exp_manager.init_module_run_paths()
    exp_manager._log_paths()

    crawler = WebsiteCrawler(
        max_depth=config.max_depth,
        max_pages=config.max_pages,
        content_threshold=config.content_threshold,
        light_mode=config.light_mode,
        wait_for_images=config.wait_for_images,
    )

    log_session("Website Crawling", style="cyan")
    crawl_results = crawler.crawl_website(
        url=config.url,
        url_patterns=config.url_patterns,
        allowed_domains=config.allowed_domains,
        exclude_words=config.exclude_words,
    )
    if crawl_results is None:
        return

    save_config_as_toml(config, exp_manager.config_toml_path)
    exp_manager.save_results_as_json(crawl_results)
    exp_manager.save_results_as_md(crawl_results, "fit_markdown")

    t1 = time.time()
    logger.info(f"Website Crawling Completed in {t1 - t0:.2f} seconds.")

    log_session("Webpage Image Summarizer", style="purple")
    t2 = time.time()

    module_name = "webpage_image_summarizer"
    exp_manager.set_module_path(module_name)

    config = WebpageImageSummarizerConfig.from_toml()
    log_config("WebpageImageSummarizer Config Loaded from toml", config)

    log_session("Experiment Paths", style="cyan")
    exp_manager.set_run_path(config.run_name)
    exp_manager.init_module_run_paths()
    exp_manager._log_paths()

    webpage_image_summarizer = WebpageImageSummarizer(
        download_timeout=config.download_timeout,
        success_threshold=config.success_threshold,
        max_retries=config.max_retries,
    )

    log_session("Image Summarization", style="cyan")
    enhanced_crawl_results = webpage_image_summarizer.summarize_crawl_results_images(
        crawl_results,
        model=config.model,
        prompt=config.prompt,
        vlm_max_workers=config.vlm_max_workers,
        image_source=config.image_source,
        **config.litellm_kwargs,
    )

    save_config_as_toml(config, exp_manager.config_toml_path)
    exp_manager.save_results_as_json(enhanced_crawl_results)
    exp_manager.save_results_as_md(enhanced_crawl_results, "enhanced_markdown")

    t2 = time.time()
    logger.info(f"Image Summarization Completed in {t2 - t1:.2f} seconds.")


if __name__ == "__main__":
    main()
