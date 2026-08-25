"""Milvus vector store 重用機制 — _should_rebuild 單元測試。

驗證 _should_rebuild() 對 Milvus 與 Qdrant 的統一路徑判斷邏輯：
- force_rebuild=True → 一律重建
- store 路徑不存在 → 重建
- store 路徑已存在 → 不重建（載入既有）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from unittest.mock import patch

import pytest

from app.engines.rag.rag_factory import RAGBuilder


@dataclass
class _FakeRAGConfig:
    """最小化的 RAGConfig 替身，僅含 _should_rebuild 所需欄位。"""

    vector_store_type: str = "milvus"
    milvus_uri: str | None = "data/rag/test/milvus.db"
    qdrant_db_folder_path: str | None = "data/rag/test/qdrant_db"
    site_id: str = "test"
    embedding_name: str = "text-embedding-3-small"
    hybrid_ranker: str = "WeightedRanker"
    hybrid_ranker_params: dict[str, Any] = field(
        default_factory=lambda: {"weights": [1.0, 0.5]}
    )
    webpages_data_folder_path: str | None = None
    chunk_size: int = 800
    chunk_overlap: int = 100
    paragraph_separator: str = "\n\n"
    query_mode: str = "hybrid"
    similarity_top_k: int = 10
    hybrid_top_k: int = 10
    alpha: float = 0.5
    query_llm_name: str = "gemini-3.1-flash-lite"
    evaluator_llm_name: str = "gpt-5.4"
    cutoff: float = 0.0
    query: str = "test"


def _make_builder(vector_store_type: str, **overrides: Any) -> RAGBuilder:
    """建立帶有指定 vector_store_type 的 RAGBuilder（使用 fake config）。"""
    config = _FakeRAGConfig(vector_store_type=vector_store_type, **overrides)
    return RAGBuilder(config)


class TestShouldRebuildMilvus:
    """Milvus 的 _should_rebuild 邏輯測試。"""

    def test_returns_false_when_milvus_db_exists(self) -> None:
        """milvus.db 已存在 + force_rebuild=False → 不重建。"""
        builder = _make_builder("milvus")
        with patch("os.path.exists", return_value=True):
            assert builder._should_rebuild(force_rebuild=False) is False

    def test_returns_true_when_milvus_db_missing(self) -> None:
        """milvus.db 不存在 → 重建。"""
        builder = _make_builder("milvus")
        with patch("os.path.exists", return_value=False):
            assert builder._should_rebuild(force_rebuild=False) is True

    def test_returns_true_when_force_rebuild(self) -> None:
        """milvus.db 已存在 + force_rebuild=True → 強制重建。"""
        builder = _make_builder("milvus")
        with patch("os.path.exists", return_value=True):
            assert builder._should_rebuild(force_rebuild=True) is True

    def test_returns_true_when_force_rebuild_and_db_missing(self) -> None:
        """milvus.db 不存在 + force_rebuild=True → 重建。"""
        builder = _make_builder("milvus")
        with patch("os.path.exists", return_value=False):
            assert builder._should_rebuild(force_rebuild=True) is True


class TestShouldRebuildQdrant:
    """Qdrant 的 _should_rebuild 邏輯測試（確認不受影響）。"""

    def test_returns_false_when_qdrant_db_exists(self) -> None:
        """qdrant_db 已存在 + force_rebuild=False → 不重建。"""
        builder = _make_builder("qdrant")
        with patch("os.path.exists", return_value=True):
            assert builder._should_rebuild(force_rebuild=False) is False

    def test_returns_true_when_qdrant_db_missing(self) -> None:
        """qdrant_db 不存在 → 重建。"""
        builder = _make_builder("qdrant")
        with patch("os.path.exists", return_value=False):
            assert builder._should_rebuild(force_rebuild=False) is True

    def test_returns_true_when_force_rebuild(self) -> None:
        """qdrant_db 已存在 + force_rebuild=True → 強制重建。"""
        builder = _make_builder("qdrant")
        with patch("os.path.exists", return_value=True):
            assert builder._should_rebuild(force_rebuild=True) is True


class TestShouldRebuildUnified:
    """Qdrant 與 Milvus 統一邏輯的一致性驗證。"""

    @pytest.mark.parametrize("vector_store_type", ["qdrant", "milvus"])
    def test_force_rebuild_always_true(self, vector_store_type: str) -> None:
        """force_rebuild=True 時，兩種 store 皆回傳 True。"""
        builder = _make_builder(vector_store_type)
        with patch("os.path.exists", return_value=True):
            assert builder._should_rebuild(force_rebuild=True) is True

    @pytest.mark.parametrize("vector_store_type", ["qdrant", "milvus"])
    def test_existing_db_returns_false(self, vector_store_type: str) -> None:
        """store 路徑已存在 + force_rebuild=False → 兩種 store 皆回傳 False。"""
        builder = _make_builder(vector_store_type)
        with patch("os.path.exists", return_value=True):
            assert builder._should_rebuild(force_rebuild=False) is False

    @pytest.mark.parametrize("vector_store_type", ["qdrant", "milvus"])
    def test_missing_db_returns_true(self, vector_store_type: str) -> None:
        """store 路徑不存在 → 兩種 store 皆回傳 True。"""
        builder = _make_builder(vector_store_type)
        with patch("os.path.exists", return_value=False):
            assert builder._should_rebuild(force_rebuild=False) is True

    def test_unsupported_type_raises(self) -> None:
        """不支援的 vector_store_type → 拋出 ValueError。"""
        builder = _make_builder("unsupported")
        with patch("os.path.exists", return_value=True):
            with pytest.raises(ValueError, match="Unsupported vector_store_type"):
                builder._should_rebuild(force_rebuild=False)
