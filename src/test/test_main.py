from app.workflow.workflow import (
    run_rag_build,
    run_webpage_image_summarizer,
    run_website_crawler,
)
from utils.log_helper import setup_logging

setup_logging("debug")


def test_main():
    crawl_results, _ = run_website_crawler(
        config_name="test",
    )
    if crawl_results is None:
        return

    enhanced_crawl_results, _ = run_webpage_image_summarizer(
        config_name="test",
        crawl_results=crawl_results,
    )
    if enhanced_crawl_results is None:
        return

    run_rag_build(
        config_name="test",
        save_vector_store_to_runs=True,
    )
