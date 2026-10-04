"""run_persistence 的最新結果／run path 搜尋：只搜尋指定站點，找不到時不退回其他站點（S7）。"""

import json
from pathlib import Path

import pytest

from website_copilot.storage.run_persistence import (
    is_run_folder,
    load_latest_results,
    load_latest_run_path,
)


def _write_results(runs: Path, ts: str, site: str, marker: str) -> None:
    run_path = runs / ts / "website_crawler" / site / "r"
    run_path.mkdir(parents=True)
    (run_path / "results.json").write_text(json.dumps({"marker": marker}))


def test_load_latest_results_of_same_site(tmp_path: Path) -> None:
    _write_results(tmp_path, "20260929_090000", "nculab", "old")
    _write_results(tmp_path, "20260929_100000", "nculab", "new")
    _write_results(
        tmp_path, "20260929_110000", "ncucsie", "other site"
    )  # 較新但不同站點

    results = load_latest_results(str(tmp_path), "website_crawler", site_id="nculab")

    assert results == {"marker": "new"}


def test_load_latest_results_does_not_fall_back_to_other_site(tmp_path: Path) -> None:
    _write_results(tmp_path, "20260929_110000", "ncucsie", "other site")

    with pytest.raises(FileNotFoundError, match="site 'nculab'"):
        load_latest_results(str(tmp_path), "website_crawler", site_id="nculab")


def test_load_latest_results_skips_newer_run_without_results_json(
    tmp_path: Path,
) -> None:
    """較新的 run 資料夾有該站點但沒有 results.json（失敗的 run）→ 用較舊的完整結果。"""
    _write_results(tmp_path, "20260929_090000", "nculab", "complete")
    (tmp_path / "20260929_100000" / "website_crawler" / "nculab" / "r").mkdir(
        parents=True
    )

    results = load_latest_results(str(tmp_path), "website_crawler", site_id="nculab")

    assert results == {"marker": "complete"}


def test_load_latest_results_ignores_non_run_folders(tmp_path: Path) -> None:
    _write_results(tmp_path, "20260929_090000", "nculab", "run")
    _write_results(tmp_path, "latest", "nculab", "not a run folder")

    results = load_latest_results(str(tmp_path), "website_crawler", site_id="nculab")

    assert results == {"marker": "run"}


def test_load_latest_results_without_run_folders(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="No run folders"):
        load_latest_results(str(tmp_path), "website_crawler", site_id="nculab")


def _make_results_folder(runs: Path, ts: str, site: str, module: str) -> Path:
    run_path = runs / ts / module / site / "r"
    (run_path / "results").mkdir(parents=True)
    return run_path


def test_load_latest_run_path_of_same_site(tmp_path: Path) -> None:
    _make_results_folder(tmp_path, "20260929_090000", "nculab", "augmenter")
    newest = _make_results_folder(tmp_path, "20260929_100000", "nculab", "augmenter")
    _make_results_folder(tmp_path, "20260929_110000", "ncucsie", "augmenter")
    _make_results_folder(tmp_path, "20260929_120000", "nculab", "website_crawler")

    path = load_latest_run_path(str(tmp_path), "augmenter", site_id="nculab")

    assert path == str(newest)


def test_load_latest_run_path_skips_newer_run_without_results_folder(
    tmp_path: Path,
) -> None:
    complete = _make_results_folder(tmp_path, "20260929_090000", "nculab", "augmenter")
    (tmp_path / "20260929_100000" / "augmenter" / "nculab" / "r").mkdir(parents=True)

    path = load_latest_run_path(str(tmp_path), "augmenter", site_id="nculab")

    assert path == str(complete)


def test_load_latest_run_path_does_not_fall_back_to_other_site(
    tmp_path: Path,
) -> None:
    _make_results_folder(tmp_path, "20260929_110000", "ncucsie", "augmenter")

    with pytest.raises(FileNotFoundError, match="augmenter run path"):
        load_latest_run_path(str(tmp_path), "augmenter", site_id="nculab")


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("20260830_172330", True),
        ("2026083_172330", False),
        ("19990830_172330", False),
        ("latest", False),
    ],
)
def test_is_run_folder(name: str, expected: bool) -> None:
    assert is_run_folder(name) is expected
