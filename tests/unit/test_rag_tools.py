"""RAG 子系統測試。

涵蓋：
- RAGRegistry：cache hit / cache miss / LRU eviction / close / list_sites
- build_rag／RAGBuilder 失敗時的資源處理與建庫順序（先讀來源再清除舊向量庫）
- Retriever 工具：依 site_id 路由到 registry、參數傳遞與錯誤傳播

load_rag 的載入路徑見 test_serve_rag_loading.py。

所有 RAG / Milvus 實例以 mock 替代，不觸發真實資源。
"""

from __future__ import annotations

import os
from collections import OrderedDict
from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from website_copilot.agent.tools.webpage_retriever import (
    create_webpage_retriever_tool,
)
from website_copilot.config.rag_config import RAGConfig
from website_copilot.ingestion.indexing.index import IndexBuilder, RAGTarget
from website_copilot.retrieval.factory import (
    build_rag,
    build_target,
    load_rag,
    published_target,
    vector_store_run_target,
)
from website_copilot.retrieval.registry import RAGRegistry

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


MakeRegistry = Callable[..., RAGRegistry]


@pytest.fixture
def make_registry(tmp_path: Path) -> MakeRegistry:
    """建立以 tmp_path/data 為 base_folder 的 RAGRegistry。

    建立 data/vector_db/<site_id>.db（模擬已 publish 的向量庫），
    讓 list_sites() 與 _site_exists() 能正確運作。
    """

    def _make(
        existing_sites: list[str] | None = None,
        max_cached: int = 5,
    ) -> RAGRegistry:
        rag_dir = tmp_path / "data" / "vector_db"
        rag_dir.mkdir(parents=True, exist_ok=True)
        for site_id in existing_sites or []:
            (rag_dir / f"{site_id}.db").mkdir(parents=True)
        return RAGRegistry(
            base_folder=str(tmp_path / "data"),
            config_name="default",
            max_cached=max_cached,
        )

    return _make


def _track_loaded_rags(mock_load_rag: MagicMock) -> OrderedDict[str, MagicMock]:
    """讓 load_rag 依 target.site_id 回傳 RAG 替身，並記錄於回傳的 dict。"""
    rags: OrderedDict[str, MagicMock] = OrderedDict()

    def make_rag_side_effect(config: Any, target: RAGTarget) -> MagicMock:
        rag = _make_mock_rag(target.site_id)
        rags[target.site_id] = rag
        return rag

    mock_load_rag.side_effect = make_rag_side_effect
    return rags


# ===========================================================================
# RAGRegistry 測試
# ===========================================================================

# ---------- list_sites ----------


class TestListSites:
    """RAGRegistry.list_sites() 掃描目錄。"""

    def test_list_sites_scans_rag_directory(self, make_registry: MakeRegistry) -> None:
        registry = make_registry(existing_sites=["nculab", "ncucsie"])
        result = registry.list_sites()
        assert result == ["ncucsie", "nculab"]

    def test_excludes_sites_without_vector_store(
        self, make_registry: MakeRegistry
    ) -> None:
        """只有 aug_webpages 或空 rag 目錄（尚未 publish 向量庫）的站點不列出。"""
        registry = make_registry(existing_sites=["nculab"])
        base = registry.base_folder
        os.makedirs(os.path.join(base, "aug_webpages", "ncucsie"))
        os.makedirs(os.path.join(base, "vector_db", "pending"))
        assert registry.list_sites() == ["nculab"]
        with pytest.raises(ValueError, match="ncucsie.*不存在"):
            registry.get("ncucsie")

    def test_ignores_publish_leftovers(self, make_registry: MakeRegistry) -> None:
        """.staging-*／.db.tmp／.db.old 等 publish 中間產物與舊版目錄不是站點。"""
        registry = make_registry(existing_sites=["nculab"])
        rag = os.path.join(registry.base_folder, "vector_db")
        for leftover in (
            ".staging-abc123",
            ".staging-xyz.db",
            "ncucsie.db.tmp",
            "ncucsie.db.old",
            "legacy/milvus.db",
        ):
            os.makedirs(os.path.join(rag, leftover))
        assert registry.list_sites() == ["nculab"]

    def test_db_file_is_not_a_vector_store(self, make_registry: MakeRegistry) -> None:
        registry = make_registry(existing_sites=["nculab"])
        Path(registry.base_folder, "vector_db", "ncucsie.db").write_text("not a dir")
        assert registry.list_sites() == ["nculab"]


# ---------- get: site not found ----------


class TestGetSiteNotFound:
    """RAGRegistry.get() 在 site 不存在時拋出 ValueError。"""

    def test_raises_value_error(self, make_registry: MakeRegistry) -> None:
        registry = make_registry(existing_sites=["nculab"])
        with pytest.raises(ValueError, match="ncucsie.*不存在"):
            registry.get("ncucsie")


# ---------- get: cache miss (build) ----------


