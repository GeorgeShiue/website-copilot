"""pipelines/exp.py 的 run_rag_query 測試：只查詢既有向量庫，不建庫、不寫入 data/。

向量庫位置、評估與 LLM 皆以 mock 替代，不觸發真實 embedding／LLM。
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from agent_stubs import setup_mock_run_manager

from website_copilot.config.pipeline_config import RAGQueryRunConfig
from website_copilot.retrieval.factory import published_target

MODULE = "website_copilot.pipelines.exp"


def _tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        h.update(str(path.relative_to(root)).encode())
        if path.is_file():
            h.update(path.read_bytes())
    return h.hexdigest()


@pytest.fixture
def mocks(monkeypatch: pytest.MonkeyPatch):
    """攔截 load_rag／評估／落盤，回傳各 mock。"""
    rag = MagicMock()
    rag.query.return_value = MagicMock()
    m = {
        "load_rag": MagicMock(return_value=rag),
        "rag": rag,
        "vs_run_target": MagicMock(),
        "evaluate": MagicMock(
            return_value=(MagicMock(passing=True), MagicMock(passing=True))
        ),
    }
    monkeypatch.setattr(f"{MODULE}.load_rag", m["load_rag"])
    monkeypatch.setattr(f"{MODULE}.vector_store_run_target", m["vs_run_target"])
    monkeypatch.setattr(f"{MODULE}.build_evaluators", MagicMock())
    monkeypatch.setattr(f"{MODULE}.evaluate_response", m["evaluate"])
    monkeypatch.setattr(f"{MODULE}.response_to_dict", MagicMock(return_value={}))
    monkeypatch.setattr(f"{MODULE}.save_run_configs", MagicMock())
    monkeypatch.setattr(f"{MODULE}.save_query_results_as_md", MagicMock())
    return m


def _run(run_config: RAGQueryRunConfig) -> None:
    from website_copilot.pipelines.exp import run_rag_query

    with (
        patch("website_copilot.storage.run_context.RunManager") as rm_cls,
        patch("website_copilot.storage.run_context.save_logging_file"),
    ):
        setup_mock_run_manager(rm_cls)
        run_rag_query(run_config)


def test_queries_published_vector_store_without_rebuild(mocks) -> None:
    _run(RAGQueryRunConfig(site="nculab", config_name="test"))

    (config, target), kwargs = mocks["load_rag"].call_args
    assert target == published_target("nculab")
    assert kwargs == {"build_query_engine": True}
    mocks["vs_run_target"].assert_not_called()


def test_vector_store_run_overrides_target(mocks, tmp_path: Path) -> None:
    run = str(tmp_path / "run")
    _run(RAGQueryRunConfig(site="nculab", config_name="test", vector_store_run=run))

    mocks["vs_run_target"].assert_called_once_with("nculab", run)
    assert mocks["load_rag"].call_args.args[1] is mocks["vs_run_target"].return_value


def test_vector_store_run_error_propagates(mocks) -> None:
    mocks["vs_run_target"].side_effect = ValueError("站點不一致")
    with pytest.raises(ValueError, match="站點不一致"):
        _run(RAGQueryRunConfig(site="nculab", config_name="test", vector_store_run="x"))
    mocks["load_rag"].assert_not_called()


def test_does_not_build_or_publish(mocks) -> None:
    """rag-query 不經 build_rag／publish：模組中不再有建庫入口。"""
    import website_copilot.pipelines.exp as exp

    assert not hasattr(exp, "build_rag")
    _run(RAGQueryRunConfig(site="nculab", config_name="test"))
    mocks["rag"].close.assert_called_once()


def test_data_folder_untouched(mocks, tmp_path: Path, monkeypatch) -> None:
    """以 tmp 的 data/ 作為已發布位置：查詢前後整個目錄樹不變。"""
    data = tmp_path / "data"
    store = data / "vector_db" / "nculab.db"
    store.mkdir(parents=True)
    (store / "x.parquet").write_bytes(b"abc")
    monkeypatch.setattr(
        f"{MODULE}.published_target",
        lambda site_id: published_target(site_id, str(data)),
    )
    before = _tree_hash(data)

    _run(RAGQueryRunConfig(site="nculab", config_name="test"))

    assert mocks["load_rag"].call_args.args[1].milvus_uri == str(store)
    assert _tree_hash(data) == before
