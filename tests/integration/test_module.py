"""各 run function 的整合測試：以 config 名稱 "test" 逐一執行，只驗證不拋例外。

會呼叫 LLM / VLM / embedding API 的測試標記 cost，可用 -m "not cost" 略過。
"""

import pytest

from website_copilot.config.pipeline_config import (
    AgentRunConfig,
    AugmenterRunConfig,
    RAGBuildRunConfig,
    ServeRunConfig,
    WebsiteCrawlerRunConfig,
)
from website_copilot.pipelines.exp import run_agent_query
from website_copilot.pipelines.prepare import (
    run_augmenter,
    run_rag_build,
    run_website_crawler,
)
from website_copilot.pipelines.serve import run_agent_build
from website_copilot.utils.log_helper import setup_logging

setup_logging("debug")


@pytest.mark.cost
def test_website_crawler():
    run_website_crawler(WebsiteCrawlerRunConfig(site="nculab", config_name="test"))


@pytest.mark.cost
def test_augmenter():
    run_augmenter(AugmenterRunConfig(site="nculab", config_name="test"))


@pytest.mark.cost
def test_rag_build():
    run_rag_build(RAGBuildRunConfig(site="nculab", config_name="test"))


def test_agent_build():
    """只建立 LLM client，不呼叫 API。"""
    agent = run_agent_build(ServeRunConfig(config_name="test"))
    agent.close()


@pytest.mark.cost
def test_agent_query():
    run_agent_query(AgentRunConfig(config_name="test", query="實驗室的成員有哪些人？"))
