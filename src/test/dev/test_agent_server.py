"""Agent + Server 層測試（合併 test_agent.py + test_server.py）。

涵蓋：
- utils.langchain_helper 純函式：thread_config / extract_sources_from_messages / _message_content_to_text
- Agent member function：save_results（透過 _FakeAgent 替身驗證）
- Server 層：SSE 事件流 / error 事件 / health / CORS / static files / resolve_site_id / _enrich_query

替身 FakeAgent 只實作 graph.astream / graph.get_state / close / astream_text / save_results，
避免測試觸發真實 LLM / RAG 資源與 LLM 呼叫。
"""

import json
from dataclasses import dataclass, field
from typing import Any, cast

from fastapi.testclient import TestClient

from app.agent.agent import Agent
from app.server.app import (
    _enrich_query_with_site_context,
    create_app,
    resolve_site_id,
)
from utils.langchain_helper import (
    _message_content_to_text,
    extract_sources_from_messages,
    thread_config,
)

# ---------------------------------------------------------------------------
# 替身基礎設施
# ---------------------------------------------------------------------------


@dataclass
class _FakeConfig:
    """替身 AgentConfig（僅需 save_conversation_results 用到的欄位）。"""

    config_name: str = "test"
    llm_name: str = "gemini-3.1-flash-lite"
    system_prompt: str = "prompt"


@dataclass
class _FakeRunManager:
    """替身 RunManager：記錄 save_results_as_json 的呼叫內容。"""

    run_name: str = "test"
    run_path: str = ""
    base_folder: str = "runs"
    module_name: str = "agent"
    saved: dict[str, Any] = field(default_factory=dict)
    saved_to: list[tuple[dict[str, Any], str]] = field(default_factory=list)

    def save_results_as_json(
        self, results: dict[str, Any], file_path: str | None = None
    ) -> None:
        self.saved = results
        if file_path is not None:
            self.saved_to.append((results, file_path))


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
    ) -> Any:
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
    ) -> Any:
        raise RuntimeError("boom")
        yield  # unreachable：使函數為 async generator


class _FakeAgent:
    """替身 Agent（僅需 graph / close / run_manager / config / astream_text / save_results）。"""

    def __init__(
        self,
        graph: _FakeGraph | None = None,
        run_manager: _FakeRunManager | None = None,
    ) -> None:
        self.graph = graph if graph is not None else _FakeGraph()
        self.run_manager = run_manager if run_manager is not None else _FakeRunManager()
        self.config = _FakeConfig()

    def close(self) -> None:
        pass

    async def astream_text(self, query: str, config: dict[str, Any]) -> Any:
        """替身串流：delegate 至 _FakeGraph.astream。"""
        async for chunk, metadata in self.graph.astream(
            {"messages": [("human", query)]},
            config=config,
            stream_mode="messages",
        ):
            if metadata.get("langgraph_node") == "model":
                text = _message_content_to_text(chunk.content)
                if text:
                    yield text

    def save_results(
        self,
        results: list[dict[str, Any]],
        thread_id: str | None = None,
    ) -> None:
        """替身落盤：直接呼叫 run_manager.save_results_as_json。"""
        if not thread_id:
            return
        safe_id = thread_id.replace("/", "_")
        self.run_manager.save_results_as_json(
            {
                "config": {
                    "config_name": self.config.config_name,
                    "run_name": self.run_manager.run_name,
                    "llm_name": self.config.llm_name,
                    "system_prompt": self.config.system_prompt,
                },
                "results": results,
            },
            file_path=f"results_{safe_id}.json",
        )


def _make_client(agent: _FakeAgent) -> TestClient:
    """建立注入替身 agent 的 TestClient（with 觸發 lifespan）。"""
    app = create_app(agent=cast(Agent, agent))
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

# ---------- thread_config ----------


