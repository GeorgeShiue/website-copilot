from dataclasses import dataclass

from app.configs.workflow_config import (
    RAGBuildRunConfig,
    WebpageImageSummarizerRunConfig,
    WebsiteCrawlerRunConfig,
)
from app.workflow.data_manager import DataManager
from app.workflow.workflow import (
    run_rag_build,
    run_webpage_image_summarizer,
    run_website_crawler,
)
from utils.config_helper import save_run_config_as_toml
from utils.log_helper import setup_logging


@dataclass
class MainCLI:
    """完整流水線：爬蟲 → 圖片摘要 → RAG 建庫，所有模組使用同一個 config_name。"""

    config_name: str = "default"


def main(cli: MainCLI | None = None) -> None:
    if cli is None:
        cli = MainCLI()

    setup_logging("info")
    data_manager = DataManager()

    # ----- Website Crawler -----
    website_crawler_run_config = WebsiteCrawlerRunConfig(
        config_name=cli.config_name,
    )
    crawl_results, crawl_run_manager = run_website_crawler(
        **vars(website_crawler_run_config),
        data_manager=data_manager,
    )
    save_run_config_as_toml(
        website_crawler_run_config,
        crawl_run_manager.run_config_toml_path,
    )
    data_manager.publish_run_metadata(
        site_id=crawl_run_manager.site_id,
        category="webpages",
        module_config_path=crawl_run_manager.module_config_toml_path,
        run_config_path=crawl_run_manager.run_config_toml_path,
        log_path=crawl_run_manager.log_path,
    )
    crawl_run_manager.log_run_paths("complete")
    if crawl_results is None:
        return

    # ----- Webpage Image Summarizer -----
    webpage_image_summarizer_run_config = WebpageImageSummarizerRunConfig(
        config_name=cli.config_name,
    )
    enhanced_results, summarizer_run_manager = run_webpage_image_summarizer(
        **vars(webpage_image_summarizer_run_config),
        crawl_results=crawl_results,
        data_manager=data_manager,
    )
    save_run_config_as_toml(
        webpage_image_summarizer_run_config,
        summarizer_run_manager.run_config_toml_path,
    )
    data_manager.publish_run_metadata(
        site_id=summarizer_run_manager.site_id,
        category="webpages",
        module_config_path=summarizer_run_manager.module_config_toml_path,
        run_config_path=summarizer_run_manager.run_config_toml_path,
        log_path=summarizer_run_manager.log_path,
    )
    summarizer_run_manager.log_run_paths("complete")
    if enhanced_results is None:
        return

    # ----- RAG Build -----
    rag_build_run_config = RAGBuildRunConfig(
        config_name=cli.config_name,
        webpages_data_use_latest_results=True,
    )
    rag_build_run_manager = run_rag_build(
        **vars(rag_build_run_config),
        data_manager=data_manager,
    )
    save_run_config_as_toml(
        rag_build_run_config,
        rag_build_run_manager.run_config_toml_path,
    )
    data_manager.publish_run_metadata(
        site_id=rag_build_run_manager.site_id,
        category="rag",
        module_config_path=rag_build_run_manager.module_config_toml_path,
        run_config_path=rag_build_run_manager.run_config_toml_path,
        log_path=rag_build_run_manager.log_path,
    )
    rag_build_run_manager.log_run_paths("complete")


if __name__ == "__main__":
    import tyro

    main(tyro.cli(MainCLI))
