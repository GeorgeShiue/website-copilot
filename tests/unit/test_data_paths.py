"""storage.data_paths：data/ 路徑規則（純函式，不存取檔案系統）。"""

import os

import pytest

from website_copilot.storage import data_paths


def test_paths_follow_published_layout() -> None:
    assert data_paths.aug_webpages_path("nculab") == os.path.join(
        "data", "aug_webpages", "nculab"
    )
    assert data_paths.site_data_path(
        data_paths.RAW_WEBPAGES, "nculab", "d"
    ) == os.path.join("d", "raw_webpages", "nculab")
    assert data_paths.vector_db_folder("d") == os.path.join("d", "vector_db")
    assert data_paths.vector_store_name("nculab") == "nculab.db"
    assert data_paths.vector_store_path("nculab", "d") == os.path.join(
        "d", "vector_db", "nculab.db"
    )


def test_functions_do_not_touch_filesystem(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    data_paths.vector_store_path("nculab")
    data_paths.aug_webpages_path("nculab")
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("nculab.db", "nculab"),
        ("ncu_csie.db", "ncu_csie"),
        (".staging-abc", None),
        (".hidden.db", None),
        ("nculab.db.tmp", None),
        ("nculab.db.old", None),
        ("README.md", None),
    ],
)
def test_site_id_from_vector_store_name(name: str, expected: str | None) -> None:
    assert data_paths.site_id_from_vector_store_name(name) == expected
