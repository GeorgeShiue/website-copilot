from dataclasses import dataclass

from app.configs.workflow_config import (
    RAGBuildRunConfig,
    WebpageImageSummarizerRunConfig,
    WebsiteCrawlerRunConfig,
)
from app.workflow.data_manager import DataManager
from app.workflow.run_manager import RunManager
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
    run_manager = RunManager()
    data_manager = DataManager()

    # ----- Website Crawler -----
    run_manager.set_module_path("website_crawler")
    website_crawler_run_config = WebsiteCrawlerRunConfig(
        config_name=cli.config_name,
    )
    crawl_results = run_website_crawler(
        run_manager=run_manager,
        **vars(website_crawler_run_config),
        data_manager=data_manager,
    )
    save_run_config_as_toml(
        website_crawler_run_config,
        run_manager.run_config_toml_path,
    )
    data_manager.publish_run_metadata(
        site_id=run_manager.site_id,
        category="webpages",
        module_config_path=run_manager.module_config_toml_path,
        run_config_path=run_manager.run_config_toml_path,
        log_path=run_manager.log_path,
    )
    run_manager.log_run_paths("complete")
    if crawl_results is None:
        return

    # ----- Webpage Image Summarizer -----
    run_manager.set_module_path("webpage_image_summarizer")
    webpage_image_summarizer_run_config = WebpageImageSummarizerRunConfig(
        config_name=cli.config_name,
    )
    enhanced_results = run_webpage_image_summarizer(
        run_manager=run_manager,
        **vars(webpage_image_summarizer_run_config),
        crawl_results=crawl_results,
        data_manager=data_manager,
    )
    save_run_config_as_toml(
        webpage_image_summarizer_run_config,
        run_manager.run_config_toml_path,
    )
    data_manager.publish_run_metadata(
        site_id=run_manager.site_id,
        category="webpages",
        module_config_path=run_manager.module_config_toml_path,
        run_config_path=run_manager.run_config_toml_path,
        log_path=run_manager.log_path,
    )
    run_manager.log_run_paths("complete")
    if enhanced_results is None:
        return

    # ----- RAG Build -----
    run_manager.set_module_path("rag_build")
    rag_build_run_config = RAGBuildRunConfig(
        config_name=cli.config_name,
        webpages_data_use_latest_results=True,
    )
    run_rag_build(
        run_manager=run_manager,
        **vars(rag_build_run_config),
        data_manager=data_manager,
    )
    save_run_config_as_toml(
        rag_build_run_config,
        run_manager.run_config_toml_path,
    )
    data_manager.publish_run_metadata(
        site_id=run_manager.site_id,
        category="rag",
        module_config_path=run_manager.module_config_toml_path,
        run_config_path=run_manager.run_config_toml_path,
        log_path=run_manager.log_path,
    )
    run_manager.log_run_paths("complete")


if __name__ == "__main__":
    import tyro

    main(tyro.cli(MainCLI))
