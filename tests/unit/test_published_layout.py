"""repo 中已發布向量庫（data/rag/{site_id}.db）的佈局檢查。

- 資料夾名稱以 .db 結尾（Milvus Lite 要求），collection 固定為 chunks。
- parquet 路徑中 site_id 只出現一次（不再重複），沒有 milvus.db 這一層。
- 設定紀錄集中在 meta/，與向量庫同版；data/rag 下沒有 publish 中間產物或舊版佈局。
"""

from pathlib import Path

import pytest

RAG_DIR = Path(__file__).resolve().parents[2] / "data" / "rag"
STORES = sorted(p for p in RAG_DIR.glob("*.db") if p.is_dir())
EXPECTED_SITES = ["claudecode", "ncucsie", "nculab"]


def test_published_sites() -> None:
    assert [p.name.removesuffix(".db") for p in STORES] == EXPECTED_SITES


def test_rag_dir_has_only_vector_stores() -> None:
    """沒有 .staging-*／.tmp／.old，也沒有舊版 data/rag/{site}/ 資料夾。"""
    assert sorted(p.name for p in RAG_DIR.iterdir()) == [
        f"{s}.db" for s in EXPECTED_SITES
    ]


@pytest.mark.parametrize("store", STORES, ids=lambda p: p.name)
def test_collection_is_chunks(store: Path) -> None:
    assert [p.name for p in (store / "collections").iterdir()] == ["chunks"]


@pytest.mark.parametrize("store", STORES, ids=lambda p: p.name)
def test_parquet_paths_do_not_repeat_site_id(store: Path) -> None:
    site_id = store.name.removesuffix(".db")
    parquets = list(store.rglob("*.parquet"))
    assert parquets
    for parquet in parquets:
        rel = parquet.relative_to(RAG_DIR)
        assert rel.parts[0] == store.name
        assert site_id not in rel.parts[1:], rel
        assert "milvus.db" not in rel.parts, rel


@pytest.mark.parametrize("store", STORES, ids=lambda p: p.name)
def test_meta_records_inside_store(store: Path) -> None:
    meta = {p.name for p in (store / "meta").iterdir()}
    assert {"module_config.yml", "site_config.yml", "run_config.yml"} <= meta
    site_id = store.name.removesuffix(".db")
    assert f"site_id: {site_id}" in (store / "meta" / "site_config.yml").read_text()
