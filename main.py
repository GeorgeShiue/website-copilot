import logging
import time

from app.webpage_image_summarizer import WebpageImageSummarizer
from app.webpage_image_summarizer_config import WebpageImageSummarizerConfig
from app.website_crawler import WebsiteCrawler
from app.website_crawler_config import WebsiteCrawlerConfig
from utils.config_helper import log_config, save_config_as_toml
from utils.log_helper import file_logging, log_session, setup_logging
from utils.run_manager import RunManager

logger = logging.getLogger(__name__)
setup_logging()


# TODO: 修改計時機制
def main(
    max_pages: int | None = None,
    webpage_image_summarizer_config_name: str | None = None,
) -> None:
    t0 = time.time()

    run_manager = RunManager()
    module_name = "website_crawler"
    run_manager.set_module_path(module_name)

    config = WebsiteCrawlerConfig.from_toml()
    config.override_init_config(max_pages=max_pages)

    run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()

    with file_logging(run_manager.log_path):
        log_session("Website Crawler", style="purple")
        log_config("WebsiteCrawler Config Loaded from toml", config)
        log_config("WebsiteCrawler Config after Override", config)
        log_session("Run Paths", style="cyan")
        run_manager.log_run_paths("init")

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

        save_config_as_toml(config, run_manager.config_toml_path)
        run_manager.save_results_as_json(crawl_results)
        run_manager.save_results_as_md(crawl_results, "fit_markdown")

        t1 = time.time()
        log_session("Website Crawling Completed", style="cyan")
        run_manager.log_run_paths("complete")
        logger.info(f"Website Crawling Completed in {t1 - t0:.2f} seconds.")

    t2 = time.time()

    module_name = "webpage_image_summarizer"
    run_manager.set_module_path(module_name)

    if webpage_image_summarizer_config_name is None:
        config = WebpageImageSummarizerConfig.from_toml()
    else:
        config = WebpageImageSummarizerConfig.from_toml(
            webpage_image_summarizer_config_name
        )

    run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()

    with file_logging(run_manager.log_path):
        log_session("Webpage Image Summarizer", style="purple")
        log_config("WebpageImageSummarizer Config Loaded from toml", config)
        log_session("Run Paths", style="cyan")
        run_manager.log_run_paths("init")

        webpage_image_summarizer = WebpageImageSummarizer(
            download_timeout=config.download_timeout,
            success_threshold=config.success_threshold,
            max_retries=config.max_retries,
            cache_download_images=config.cache_download_images,
        )

        log_session("Image Summarization", style="cyan")
        enhanced_crawl_results = (
            webpage_image_summarizer.summarize_crawl_results_images(
                crawl_results,
                model=config.model,
                prompt=config.prompt,
                vlm_max_workers=config.vlm_max_workers,
                image_source=config.image_source,
                **config.litellm_kwargs,
            )
        )

        save_config_as_toml(config, run_manager.config_toml_path)
        run_manager.save_results_as_json(enhanced_crawl_results)
        run_manager.save_results_as_md(enhanced_crawl_results, "enhanced_markdown")

        t2 = time.time()
        log_session("Image Summarization Completed", style="cyan")
        run_manager.log_run_paths("complete")
        logger.info(f"Image Summarization Completed in {t2 - t1:.2f} seconds.")


if __name__ == "__main__":
    main()
