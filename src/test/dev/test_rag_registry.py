"""RAGRegistry 單元測試（不觸發真實 Milvus / RAG 建構）。

涵蓋：
- RAGRegistry.get(): cache hit / cache miss / site not found ValueError
- RAGRegistry._evict_if_needed(): LRU eviction
- RAGRegistry.close(): 釋放所有快取資源
- RAGRegistry.list_sites(): 委派 DataManager

所有 RAG / RAGBuilder / RAGConfig 均以 mock 替代，不觸及真實資料。
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.tools.rag_registry import RAGRegistry

# ---------- Helpers ----------


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

        rags = {}

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

        # Each site gets a unique config path so mock RAG can be keyed by site
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
