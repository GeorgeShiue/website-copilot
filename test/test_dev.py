import logging

from app.webpage_image_summarizer import WebpageImageSummarizer
from app.webpage_image_summarizer_config import WebpageImageSummarizerConfig
from app.website_crawler import WebsiteCrawler
from app.website_crawler_config import WebsiteCrawlerConfig
from utils.config_helper import log_config, save_config_as_toml
from utils.exp_manager import ExperimentManager
from utils.log_helper import file_logging, log_session, setup_logging

logger = logging.getLogger(__name__)
setup_logging("debug", logger)


# TODO: 將以下兩個function改為run...，放到run.py


def test_website_crawler(config_name: str = "test") -> None:
    # ----- 初始化實驗 -----
    module_name = "website_crawler"
    exp_manager = ExperimentManager(module_name)
    config = WebsiteCrawlerConfig.from_toml(config_name)

    # max_pages = 20  # test
    # config.override_init_config(max_pages=max_pages)
    # log_config("WebsiteCrawler Config after Override", config)

    exp_manager.set_run_path(config.run_name)
    exp_manager.init_module_run_paths()

    with file_logging(exp_manager.log_path):
        log_session("Website Crawler", style="purple")
        log_config("WebsiteCrawler Config Loaded from toml", config)
        log_session("Experiment Paths", style="cyan")
        exp_manager.log_run_paths("init")

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

        log_session("Website Crawling Completed", style="cyan")
        exp_manager.log_run_paths("complete")


def test_webpage_image_summarizer(
    exp_manager: ExperimentManager | None = None, config_name: str = "test"
) -> None:
    # ----- 初始化實驗 -----
    if exp_manager is None:
        exp_manager = ExperimentManager("webpage_image_summarizer")

    config = WebpageImageSummarizerConfig.from_toml(config_name)

    # download_timeout = 30.0
    # model = "gpt-4o-mini"
    # config.override_init_config(download_timeout=download_timeout)
    # config.override_summarize_config(model=model)
    # log_config("WebpageImageSummarizer Config after Override:", config)

    exp_manager.set_run_path(config.run_name)
    exp_manager.init_module_run_paths()

    with file_logging(exp_manager.log_path):
        log_session("Webpage Image Summarizer", style="purple")
        log_config("WebpageImageSummarizer Config Loaded from toml", config)
        log_session("Experiment Paths", style="cyan")
        exp_manager.log_run_paths("init")

        # ----- 獲取最近一次結果 -----
        log_session("Loading Latest Results", style="cyan")
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

        log_session("Image Summarization Completed", style="cyan")
        exp_manager.log_run_paths("complete")