class TestGetCacheMiss:
    """RAGRegistry.get() cache miss 時建立 RAG 並快取。"""

    @patch("website_copilot.retrieval.registry.load_rag")
    @patch("website_copilot.retrieval.registry.RAGConfig")
    def test_builds_rag_on_first_call(
        self,
        mock_config_cls: MagicMock,
        mock_load_rag: MagicMock,
        make_registry: MakeRegistry,
    ) -> None:
        registry = make_registry(existing_sites=["nculab"])

        fake_config = MagicMock()
        mock_config_cls.from_yaml.return_value = fake_config

        fake_rag = _make_mock_rag("nculab")
        mock_load_rag.return_value = fake_rag

        result = registry.get("nculab")

        mock_config_cls.from_yaml.assert_called_once_with("default")
        mock_load_rag.assert_called_once_with(
            fake_config, published_target("nculab", registry.base_folder)
        )
        assert result is fake_rag


# ---------- get: cache hit ----------


class TestGetCacheHit:
    """RAGRegistry.get() cache hit 時不重建，直接回傳快取。"""

    @patch("website_copilot.retrieval.registry.load_rag")
    @patch("website_copilot.retrieval.registry.RAGConfig")
    def test_returns_same_instance(
        self,
        mock_config_cls: MagicMock,
        mock_load_rag: MagicMock,
        make_registry: MakeRegistry,
    ) -> None:
        registry = make_registry(existing_sites=["nculab"])

        mock_config_cls.from_yaml.return_value = MagicMock()
        fake_rag = _make_mock_rag("nculab")
        mock_load_rag.return_value = fake_rag

        first = registry.get("nculab")
        second = registry.get("nculab")

        assert first is second
        # RAG 只載入一次
        mock_load_rag.assert_called_once()


# ---------- LRU eviction ----------


class TestLRUEviction:
    """RAGRegistry._evict_if_needed() 淘汰最久未使用項。"""

    @patch("website_copilot.retrieval.registry.load_rag")
    @patch("website_copilot.retrieval.registry.RAGConfig")
    def test_evicts_oldest_when_exceeding_max(
        self,
        mock_config_cls: MagicMock,
        mock_load_rag: MagicMock,
        make_registry: MakeRegistry,
    ) -> None:
        registry = make_registry(existing_sites=["a", "b", "c"], max_cached=2)

        mock_config_cls.from_yaml.return_value = MagicMock()

        rags = _track_loaded_rags(mock_load_rag)

        registry.get("a")  # cache: [a]
        registry.get("b")  # cache: [a, b]
        assert list(registry._cache.keys()) == ["a", "b"]

        registry.get("c")  # cache: [b, c] — a evicted
        assert list(registry._cache.keys()) == ["b", "c"]
        rags["a"].close.assert_called_once()


# ---------- close ----------


class TestClose:
    """RAGRegistry.close() 釋放所有快取中的 RAG 實例。"""

    @patch("website_copilot.retrieval.registry.load_rag")
    @patch("website_copilot.retrieval.registry.RAGConfig")
    def test_closes_all_cached_rags(
        self,
        mock_config_cls: MagicMock,
        mock_load_rag: MagicMock,
        make_registry: MakeRegistry,
    ) -> None:
        registry = make_registry(existing_sites=["a", "b"])

        mock_config_cls.from_yaml.return_value = MagicMock()

        rags = _track_loaded_rags(mock_load_rag)

        registry.get("a")
        registry.get("b")
        registry.close()

        rags["a"].close.assert_called_once()
        rags["b"].close.assert_called_once()
        assert len(registry._cache) == 0


# ===========================================================================
# build_target / build_rag / load_rag 測試
# ===========================================================================


def test_build_target_uses_latest_summarizer_run_of_same_site(tmp_path: Path) -> None:
    """use_latest_results=True：改用 runs/ 中同 site 最新的圖片摘要結果。"""
    runs = tmp_path / "runs"
    for ts, site in [
        ("20260929_090000", "nculab"),
        ("20260929_100000", "nculab"),
        ("20260929_110000", "ncucsie"),  # 較新但不同 site
    ]:
        (runs / ts / "augmenter" / site / "r" / "results").mkdir(parents=True)

    target = build_target(
        "nculab",
        str(tmp_path / "out" / "milvus.db"),
        use_latest_results=True,
        runs_folder=str(runs),
    )

    assert target == RAGTarget(
        site_id="nculab",
        aug_webpages_dir=str(runs / "20260929_100000" / "augmenter" / "nculab" / "r"),
        milvus_uri=str(tmp_path / "out" / "milvus.db"),
    )


def test_build_target_defaults_to_published_webpages() -> None:
    target = build_target("nculab", "/tmp/x/milvus.db", data_folder="data")

    assert target.aug_webpages_dir == "data/aug_webpages/nculab"
    assert target.milvus_uri == "/tmp/x/milvus.db"


