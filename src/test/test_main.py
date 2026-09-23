import pytest

from app.workflow.workflow import (
    run_agent_query,
    run_rag_build,
    run_webpage_image_summarizer,
    run_website_crawler,
)
from utils.log_helper import setup_logging

setup_logging("debug")

pytestmark = pytest.mark.slow


def test_main():
    crawl_results = run_website_crawler(config_name="test")
    if crawl_results is None:
        return

    enhanced_crawl_results = run_webpage_image_summarizer(
        config_name="test",
        crawl_results=crawl_results,
    )
    if enhanced_crawl_results is None:
        return

    run_rag_build(config_name="test")

    run_agent_query(config_name="test", query="實驗室有哪些成員？")
