"""M3 server 測試：SSE 事件流 / error 事件 / health（替身 agent）。

替身 FakeAgent 只實作 graph.astream / graph.get_state / close，
避免測試觸發真實 RAG 資源與 LLM 呼叫。
"""

import json
from dataclasses import dataclass
from typing import Any, cast

from fastapi.testclient import TestClient

from app.agent.agent import RAGAgent
from app.server.app import create_app


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


@dataclass
class _Config:
    """替身 AgentConfig（僅需 save_conversation_results 用到的欄位）。"""

    config_name: str = "test"
    llm_name: str = "gemini-3.1-flash-lite"
    system_prompt: str = "prompt"


class FakeRunManager:
    """替身 RunManager：記錄 save_results_as_json 的呼叫內容。"""

    run_name: str = "test"

    def __init__(self) -> None:
        self.saved: dict[str, Any] | None = None

    def save_results_as_json(self, results: dict[str, Any]) -> None:
        self.saved = results


class FakeGraph:
    """替身 graph：astream 產 2 個 token，get_state 回傳含來源的 messages。"""

    async def astream(
        self,
        inputs: dict[str, Any],
        config: dict[str, Any] | None = None,
        stream_mode: str = "messages",
    ) -> Any:
        for token in ("你", "好"):
            yield _Chunk(content=token), {"langgraph_node": "model"}

    def get_state(self, config: dict[str, Any] | None = None) -> _GraphState:
        tool_message = _Message(content="來源：\nURL: https://example.com/page")
        return _GraphState(values={"messages": [tool_message]})


class FailingGraph(FakeGraph):
    """替身 graph：astream 拋出例外（驗證 error 事件）。"""

    async def astream(
        self,
        inputs: dict[str, Any],
        config: dict[str, Any] | None = None,
        stream_mode: str = "messages",
    ) -> Any:
        raise RuntimeError("boom")
        yield  # unreachable：使函數為 async generator（async for 才可迭代）


class FakeAgent:
    """替身 RAGAgent（僅需 graph / close / run_manager / config）。"""

    def __init__(
        self,
        graph: FakeGraph | None = None,
        run_manager: FakeRunManager | None = None,
    ) -> None:
        self.graph = graph if graph is not None else FakeGraph()
        self.run_manager = run_manager if run_manager is not None else FakeRunManager()
        self.config = _Config()

    def close(self) -> None:
        pass


def _make_client(agent: FakeAgent) -> TestClient:
    """建立注入替身 agent 的 TestClient（with 觸發 lifespan）。"""
    app = create_app(agent=cast(RAGAgent, agent))
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


def test_chat_sse_streams_tokens_and_done():
    fake = FakeAgent()
    with _make_client(fake) as client:
        with client.stream("POST", "/api/chat", json={"query": "你好"}) as response:
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

    # 落盤：save_conversation_results 以單輪結果覆寫（與 CLI 慣例一致），sources 保留
    saved = fake.run_manager.saved
    assert saved is not None
    assert saved["results"][0]["response"] == "你好"
    assert saved["results"][0]["sources"] == ["https://example.com/page"]


def test_chat_thread_id_echo():
    with _make_client(FakeAgent()) as client:
        with client.stream(
            "POST", "/api/chat", json={"query": "你好", "thread_id": "demo"}
        ) as response:
            body = "".join(response.iter_text())

    done = _parse_events(body)[-1]
    assert done["thread_id"] == "demo"


def test_chat_error_event_on_stream_failure():
    with _make_client(FakeAgent(graph=FailingGraph())) as client:
        with client.stream("POST", "/api/chat", json={"query": "你好"}) as response:
            body = "".join(response.iter_text())

    events = _parse_events(body)
    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert events[0]["message"] == "boom"


def test_chat_empty_query_returns_error_event():
    with _make_client(FakeAgent()) as client:
        with client.stream("POST", "/api/chat", json={"query": "   "}) as response:
            body = "".join(response.iter_text())

    events = _parse_events(body)
    assert len(events) == 1
    assert events[0]["type"] == "error"


def test_health():
    with _make_client(FakeAgent()) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_static_files_served():
    """M4a：嵌入表面 static 檔皆可取得。"""
    with _make_client(FakeAgent()) as client:
        for path in ("/static/widget.js", "/static/chat.html", "/static/demo.html"):
            response = client.get(path)
            assert response.status_code == 200, path
            assert len(response.content) > 0


def test_root_redirects_to_demo():
    with _make_client(FakeAgent()) as client:
        response = client.get("/", follow_redirects=False)
    assert response.status_code in (301, 302, 307)
    assert response.headers["location"] == "/static/demo.html"