def test_published_target() -> None:
    assert published_target("ncucsie", "data") == RAGTarget(
        site_id="ncucsie",
        aug_webpages_dir="data/aug_webpages/ncucsie",
        milvus_uri="data/vector_db/ncucsie.db",
    )


def test_build_rag_does_not_modify_config(tmp_path: Path) -> None:
    """建庫過程只讀 config，位置由 RAGTarget 提供（config 不再被改寫）。"""
    config = RAGConfig()
    before = config.model_dump()
    target = RAGTarget("nculab", str(tmp_path / "web"), str(tmp_path / "milvus.db"))

    with (
        patch("website_copilot.retrieval.factory.load_source"),
        patch("website_copilot.retrieval.factory.IndexBuilder") as index_builder,
        patch("website_copilot.retrieval.factory.RAG"),
    ):
        build_rag(config, target)

    index_builder.assert_called_once_with(config, target)
    assert config.model_dump() == before


def _make_rag_build_run(root: Path, site_id: str = "nculab") -> Path:
    run = root / "runs" / "20260101_000000" / "rag_build" / site_id / "r"
    (run / "results" / "milvus.db").mkdir(parents=True)
    (run / "site_config.yml").write_text(f"site_id: {site_id}\n", encoding="utf-8")
    (run / "module_config.yml").write_text(
        "# source: configs/rag/test.yml\nnodes: {}\n", encoding="utf-8"
    )
    return run


class TestVectorStoreRunTarget:
    """rag-query --run.vector-store-run：指向 runs/ 中 rag-build 的向量庫（唯讀）。"""

    def test_target_points_to_run_results(self, tmp_path: Path) -> None:
        run = _make_rag_build_run(tmp_path)

        target = vector_store_run_target("nculab", str(run), data_folder="data")

        assert target == RAGTarget(
            site_id="nculab",
            aug_webpages_dir="data/aug_webpages/nculab",
            milvus_uri=str(run / "results" / "milvus.db"),
        )

    def test_logs_source_of_build_run(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        run = _make_rag_build_run(tmp_path)
        with patch("website_copilot.retrieval.factory.print_log") as print_log:
            vector_store_run_target("nculab", str(run))
        assert "configs/rag/test.yml" in print_log.call_args.args[0]

    def test_missing_run_path_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="vector_store_run"):
            vector_store_run_target("nculab", str(tmp_path / "nope"))

    def test_missing_vector_store_raises(self, tmp_path: Path) -> None:
        run = _make_rag_build_run(tmp_path)
        (run / "results" / "milvus.db").rmdir()
        with pytest.raises(FileNotFoundError, match="找不到向量庫"):
            vector_store_run_target("nculab", str(run))

    def test_missing_site_config_raises(self, tmp_path: Path) -> None:
        run = _make_rag_build_run(tmp_path)
        (run / "site_config.yml").unlink()
        with pytest.raises(FileNotFoundError, match="site_config.yml"):
            vector_store_run_target("nculab", str(run))

    def test_site_mismatch_raises(self, tmp_path: Path) -> None:
        run = _make_rag_build_run(tmp_path, site_id="ncucsie")
        with pytest.raises(ValueError, match="站點不一致"):
            vector_store_run_target("nculab", str(run))


def test_load_rag_never_builds_and_reports_missing_store(tmp_path: Path) -> None:
    """load_rag 向量庫不存在時報錯（不退回重建），提示先 prepare。"""
    target = RAGTarget("nculab", str(tmp_path / "web"), str(tmp_path / "milvus.db"))
    with patch("website_copilot.retrieval.factory.IndexBuilder") as index_builder:
        with pytest.raises(FileNotFoundError, match="prepare"):
            load_rag(RAGConfig(), target, build_query_engine=True)
    index_builder.assert_not_called()


class TestReturnStyleBuild:
    """回傳式建構：失敗時釋放資源、重建前先讀來源。"""

    def test_rag_builder_closes_handle_when_build_fails(self) -> None:
        from website_copilot.retrieval.factory import RAGBuilder

        handle = MagicMock()
        builder = RAGBuilder(MagicMock())
        with (
            patch.object(builder, "build_retriever", side_effect=RuntimeError("boom")),
            pytest.raises(RuntimeError, match="boom"),
        ):
            builder.build(handle)
        handle.close.assert_called_once()

    def test_rebuild_reads_source_before_cleaning(self, tmp_path: Any) -> None:
        """results.json 不存在 → 在清除既有向量庫前就失敗。"""
        target = RAGTarget("demo", str(tmp_path / "missing"), str(tmp_path / "db"))
        with (
            patch.object(IndexBuilder, "clean") as mock_clean,
            pytest.raises(FileNotFoundError, match="results.json"),
        ):
            build_rag(RAGConfig(), target)
        mock_clean.assert_not_called()


# ===========================================================================
# Retriever 工具測試
# ===========================================================================

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
