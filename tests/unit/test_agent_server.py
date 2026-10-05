"""Agent + Server 層測試。

涵蓋：
- agent.langchain_helper 純函式：extract_sources_from_messages / _message_content_to_text（Gemini list 格式）
- Server 層：SSE 事件流 / error 事件 / thread_id / page_url 帶入網站資訊 / resolve_site_id
- 落盤委派：_event_stream 呼叫 run_manager.save_agent_results_as_json(agent_config=agent.config)

替身 FakeAgent 只實作 graph.astream / graph.get_state / astream_text，
避免測試觸發真實 LLM / RAG 資源與 LLM 呼叫。
落盤責任已從 Agent 移至呼叫端：ChatApp 以注入的 RunManager 負責寫檔，
因此替身 RunManager 只記錄呼叫內容，不做任何 I/O。
"""

import asyncio
import json
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, cast
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from website_copilot.agent.agent import Agent, build_result, state_messages
from website_copilot.agent.langchain_helper import (
    extract_sources_from_messages,
    message_content_to_text,
    new_thread_id,
    thread_config,
)
from website_copilot.server.app import (
    ChatApp,
    resolve_site_id,
)
from website_copilot.storage.run_manager import RunManager

# ---------------------------------------------------------------------------
# 替身基礎設施
# ---------------------------------------------------------------------------


@dataclass
class _FakeConfig:
    """替身 AgentConfig（僅需落盤摘要用到的欄位）。"""

    config_name: str = "test"
    llm_name: str = "gemini-3.1-flash-lite"
    system_prompt: str = "prompt"


@dataclass
class _FakeRunManager:
    """替身 RunManager：記錄 save_agent_results_as_json 的呼叫內容。"""

    run_name: str = "test"
    saved_thread_id: str | None = None
    saved_results: list[dict[str, Any]] = field(default_factory=list)
    saved_agent_config: Any = None
    save_call_count: int = 0

    def save_agent_results_as_json(
        self,
        thread_id: str,
        results: list[dict[str, Any]],
        agent_config: Any,
    ) -> str | None:
        self.save_call_count += 1
        self.saved_thread_id = thread_id
        self.saved_results = results
        self.saved_agent_config = agent_config
        return f"results_{thread_id.replace('/', '_')}.json"


@dataclass
class _Chunk:
    """替身 astream chunk（僅需 .content）。"""

    content: str


@dataclass
class _Message:
    """替身 message（僅需 .content，供 extract_sources_from_messages）。"""

    content: str


@dataclass
class _GraphState:
    """替身 graph state（僅需 .values）。"""

    values: dict[str, Any]


class _FakeGraph:
    """替身 graph：astream 產 2 個 token，get_state 回傳含來源的 messages。"""

    async def astream(
        self,
        inputs: dict[str, Any],
        config: dict[str, Any] | None = None,
        stream_mode: str = "messages",
    ) -> AsyncIterator[tuple[_Chunk, dict[str, Any]]]:
        for token in ("你", "好"):
            yield _Chunk(content=token), {"langgraph_node": "model"}

    def get_state(self, config: dict[str, Any] | None = None) -> _GraphState:
        tool_message = _Message(content="來源：\nURL: https://example.com/page")
        return _GraphState(values={"messages": [tool_message]})


class _FailingGraph(_FakeGraph):
    """替身 graph：astream 拋出例外（驗證 error 事件）。"""

    async def astream(
        self,
        inputs: dict[str, Any],
        config: dict[str, Any] | None = None,
        stream_mode: str = "messages",
    ) -> AsyncIterator[tuple[_Chunk, dict[str, Any]]]:
        raise RuntimeError("boom")
        yield  # unreachable：使函數為 async generator


class _FakeAgent:
    """替身 Agent（僅需 graph / config / astream_text）。"""

    def __init__(self, graph: _FakeGraph | None = None) -> None:
        self.graph = graph if graph is not None else _FakeGraph()
        self.config = _FakeConfig()

    async def astream_text(self, query: str, config: dict[str, Any]) -> Any:
        """替身串流：delegate 至 _FakeGraph.astream。"""
        async for chunk, metadata in self.graph.astream(
            {"messages": [("human", query)]},
            config=config,
            stream_mode="messages",
        ):
            if metadata.get("langgraph_node") == "model":
                text = message_content_to_text(chunk.content)
                if text:
                    yield text


def _make_client(
    agent: _FakeAgent,
    run_manager: _FakeRunManager | None = None,
) -> TestClient:
    """建立注入替身 agent / run_manager 的 TestClient（with 觸發 lifespan）。"""
    app = ChatApp.create(
        agent=cast(Agent, agent),
        run_manager=cast(RunManager, run_manager or _FakeRunManager()),
    ).app
    return TestClient(app)


