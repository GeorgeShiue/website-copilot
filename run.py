from app.webpage_image_summarizer import WebpageImageSummarizer
from app.webpage_image_summarizer_config import WebpageImageSummarizerConfig
from app.website_crawler import WebsiteCrawler
from app.website_crawler_config import WebsiteCrawlerConfig
from utils.config_helper import log_config, save_config_as_toml
from utils.log_helper import (
    log_execution_time,
    log_session,
    save_logging_file,
)
from utils.run_manager import RunManager


def run_website_crawler(
    config_names: list[str] = ["default"],
    run_name_use_config_name: bool = False,
    run_manager: RunManager | None = None,
) -> dict[str, dict] | None:
    if run_manager is None:
        run_manager = RunManager("website_crawler")
    website_crawler = WebsiteCrawler(max_depth=0)

    crawl_results = None
    for config_name in config_names:
        # ----- 初始化設定和路徑 -----
        config = WebsiteCrawlerConfig.from_toml(config_name)
        if run_name_use_config_name:
            run_manager.set_run_path(config_name)
        else:
            run_manager.set_run_path(config.run_name)
        run_manager.init_module_run_paths()

        with (
            save_logging_file(run_manager.log_path),
            log_execution_time("Website Crawling"),
        ):
            # ----- 輸出開始訊息 -----
            log_session(f"Website Crawler ({config_name})", style="purple")
            log_config("WebsiteCrawler Config Loaded from toml", config)
            log_session("Run Paths", style="cyan")
            run_manager.log_run_paths("init")

            # ----- 初始化物件 -----
            website_crawler.override_init_config(
                max_depth=config.max_depth,
                max_pages=config.max_pages,
                content_threshold=config.content_threshold,
                light_mode=config.light_mode,
                wait_for_images=config.wait_for_images,
            )

            # ---- 執行網站爬蟲 -----
            log_session("Website Crawling", style="cyan")
            crawl_results = website_crawler.crawl_website(
                url=config.url,
                url_patterns=config.url_patterns,
                allowed_domains=config.allowed_domains,
                exclude_words=config.exclude_words,
            )

            if crawl_results is not None:
                # ----- 儲存設定和結果 -----
                save_config_as_toml(config, run_manager.config_toml_path)
                run_manager.save_results_as_json(crawl_results)
                run_manager.save_results_as_md(crawl_results, "fit_markdown")

                # ----- 輸出完成訊息 -----
                log_session("Website Crawling Completed", style="cyan")
                run_manager.log_run_paths("complete")

    return crawl_results


def run_webpage_image_summarizer(
    config_names: list[str] = ["default"],
    run_name_use_config_name: bool = False,
    run_manager: RunManager | None = None,
    crawl_results: dict[str, dict] | None = None,
) -> None:
    if run_manager is None:
        run_manager = RunManager("webpage_image_summarizer")
    webpage_image_summarizer = WebpageImageSummarizer()

    for config_name in config_names:
        # ----- 初始化設定 -----
        config = WebpageImageSummarizerConfig.from_toml(config_name)
        if run_name_use_config_name:
            run_manager.set_run_path(config_name)
        else:
            run_manager.set_run_path(config.run_name)
        run_manager.init_module_run_paths()

        with (
            save_logging_file(run_manager.log_path),
            log_execution_time("Image Summarization"),
        ):
            # ----- 輸出開始訊息 -----
            log_session(f"Webpage Image Summarizer ({config_name})", style="purple")
            log_config("WebpageImageSummarizer Config Loaded from toml", config)
            log_session("Run Paths", style="cyan")
            run_manager.log_run_paths("init")

            # ----- 初始化物件 -----
            webpage_image_summarizer.override_init_config(
                download_timeout=config.download_timeout,
                success_threshold=config.success_threshold,
                max_retries=config.max_retries,
                cache_download_images=config.cache_download_images,
                cache_image_captions=config.cache_image_captions,
            )

            # ----- 獲取最近一次結果 -----
            if crawl_results is None:
                log_session("Loading Latest Results", style="cyan")
                crawl_results = run_manager.load_latest_results_from_json()

            # ---- 執行圖片摘要 -----
            log_session("Image Summarization", style="cyan")
            enhanced_results = webpage_image_summarizer.summarize_crawl_results_images(
                crawl_results,
                model=config.model,
                prompt=config.prompt,
                vlm_max_workers=config.vlm_max_workers,
                image_source=config.image_source,
                **config.litellm_kwargs,
            )

            # ----- 儲存設定和結果 -----
            save_config_as_toml(config, run_manager.config_toml_path)
            run_manager.save_results_as_json(enhanced_results)
            run_manager.save_results_as_md(enhanced_results, "enhanced_markdown")

            # ----- 輸出完成訊息 -----
            log_session("Image Summarization Completed", style="cyan")
            run_manager.log_run_paths("complete")
