import logging
import time

from app.webpage_image_summarizer import WebpageImageSummarizer
from app.webpage_image_summarizer_config import (
    WebpageImageSummarizerConfig,
    save_summarizer_config_as_toml,
)
from app.website_crawler import WebsiteCrawler
from app.website_crawler_config import (
    WebsiteCrawlerConfig,
    save_crawler_config_as_toml,
)
from utils.config_manager import log_config
from utils.exp_manager import ExperimentManager

logger = logging.getLogger(__name__)

# TODO: 紀錄實驗 log (logfire/rich)


def test_website_crawler():
    logger.info("1. Website Crawling")
    logger.info("-" * 30)
    t0 = time.time()

    # ----- 初始化實驗管理器 -----
    module_name = "website_crawler"
    exp_manager = ExperimentManager(module_name)

    # ----- 初始化參數 -----
    test_config_path = "./config/website_crawler_test.toml"
    config = WebsiteCrawlerConfig.from_toml(test_config_path)
    log_config("WebsiteCrawler config loaded from toml:", vars(config))
    # max_pages = 10  # test
    # config.override_init_config(max_pages=max_pages)
    # log_config("WebsiteCrawler config after override:", vars(config))

    # ----- 初始化實驗路徑 -----
    exp_manager.set_run_path(config.run_name)
    exp_manager.init_module_run_paths()
    save_crawler_config_as_toml(config, exp_manager.config_toml_path)

    # ----- 初始化實例 -----
    crawler = WebsiteCrawler(
        max_depth=config.max_depth,
        max_pages=config.max_pages,
        content_threshold=config.content_threshold,
        light_mode=config.light_mode,
        wait_for_images=config.wait_for_images,
    )
    # crawler = WebsiteCrawler(
    #     max_depth=2,
    #     max_pages=max_pages,
    # )

    # ---- 執行網站爬取 -----
    crawl_results = crawler.crawl_website(
        url=config.url,
        url_patterns=config.url_patterns,
        allowed_domains=config.allowed_domains,
        exclude_words=config.exclude_words,
    )
    if crawl_results is None:
        logger.error("Crawling failed.")
        return

    # ----- 儲存執行結果 -----
    exp_manager.save_results_as_json(crawl_results)
    exp_manager.save_results_as_md(crawl_results, "fit_markdown")

    t1 = time.time()
    logger.info(f"Crawling completed in {t1 - t0:.2f} seconds.")
    logger.info("=" * 30)


def test_webpage_image_summarizer(skip_website_crawling: bool = True):
    logger.info("2. Image Summarization")
    logger.info("-" * 30)
    t1 = time.time()

    # ----- 初始化實驗管理器 -----
    module_name = "webpage_image_summarizer"
    exp_manager = ExperimentManager(module_name)

    # ----- 初始化參數 -----
    test_config_path = "./config/webpage_image_summarizer_test.toml"
    config = WebpageImageSummarizerConfig.from_toml(test_config_path)
    log_config("WebpageImageSummarizer config loaded from toml:", vars(config))
    # download_timeout = 30.0
    # model = "gpt-4o-mini"
    # config.override_init_config(download_timeout=download_timeout)
    # config.override_summarize_config(model=model)
    # log_config("WebpageImageSummarizer config after override:", vars(config))
    # logger.info("-" * 30)

    # ----- 初始化實驗路徑 -----
    exp_manager.set_run_path(config.run_name)
    exp_manager.init_module_run_paths()
    save_summarizer_config_as_toml(config, exp_manager.config_toml_path)

    # ----- 執行網站爬取 (可選) -----
    # skip_website_crawling = False
    if not skip_website_crawling:
        test_website_crawler()
    latest_results = exp_manager.load_latest_results_from_json()
    logger.info("-" * 30)

    # ----- 初始化實例 -----
    webpage_image_summarizer = WebpageImageSummarizer(
        download_timeout=config.download_timeout,
        success_threshold=config.success_threshold,
        max_retries=config.max_retries,
    )
    # webpage_image_summarizer = WebpageImageSummarizer(
    #     download_timeout=10.0,
    #     success_threshold=0.8,
    #     max_retries=6,
    # )

    # ---- 執行圖片摘要 -----
    enhanced_results = webpage_image_summarizer.summarize_crawl_results_images(
        latest_results,
        model=config.model,
        prompt=config.prompt,
        vlm_max_workers=config.vlm_max_workers,
        image_source=config.image_source,
        **config.litellm_kwargs,
    )

    # ----- 儲存執行結果 -----
    exp_manager.save_results_as_json(enhanced_results)
    exp_manager.save_results_as_md(enhanced_results, "enhanced_markdown")

    t2 = time.time()
    logger.info(f"Image summarization completed in {t2 - t1:.2f} seconds.")
    logger.info("=" * 30)