def _parse_events(body: str) -> list[dict[str, Any]]:
    """解析 SSE body（data: JSON 行，空行分隔）為事件 dict 列表。"""
    events: list[dict[str, Any]] = []
    for block in body.split("\n\n"):
        data_lines = [
            line[6:] for line in block.split("\n") if line.startswith("data:")
        ]
        if data_lines:
            events.append(json.loads("".join(data_lines)))
    return events


def _msg(content: Any) -> Any:
    """建立替身 message（僅需 .content）。"""
    return type("Message", (), {"content": content})()


# ===========================================================================
# Agent 純函式測試
# ===========================================================================

# ---------- extract_sources_from_messages ----------


def test_extract_sources_deduplicates_and_preserves_order():
    """依出現順序去重，不重複的 URL 保留原序。"""
    messages = [
        _msg("來源：\nURL: https://example.com/a\nURL: https://example.com/b"),
        _msg("其他內容，無 URL"),
        _msg("再次提到 URL: https://example.com/a\n（應去重）"),
    ]
    assert extract_sources_from_messages(messages) == [
        "https://example.com/a",
        "https://example.com/b",
    ]


def test_extract_sources_skips_non_string_content():
    """content 非字串（如 list[dict]）的 message 應跳過不報錯。"""
    messages = [_msg("URL: https://example.com/a"), _msg(["not", "a", "string"])]
    assert extract_sources_from_messages(messages) == ["https://example.com/a"]


# ---------- _message_content_to_text ----------


def test_new_thread_id_format_and_uniqueness():
    first, second = new_thread_id(), new_thread_id()
    assert first.startswith("auto-") and len(first) == len("auto-") + 8
    assert first != second


def test_thread_config_generates_id_only_when_missing():
    assert thread_config("demo") == {"configurable": {"thread_id": "demo"}}
    auto = thread_config(None)["configurable"]["thread_id"]
    assert auto.startswith("auto-")


# ---------------------------------------------------------------------------
# 問答結果組裝：build_result／state_messages／Agent.ask／Agent.astream_result
# ---------------------------------------------------------------------------

_RESULT_KEYS = ["query", "response", "sources", "timestamp"]


def test_build_result_fields_and_sources():
    messages = [_Message(content="來源：\nURL: https://example.com/a")]

    result = build_result("Q", "A", messages)

    assert list(result) == _RESULT_KEYS
    assert result["query"] == "Q" and result["response"] == "A"
    assert result["sources"] == ["https://example.com/a"]
    assert result["timestamp"]


def test_state_messages_returns_messages_or_empty():
    assert [m.content for m in state_messages(_FakeGraph(), {})] == [
        "來源：\nURL: https://example.com/page"
    ]

    class _EmptyGraph:
        def get_state(self, config):
            return _GraphState(values={})

    assert state_messages(_EmptyGraph(), {}) == []


class _InvokeGraph(_FakeGraph):
    """替身 graph：invoke 回傳 [工具訊息, 最終回答]。"""

    def invoke(self, inputs: dict[str, Any], config: dict[str, Any] | None = None):
        return {
            "messages": [
                _Message(content="來源：\nURL: https://example.com/page"),
                _Message(content="最終回答"),
            ]
        }


def _make_agent(graph: _FakeGraph) -> Agent:
    return Agent(
        graph=graph, tool=MagicMock(), config=MagicMock(), checkpointer=MagicMock()
    )


def test_agent_ask_returns_built_result():
    result = _make_agent(_InvokeGraph()).ask("Q", "t1")

    assert list(result) == _RESULT_KEYS
    assert result["response"] == "最終回答"
    assert result["sources"] == ["https://example.com/page"]


def test_agent_astream_result_collects_tokens_and_sources():
    tokens: list[str] = []

    result = asyncio.run(
        _make_agent(_FakeGraph()).astream_result("Q", "t1", on_token=tokens.append)
    )

    assert tokens == ["你", "好"]
    assert list(result) == _RESULT_KEYS
    assert result["response"] == "你好"
    assert result["sources"] == ["https://example.com/page"]


def test_message_content_to_text_list_of_dicts():
    """Gemini 常見的 list[dict]（含 text 欄位）串接回傳。"""
    content = [{"type": "text", "text": "第一段"}, {"text": "第二段"}, {"type": "x"}]
    assert message_content_to_text(content) == "第一段\n第二段"


def test_message_content_to_text_mixed_list():
    """list 內混字串與 dict 皆處理。"""
    assert message_content_to_text(["a", {"text": "b"}]) == "a\nb"


# ---------- 落盤委派（server → RunManager） ----------


