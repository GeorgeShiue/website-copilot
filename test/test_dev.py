import logging
import os
import time

from app.webpage_image_summarizer import WebpageImageSummarizer
from app.webpage_image_summarizer_config import (
    WebpageImageSummarizerConfig,
    log_config,
    save_config_as_toml,
)
from app.website_crawler import WebsiteCrawler
from utils.file_manager import (
    load_crawl_results_from_json,
    save_crawl_results_as_json,
    save_crawl_results_as_md,
)

logger = logging.getLogger(__name__)


TEST_DATA_FOLDER_PATH = "./data/test"


# TODO: 開始時輸出單元測試設定
def test_website_crawler(max_pages: int | None = None):
    max_pages = 10  # test

    logger.info("1. Website Crawling")
    logger.info("-" * 30)
    t0 = time.time()

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_name = "WebpageImageSummarizer"
    base_path = os.path.join(TEST_DATA_FOLDER_PATH, timestamp, run_name)
    os.makedirs(base_path, exist_ok=True)
    markdown_folder_path = os.path.join(base_path, "results")
    os.makedirs(markdown_folder_path, exist_ok=True)
    # config_path = os.path.join(base_path, "config.toml")

    crawler = WebsiteCrawler(
        max_depth=2,
        max_pages=max_pages,
    )
    crawl_results = crawler.crawl_website(
        url="https://sites.google.com/site/nculab/labintro",
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
    )

    if crawl_results is None:
        logger.error("Crawling failed.")
        return

    save_crawl_results_as_json(crawl_results)
    save_crawl_results_as_md(crawl_results, markdown_folder_path, "fit_markdown")

    t1 = time.time()
    logger.info(f"Crawling completed in {t1 - t0:.2f} seconds.")
    logger.info("=" * 30)


# TODO: 測試多組初始化參數
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

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_name = "WebpageImageSummarizer"
    base_path = os.path.join(TEST_DATA_FOLDER_PATH, timestamp, run_name)
    os.makedirs(base_path, exist_ok=True)
    markdown_folder_path = os.path.join(base_path, "results")
    os.makedirs(markdown_folder_path, exist_ok=True)
    config_path = os.path.join(base_path, "config.toml")

    # ----- 載入參數 -----
    logger.info("Loading WebpageImageSummarizer config from toml")
    config = WebpageImageSummarizerConfig.from_toml()
    logger.info("WebpageImageSummarizer config loaded successfully from toml")
    logger.info("-" * 30)
    log_config("WebpageImageSummarizer config from toml:", vars(config))
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

    # ----- 覆寫參數 -----
    # download_timeout = 30.0
    # model = "gpt-4o-mini"
    # logger.info("Overriding WebpageImageSummarizer config")

    # config.override_init_config(download_timeout=download_timeout)
    # config.override_summarize_config(model=model)

    # webpage_image_summarizer.override_init_config(**vars(config))
    # webpage_image_summarizer.override_summarize_config(**vars(config))
    # logger.info("WebpageImageSummarizer config overridden successfully")
    # logger.info("-" * 30)

    # log_config("WebpageImageSummarizer config after override:", vars(config))
    # logger.info("-" * 30)

    save_config_as_toml(config, config_path)

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

    save_crawl_results_as_json(enhanced_crawl_results)
    save_crawl_results_as_md(
        enhanced_crawl_results, markdown_folder_path, "enhanced_markdown"
    )

    # first_enhanced_crawl_result = enhanced_crawl_results[0]
    # print("first_enhanced_crawl_result:\n", first_enhanced_crawl_result)
    # print("enhanced_markdown:\n", first_enhanced_crawl_result["enhanced_markdown"])
