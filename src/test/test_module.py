from app.workflow.workflow import (
    run_agent,
    run_rag_build,
    run_webpage_image_summarizer,
    run_website_crawler,
)
from utils.log_helper import setup_logging

setup_logging("debug")


def test_website_crawler():
    run_website_crawler(config_name="test")


def test_webpage_image_summarizer():
    run_webpage_image_summarizer(config_name="test")


def test_rag():
    run_rag_build(config_name="test", save_vector_store_to_runs=True)


def test_agent():
    run_agent(query="實驗室的成員有哪些人？", config_name="test")
