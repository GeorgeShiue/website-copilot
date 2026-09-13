"""run_agent_build / run_agent_query / run_app 函數測試。

涵蓋：
- run_agent_build：建立 run context + 呼叫 create_agent，回傳 None，
  agent.close() 於 with 區塊結束後呼叫；create_agent 失敗時錯誤往外拋
- run_agent_query：內部建立 run context（module="agent" / base_folder="runs"）、
  agent.ask() 以正確參數呼叫、落盤委派 run_manager.save_agent_results_as_json()、
  auto thread_id、回傳 None
- run_agent_query（stream=True）：astream_result（coroutine）串流結果同樣經
  save_agent_results_as_json() 落盤
- run_agent_query（Goal 4）：run_config= 觸發一次 run_config.toml 落盤、log 生命週期 init → complete
- run_agent_query 的 finally 於成功與失敗路徑呼叫 agent.close()
- run_app：回傳 (uvicorn.Server, ChatApp)、以注入的 run_manager 建立 ChatApp、
  log 生命週期僅 init → complete、ChatApp.create 失敗時 agent.close() 且例外往外拋（R4）
- ChatApp.close() 觸發 agent.close()

所有外部依賴以 mock 替代，不觸發真實 LLM / RAG 資源。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from app.agent.agent import Agent


@dataclass
class _FakeAgentStub:
    """最小化 Agent 替身：記錄呼叫以便斷言。"""

    asked: list[dict[str, Any]] = field(default_factory=list)
    config: Any = field(
        default_factory=lambda: MagicMock(
            config_name="test",
            llm_name="test_llm",
            system_prompt="prompt",
        )
    )
    close_called: bool = field(default=False)

    def ask(self, query: str, thread_id: str | None = None) -> dict[str, Any]:
        self.asked.append({"query": query, "thread_id": thread_id})
        return {
            "query": query,
            "response": "fake answer",
            "sources": [],
            "timestamp": "2026-01-01 00:00:00",
        }

    async def astream_result(
        self,
        query: str,
        thread_id: str | None = None,
        on_token: Any = None,
    ) -> dict[str, Any]:
        # 與 production Agent.astream_result 同構（coroutine）：先逐 token 回呼，
        # 再回傳彙整結果；run_agent_query 以 asyncio.run(...) await 之。
        if on_token is not None:
            on_token("streamed answer")
        return {
            "query": query,
            "response": "streamed answer",
            "sources": [],
            "timestamp": "2026-01-01 00:00:00",
        }

    def close(self) -> None:
        self.close_called = True


@dataclass
class _FailingAgentStub(_FakeAgentStub):
    """Agent 替身：ask() 拋出例外（驗證 run_agent_query 的錯誤路徑）。"""

    def ask(self, query: str, thread_id: str | None = None) -> dict[str, Any]:
        raise RuntimeError("boom")


@dataclass
class _FailingStreamAgentStub(_FakeAgentStub):
    """Agent 替身：astream_result() 拋出例外（驗證 stream 模式的錯誤路徑）。"""

    async def astream_result(
        self,
        query: str,
        thread_id: str | None = None,
        on_token: Any = None,
    ) -> dict[str, Any]:
        raise RuntimeError("stream boom")


def _setup_mock_run_manager(mock_rm_cls: MagicMock) -> MagicMock:
    """設定 mock RunManager 的常用欄位，並回傳該 mock 實例。"""
    mock_rm = MagicMock()
    mock_rm.log_path = "fake.log"
    mock_rm.run_config_toml_path = "fake_run_config.toml"
    mock_rm.module_config_toml_path = "fake_module_config.toml"
    mock_rm.run_name = "test"
    mock_rm_cls.for_run_no_site.return_value = mock_rm
    return mock_rm


# ===========================================================================
# run_agent_build：純建構 API
# ===========================================================================


@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow_helper.RunManager")
@patch("app.workflow.workflow_helper.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_run_agent_build_calls_create_agent_and_returns_none(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
):
    """run_agent_build：建立 run context + 呼叫 create_agent，回傳 None，agent.close() 被呼叫。"""
    from app.workflow.workflow import run_agent_build

    fake_agent = _FakeAgentStub()
    mock_create_agent.return_value = fake_agent
    _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

    result = run_agent_build(config_name="test")

    assert result is None
    mock_create_agent.assert_called_once_with("test")
    assert fake_agent.close_called


@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow_helper.RunManager")
@patch("app.workflow.workflow_helper.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_run_agent_build_propagates_create_agent_error(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
):
    """create_agent 拋出例外時，錯誤往外拋且 agent.close() 不會被呼叫（agent 未建立）。"""
    from app.workflow.workflow import run_agent_build

    _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")
    mock_create_agent.side_effect = RuntimeError("init failed")

    with pytest.raises(RuntimeError):
        run_agent_build(config_name="test")


@patch("app.workflow.workflow.save_run_config_as_toml")
@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow_helper.RunManager")
@patch("app.workflow.workflow_helper.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_run_agent_build_writes_run_config_when_provided(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
    mock_save_run_config,
):
    """run_config= 觸發一次 run_config.toml 落盤，且 agent.close() 被呼叫。"""
    from app.workflow.workflow import run_agent_build

    fake_agent = _FakeAgentStub()
    mock_create_agent.return_value = fake_agent
    mock_rm = _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")
    run_config = MagicMock()

    run_agent_build(config_name="test", run_config=run_config)

    mock_save_run_config.assert_called_once_with(
        run_config, mock_rm.run_config_toml_path
    )
    assert fake_agent.close_called


# ===========================================================================
# run_agent_query：run context 所有者
# ===========================================================================


@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow_helper.RunManager")
@patch("app.workflow.workflow_helper.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_run_agent_query_creates_run_manager_with_runs(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
):
    """run_agent_query：RunManager 以 module="agent" / base_folder="runs" 建立。"""
    from app.workflow.workflow import run_agent_query

    mock_create_agent.return_value = _FakeAgentStub()
    _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

    run_agent_query(config_name="test", query="hello")

    mock_rm_cls.for_run_no_site.assert_called_once_with(
        module="agent",
        run_name="test",
        base_folder="runs",
    )


@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow_helper.RunManager")
@patch("app.workflow.workflow_helper.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_run_agent_query_calls_agent_ask(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
):
    """run_agent_query：agent.ask() 以正確 query 和 thread_id 呼叫。"""
    from app.workflow.workflow import run_agent_query

    fake_agent = _FakeAgentStub()
    mock_create_agent.return_value = fake_agent
    _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

    run_agent_query(config_name="test", query="你好", thread_id="session-1")

    assert len(fake_agent.asked) == 1
    assert fake_agent.asked[0]["query"] == "你好"
    assert fake_agent.asked[0]["thread_id"] == "session-1"


@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow_helper.RunManager")
@patch("app.workflow.workflow_helper.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_run_agent_query_delegates_save_to_run_manager(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
):
    """run_agent_query：落盤委派 run_manager.save_agent_results_as_json()。"""
    from app.workflow.workflow import run_agent_query

    fake_agent = _FakeAgentStub()
    mock_create_agent.return_value = fake_agent
    mock_rm = _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

    run_agent_query(config_name="test", query="hello", thread_id="session-1")

    mock_rm.save_agent_results_as_json.assert_called_once()
    save_kwargs = mock_rm.save_agent_results_as_json.call_args.kwargs
    assert save_kwargs["thread_id"] == "session-1"
    assert save_kwargs["agent_config"] is fake_agent.config
    assert save_kwargs["results"][0]["response"] == "fake answer"


@patch("app.workflow.workflow.log_session")
def test_run_agent_query_returns_none(mock_log_session):
    """run_agent_query 回傳 None。"""
    from app.workflow.workflow import run_agent_query

    with (
        patch("app.workflow.workflow.create_agent") as mock_create_agent,
        patch("app.workflow.workflow.AgentConfig") as mock_config_cls,
        patch("app.workflow.workflow_helper.RunManager") as mock_rm_cls,
        patch("app.workflow.workflow_helper.save_logging_file"),
    ):
        mock_create_agent.return_value = _FakeAgentStub()
        _setup_mock_run_manager(mock_rm_cls)
        mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

        assert run_agent_query(config_name="test", query="hello") is None


@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow_helper.RunManager")
@patch("app.workflow.workflow_helper.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_run_agent_query_auto_generates_thread_id(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
):
    """thread_id 為 None 時自動產生 auto-{uuid} 並用於落盤。"""
    from app.workflow.workflow import run_agent_query

    mock_create_agent.return_value = _FakeAgentStub()
    mock_rm = _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

    run_agent_query(config_name="test", query="hello")

    thread_id = mock_rm.save_agent_results_as_json.call_args.kwargs["thread_id"]
    assert thread_id is not None
    assert thread_id.startswith("auto-")


@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow_helper.RunManager")
@patch("app.workflow.workflow_helper.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_run_agent_query_closes_agent_on_success(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
):
    """run_agent_query 在成功時以 finally 呼叫 agent.close()。"""
    from app.workflow.workflow import run_agent_query

    fake_agent = _FakeAgentStub()
    mock_create_agent.return_value = fake_agent
    _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

    run_agent_query(config_name="test", query="hello")

    assert fake_agent.close_called


@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow_helper.RunManager")
@patch("app.workflow.workflow_helper.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_run_agent_query_closes_agent_on_error(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
):
    """run_agent_query 在 ask() 拋出例外時仍呼叫 agent.close()。"""
    from app.workflow.workflow import run_agent_query

    fake_agent = _FailingAgentStub()
    mock_create_agent.return_value = fake_agent
    _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

    with pytest.raises(RuntimeError):
        run_agent_query(config_name="test", query="hello")

    assert fake_agent.close_called


@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow_helper.RunManager")
@patch("app.workflow.workflow_helper.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_run_agent_query_closes_agent_on_stream_error(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
):
    """run_agent_query 在 stream 模式例外時仍呼叫 agent.close()。"""
    from app.workflow.workflow import run_agent_query

    fake_agent = _FailingStreamAgentStub()
    mock_create_agent.return_value = fake_agent
    _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

    with pytest.raises(RuntimeError):
        run_agent_query(config_name="test", query="hello", stream=True)

    assert fake_agent.close_called


@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow_helper.RunManager")
@patch("app.workflow.workflow_helper.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_run_agent_query_stream_persists_streamed_result(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
):
    """stream=True 的 happy path：astream_result 的串流結果經 save_agent_results_as_json 落盤。"""
    from app.workflow.workflow import run_agent_query

    fake_agent = _FakeAgentStub()
    mock_create_agent.return_value = fake_agent
    mock_rm = _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

    run_agent_query(
        config_name="test",
        query="hello",
        thread_id="session-1",
        stream=True,
    )

    mock_rm.save_agent_results_as_json.assert_called_once()
    save_kwargs = mock_rm.save_agent_results_as_json.call_args.kwargs
    assert save_kwargs["thread_id"] == "session-1"
    assert save_kwargs["agent_config"] is fake_agent.config
    assert save_kwargs["results"][0]["response"] == "streamed answer"
    assert fake_agent.close_called


@patch("app.workflow.workflow.save_run_config_as_toml")
@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow_helper.RunManager")
@patch("app.workflow.workflow_helper.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_run_agent_query_writes_run_config_and_log_lifecycle(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
    mock_save_run_config,
):
    """Goal 4：run_config= 觸發恰好一次 run_config.toml 落盤，log 生命週期為 init → complete。"""
    from app.workflow.workflow import run_agent_query

    mock_create_agent.return_value = _FakeAgentStub()
    mock_rm = _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")
    run_config = MagicMock()

    run_agent_query(config_name="test", query="hello", run_config=run_config)

    mock_save_run_config.assert_called_once_with(
        run_config, mock_rm.run_config_toml_path
    )
    assert [call.args[0] for call in mock_rm.log_run_paths.call_args_list] == [
        "init",
        "complete",
    ]


# ===========================================================================
# run_app：回傳 tuple、log 生命週期、失敗守衛
# ===========================================================================


@patch("app.workflow.workflow.uvicorn")
@patch("app.workflow.workflow.ChatApp")
@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow_helper.RunManager")
@patch("app.workflow.workflow_helper.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_run_app_returns_server_and_chat_app(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
    mock_chat_app_cls,
    mock_uvicorn,
):
    """run_app：回傳 (uvicorn.Server, ChatApp)，ChatApp 以注入的 run_manager 建立。"""
    from app.workflow.workflow import run_app

    fake_agent = _FakeAgentStub()
    mock_create_agent.return_value = fake_agent
    mock_rm = _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

    server, chat_app = run_app(config_name="test")

    assert server is mock_uvicorn.Server.return_value
    assert chat_app is mock_chat_app_cls.create.return_value
    mock_chat_app_cls.create.assert_called_once_with(
        agent=fake_agent,
        run_manager=mock_rm,
        allowed_origins=None,
    )
    mock_uvicorn.Config.assert_called_once_with(
        chat_app.app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
    # 建構成功：不關閉 agent（由呼叫端的 ChatApp.close() 負責）
    assert not fake_agent.close_called


@patch("app.workflow.workflow.uvicorn")
@patch("app.workflow.workflow.ChatApp")
@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow_helper.RunManager")
@patch("app.workflow.workflow_helper.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_run_app_logs_init_then_complete_only(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
    mock_chat_app_cls,
    mock_uvicorn,
):
    """run_app 的 log 生命週期僅 init → complete（不使用未定義的 "ready"）。"""
    from app.workflow.workflow import run_app

    mock_create_agent.return_value = _FakeAgentStub()
    mock_rm = _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

    run_app(config_name="test")

    assert [call.args[0] for call in mock_rm.log_run_paths.call_args_list] == [
        "init",
        "complete",
    ]


@patch("app.workflow.workflow.uvicorn")
@patch("app.workflow.workflow.ChatApp")
@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow_helper.RunManager")
@patch("app.workflow.workflow_helper.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_run_app_closes_agent_when_chat_app_creation_fails(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
    mock_chat_app_cls,
    mock_uvicorn,
):
    """run_app：ChatApp.create 失敗時 agent.close() 被呼叫且例外往外拋（R4 守衛）。"""
    from app.workflow.workflow import run_app

    fake_agent = _FakeAgentStub()
    mock_create_agent.return_value = fake_agent
    _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")
    mock_chat_app_cls.create.side_effect = RuntimeError("chat app boom")

    with pytest.raises(RuntimeError):
        run_app(config_name="test")

    assert fake_agent.close_called


def test_chat_app_close_closes_agent():
    """ChatApp.close() 觸發 agent.close()（server 路徑的關閉歸屬）。"""
    from app.server.app import ChatApp

    fake_agent = _FakeAgentStub()
    chat_app = ChatApp.create(
        agent=cast(Agent, fake_agent),
        run_manager=MagicMock(),
    )

    chat_app.close()

    assert fake_agent.close_called
