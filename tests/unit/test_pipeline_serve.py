"""pipelines/serve.py 測試：run_agent_build / run_server_build / serve，以及 ChatApp / ChatServer 的關閉歸屬。

涵蓋：
- run_agent_build：建立 run context（module="agent_build"）+ 呼叫 create_agent，
  回傳未關閉的 agent；落盤失敗時關閉 agent
- run_server_build：ChatApp.create 失敗時例外往外拋且不關閉注入的 agent
- serve：依序呼叫 run_agent_build → run_server_build(agent) → run()，吞下 KeyboardInterrupt；
  server build 失敗時關閉 agent（R4）
- ChatApp.close() 觸發 agent.close()；ChatServer.serve 結束時（正常／中斷／例外）自動關閉 ChatApp

所有外部依賴以 mock 替代，不觸發真實 LLM / RAG 資源。
"""

from __future__ import annotations

from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from agent_stubs import FakeAgentStub, setup_mock_run_manager

from website_copilot.agent.agent import Agent
from website_copilot.config.agent_config import AgentConfig
from website_copilot.server.server import ChatServer


# ===========================================================================
# run_agent_build：純建構 API
# ===========================================================================


@patch("website_copilot.pipelines.serve.save_module_config")
@patch("website_copilot.pipelines.serve.create_agent")
@patch("website_copilot.pipelines.serve.AgentConfig")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.serve.log_session")
def test_run_agent_build_calls_create_agent_and_returns_agent(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
    mock_save_module_config,
):
    """run_agent_build：建立 run context + 呼叫 create_agent，回傳 agent 且不關閉（由呼叫端負責）。"""
    from website_copilot.pipelines.serve import run_agent_build

    fake_agent = FakeAgentStub()
    mock_create_agent.return_value = fake_agent
    setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_yaml.return_value = AgentConfig(
        llm_name="test_llm", system_prompt="prompt"
    )

    result = run_agent_build(config_name="test")

    assert result is fake_agent
    mock_create_agent.assert_called_once_with(mock_config_cls.from_yaml.return_value)
    assert mock_rm_cls.for_run_no_site.call_args.kwargs["module"] == "agent_build"
    assert not fake_agent.close_called


@patch("website_copilot.pipelines.serve.save_module_config")
@patch("website_copilot.pipelines.serve.create_agent")
@patch("website_copilot.pipelines.serve.AgentConfig")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.serve.log_session")
def test_run_agent_build_closes_agent_when_save_fails(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
    mock_save_module_config,
):
    """agent 建立後落盤失敗：agent.close() 被呼叫且例外往外拋。"""
    from website_copilot.pipelines.serve import run_agent_build

    fake_agent = FakeAgentStub()
    mock_create_agent.return_value = fake_agent
    setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_yaml.return_value = AgentConfig(
        llm_name="test_llm", system_prompt="prompt"
    )
    mock_save_module_config.side_effect = OSError("disk full")

    with pytest.raises(OSError):
        run_agent_build(config_name="test")

    assert fake_agent.close_called


# ===========================================================================
# run_server_build：注入 agent、獨立 run context、log 生命週期、失敗不關閉 agent
# ===========================================================================


@patch("website_copilot.pipelines.serve.uvicorn")
@patch("website_copilot.pipelines.serve.ChatApp")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.serve.log_session")
def test_run_server_build_does_not_close_injected_agent_on_failure(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_chat_app_cls,
    mock_uvicorn,
):
    """run_server_build：ChatApp.create 失敗時例外往外拋，注入的 agent 不由此關閉。"""
    from website_copilot.pipelines.serve import run_server_build

    fake_agent = FakeAgentStub()
    setup_mock_run_manager(mock_rm_cls)
    mock_chat_app_cls.create.side_effect = RuntimeError("chat app boom")

    with pytest.raises(RuntimeError):
        run_server_build(cast(Agent, fake_agent))

    assert not fake_agent.close_called


# ===========================================================================
# serve：串接 run_agent_build → run_server_build，失敗守衛
# ===========================================================================


@patch("website_copilot.pipelines.serve.run_server_build")
@patch("website_copilot.pipelines.serve.run_agent_build")
def test_serve_builds_agent_then_server_and_runs(
    mock_run_agent_build, mock_run_server_build
):
    """serve：以 run_config.config_name 建構 agent，再注入 run_server_build 並 run()；吞下 KeyboardInterrupt。"""
    from website_copilot.config.pipeline_config import ServeRunConfig
    from website_copilot.pipelines.serve import serve

    fake_agent = FakeAgentStub()
    mock_run_agent_build.return_value = fake_agent
    mock_run_server_build.return_value.run.side_effect = KeyboardInterrupt
    run_config = ServeRunConfig(config_name="test", port=9000)

    serve(run_config)

    mock_run_agent_build.assert_called_once_with(config_name="test")
    mock_run_server_build.assert_called_once_with(
        fake_agent,
        run_config=run_config,
        allowed_origins=run_config.allowed_origins,
        host=run_config.host,
        port=9000,
    )
    mock_run_server_build.return_value.run.assert_called_once()
    # 成功路徑：agent 由 ChatServer 結束時關閉，serve 不直接關閉
    assert not fake_agent.close_called


@patch("website_copilot.pipelines.serve.run_server_build")
@patch("website_copilot.pipelines.serve.run_agent_build")
def test_serve_closes_agent_when_server_build_fails(
    mock_run_agent_build, mock_run_server_build
):
    """serve：run_server_build 失敗時 agent.close() 被呼叫且例外往外拋（R4 守衛）。"""
    from website_copilot.config.pipeline_config import ServeRunConfig
    from website_copilot.pipelines.serve import serve

    fake_agent = FakeAgentStub()
    mock_run_agent_build.return_value = fake_agent
    mock_run_server_build.side_effect = RuntimeError("server boom")

    with pytest.raises(RuntimeError):
        serve(ServeRunConfig(config_name="test"))

    assert fake_agent.close_called


# ===========================================================================
# ChatApp / ChatServer：agent 資源的關閉歸屬
# ===========================================================================


def test_chat_app_close_closes_agent():
    """ChatApp.close() 觸發 agent.close()（server 路徑的關閉歸屬）。"""
    from website_copilot.server.app import ChatApp

    fake_agent = FakeAgentStub()
    chat_app = ChatApp.create(
        agent=cast(Agent, fake_agent),
        run_manager=MagicMock(),
    )

    chat_app.close()

    assert fake_agent.close_called


@pytest.mark.parametrize(
    "serve_error", [None, KeyboardInterrupt(), RuntimeError("boom")]
)
@patch("website_copilot.server.server.log_session")
def test_chat_server_serve_closes_chat_app_on_exit(mock_log_session, serve_error):
    """ChatServer.serve 結束時（正常、中斷、例外）皆關閉 ChatApp，且例外照常往外拋。"""
    import asyncio

    import uvicorn

    chat_app = MagicMock()
    server = ChatServer(uvicorn.Config(app=MagicMock()), chat_app=chat_app)

    with patch.object(uvicorn.Server, "serve", side_effect=serve_error) as mock_serve:
        if serve_error is None:
            asyncio.run(server.serve())
        else:
            with pytest.raises(type(serve_error)):
                asyncio.run(server.serve())

    mock_serve.assert_awaited_once()
    chat_app.close.assert_called_once()
    mock_log_session.assert_called_with("Server Stopped", style="cyan")
