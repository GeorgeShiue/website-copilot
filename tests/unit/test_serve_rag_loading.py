"""serve 載入路徑的特性測試（characterization test）。

鎖定 RAGRegistry.get(site_id) 從 config 解析到載入 retriever 的實際行為：
- 走「載入既有向量庫」路徑：不清除、不建 nodes、不建 index，並重新 load collection。
- 只建到 retriever 層級，不建 query engine。
- 向量庫不存在時，拋出指示先執行 prepare 的 FileNotFoundError。
- 不需要 data/webpages/（serve 只讀向量庫）。

只 patch 掉 Milvus / embedding / retriever 等外部資源，其餘（RAGConfig、RAGRegistry、
IndexBuilder／RAGBuilder 的流程）皆為真實程式碼。
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from website_copilot.config.rag_config import RAGConfig
from website_copilot.retrieval.factory import load_rag
from website_copilot.retrieval.registry import RAGRegistry

REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_ID = "demo"
INDEX = "website_copilot.ingestion.indexing.index"
FACTORY = "website_copilot.retrieval.factory"


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """在 tmp 目錄建立 configs/ 與已 publish 的 data/，並切換工作目錄。"""
    config_dir = tmp_path / "configs" / "rag"
    config_dir.mkdir(parents=True)
    shutil.copy(REPO_ROOT / "configs" / "rag" / "default.yml", config_dir)

    rag_dir = tmp_path / "data" / "rag" / SITE_ID
    rag_dir.mkdir(parents=True)
    (rag_dir / "milvus.db").touch()

    webpages_dir = tmp_path / "data" / "webpages" / SITE_ID
    webpages_dir.mkdir(parents=True)
    (webpages_dir / "results.json").write_text(json.dumps({}), encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def fake_backends() -> Iterator[dict[str, MagicMock]]:
    """patch 掉 Milvus、embedding、index 與 retriever，並記錄建置步驟是否被呼叫。"""
    with (
        patch(f"{INDEX}.VectorStoreBuilder.build") as build_store,
        patch(f"{INDEX}.IndexBuilder.clean") as clean_store,
        patch(f"{INDEX}.NodePipelineBuilder.build") as build_nodes,
        patch(f"{INDEX}.IndexBuilder._create_embed_model") as embed_model,
        patch(f"{INDEX}.VectorStoreIndex") as index_cls,
        patch(f"{FACTORY}.VectorIndexRetriever") as retriever_cls,
    ):
        yield {
            "build_store": build_store,
            "clean_store": clean_store,
            "build_nodes": build_nodes,
            "embed_model": embed_model,
            "index_cls": index_cls,
            "retriever_cls": retriever_cls,
        }


def test_registry_get_loads_published_store_to_retriever(
    workspace: Path, fake_backends: dict[str, MagicMock]
) -> None:
    with RAGRegistry(config_name="default", base_folder="data") as registry:
        rag = registry.get(SITE_ID)

        store = fake_backends["build_store"].return_value
        fake_backends["build_store"].assert_called_once()
        store_kwargs = fake_backends["build_store"].call_args.kwargs
        assert store_kwargs["collection_name"] == SITE_ID
        assert store_kwargs["milvus_uri"] == f"data/rag/{SITE_ID}/milvus.db"
        store.client.load_collection.assert_called_once_with(store.collection_name)

        fake_backends["clean_store"].assert_not_called()
        fake_backends["build_nodes"].assert_not_called()
        fake_backends["index_cls"].assert_not_called()
        fake_backends["index_cls"].from_vector_store.assert_called_once()

        assert rag.retriever is fake_backends["retriever_cls"].return_value
        assert rag.query_engine is None
        assert registry.get(SITE_ID) is rag


def test_load_raises_when_vector_store_missing(
    workspace: Path, fake_backends: dict[str, MagicMock]
) -> None:
    (workspace / "data" / "rag" / SITE_ID / "milvus.db").unlink()
    config = RAGConfig.from_yaml("default", {"site_id": SITE_ID})

    with pytest.raises(FileNotFoundError) as exc_info:
        load_rag(config)

    assert str(exc_info.value) == (
        f"Vector store not found: data/rag/{SITE_ID}/milvus.db"
        "（請先執行 prepare 階段建置並 publish 向量庫）"
    )
    fake_backends["build_store"].assert_not_called()


def test_registry_get_works_without_webpages(
    workspace: Path, fake_backends: dict[str, MagicMock]
) -> None:
    shutil.rmtree(workspace / "data" / "webpages")

    with RAGRegistry(config_name="default", base_folder="data") as registry:
        rag = registry.get(SITE_ID)

        assert rag.retriever is fake_backends["retriever_cls"].return_value
        assert rag.milvus_uri == f"data/rag/{SITE_ID}/milvus.db"
