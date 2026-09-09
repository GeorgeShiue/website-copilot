from dataclasses import dataclass

from app.workflow.data_manager import DataManager
from app.workflow.workflow import (
    run_rag_build,
    run_webpage_image_summarizer,
    run_website_crawler,
)
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
    crawl_results = run_website_crawler(
        config_name=cli.config_name,
        data_manager=data_manager,
    )
    if crawl_results is None:
        return

    # ----- Webpage Image Summarizer -----
    enhanced_results = run_webpage_image_summarizer(
        config_name=cli.config_name,
        crawl_results=crawl_results,
        data_manager=data_manager,
    )
    if enhanced_results is None:
        return

    # ----- RAG Build -----
    run_rag_build(
        config_name=cli.config_name,
        force_rebuild=True,
        webpages_data_use_latest_results=True,
        save_vector_store_to_runs=True,
        data_manager=data_manager,
    )


if __name__ == "__main__":
    import tyro

    main(tyro.cli(MainCLI))
