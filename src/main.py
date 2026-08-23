from app.workflow.run_manager import RunManager
from app.workflow.workflow import (
    run_rag_build,
    run_webpage_image_summarizer,
    run_website_crawler,
)
from app.workflow.workflow_config import (
    RAGBuildRunConfig,
    WebpageImageSummarizerRunConfig,
    WebsiteCrawlerRunConfig,
)
from utils.config_helper import save_run_config_as_toml
from utils.log_helper import setup_logging

setup_logging("info")

SITE_ID = "nculab"


def main() -> None:
    run_manager = RunManager()

    # ----- Website Crawler -----
    run_manager.set_module_path("website_crawler")
    website_crawler_run_config = WebsiteCrawlerRunConfig(site_id=SITE_ID)
    crawl_results = run_website_crawler(
        run_manager=run_manager, **vars(website_crawler_run_config)
    )
    save_run_config_as_toml(
        website_crawler_run_config,
        run_manager.run_config_toml_path,
    )
    run_manager.log_run_paths("complete")
    if crawl_results is None:
        return

    # ----- Webpage Image Summarizer -----
    run_manager.set_module_path("webpage_image_summarizer")
    webpage_image_summarizer_run_config = WebpageImageSummarizerRunConfig(
        site_id=SITE_ID
    )
    enhanced_results = run_webpage_image_summarizer(
        run_manager=run_manager,
        **vars(webpage_image_summarizer_run_config),
        crawl_results=crawl_results,
    )
    save_run_config_as_toml(
        webpage_image_summarizer_run_config,
        run_manager.run_config_toml_path,
    )
    run_manager.log_run_paths("complete")
    if enhanced_results is None:
        return

    # ----- RAG Build -----
    run_manager.set_module_path("rag_build")
    rag_build_run_config = RAGBuildRunConfig(
        site_id=SITE_ID, webpages_data_use_latest_results=True
    )
    run_rag_build(run_manager=run_manager, **vars(rag_build_run_config))
    save_run_config_as_toml(
        rag_build_run_config,
        run_manager.run_config_toml_path,
    )
    run_manager.log_run_paths("complete")


if __name__ == "__main__":
    main()
