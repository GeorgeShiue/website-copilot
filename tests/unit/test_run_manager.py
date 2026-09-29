"""RunManager.save_agent_results_as_json 單元測試（依 thread_id 分檔的對話歷史）。

涵蓋：首寫、合併 append、跨 run 取最新、thread_id 含 '/' 淨化、JSON 損壞或結構非預期時 fallback。

全部以 tmp_path 為 base_folder。
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import pytest

from website_copilot.config.agent_config import AgentConfig
from website_copilot.storage.run_manager import RunManager


@dataclass
class _FakeAgentConfig:
    """替身 AgentConfig：save_agent_results_as_json 僅需組 config 摘要的欄位。"""

    config_name: str = "test-config"
    llm_name: str = "test-llm"
    system_prompt: str = "test-prompt"


# 替身僅具備落盤所需欄位，故需 cast 才符合 save_agent_results_as_json 的型別簽章
FAKE_AGENT_CONFIG: AgentConfig = cast(AgentConfig, _FakeAgentConfig())

# run_name 來自 RunManager.run_name（_make_agent_run_manager 固定為 "test-run"）
EXPECTED_CONFIG: dict[str, Any] = {
    "config_name": "test-config",
    "run_name": "test-run",
    "llm_name": "test-llm",
    "system_prompt": "test-prompt",
}


def _make_agent_run_manager(base_folder: Path) -> RunManager:
    """建立指向 tmp_path 的 RunManager（agent 模組、無 site）。"""
    return RunManager.for_run_no_site(
        module="agent",
        run_name="test-run",
        base_folder=str(base_folder),
    )


def _result(marker: str) -> dict[str, Any]:
    """建立一筆最小對話結果。"""
    return {"query": marker, "response": marker, "sources": [], "timestamp": "t-0"}


def _load(path: str | Path) -> Any:
    """讀回落盤 JSON。"""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_agent_results_first_write_creates_file(tmp_path: Path) -> None:
    """無舊檔：首寫建立 results_{thread_id}.json，含 config 與單筆結果。"""
    run_manager = _make_agent_run_manager(tmp_path)

    run_manager.save_agent_results_as_json(
        thread_id="thread-1",
        results=[_result("a")],
        agent_config=FAKE_AGENT_CONFIG,
    )

    expected_path = Path(run_manager.run_path) / "results_thread-1.json"
    assert expected_path.is_file()
    payload = _load(expected_path)
    assert payload["config"] == EXPECTED_CONFIG
    assert [r["query"] for r in payload["results"]] == ["a"]


def test_agent_results_merge_appends_to_existing_history(tmp_path: Path) -> None:
    """舊檔存在：新結果 append 於既有歷史之後（順序保留）。"""
    run_manager = _make_agent_run_manager(tmp_path)
    history = Path(run_manager.run_path) / "results_t1.json"
    history.write_text(
        json.dumps({"config": {}, "results": [_result("old")]}, ensure_ascii=False),
        encoding="utf-8",
    )

    run_manager.save_agent_results_as_json(
        thread_id="t1",
        results=[_result("new")],
        agent_config=FAKE_AGENT_CONFIG,
    )

    payload = _load(history)
    assert [r["query"] for r in payload["results"]] == ["old", "new"]
    assert payload["config"] == EXPECTED_CONFIG


def test_agent_results_cross_run_finds_latest_history(tmp_path: Path) -> None:
    """本 run 無檔：跨 run 搜尋取時間戳最新（lexicographically last）的歷史。"""
    older_dir = tmp_path / "20260801_120000" / "agent" / "test-run"
    newer_dir = tmp_path / "20260901_120000" / "agent" / "test-run"
    for folder in (older_dir, newer_dir):
        folder.mkdir(parents=True)
    (older_dir / "results_cross.json").write_text(
        json.dumps({"config": {}, "results": [_result("older")]}), encoding="utf-8"
    )
    (newer_dir / "results_cross.json").write_text(
        json.dumps({"config": {}, "results": [_result("newer")]}), encoding="utf-8"
    )
    run_manager = _make_agent_run_manager(tmp_path)

    run_manager.save_agent_results_as_json(
        thread_id="cross",
        results=[_result("current")],
        agent_config=FAKE_AGENT_CONFIG,
    )

    expected_path = newer_dir / "results_cross.json"
    assert [r["query"] for r in _load(expected_path)["results"]] == ["newer", "current"]


def test_agent_results_thread_id_slash_is_sanitized(tmp_path: Path) -> None:
    """thread_id 含 '/'：檔名淨化為 '_'，不產生巢狀路徑。"""
    run_manager = _make_agent_run_manager(tmp_path)

    run_manager.save_agent_results_as_json(
        thread_id="a/b",
        results=[_result("x")],
        agent_config=FAKE_AGENT_CONFIG,
    )

    expected_path = Path(run_manager.run_path) / "results_a_b.json"
    assert expected_path.is_file()


def test_agent_results_corrupt_json_falls_back_to_new_results(tmp_path: Path) -> None:
    """JSON 損壞：不中斷落盤，以空歷史重寫僅含本輪結果。"""
    run_manager = _make_agent_run_manager(tmp_path)
    history = Path(run_manager.run_path) / "results_bad.json"
    history.write_text("{not valid json", encoding="utf-8")

    run_manager.save_agent_results_as_json(
        thread_id="bad",
        results=[_result("fresh")],
        agent_config=FAKE_AGENT_CONFIG,
    )

    payload = _load(history)
    assert [r["query"] for r in payload["results"]] == ["fresh"]


@pytest.mark.parametrize(
    "raw_json",
    [
        '["legacy"]',  # 合法 JSON，頂層非 dict
        '{"results": "oops"}',  # dict，但 results 非 list
    ],
)
def test_agent_results_wrong_shape_falls_back(tmp_path: Path, raw_json: str) -> None:
    """合法 JSON 但結構非預期：視為無歷史，不因 AttributeError 中斷。"""
    run_manager = _make_agent_run_manager(tmp_path)
    history = Path(run_manager.run_path) / "results_shape.json"
    history.write_text(raw_json, encoding="utf-8")

    run_manager.save_agent_results_as_json(
        thread_id="shape",
        results=[_result("ok")],
        agent_config=FAKE_AGENT_CONFIG,
    )

    payload = _load(history)
    assert [r["query"] for r in payload["results"]] == ["ok"]
    assert payload["config"] == EXPECTED_CONFIG
