import asyncio

import pytest

from app.workflow.workflow import (
    run_agent_query,
    run_app,
    run_rag_build,
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
    run_rag_build(config_name="test", force_rebuild=True)


def test_agent():
    run_agent_query(config_name="test", query="實驗室的成員有哪些人？")


def test_server():
    """config_name='test' 時，啟動後自動關閉。"""
    server, chat_app = run_app(config_name="test", host="0.0.0.0", port=SERVER_PORT)

    async def _run_and_stop():
        serve_task = asyncio.create_task(server.serve())
        await asyncio.sleep(2)  # 給伺服器啟動時間
        server.should_exit = True  # 觸發優雅關閉
        await serve_task

    try:
        asyncio.run(_run_and_stop())
    finally:
        chat_app.close()
