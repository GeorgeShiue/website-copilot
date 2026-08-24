"""Agent 層純函式測試（不觸發真實 LLM / RAG 資源）。

涵蓋：
- thread_config：auto thread_id / 指定 thread_id / None
- extract_sources_from_messages：URL 擷取與去重
- _message_content_to_text：str / list[dict] / 其他型別
- save_conversation_results：落盤 dict 組裝（替身 agent）
"""

from dataclasses import dataclass, field
from typing import Any

from app.agent.agent import (
    _message_content_to_text,
    extract_sources_from_messages,
    save_conversation_results,
    thread_config,
)

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


def _msg(content: Any) -> Any:
    return type("Message", (), {"content": content})()


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


@dataclass
class _FakeConfig:
    config_name: str = "test"
    llm_name: str = "gemini-3.1-flash-lite"
    system_prompt: str = "prompt"


@dataclass
class _FakeRunManager:
    run_name: str = "test"
    run_path: str = ""  # save_conversation_results 分檔路徑需要
    saved: dict[str, Any] = field(default_factory=dict)
    saved_to: list[tuple[dict[str, Any], str]] = field(default_factory=list)

    def save_results_as_json(
        self, results: dict[str, Any], file_path: str | None = None
    ) -> None:
        self.saved = results
        if file_path is not None:
            self.saved_to.append((results, file_path))


@dataclass
class _FakeAgent:
    run_manager: _FakeRunManager = field(default_factory=_FakeRunManager)
    config: _FakeConfig = field(default_factory=_FakeConfig)


def test_save_conversation_results_builds_dict():
    """落盤 dict 含 config 摘要與 results 列表。"""
    agent = _FakeAgent()
    results = [{"query": "Q", "response": "A", "sources": ["u1"], "timestamp": "t"}]
    save_conversation_results(agent, results)  # type: ignore[arg-type]

    saved = agent.run_manager.saved
    assert saved["config"]["config_name"] == "test"
    assert saved["config"]["llm_name"] == "gemini-3.1-flash-lite"
    assert saved["config"]["system_prompt"] == "prompt"
    assert saved["config"]["run_name"] == "test"
    assert saved["results"] == results


def test_save_conversation_results_with_thread_id_splits_file():
    """提供 thread_id 時另寫入 results_<thread_id>.json 分檔。"""
    agent = _FakeAgent()
    results = [{"query": "Q", "response": "A", "sources": [], "timestamp": "t"}]
    save_conversation_results(agent, results, thread_id="demo-1")  # type: ignore[arg-type]

    assert agent.run_manager.saved["results"] == results  # results.json 仍寫
    assert len(agent.run_manager.saved_to) == 1
    file_path = agent.run_manager.saved_to[0][1]
    assert file_path.endswith("results_demo-1.json")


def test_save_conversation_results_sanitizes_thread_id():
    """thread_id 含 / 時置換為 _（檔名安全）。"""
    agent = _FakeAgent()
    save_conversation_results(agent, [], thread_id="a/b")  # type: ignore[arg-type]

    file_path = agent.run_manager.saved_to[0][1]
    assert file_path.endswith("results_a_b.json")