def test_thread_config_auto_generates_unique_id():
    """thread_id 為 None 時自動產生 auto-{uuid} 且每次不同。"""
    config1 = thread_config(None)
    config2 = thread_config(None)
    assert config1["configurable"]["thread_id"].startswith("auto-")
    assert config1["configurable"]["thread_id"] != config2["configurable"]["thread_id"]


def test_thread_config_uses_given_id():
    """指定 thread_id 時原樣使用。"""
    config = thread_config("demo-session")
    assert config == {"configurable": {"thread_id": "demo-session"}}


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


def test_extract_sources_empty():
    """無任何來源時回傳空列表。"""
    assert extract_sources_from_messages([_msg("沒有 URL 的內容")]) == []
    assert extract_sources_from_messages([]) == []


# ---------- _message_content_to_text ----------


def test_message_content_to_text_str():
    """純字串原樣回傳。"""
    assert _message_content_to_text("你好") == "你好"


def test_message_content_to_text_list_of_dicts():
    """Gemini 常見的 list[dict]（含 text 欄位）串接回傳。"""
    content = [{"type": "text", "text": "第一段"}, {"text": "第二段"}, {"type": "x"}]
    assert _message_content_to_text(content) == "第一段\n第二段"


def test_message_content_to_text_mixed_list():
    """list 內混字串與 dict 皆處理。"""
    assert _message_content_to_text(["a", {"text": "b"}]) == "a\nb"


def test_message_content_to_text_other_types():
    """其他型別（int）轉為字串。"""
    assert _message_content_to_text(123) == "123"
    assert _message_content_to_text(None) == "None"


# ---------- save_conversation_results ----------


def test_save_conversation_results_builds_dict():
    """落盤 dict 含 config 摘要與 results 列表。"""
    agent = _FakeAgent()
    results = [{"query": "Q", "response": "A", "sources": ["u1"], "timestamp": "t"}]
    agent.save_results(results, thread_id="test-thread")

    saved = agent.run_manager.saved
    assert saved["config"]["config_name"] == "test"
    assert saved["config"]["llm_name"] == "gemini-3.1-flash-lite"
    assert saved["config"]["system_prompt"] == "prompt"
    assert saved["config"]["run_name"] == "test"
    assert saved["results"] == results


def test_save_conversation_results_with_thread_id_splits_file():
    """提供 thread_id 時寫入 results_<thread_id>.json 累積多輪歷史。"""
    agent = _FakeAgent()
    results = [{"query": "Q", "response": "A", "sources": [], "timestamp": "t"}]
    agent.save_results(results, thread_id="demo-1")

    assert len(agent.run_manager.saved_to) == 1
    file_path = agent.run_manager.saved_to[0][1]
    assert file_path.endswith("results_demo-1.json")
    assert agent.run_manager.saved["results"] == results


def test_save_conversation_results_sanitizes_thread_id():
    """thread_id 含 / 時置換為 _（檔名安全）。"""
    agent = _FakeAgent()
    results = [{"query": "Q", "response": "A", "sources": [], "timestamp": "t"}]
    agent.save_results(results, thread_id="a/b")

    file_path = agent.run_manager.saved_to[0][1]
    assert file_path.endswith("results_a_b.json")


# ===========================================================================
# Server 層測試
# ===========================================================================

# ---------- SSE 串流 ----------


def test_chat_sse_streams_tokens_and_done():
    fake = _FakeAgent()
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
    # thread_id 分檔：auto-{uuid} 亦寫入 results_<thread_id>.json
    assert len(fake.run_manager.saved_to) == 1
    assert fake.run_manager.saved_to[0][1].endswith(".json")


def test_chat_thread_id_echo():
    with _make_client(_FakeAgent()) as client:
        with client.stream(
            "POST", "/api/chat", json={"query": "你好", "thread_id": "demo"}
        ) as response:
            body = "".join(response.iter_text())

    done = _parse_events(body)[-1]
    assert done["thread_id"] == "demo"


