"""RAGRegistry.close()／__exit__／LRU 淘汰：資源釋放的穩健性。"""

import logging
from typing import cast
from unittest.mock import patch

import pytest

from website_copilot.retrieval.rag import RAG
from website_copilot.retrieval.registry import RAGRegistry


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
