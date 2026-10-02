"""prepare / serve 階段的整合測試：以 config 名稱 "test" 執行完整流程，只驗證不拋例外。

會呼叫 LLM / VLM / embedding API 的測試標記 cost，可用 -m "not cost" 略過。
"""

import asyncio

import pytest

from website_copilot.config.pipeline_config import PrepareRunConfig, ServeRunConfig
from website_copilot.pipelines.prepare import run_prepare
from website_copilot.pipelines.serve import run_agent_build, run_server_build
from website_copilot.utils.log_helper import setup_logging

setup_logging("debug")

SERVER_PORT = 8001


@pytest.mark.cost
def test_prepare():
    """publish=False：結果只存到 runs/，不覆寫 data/。"""
    run_prepare(PrepareRunConfig(site="nculab", config_name="test", publish=False))


def test_serve():
    """啟動後自動關閉；不直接呼叫 serve()，因其 server.run() 會阻塞。"""
    run_config = ServeRunConfig(config_name="test", host="0.0.0.0", port=SERVER_PORT)
    agent = run_agent_build(run_config)
    server = run_server_build(agent, run_config)

    async def _run_and_stop():
        serve_task = asyncio.create_task(server.serve())
        await asyncio.sleep(2)  # 給伺服器啟動時間
        server.should_exit = True  # 觸發優雅關閉
        await serve_task

    asyncio.run(_run_and_stop())  # ChatServer.serve 結束時自動關閉 ChatApp
