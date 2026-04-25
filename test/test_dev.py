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
setup_logging("debug")
# setup_logging() # temp

# TODO: 修改路徑初始化 log
# TODO: 新增實驗完成 log
# TODO: 紀錄實驗 log


def test_website_crawler():
    t0 = time.time()

    # ----- 初始化實驗 -----
    log_session("Website Crawler", style="purple")
    module_name = "website_crawler"
    exp_manager = ExperimentManager(module_name)

    test_config_path = "./config/website_crawler_test.toml"
    config = WebsiteCrawlerConfig.from_toml(test_config_path)
    log_config("WebsiteCrawler Config Loaded from toml", config)

    # max_pages = 20  # test
    # config.override_init_config(max_pages=max_pages)
    # log_config("WebsiteCrawler Config after Override", config)

    log_session("Experiment Paths", style="cyan")
    exp_manager.set_run_path(config.run_name)
    exp_manager.init_module_run_paths()
    exp_manager._log_paths()

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
    log_session("Website Crawling", style="cyan")
    crawl_results = crawler.crawl_website(
        url=config.url,
        url_patterns=config.url_patterns,
        allowed_domains=config.allowed_domains,
        exclude_words=config.exclude_words,
    )
    if crawl_results is None:
        return

    # ----- 儲存設定和結果 -----
    save_config_as_toml(config, exp_manager.config_toml_path)
    exp_manager.save_results_as_json(crawl_results)
    exp_manager.save_results_as_md(crawl_results, "fit_markdown")

    t1 = time.time()
    logger.info(f"Website Crawling Completed in {t1 - t0:.2f} seconds.")


def test_webpage_image_summarizer(skip_website_crawling: bool = True):
    t1 = time.time()

    # ----- 初始化實驗 -----
    log_session("Webpage Image Summarizer", style="purple")
    module_name = "webpage_image_summarizer"
    exp_manager = ExperimentManager(module_name)

    test_config_path = "./config/webpage_image_summarizer_test.toml"
    config = WebpageImageSummarizerConfig.from_toml(test_config_path)
    log_config("WebpageImageSummarizer Config Loaded from toml", config)

    # download_timeout = 30.0
    # model = "gpt-4o-mini"
    # config.override_init_config(download_timeout=download_timeout)
    # config.override_summarize_config(model=model)
    # log_config("WebpageImageSummarizer Config after Override:", config)

    log_session("Experiment Paths", style="cyan")
    exp_manager.set_run_path(config.run_name)
    exp_manager.init_module_run_paths()
    exp_manager._log_paths()

    # ----- 執行網站爬取 (可選) -----
    # skip_website_crawling = False
    if not skip_website_crawling:
        test_website_crawler()
    latest_results = exp_manager.load_latest_results_from_json()

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
    log_session("Image Summarization", style="cyan")
    enhanced_results = webpage_image_summarizer.summarize_crawl_results_images(
        latest_results,
        model=config.model,
        prompt=config.prompt,
        vlm_max_workers=config.vlm_max_workers,
        image_source=config.image_source,
        **config.litellm_kwargs,
    )

    # ----- 儲存設定和結果 -----
    save_config_as_toml(config, exp_manager.config_toml_path)
    exp_manager.save_results_as_json(enhanced_results)
    exp_manager.save_results_as_md(enhanced_results, "enhanced_markdown")

    t2 = time.time()
    logger.info(f"Image Summarization Completed in {t2 - t1:.2f} seconds.")
