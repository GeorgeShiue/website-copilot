from app.workflow.workflow import (
    run_rag_build,
    run_webpage_image_summarizer,
    run_website_crawler,
)
from app.workflow.workflow_manager import RunManager
from utils.log_helper import setup_logging

setup_logging("debug")


# TODO: 更新測試 config
def test_main():
    run_manager = RunManager()

    run_manager.set_module_path("website_crawler")
    crawl_results = run_website_crawler(run_manager=run_manager, config_name="test")
    if crawl_results is None:
        return

    run_manager.set_module_path("webpage_image_summarizer")
    enhanced_crawl_results = run_webpage_image_summarizer(
        run_manager=run_manager, config_name="test", crawl_results=crawl_results
    )
    if enhanced_crawl_results is None:
        return

    run_manager.set_module_path("rag_build")
    run_rag_build(
        run_manager=run_manager,
        config_name="test",
        webpages_data_use_latest_results=True,
        save_vector_store_to_runs=True,
    )
