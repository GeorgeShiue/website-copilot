"""RAGRegistry：站點列表、快取（hit／miss／LRU）、關閉與資源釋放的穩健性。

所有 RAG／Milvus 實例以 mock 替代，不觸發真實資源。
load_rag 的載入路徑見 test_serve_rag_loading.py。
"""

from __future__ import annotations

import logging
import os
from collections import OrderedDict
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from website_copilot.ingestion.indexing.index import RAGTarget
from website_copilot.retrieval.factory import published_target
from website_copilot.retrieval.rag import RAG
from website_copilot.retrieval.registry import RAGRegistry

# ===========================================================================
# Helpers
# ===========================================================================


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
# close／__exit__／淘汰：資源釋放的穩健性
# ===========================================================================


class _FakeRAG:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.closed = False

    def close(self) -> None:
        self.closed = True
        if self.fail:
            raise RuntimeError("close failed")


def _registry_with(**rags: _FakeRAG) -> RAGRegistry:
    registry = RAGRegistry()
    for site_id, rag in rags.items():
        registry._cache[site_id] = cast(RAG, rag)
    return registry


def test_close_closes_every_rag_even_if_one_fails(
    caplog: pytest.LogCaptureFixture,
) -> None:
    first, failing, last = _FakeRAG(), _FakeRAG(fail=True), _FakeRAG()
    registry = _registry_with(a=first, b=failing, c=last)

    with caplog.at_level(logging.ERROR):
        registry.close()  # 不重新拋出

    assert first.closed and failing.closed and last.closed
    assert not registry._cache
    assert "site_id=b" in caplog.text


def test_exit_does_not_swallow_exception_from_with_body() -> None:
    with pytest.raises(ValueError, match="body failed"), RAGRegistry():
        raise ValueError("body failed")


def test_exit_does_not_mask_body_exception_when_close_fails() -> None:
    registry = _registry_with(a=_FakeRAG(fail=True))

    with pytest.raises(ValueError, match="body failed"), registry:
        raise ValueError("body failed")

    assert not registry._cache


def test_get_survives_eviction_close_failure(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    registry = RAGRegistry(max_cached=1)
    failing = _FakeRAG(fail=True)
    registry._cache["old"] = cast(RAG, failing)
    new_rag = _FakeRAG()
    monkeypatch.setattr(registry, "_site_exists", lambda site_id: True)

    with (
        patch("website_copilot.retrieval.registry.RAGConfig"),
        patch("website_copilot.retrieval.registry.published_target"),
        patch("website_copilot.retrieval.registry.load_rag", return_value=new_rag),
        caplog.at_level(logging.ERROR),
    ):
        got = registry.get("new")  # 淘汰 old 時 close 失敗，不應讓 get() 失敗

    assert got is new_rag
    assert list(registry._cache) == ["new"]
    assert failing.closed
    assert "site_id=old" in caplog.text
