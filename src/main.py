from app.workflow.data_manager import DataManager
from app.workflow.workflow import (
    run_app,
    run_rag_build,
    run_webpage_image_summarizer,
    run_website_crawler,
)
from utils.log_helper import setup_logging

DEFAULT_CONFIG_NAME = "default"


def main() -> None:
    setup_logging("info")
    data_manager = DataManager()

    # ----- Website Crawler -----
    crawl_results = run_website_crawler(
        config_name=DEFAULT_CONFIG_NAME,
        data_manager=data_manager,
    )
    if crawl_results is None:
        return

    # ----- Webpage Image Summarizer -----
    enhanced_results = run_webpage_image_summarizer(
        config_name=DEFAULT_CONFIG_NAME,
        crawl_results=crawl_results,
        data_manager=data_manager,
    )
    if enhanced_results is None:
        return

    # ----- RAG Build -----
    run_rag_build(
        config_name=DEFAULT_CONFIG_NAME,
        force_rebuild=True,
        webpages_data_use_latest_results=True,
        save_vector_store_to_runs=True,
        data_manager=data_manager,
    )

    # ----- Chat Server（阻塞至中斷）-----
    # run_app 在 try 之外：建構失敗時不進入 try，close 對象必然存在
    server, chat_app = run_app(config_name=DEFAULT_CONFIG_NAME)
    try:
        server.run()
    finally:
        chat_app.close()


if __name__ == "__main__":
    main()
