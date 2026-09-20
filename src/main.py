from dataclasses import dataclass

from app.configs.workflow_config import MainRunConfig
from app.workflow.data_manager import DataManager
from app.workflow.workflow import (
    run_app,
    run_rag_build,
    run_webpage_image_summarizer,
    run_website_crawler,
)
from utils.log_helper import log_run_time, setup_logging


@dataclass
class MainCLI:
    run: MainRunConfig


def main(config_name: str = "default") -> None:
    setup_logging("info")
    data_manager = DataManager()

    # 計時範圍：爬蟲 → 圖片摘要 → RAG build（不含阻塞的 server 執行時間）
    with log_run_time(f"Main Workflow ({config_name})"):
        # ----- Website Crawler -----
        crawl_results = run_website_crawler(
            config_name=config_name,
            data_manager=data_manager,
        )
        if crawl_results is None:
            return

        # ----- Webpage Image Summarizer -----
        enhanced_results = run_webpage_image_summarizer(
            config_name=config_name,
            crawl_results=crawl_results,
            data_manager=data_manager,
        )
        if enhanced_results is None:
            return

        # ----- RAG Build -----
        run_rag_build(
            config_name=config_name,
            force_rebuild=True,
            webpages_data_use_latest_results=True,
            save_vector_store_to_runs=True,
            data_manager=data_manager,
        )

    # ----- Chat Server（阻塞至中斷）-----
    # run_app 在 try 之外：建構失敗時不進入 try，close 對象必然存在
    server, chat_app = run_app(config_name="default")  # server 不因網站變更 config
    try:
        server.run()
    finally:
        chat_app.close()


if __name__ == "__main__":
    import tyro

    cli_arg = tyro.cli(MainCLI)
    main(config_name=cli_arg.run.config_name)
