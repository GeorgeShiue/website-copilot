"""RAG 子系統測試（合併 test_rag_registry + test_rag_reuse + test_multi_site_tool + m0_rag_smoke）。

涵蓋：
- RAGRegistry：cache hit / cache miss / LRU eviction / close / list_sites
- RAGBuilder._should_rebuild：Milvus 路徑判斷
- Retriever 工具：schema 驗證、tool 建立、retrieve 路由、格式化
- create_site_discovery_tool / Agent dataclass
- Smoke 驗證：registry + tool 建立 → invoke → close 流程

所有 RAG / Milvus 實例以 mock 替代，不觸發真實資源。
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.tools import StructuredTool

from app.engines.rag.rag_factory import RAGBuilder
from app.tools.rag_registry import RAGRegistry
from app.tools.webpage_retriever import (
    RetrieverInputSchema,
    _format_retrieval_results,
    create_webpage_retriever_tool,
)

# ===========================================================================
# Helpers
# ===========================================================================


def _make_mock_registry(
    existing_sites: list[str] | None = None,
) -> MagicMock:
    """建立 mock RAGRegistry（使用 spec=RAGRegistry）。"""
    registry = MagicMock(spec=RAGRegistry)
    registry.list_sites.return_value = existing_sites or []
    return registry


def _make_fake_retrieval_results(n: int = 2) -> list[dict[str, Any]]:
    """建立假的檢索結果。"""
    return [
        {
            "page_title": f"Page_{i}",
            "score": 0.9 - i * 0.1,
            "page_type": "paper" if i % 2 == 0 else "general",
            "url": f"https://example.com/page_{i}",
            "content": f"Content of page {i}",
        }
        for i in range(1, n + 1)
    ]


def _make_mock_rag(site_id: str = "test") -> MagicMock:
    """建立最小化的 RAG 替身。"""
    rag = MagicMock()
    rag.site_id = site_id
    rag._closed = False
    rag.close = MagicMock(side_effect=lambda: setattr(rag, "_closed", True))
    return rag


def _make_registry(
    existing_sites: list[str] | None = None,
    max_cached: int = 5,
) -> tuple[RAGRegistry, MagicMock]:
    """建立帶有 mock DataManager 的 RAGRegistry。

    Returns:
        (registry, mock_data_manager)
    """
    dm = MagicMock()
    dm.list_sites.return_value = existing_sites or []
    dm.site_exists = MagicMock(side_effect=lambda sid: sid in (existing_sites or []))
    registry = RAGRegistry(
        data_manager=dm,
        default_config_name="default",
        max_cached=max_cached,
    )
    return registry, dm


# ===========================================================================
# RAGRegistry 測試
# ===========================================================================

# ---------- list_sites ----------


class TestListSites:
    """RAGRegistry.list_sites() 委派 DataManager。"""

    def test_delegates_to_data_manager(self) -> None:
        registry, dm = _make_registry(existing_sites=["nculab", "ncucsie"])
        result = registry.list_sites()
        assert result == ["nculab", "ncucsie"]
        dm.list_sites.assert_called_once()

    def test_empty_when_no_sites(self) -> None:
        registry, _ = _make_registry(existing_sites=[])
        assert registry.list_sites() == []


# ---------- get: site not found ----------


class TestGetSiteNotFound:
    """RAGRegistry.get() 在 site 不存在時拋出 ValueError。"""

    def test_raises_value_error(self) -> None:
        registry, _ = _make_registry(existing_sites=["nculab"])
        with pytest.raises(ValueError, match="ncucsie.*不存在"):
            registry.get("ncucsie")

    def test_error_message_lists_available_sites(self) -> None:
        registry, _ = _make_registry(existing_sites=["alpha", "beta"])
        with pytest.raises(ValueError) as exc_info:
            registry.get("gamma")
        msg = str(exc_info.value)
        assert "alpha" in msg
        assert "beta" in msg

    def test_error_message_when_no_sites_available(self) -> None:
        registry, _ = _make_registry(existing_sites=[])
        with pytest.raises(ValueError, match="（無）"):
            registry.get("any_site")


# ---------- get: cache miss (build) ----------


class TestGetCacheMiss:
    """RAGRegistry.get() cache miss 時建立 RAG 並快取。"""

    @patch("app.tools.rag_registry.RAGBuilder")
    @patch("app.tools.rag_registry.RAG")
    @patch("app.tools.rag_registry.RAGConfig")
    def test_builds_rag_on_first_call(
        self,
        mock_config_cls: MagicMock,
        mock_rag_cls: MagicMock,
        mock_builder_cls: MagicMock,
    ) -> None:
        registry, _ = _make_registry(existing_sites=["nculab"])

        fake_config = MagicMock()
        fake_config.webpages_data_folder_path = "data/webpages/nculab"
        mock_config_cls.from_toml.return_value = fake_config

        fake_rag = _make_mock_rag("nculab")
        mock_rag_cls.return_value = fake_rag

        result = registry.get("nculab")

        mock_config_cls.from_toml.assert_called_once_with("default", site_id="nculab")
        mock_rag_cls.assert_called_once_with(
            webpages_data_folder_path="data/webpages/nculab"
        )
        mock_builder_cls.return_value.build_reusable.assert_called_once_with(
            fake_rag, force_rebuild=False
        )
        assert result is fake_rag

    @patch("app.tools.rag_registry.RAGBuilder")
    @patch("app.tools.rag_registry.RAG")
    @patch("app.tools.rag_registry.RAGConfig")
    def test_stores_in_cache_after_build(
        self,
        mock_config_cls: MagicMock,
        mock_rag_cls: MagicMock,
        mock_builder_cls: MagicMock,
    ) -> None:
        registry, _ = _make_registry(existing_sites=["nculab"])

        fake_config = MagicMock()
        fake_config.webpages_data_folder_path = "data/webpages/nculab"
        mock_config_cls.from_toml.return_value = fake_config
        fake_rag = _make_mock_rag("nculab")
        mock_rag_cls.return_value = fake_rag

        registry.get("nculab")
        assert "nculab" in registry._cache
        assert registry._cache["nculab"] is fake_rag


# ---------- get: cache hit ----------


class TestGetCacheHit:
    """RAGRegistry.get() cache hit 時不重建，直接回傳快取。"""

    @patch("app.tools.rag_registry.RAGBuilder")
    @patch("app.tools.rag_registry.RAG")
    @patch("app.tools.rag_registry.RAGConfig")
    def test_returns_same_instance(
        self,
        mock_config_cls: MagicMock,
        mock_rag_cls: MagicMock,
        mock_builder_cls: MagicMock,
    ) -> None:
        registry, _ = _make_registry(existing_sites=["nculab"])

        fake_config = MagicMock()
        fake_config.webpages_data_folder_path = "data/webpages/nculab"
        mock_config_cls.from_toml.return_value = fake_config
        fake_rag = _make_mock_rag("nculab")
        mock_rag_cls.return_value = fake_rag

        first = registry.get("nculab")
        second = registry.get("nculab")

        assert first is second
        # RAG 只建立一次
        mock_rag_cls.assert_called_once()

    @patch("app.tools.rag_registry.RAGBuilder")
    @patch("app.tools.rag_registry.RAG")
    @patch("app.tools.rag_registry.RAGConfig")
    def test_moves_to_end_on_hit(
        self,
        mock_config_cls: MagicMock,
        mock_rag_cls: MagicMock,
        mock_builder_cls: MagicMock,
    ) -> None:
        """cache hit 時 move_to_end 更新 LRU 順序。"""
        registry, _ = _make_registry(existing_sites=["a", "b", "c"], max_cached=3)
        fake_config = MagicMock()
        fake_config.webpages_data_folder_path = "data/webpages/x"
        mock_config_cls.from_toml.return_value = fake_config

        rags: OrderedDict[str, MagicMock] = OrderedDict()

        def make_rag_side_effect(**kwargs: Any) -> MagicMock:
            site = kwargs["webpages_data_folder_path"].split("/")[-1]
            rag = _make_mock_rag(site)
            rags[site] = rag
            return rag

        mock_rag_cls.side_effect = make_rag_side_effect

        registry.get("a")
        registry.get("b")
        registry.get("c")
        # LRU 順序: a, b, c
        assert list(registry._cache.keys()) == ["a", "b", "c"]

        # 命中 a → 移到末尾
        registry.get("a")
        assert list(registry._cache.keys()) == ["b", "c", "a"]


# ---------- LRU eviction ----------


class TestLRUEviction:
    """RAGRegistry._evict_if_needed() 淘汰最久未使用項。"""

    @patch("app.tools.rag_registry.RAGBuilder")
    @patch("app.tools.rag_registry.RAG")
    @patch("app.tools.rag_registry.RAGConfig")
    def test_evicts_oldest_when_exceeding_max(
        self,
        mock_config_cls: MagicMock,
        mock_rag_cls: MagicMock,
        mock_builder_cls: MagicMock,
    ) -> None:
        registry, _ = _make_registry(existing_sites=["a", "b", "c"], max_cached=2)

        def config_side_effect(config_name: str, **overrides: Any) -> MagicMock:
            site = overrides.get("site_id", "x")
            cfg = MagicMock()
            cfg.webpages_data_folder_path = f"data/webpages/{site}"
            return cfg

        mock_config_cls.from_toml.side_effect = config_side_effect

        rags: OrderedDict[str, MagicMock] = OrderedDict()

        def make_rag_side_effect(**kwargs: Any) -> MagicMock:
            path = kwargs["webpages_data_folder_path"]
            site = path.split("/")[-1]
            rag = _make_mock_rag(site)
            rags[site] = rag
            return rag

        mock_rag_cls.side_effect = make_rag_side_effect

        registry.get("a")  # cache: [a]
        registry.get("b")  # cache: [a, b]
        assert list(registry._cache.keys()) == ["a", "b"]

        registry.get("c")  # cache: [b, c] — a evicted
        assert list(registry._cache.keys()) == ["b", "c"]
        rags["a"].close.assert_called_once()

    @patch("app.tools.rag_registry.RAGBuilder")
    @patch("app.tools.rag_registry.RAG")
    @patch("app.tools.rag_registry.RAGConfig")
    def test_does_not_evict_when_under_max(
        self,
        mock_config_cls: MagicMock,
        mock_rag_cls: MagicMock,
        mock_builder_cls: MagicMock,
    ) -> None:
        registry, _ = _make_registry(existing_sites=["a", "b"], max_cached=5)
        fake_config = MagicMock()
        fake_config.webpages_data_folder_path = "data/webpages/x"
        mock_config_cls.from_toml.return_value = fake_config

        rags: OrderedDict[str, MagicMock] = OrderedDict()

        def make_rag_side_effect(**kwargs: Any) -> MagicMock:
            path = kwargs["webpages_data_folder_path"]
            site = path.split("/")[-1]
            rag = _make_mock_rag(site)
            rags[site] = rag
            return rag

        mock_rag_cls.side_effect = make_rag_side_effect

        registry.get("a")
        registry.get("b")
        assert list(registry._cache.keys()) == ["a", "b"]
        # 沒有任何 rag 被 close
        for rag in rags.values():
            rag.close.assert_not_called()


# ---------- close ----------


class TestClose:
    """RAGRegistry.close() 釋放所有快取中的 RAG 實例。"""

    @patch("app.tools.rag_registry.RAGBuilder")
    @patch("app.tools.rag_registry.RAG")
    @patch("app.tools.rag_registry.RAGConfig")
    def test_closes_all_cached_rags(
        self,
        mock_config_cls: MagicMock,
        mock_rag_cls: MagicMock,
        mock_builder_cls: MagicMock,
    ) -> None:
        registry, _ = _make_registry(existing_sites=["a", "b"])

        def config_side_effect(config_name: str, **overrides: Any) -> MagicMock:
            site = overrides.get("site_id", "x")
            cfg = MagicMock()
            cfg.webpages_data_folder_path = f"data/webpages/{site}"
            return cfg

        mock_config_cls.from_toml.side_effect = config_side_effect

        rags: OrderedDict[str, MagicMock] = OrderedDict()

        def make_rag_side_effect(**kwargs: Any) -> MagicMock:
            path = kwargs["webpages_data_folder_path"]
            site = path.split("/")[-1]
            rag = _make_mock_rag(site)
            rags[site] = rag
            return rag

        mock_rag_cls.side_effect = make_rag_side_effect

        registry.get("a")
        registry.get("b")
        registry.close()

        rags["a"].close.assert_called_once()
        rags["b"].close.assert_called_once()
        assert len(registry._cache) == 0

    def test_close_on_empty_cache(self) -> None:
        """空快取呼叫 close 不報錯。"""
        registry, _ = _make_registry()
        registry.close()
        assert len(registry._cache) == 0


# ===========================================================================
# RAGBuilder 測試
# ===========================================================================


@dataclass
class _FakeRAGConfig:
    """最小化的 RAGConfig 替身，僅含 RAGBuilder 所需欄位。

    RAGBuilder.__init__ 僅儲存 config；
    _should_rebuild 只讀取 vector_store_type 與 milvus_uri。
    """

    vector_store_type: str = "milvus"
    milvus_uri: str | None = "data/rag/test/milvus.db"


def _make_builder(vector_store_type: str, **overrides: Any) -> RAGBuilder:
    """建立帶有指定 vector_store_type 的 RAGBuilder（使用 fake config）。"""
    config = _FakeRAGConfig(vector_store_type=vector_store_type, **overrides)
    return RAGBuilder(config)  # type: ignore[arg-type]


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


class TestShouldRebuildUnified:
    """_should_rebuild 邏輯的一致性驗證。"""

    def test_force_rebuild_always_true(self) -> None:
        """force_rebuild=True 時回傳 True。"""
        builder = _make_builder("milvus")
        with patch("os.path.exists", return_value=True):
            assert builder._should_rebuild(force_rebuild=True) is True

    def test_existing_db_returns_false(self) -> None:
        """store 路徑已存在 + force_rebuild=False → 回傳 False。"""
        builder = _make_builder("milvus")
        with patch("os.path.exists", return_value=True):
            assert builder._should_rebuild(force_rebuild=False) is False

    def test_missing_db_returns_true(self) -> None:
        """store 路徑不存在 → 回傳 True。"""
        builder = _make_builder("milvus")
        with patch("os.path.exists", return_value=False):
            assert builder._should_rebuild(force_rebuild=False) is True


# ===========================================================================
# Retriever 工具測試
# ===========================================================================

# ---------- RetrieverInputSchema ----------


class TestRetrieverInputSchema:
    """RetrieverInputSchema 欄位驗證。"""

    def test_has_site_id_field(self) -> None:
        """schema 包含必要的 site_id 欄位。"""
        fields = list(RetrieverInputSchema.model_fields.keys())
        assert "site_id" in fields
        assert "query" in fields
        assert "filter_dict" in fields
        assert "similarity_top_k" in fields

    def test_site_id_is_required(self) -> None:
        """site_id 為必要欄位，缺少時 Pydantic 拒絕。"""
        with pytest.raises(Exception):
            RetrieverInputSchema(query="test")  # type: ignore[call-arg]

    def test_valid_construction(self) -> None:
        """提供 site_id + query 可正常建立。"""
        schema = RetrieverInputSchema(site_id="nculab", query="成員")
        assert schema.site_id == "nculab"
        assert schema.query == "成員"
        assert schema.filter_dict is None
        assert schema.similarity_top_k is None

    def test_optional_fields_defaults(self) -> None:
        """filter_dict 與 similarity_top_k 預設為 None。"""
        schema = RetrieverInputSchema(site_id="x", query="y")
        assert schema.filter_dict is None
        assert schema.similarity_top_k is None


# ---------- create_webpage_retriever_tool ----------


class TestCreateWebpageRetrieverTool:
    """create_webpage_retriever_tool 工廠函數。"""

    def test_returns_structured_tool(self) -> None:
        """回傳 StructuredTool 實例。"""
        registry = _make_mock_registry()
        tool = create_webpage_retriever_tool(registry)
        assert isinstance(tool, StructuredTool)

    def test_tool_name(self) -> None:
        """工具名稱為 webpage_retriever。"""
        registry = _make_mock_registry()
        tool = create_webpage_retriever_tool(registry)
        assert tool.name == "webpage_retriever"

    def test_tool_description_mentions_site_id(self) -> None:
        """工具描述提及 site_id。"""
        registry = _make_mock_registry()
        tool = create_webpage_retriever_tool(registry)
        assert "site_id" in tool.description

    def test_tool_description_mentions_list_knowledge_bases(self) -> None:
        """工具描述提及 list_knowledge_bases。"""
        registry = _make_mock_registry()
        tool = create_webpage_retriever_tool(registry)
        assert "list_knowledge_bases" in tool.description

    def test_tool_has_correct_args_schema(self) -> None:
        """工具使用 RetrieverInputSchema。"""
        registry = _make_mock_registry()
        tool = create_webpage_retriever_tool(registry)
        assert tool.args_schema is RetrieverInputSchema


# ---------- retrieve routing ----------


class TestRetrieveRouting:
    """webpage_retriever 工具的 site_id 路由邏輯。"""

    def test_calls_registry_get_with_site_id(self) -> None:
        """_retrieve 呼叫 registry.get(site_id)。"""
        registry = _make_mock_registry()
        fake_rag = MagicMock()
        fake_rag.retrieve.return_value = _make_fake_retrieval_results(1)
        registry.get.return_value = fake_rag

        tool = create_webpage_retriever_tool(registry)
        result = tool.invoke({"site_id": "nculab", "query": "test"})

        registry.get.assert_called_once_with("nculab")
        fake_rag.retrieve.assert_called_once()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_passes_filter_and_top_k(self) -> None:
        """filter_dict 與 similarity_top_k 正確傳遞。"""
        registry = _make_mock_registry()
        fake_rag = MagicMock()
        fake_rag.retrieve.return_value = _make_fake_retrieval_results(1)
        registry.get.return_value = fake_rag

        tool = create_webpage_retriever_tool(registry)
        tool.invoke(
            {
                "site_id": "nculab",
                "query": "paper",
                "filter_dict": {"page_type": "paper"},
                "similarity_top_k": 3,
            }
        )

        fake_rag.retrieve.assert_called_once_with(
            query="paper",
            filter_dict={"page_type": "paper"},
            similarity_top_k=3,
        )

    def test_propagates_registry_error(self) -> None:
        """registry.get 拋出 ValueError 時工具向上傳播。"""
        registry = _make_mock_registry()
        registry.get.side_effect = ValueError("site_id 'x' 不存在")

        tool = create_webpage_retriever_tool(registry)
        with pytest.raises(ValueError, match="不存在"):
            tool.invoke({"site_id": "x", "query": "test"})


# ---------- _format_retrieval_results ----------


class TestFormatRetrievalResults:
    """_format_retrieval_results 格式化邏輯。"""

    def test_empty_results(self) -> None:
        """空結果回傳提示字串。"""
        result = _format_retrieval_results([])
        assert "未檢索到" in result

    def test_single_result(self) -> None:
        """單筆結果包含標題、分數、URL。"""
        results = _make_fake_retrieval_results(1)
        formatted = _format_retrieval_results(results)
        assert "Page_1" in formatted
        assert "0.800" in formatted
        assert "https://example.com/page_1" in formatted


# ===========================================================================
# Smoke 驗證（from scripts/m0_rag_smoke.py）
# ===========================================================================


class TestRAGRetrieverSmoke:
    """webpage_retriever 工具的 smoke 驗證：建立 → invoke → close 流程。

    使用 mock registry 避免依賴真實 Milvus 資料。
    """

    def test_retriever_tool_create_invoke_close(self) -> None:
        """registry + tool 建立、invoke、close 完整流程。"""
        registry = _make_mock_registry(existing_sites=["nculab"])

        fake_rag = MagicMock()
        fake_rag.retrieve.return_value = _make_fake_retrieval_results(2)
        registry.get.return_value = fake_rag

        tool = create_webpage_retriever_tool(registry)
        try:
            sites = registry.list_sites()
            assert len(sites) > 0, "smoke：無可用 site"
            site_id = sites[0]
            result = tool.invoke(
                {
                    "site_id": site_id,
                    "query": "實驗室的成員有哪些人？",
                    "similarity_top_k": 3,
                }
            )
            assert isinstance(result, str) and len(result) > 0, "smoke：檢索結果為空"
            assert "Page_" in result, "smoke：結果未含頁面標題"
        finally:
            registry.close()
