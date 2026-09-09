"""Resource lifecycle 整合測試：create_tool → create_agent → run_agent 管線。

涵蓋：
- 資源在管線中正確流動
- registry.close() 在成功時被呼叫
- registry.close() 在失敗時仍被呼叫（context manager __exit__）

所有外部依賴以 mock 替代，不觸發真實 LLM / RAG / Milvus 資源。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from unittest.mock import MagicMock, patch


from test.dev._helpers import (
    mock_exit_delegates_to_real as _mock_exit_delegates_to_real,
)


@dataclass
class _FakeAgentStub:
    """最小化 Agent 替身：記錄呼叫以便斷言。"""

    created_with: dict[str, Any] = field(default_factory=dict)

    def ask(self, query: str, thread_id: str | None = None) -> dict[str, Any]:
        return {
            "query": query,
            "response": "lifecycle answer",
            "sources": [],
            "timestamp": "2026-01-01 00:00:00",
        }

    def save_results(
        self,
        results: list[dict[str, Any]],
        thread_id: str | None = None,
    ) -> None:
        pass


@dataclass
class _FailingAgentStub(_FakeAgentStub):
    """Agent 替身：ask() 拋出例外（驗證 context manager __exit__）。"""

    def ask(self, query: str, thread_id: str | None = None) -> dict[str, Any]:
        raise RuntimeError("lifecycle boom")


# ===========================================================================
# Integration: create_tool → create_agent → run_agent
# ===========================================================================


@patch("app.workflow.workflow.RAGRegistry")
@patch("app.workflow.workflow.create_tool")
@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow.RunManager")
@patch("app.workflow.workflow.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_lifecycle_resources_flow_correctly(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
    mock_create_tool,
    mock_registry_cls,
):
    """tools 從 create_tool 流入 create_agent，registry 由 run_agent 管理。"""
    from app.workflow.workflow import run_agent

    fake_agent = _FakeAgentStub()
    mock_create_agent.return_value = fake_agent

    mock_rm = MagicMock()
    mock_rm.log_path = "fake.log"
    mock_rm.results_json_path = "fake.json"
    mock_rm.run_config_toml_path = "fake_run_config.toml"
    mock_rm.module_config_toml_path = "fake_module_config.toml"
    mock_rm_cls.for_run_no_site.return_value = mock_rm
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

    # Simulate tools from create_tool
    mock_tools = [MagicMock(name="tool1"), MagicMock(name="tool2")]
    mock_create_tool.return_value = mock_tools

    _mock_exit_delegates_to_real(
        mock_registry_cls.return_value.__exit__, mock_registry_cls.return_value
    )
    run_agent(
        query="hello",
        config_name="test",
    )

    # create_agent was called with tools
    call_kwargs = mock_create_agent.call_args
    assert call_kwargs.kwargs["tools"] is mock_tools
    assert call_kwargs.kwargs["config"] is mock_config_cls.from_toml.return_value
    assert call_kwargs.kwargs["run_manager"] is mock_rm

    # registry.close() is called via context manager __exit__
    mock_registry_cls.return_value.close.assert_called_once()


@patch("app.workflow.workflow.RAGRegistry")
@patch("app.workflow.workflow.create_tool")
@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow.RunManager")
@patch("app.workflow.workflow.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_lifecycle_close_on_success(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
    mock_create_tool,
    mock_registry_cls,
):
    """成功路徑：registry.close() 被呼叫。"""
    from app.workflow.workflow import run_agent

    fake_agent = _FakeAgentStub()
    mock_create_agent.return_value = fake_agent

    mock_rm = MagicMock()
    mock_rm.log_path = "fake.log"
    mock_rm.results_json_path = "fake.json"
    mock_rm.run_config_toml_path = "fake_run_config.toml"
    mock_rm.module_config_toml_path = "fake_module_config.toml"
    mock_rm_cls.for_run_no_site.return_value = mock_rm
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

    mock_create_tool.return_value = [MagicMock()]

    _mock_exit_delegates_to_real(
        mock_registry_cls.return_value.__exit__, mock_registry_cls.return_value
    )
    run_agent(
        query="hello",
        config_name="test",
    )

    mock_registry_cls.return_value.close.assert_called_once()


@patch("app.workflow.workflow.RAGRegistry")
@patch("app.workflow.workflow.create_tool")
@patch("app.workflow.workflow.create_agent")
@patch("app.workflow.workflow.AgentConfig")
@patch("app.workflow.workflow.RunManager")
@patch("app.workflow.workflow.save_logging_file")
@patch("app.workflow.workflow.log_session")
def test_lifecycle_close_on_error(
    mock_log_session,
    mock_save_logging,
    mock_rm_cls,
    mock_config_cls,
    mock_create_agent,
    mock_create_tool,
    mock_registry_cls,
):
    """錯誤路徑：agent.ask() 拋出例外時 registry.close() 仍被呼叫。"""
    from app.workflow.workflow import run_agent

    fake_agent = _FailingAgentStub()
    mock_create_agent.return_value = fake_agent

    mock_rm = MagicMock()
    mock_rm.log_path = "fake.log"
    mock_rm_cls.for_run_no_site.return_value = mock_rm
    mock_config_cls.from_toml.return_value = MagicMock(llm_name="test_llm")

    mock_create_tool.return_value = [MagicMock()]

    _mock_exit_delegates_to_real(
        mock_registry_cls.return_value.__exit__, mock_registry_cls.return_value
    )
    try:
        run_agent(
            query="hello",
            config_name="test",
        )
    except RuntimeError:
        pass

    mock_registry_cls.return_value.close.assert_called_once()
