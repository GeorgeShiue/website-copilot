import pytest

from app.workflow.workflow import (
    run_agent,
    run_rag_build,
    run_server,
    run_webpage_image_summarizer,
    run_website_crawler,
)
from utils.log_helper import setup_logging

setup_logging("debug")

# 端到端測試（真實爬蟲 / LLM / 建庫），以 pytest -m "not slow" 略過
pytestmark = pytest.mark.slow

SERVER_PORT = 8001


def test_website_crawler():
    run_website_crawler(config_name="test")


def test_webpage_image_summarizer():
    run_webpage_image_summarizer(config_name="test")


def test_rag():
    run_rag_build(config_name="test", save_vector_store_to_runs=True)


def test_agent():
    run_agent(query="實驗室的成員有哪些人？", config_name="test")


def test_server():
    run_server(host="127.0.0.1", port=SERVER_PORT, config_name="test")
