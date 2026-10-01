"""run_persistence 的最新結果搜尋：只搜尋指定站點，找不到時不退回其他站點（S7）。"""

import json
from pathlib import Path

import pytest

from website_copilot.storage.run_persistence import load_latest_results


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
