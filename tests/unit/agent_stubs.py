"""pipelines 測試共用的 Agent 替身與 mock RunManager 設定。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from unittest.mock import MagicMock


@dataclass
class FakeAgentStub:
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
class FailingAgentStub(FakeAgentStub):
    """Agent 替身：ask() 拋出例外（驗證 run_agent_query 的錯誤路徑）。"""

    def ask(self, query: str, thread_id: str | None = None) -> dict[str, Any]:
        raise RuntimeError("boom")


@dataclass
class FailingStreamAgentStub(FakeAgentStub):
    """Agent 替身：astream_result() 拋出例外（驗證 stream 模式的錯誤路徑）。"""

    async def astream_result(
        self,
        query: str,
        thread_id: str | None = None,
        on_token: Any = None,
    ) -> dict[str, Any]:
        raise RuntimeError("stream boom")


def setup_mock_run_manager(mock_rm_cls: MagicMock) -> MagicMock:
    """設定 mock RunManager 的常用欄位，並回傳該 mock 實例。"""
    mock_rm = MagicMock()
    mock_rm.log_path = "fake.log"
    mock_rm.run_config_toml_path = "fake_run_config.toml"
    mock_rm.module_config_toml_path = "fake_module_config.toml"
    mock_rm.run_name = "test"
    mock_rm_cls.for_run_no_site.return_value = mock_rm
    return mock_rm
