"""serve 載入路徑的特性測試（characterization test）。

鎖定 RAGRegistry.get(site_id) 從 config 解析到載入 retriever 的實際行為：
- 走「載入既有向量庫」路徑：不清除、不建 nodes、不建 index，並重新 load collection。
- 只建到 retriever 層級，不建 query engine。
- 向量庫不存在時，拋出指示先執行 prepare 的 FileNotFoundError。
- 不需要 data/aug_webpages/（serve 只讀向量庫），也不需要 configs/（RAG 參數使用 class 預設值）。
- repo 中已 publish 的 data/vector_db/{site_id}.db 皆能以 site_id 載入。

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
from website_copilot.retrieval.factory import load_rag, published_target
from website_copilot.retrieval.registry import RAGRegistry

REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_ID = "demo"
INDEX = "website_copilot.ingestion.indexing.index"
FACTORY = "website_copilot.retrieval.factory"


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """在 tmp 目錄建立已 publish 的 data/（沒有 configs/），並切換工作目錄。"""
    (tmp_path / "data" / "vector_db" / f"{SITE_ID}.db").mkdir(parents=True)

    aug_webpages_dir = tmp_path / "data" / "aug_webpages" / SITE_ID
    aug_webpages_dir.mkdir(parents=True)
    (aug_webpages_dir / "results.json").write_text(json.dumps({}), encoding="utf-8")

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
        assert store_kwargs["collection_name"] == "chunks"
        assert store_kwargs["milvus_uri"] == f"data/vector_db/{SITE_ID}.db"
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
    (workspace / "data" / "vector_db" / f"{SITE_ID}.db").rmdir()
    with pytest.raises(FileNotFoundError) as exc_info:
        load_rag(RAGConfig(), published_target(SITE_ID))

    assert str(exc_info.value) == (
        f"Vector store not found: data/vector_db/{SITE_ID}.db"
        "（請先執行 prepare 階段建置並 publish 向量庫）"
    )
    fake_backends["build_store"].assert_not_called()


def test_registry_get_works_without_webpages(
    workspace: Path, fake_backends: dict[str, MagicMock]
) -> None:
    shutil.rmtree(workspace / "data" / "aug_webpages")

    with RAGRegistry(config_name="default", base_folder="data") as registry:
        rag = registry.get(SITE_ID)

        assert rag.retriever is fake_backends["retriever_cls"].return_value
        assert rag.milvus_uri == f"data/vector_db/{SITE_ID}.db"


PUBLISHED_SITES = sorted(
    path.name.removesuffix(".db")
    for path in (REPO_ROOT / "data" / "vector_db").glob("*.db")
    if path.is_dir()
)


@pytest.mark.parametrize("site_id", PUBLISHED_SITES)
def test_registry_loads_published_sites_in_repo(
    site_id: str, fake_backends: dict[str, MagicMock]
) -> None:
    """repo 中已 publish 的向量庫 collection 名稱固定為 chunks，且位於 data/vector_db/{site_id}.db。"""
    data_folder = str(REPO_ROOT / "data")
    with RAGRegistry(config_name="default", base_folder=data_folder) as registry:
        assert site_id in registry.list_sites()
        rag = registry.get(site_id)

        store_kwargs = fake_backends["build_store"].call_args.kwargs
        assert store_kwargs["collection_name"] == "chunks"
        assert rag.milvus_uri == f"{data_folder}/vector_db/{site_id}.db"


def test_published_sites_found() -> None:
    assert PUBLISHED_SITES == ["ncucsie", "nculab"]