def test_chat_delegates_save_to_run_manager_with_agent_config():
    """_event_stream 以 agent.config 呼叫 run_manager.save_agent_results_as_json。"""
    fake = _FakeAgent()
    run_manager = _FakeRunManager()

    with (
        _make_client(fake, run_manager) as client,
        client.stream("POST", "/api/chat", json={"query": "Q"}) as response,
    ):
        _ = "".join(response.iter_text())

    assert run_manager.save_call_count == 1
    assert run_manager.saved_agent_config is fake.config
    assert run_manager.saved_results[0]["query"] == "Q"
    assert run_manager.saved_results[0]["response"] == "你好"
    assert run_manager.saved_results[0]["sources"] == ["https://example.com/page"]


def test_chat_passes_given_thread_id_to_run_manager():
    """提供 thread_id 時原樣傳給 run_manager（分檔由 RunManager 負責）。"""
    run_manager = _FakeRunManager()

    with (
        _make_client(_FakeAgent(), run_manager) as client,
        client.stream(
            "POST", "/api/chat", json={"query": "Q", "thread_id": "demo-1"}
        ) as response,
    ):
        _ = "".join(response.iter_text())

    assert run_manager.saved_thread_id == "demo-1"


# ===========================================================================
# Server 層測試
# ===========================================================================

# ---------- SSE 串流 ----------


def test_chat_sse_streams_tokens_and_done():
    fake = _FakeAgent()
    run_manager = _FakeRunManager()
    with (
        _make_client(fake, run_manager) as client,
        client.stream("POST", "/api/chat", json={"query": "你好"}) as response,
    ):
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        body = "".join(response.iter_text())

    events = _parse_events(body)
    assert [event["type"] for event in events] == ["token", "token", "done"]

    done = events[-1]
    assert done["response"] == "你好"
    assert done["thread_id"].startswith("auto-")
    # 引用已由 agent 寫入 response；done 事件不再回傳 sources
    assert "sources" not in done

    # 落盤：以單輪結果寫入（與 CLI 慣例一致），sources 保留
    assert run_manager.save_call_count == 1
    assert run_manager.saved_results[0]["response"] == "你好"
    assert run_manager.saved_results[0]["sources"] == ["https://example.com/page"]
    # thread_id 分檔：auto-{uuid} 亦傳入 run_manager
    assert run_manager.saved_thread_id == done["thread_id"]
    assert run_manager.saved_thread_id is not None
    assert run_manager.saved_thread_id.startswith("auto-")


def test_chat_thread_id_echo():
    with (
        _make_client(_FakeAgent()) as client,
        client.stream(
            "POST", "/api/chat", json={"query": "你好", "thread_id": "demo"}
        ) as response,
    ):
        body = "".join(response.iter_text())

    done = _parse_events(body)[-1]
    assert done["thread_id"] == "demo"


def test_chat_error_event_on_stream_failure():
    with (
        _make_client(_FakeAgent(graph=_FailingGraph())) as client,
        client.stream("POST", "/api/chat", json={"query": "你好"}) as response,
    ):
        body = "".join(response.iter_text())

    events = _parse_events(body)
    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert events[0]["message"] == "boom"


def test_chat_empty_query_returns_error_event():
    with (
        _make_client(_FakeAgent()) as client,
        client.stream("POST", "/api/chat", json={"query": "   "}) as response,
    ):
        body = "".join(response.iter_text())

    events = _parse_events(body)
    assert len(events) == 1
    assert events[0]["type"] == "error"


# ---------- resolve_site_id ----------


def test_resolve_site_id_exact_match():
    assert resolve_site_id("nculab.csie.ncu.edu.tw") == "nculab"
    assert resolve_site_id("csie.ncu.edu.tw") == "ncucsie"


def test_resolve_site_id_suffix_match():
    assert resolve_site_id("lab.nculab.csie.ncu.edu.tw") == "nculab"
    assert resolve_site_id("www.csie.ncu.edu.tw") == "ncucsie"


def test_resolve_site_id_none_and_empty():
    assert resolve_site_id(None) is None
    assert resolve_site_id("") is None
    assert resolve_site_id("  ") is None


def test_resolve_site_id_unknown():
    assert resolve_site_id("localhost") is None
    assert resolve_site_id("example.com") is None


def test_chat_page_url_routed_to_enriched_query():
    """page_url 帶入後，_event_stream 使用 enriched_query 呼叫 agent。"""
    graph = _FakeGraph()
    fake = _FakeAgent(graph=graph)
    with (
        _make_client(fake) as client,
        client.stream(
            "POST",
            "/api/chat",
            json={"query": "成員", "page_url": "nculab.csie.ncu.edu.tw"},
        ) as response,
    ):
        body = "".join(response.iter_text())
    events = _parse_events(body)
    assert events[-1]["type"] == "done"