def test_chat_error_event_on_stream_failure():
    with _make_client(_FakeAgent(graph=_FailingGraph())) as client:
        with client.stream("POST", "/api/chat", json={"query": "你好"}) as response:
            body = "".join(response.iter_text())

    events = _parse_events(body)
    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert events[0]["message"] == "boom"


def test_chat_empty_query_returns_error_event():
    with _make_client(_FakeAgent()) as client:
        with client.stream("POST", "/api/chat", json={"query": "   "}) as response:
            body = "".join(response.iter_text())

    events = _parse_events(body)
    assert len(events) == 1
    assert events[0]["type"] == "error"


# ---------- Health ----------


def test_health():
    with _make_client(_FakeAgent()) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------- CORS ----------


def test_cors_headers_present():
    """CORS middleware：跨域請求帶正確 header。"""
    with _make_client(_FakeAgent()) as client:
        response = client.get("/api/health", headers={"Origin": "http://example.com"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "*"


def test_cors_preflight():
    """CORS preflight（OPTIONS）應允許 POST。"""
    with _make_client(_FakeAgent()) as client:
        response = client.options(
            "/api/chat",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "*"
    assert "POST" in response.headers.get("access-control-allow-methods", "")


def _make_client_with_origins(agent: _FakeAgent, origins: list[str]) -> TestClient:
    """建立指定 CORS 來源的 TestClient。"""
    app = create_app(agent=cast(Agent, agent), allowed_origins=origins)
    return TestClient(app)


def test_cors_restricted_origins_allows_listed():
    """限縮來源時：清單內的 origin 帶 access-control-allow-origin header。"""
    with _make_client_with_origins(
        _FakeAgent(), ["https://lab.example.edu.tw"]
    ) as client:
        response = client.get(
            "/api/health", headers={"Origin": "https://lab.example.edu.tw"}
        )
    assert response.status_code == 200
    assert (
        response.headers.get("access-control-allow-origin")
        == "https://lab.example.edu.tw"
    )


def test_cors_restricted_origins_rejects_others():
    """限縮來源時：清單外的 origin 不帶 access-control-allow-origin header。"""
    with _make_client_with_origins(
        _FakeAgent(), ["https://lab.example.edu.tw"]
    ) as client:
        response = client.get(
            "/api/health", headers={"Origin": "https://evil.example.com"}
        )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") is None


# ---------- Static files ----------


def test_static_files_served():
    """M4a：嵌入表面 static 檔皆可取得。"""
    with _make_client(_FakeAgent()) as client:
        for path in ("/static/widget.js", "/static/chat.html", "/static/demo.html"):
            response = client.get(path)
            assert response.status_code == 200, path
            assert len(response.content) > 0


def test_root_redirects_to_demo():
    with _make_client(_FakeAgent()) as client:
        response = client.get("/", follow_redirects=False)
    assert response.status_code in (301, 302, 307)
    assert response.headers["location"] == "/static/demo.html"


# ---------- resolve_site_id / _enrich_query_with_site_context ----------


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


def test_enrich_query_with_site_context():
    assert (
        _enrich_query_with_site_context("hello", "nculab")
        == "[使用者瀏覽 nculab 網站] hello"
    )


def test_enrich_query_with_site_context_none():
    assert _enrich_query_with_site_context("hello", None) == "hello"


def test_chat_page_url_routed_to_enriched_query():
    """page_url 帶入後，_event_stream 使用 enriched_query 呼叫 agent。"""
    graph = _FakeGraph()
    fake = _FakeAgent(graph=graph)
    with _make_client(fake) as client:
        with client.stream(
            "POST",
            "/api/chat",
            json={"query": "成員", "page_url": "nculab.csie.ncu.edu.tw"},
        ) as response:
            body = "".join(response.iter_text())
    events = _parse_events(body)
    assert events[-1]["type"] == "done"
