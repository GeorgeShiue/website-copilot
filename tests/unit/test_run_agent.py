"""run_agent_build / run_agent_query / run_server_build / serve 函數測試。

涵蓋：
- run_agent_build：建立自己的 run context（module="agent_build"）+ 呼叫 create_agent，
  回傳未關閉的 agent；create_agent 失敗時錯誤往外拋
- run_agent_query：內部建立 run context（module="agent" / base_folder="runs"）、
  agent.ask() 以正確參數呼叫、落盤委派 run_manager.save_agent_results_as_json()、
  auto thread_id、回傳 None
- run_agent_query（stream=True）：astream_result（coroutine）串流結果同樣經
  save_agent_results_as_json() 落盤
- run_agent_query（Goal 4）：run_config= 觸發一次 run_config.toml 落盤、log 生命週期 init → complete
- run_agent_query：agent 經 run_agent_build 建構、不寫 module_config.toml；
  finally 於成功與失敗路徑呼叫 agent.close()（失敗路徑只呼叫一次）
- run_server_build：以注入的 agent 建立自己的 run context（module="server"）、
  回傳持有 ChatApp 的 ChatServer、不寫 module_config.toml、
  log 生命週期僅 init → complete、ChatApp.create 失敗時例外往外拋且不關閉注入的 agent
- serve：依序呼叫 run_agent_build → run_server_build(agent)；server build 失敗時關閉 agent（R4）
- ChatApp.close() 觸發 agent.close()；ChatServer.serve 結束時（正常／中斷／例外）自動關閉 ChatApp

所有外部依賴以 mock 替代，不觸發真實 LLM / RAG 資源。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from website_copilot.agent.agent import Agent
from website_copilot.server.server import ChatServer


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
    close_count: int = field(default=0)

    @property
    def close_called(self) -> bool:
        return self.close_count > 0

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
        self.close_count += 1


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


@patch("website_copilot.pipelines.serve.save_module_config_as_toml")
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

    fake_agent = _FakeAgentStub()
    mock_create_agent.return_value = fake_agent
    _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

    result = run_agent_build(config_name="test")

    assert result is fake_agent
    mock_create_agent.assert_called_once_with(mock_config_cls.from_toml.return_value)
    assert mock_rm_cls.for_run_no_site.call_args.kwargs["module"] == "agent_build"
    assert not fake_agent.close_called


@patch("website_copilot.pipelines.serve.create_agent")
@patch("website_copilot.pipelines.serve.AgentConfig")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.serve.log_session")
def test_run_agent_build_propagates_create_agent_error(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
):
    """create_agent 拋出例外時，錯誤往外拋且 agent.close() 不會被呼叫（agent 未建立）。"""
    from website_copilot.pipelines.serve import run_agent_build

    _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")
    mock_create_agent.side_effect = RuntimeError("init failed")

    with pytest.raises(RuntimeError):
        run_agent_build(config_name="test")


@patch("website_copilot.pipelines.serve.save_module_config_as_toml")
@patch("website_copilot.pipelines.serve.save_run_config_as_toml")
@patch("website_copilot.pipelines.serve.create_agent")
@patch("website_copilot.pipelines.serve.AgentConfig")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.serve.log_session")
def test_run_agent_build_writes_run_config_when_provided(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
    mock_save_run_config,
    mock_save_module_config,
):
    """run_config= 觸發一次 run_config.toml 落盤。"""
    from website_copilot.pipelines.serve import run_agent_build

    fake_agent = _FakeAgentStub()
    mock_create_agent.return_value = fake_agent
    mock_rm = _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")
    run_config = MagicMock()

    run_agent_build(config_name="test", run_config=run_config)

    mock_save_run_config.assert_called_once_with(
        run_config, mock_rm.run_config_toml_path
    )


@patch("website_copilot.pipelines.serve.save_module_config_as_toml")
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

    fake_agent = _FakeAgentStub()
    mock_create_agent.return_value = fake_agent
    _setup_mock_run_manager(mock_rm_cls)
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")
    mock_save_module_config.side_effect = OSError("disk full")

    with pytest.raises(OSError):
        run_agent_build(config_name="test")

    assert fake_agent.close_called


# ===========================================================================
# run_agent_query：run context 所有者（agent 經 run_agent_build 建構）
# ===========================================================================


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_creates_run_manager_with_runs(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
):
    """run_agent_query：RunManager 以 module="agent" / base_folder="runs" 建立。"""
    from website_copilot.pipelines.exp import run_agent_query

    mock_run_agent_build.return_value = _FakeAgentStub()
    _setup_mock_run_manager(mock_rm_cls)

    run_agent_query(config_name="test", query="hello")

    mock_rm_cls.for_run_no_site.assert_called_once_with(
        module="agent",
        run_name="test",
        base_folder="runs",
    )


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_calls_agent_ask(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
):
    """run_agent_query：agent.ask() 以正確 query 和 thread_id 呼叫。"""
    from website_copilot.pipelines.exp import run_agent_query

    fake_agent = _FakeAgentStub()
    mock_run_agent_build.return_value = fake_agent
    _setup_mock_run_manager(mock_rm_cls)

    run_agent_query(config_name="test", query="你好", thread_id="session-1")

    assert len(fake_agent.asked) == 1
    assert fake_agent.asked[0]["query"] == "你好"
    assert fake_agent.asked[0]["thread_id"] == "session-1"


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_delegates_save_to_run_manager(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
):
    """run_agent_query：落盤委派 run_manager.save_agent_results_as_json()。"""
    from website_copilot.pipelines.exp import run_agent_query

    fake_agent = _FakeAgentStub()
    mock_run_agent_build.return_value = fake_agent
    mock_rm = _setup_mock_run_manager(mock_rm_cls)

    run_agent_query(config_name="test", query="hello", thread_id="session-1")

    mock_rm.save_agent_results_as_json.assert_called_once()
    save_kwargs = mock_rm.save_agent_results_as_json.call_args.kwargs
    assert save_kwargs["thread_id"] == "session-1"
    assert save_kwargs["agent_config"] is fake_agent.config
    assert save_kwargs["results"][0]["response"] == "fake answer"


@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_returns_none(mock_log_session):
    """run_agent_query 回傳 None。"""
    from website_copilot.pipelines.exp import run_agent_query

    with (
        patch("website_copilot.pipelines.exp.run_agent_build") as mock_run_agent_build,
        patch("website_copilot.storage.run_context.RunManager") as mock_rm_cls,
        patch("website_copilot.storage.run_context.save_logging_file"),
    ):
        mock_run_agent_build.return_value = _FakeAgentStub()
        _setup_mock_run_manager(mock_rm_cls)

        assert run_agent_query(config_name="test", query="hello") is None


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_auto_generates_thread_id(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
):
    """thread_id 為 None 時自動產生 auto-{uuid} 並用於落盤。"""
    from website_copilot.pipelines.exp import run_agent_query

    mock_run_agent_build.return_value = _FakeAgentStub()
    mock_rm = _setup_mock_run_manager(mock_rm_cls)

    run_agent_query(config_name="test", query="hello")

    thread_id = mock_rm.save_agent_results_as_json.call_args.kwargs["thread_id"]
    assert thread_id is not None
    assert thread_id.startswith("auto-")


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_closes_agent_on_success(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
):
    """run_agent_query 在成功時以 finally 呼叫 agent.close()。"""
    from website_copilot.pipelines.exp import run_agent_query

    fake_agent = _FakeAgentStub()
    mock_run_agent_build.return_value = fake_agent
    _setup_mock_run_manager(mock_rm_cls)

    run_agent_query(config_name="test", query="hello")

    assert fake_agent.close_called


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_closes_agent_on_error(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
):
    """run_agent_query 在 ask() 拋出例外時仍呼叫 agent.close()，且只呼叫一次。"""
    from website_copilot.pipelines.exp import run_agent_query

    fake_agent = _FailingAgentStub()
    mock_run_agent_build.return_value = fake_agent
    _setup_mock_run_manager(mock_rm_cls)

    with pytest.raises(RuntimeError):
        run_agent_query(config_name="test", query="hello")

    assert fake_agent.close_count == 1


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_closes_agent_on_stream_error(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
):
    """run_agent_query 在 stream 模式例外時仍呼叫 agent.close()，且只呼叫一次。"""
    from website_copilot.pipelines.exp import run_agent_query

    fake_agent = _FailingStreamAgentStub()
    mock_run_agent_build.return_value = fake_agent
    _setup_mock_run_manager(mock_rm_cls)

    with pytest.raises(RuntimeError):
        run_agent_query(config_name="test", query="hello", stream=True)

    assert fake_agent.close_count == 1


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_stream_persists_streamed_result(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
):
    """stream=True 的 happy path：astream_result 的串流結果經 save_agent_results_as_json 落盤。"""
    from website_copilot.pipelines.exp import run_agent_query

    fake_agent = _FakeAgentStub()
    mock_run_agent_build.return_value = fake_agent
    mock_rm = _setup_mock_run_manager(mock_rm_cls)

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


@patch("website_copilot.pipelines.exp.save_run_config_as_toml")
@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_writes_run_config_and_log_lifecycle(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
    mock_save_run_config,
):
    """Goal 4：run_config= 觸發恰好一次 run_config.toml 落盤，log 生命週期為 init → complete。"""
    from website_copilot.pipelines.exp import run_agent_query

    mock_run_agent_build.return_value = _FakeAgentStub()
    mock_rm = _setup_mock_run_manager(mock_rm_cls)
    run_config = MagicMock()

    run_agent_query(config_name="test", query="hello", run_config=run_config)

    mock_save_run_config.assert_called_once_with(
        run_config, mock_rm.run_config_toml_path
    )
    assert [call.args[0] for call in mock_rm.log_run_paths.call_args_list] == [
        "init",
        "complete",
    ]


@patch("website_copilot.pipelines.exp.save_module_config_as_toml")
@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_builds_agent_via_run_agent_build(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
    mock_save_module_config,
):
    """run_agent_query：agent 經 run_agent_build 建構（轉發覆寫值），本身不寫 module_config.toml。"""
    from website_copilot.pipelines import exp

    mock_run_agent_build.return_value = _FakeAgentStub()
    _setup_mock_run_manager(mock_rm_cls)

    exp.run_agent_query(config_name="test", query="hello", llm_name="gpt-x")

    mock_run_agent_build.assert_called_once_with("test", llm_name="gpt-x")
    # module_config.toml 只由 run_agent_build 寫入 agent_build/
    mock_save_module_config.assert_not_called()


# ===========================================================================
# run_server_build：注入 agent、獨立 run context、log 生命週期、失敗不關閉 agent
# ===========================================================================


@patch("website_copilot.pipelines.serve.save_module_config_as_toml")
@patch("website_copilot.pipelines.serve.uvicorn")
@patch("website_copilot.pipelines.serve.ChatApp")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.serve.log_session")
def test_run_server_build_returns_chat_server_holding_chat_app(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_chat_app_cls,
    mock_uvicorn,
    mock_save_module_config,
):
    """run_server_build：以注入的 agent 建立 ChatApp，回傳持有 ChatApp 的 ChatServer。"""
    from website_copilot.pipelines.serve import run_server_build

    fake_agent = _FakeAgentStub()
    mock_rm = _setup_mock_run_manager(mock_rm_cls)

    server = run_server_build(cast(Agent, fake_agent))
    chat_app = server.chat_app

    assert isinstance(server, ChatServer)
    assert server.config is mock_uvicorn.Config.return_value
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
    # 獨立 run context：module="server"，run 名稱取自 agent 的 config_name
    mock_rm_cls.for_run_no_site.assert_called_once_with(
        module="server", run_name="test", base_folder="runs"
    )
    # server 目錄不寫 module_config.toml（agent 設定只寫在 agent_build 目錄）
    mock_save_module_config.assert_not_called()
    # 建構成功：不關閉 agent（由 ChatServer 結束時的 ChatApp.close() 負責）
    assert not fake_agent.close_called


@patch("website_copilot.pipelines.serve.uvicorn")
@patch("website_copilot.pipelines.serve.ChatApp")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.serve.log_session")
def test_run_server_build_logs_init_then_complete_only(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_chat_app_cls,
    mock_uvicorn,
):
    """run_server_build 的 log 生命週期僅 init → complete（不使用未定義的 "ready"）。"""
    from website_copilot.pipelines.serve import run_server_build

    mock_rm = _setup_mock_run_manager(mock_rm_cls)

    run_server_build(cast(Agent, _FakeAgentStub()))

    assert [call.args[0] for call in mock_rm.log_run_paths.call_args_list] == [
        "init",
        "complete",
    ]


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

    fake_agent = _FakeAgentStub()
    _setup_mock_run_manager(mock_rm_cls)
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
    """serve：以 run_config.config_name 建構 agent，再注入 run_server_build 並 run()。"""
    from website_copilot.config.pipeline_config import ServeRunConfig
    from website_copilot.pipelines.serve import serve

    fake_agent = _FakeAgentStub()
    mock_run_agent_build.return_value = fake_agent
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

    fake_agent = _FakeAgentStub()
    mock_run_agent_build.return_value = fake_agent
    mock_run_server_build.side_effect = RuntimeError("server boom")

    with pytest.raises(RuntimeError):
        serve(ServeRunConfig(config_name="test"))

    assert fake_agent.close_called


def test_chat_app_close_closes_agent():
    """ChatApp.close() 觸發 agent.close()（server 路徑的關閉歸屬）。"""
    from website_copilot.server.app import ChatApp

    fake_agent = _FakeAgentStub()
    chat_app = ChatApp.create(
        agent=cast(Agent, fake_agent),
        run_manager=MagicMock(),
    )

    chat_app.close()

    assert fake_agent.close_called


@patch("website_copilot.server.server.log_session")
def test_chat_server_handle_exit_logs_before_delegating(mock_log_session):
    """ChatServer.handle_exit：先印 "Server Stopping"，再交回 uvicorn 原生行為。"""
    import uvicorn

    config = uvicorn.Config(app=MagicMock())
    server = ChatServer(config, chat_app=MagicMock())

    server.handle_exit(sig=2, frame=None)  # signal.SIGINT

    mock_log_session.assert_called_once_with("Server Stopping", style="yellow")
    assert server.should_exit is True


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
