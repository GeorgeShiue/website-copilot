"""Augmentation 基準快照測試：重構（P1b、P1c）前後輸出必須逐字一致。

輸入為 nculab 真實爬取結果（tests/fixtures/augmentation_snapshot/input.json，47 頁、74 個圖片
引用）加上少量注入的圖片（跨頁共用、下載失敗、格式不符、svg），使快照涵蓋：
下載失敗、Content-Type 不符、svg 略過、跨頁快取、VLM 失敗、整輪重試（time.sleep 以 fake 取代）。

下載與 VLM 皆以確定性 fake 取代，不連網、不產生費用。fake 的行為由 URL 的 sha1 決定
（見 _behavior），與實作無關，因此重構時只需替換 fake 掛入的位置，期望值不變
（P1a 以 urlopen 的 fake 建立基準，P1c 起改為下載器 fake，期望值未更動）。

P1d 起 fake 下載回傳真實的 PNG（指定尺寸、可共用內容），使尺寸門檻（長邊 < 100px 略過）與
內容去重（sha1 相同只描述一次）可在快照中觸發；快照差異經審查後更新（見 verification.md）。
圖片內容 = URL、caption = "caption of <url>"。

更新快照（僅限有意的輸出變更，如 P1d）：UPDATE_SNAPSHOT=1 pytest tests/unit/test_augmentation_snapshot.py
"""

import base64
import copy
import hashlib
import json
import os
import shutil
from collections.abc import Callable, Iterable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from augmentation_fakes import failed_result, image_key, ok_result, png_bytes

from website_copilot.ingestion.augmentation import augmenter as augmenter_module
from website_copilot.ingestion.augmentation.augmenter import Augmenter
from website_copilot.ingestion.augmentation.processors import (
    image_captioner as captioner_module,
)
from website_copilot.storage.run_persistence import save_results_as_md
from website_copilot.utils.http_downloader import DownloadResult

FIXTURE_DIR = Path("tests/fixtures/augmentation_snapshot")
INPUT_PATH = FIXTURE_DIR / "input.json"
EXPECTED_JSON = FIXTURE_DIR / "expected" / "results.json"
EXPECTED_MD_DIR = FIXTURE_DIR / "expected" / "results"

INJECTED = "https://example.com/injected"
# 注入圖片的固定行為（其餘圖片由 sha1 決定）
FORCED_BEHAVIORS = {
    f"{INJECTED}/shared.png": "ok",
    f"{INJECTED}/gone.png": "not_found",
    f"{INJECTED}/page.png": "wrong_type",
}


MIN_SIZE = 100


def _image_spec(url: str) -> tuple[int, int, str]:
    """URL → 圖片 (寬, 高, 內容 key)：小圖、剛好等於門檻、內容相同（共用 key）、一般。

    同 key 的 PNG 位元組完全相同（內容 sha1 相同）；fake VLM 以 key 產生描述。
    """
    if url in FORCED_BEHAVIORS:
        return 300, 200, url
    bucket = int(hashlib.sha1(url.encode()).hexdigest()[8:16], 16) % 100
    if bucket < 15:  # 小圖：長邊 1、16、99
        edge = (1, 16, 99)[bucket % 3]
        return edge, max(edge // 2, 1), url
    if bucket < 20:  # 長邊剛好等於門檻：不略過
        return MIN_SIZE, 40, url
    if bucket < 35:  # 內容相同、URL 不同
        return 300, 200, f"shared-content-{bucket % 4}"
    return 300, 200, url


def _behavior(url: str) -> str:
    """URL → fake 行為：404、Content-Type 不符、首次下載逾時（重試後成功）、VLM 失敗、正常。"""
    if url in FORCED_BEHAVIORS:
        return FORCED_BEHAVIORS[url]
    bucket = int(hashlib.sha1(url.encode()).hexdigest()[:8], 16) % 100
    if bucket < 10:
        return "not_found"
    if bucket < 15:
        return "wrong_type"
    if bucket < 45:
        return "flaky"
    if bucket < 52:
        return "vlm_failure"
    return "ok"


def _load_input() -> dict[str, dict[str, Any]]:
    """讀取 fixture 並注入圖片（附加在頁面最後，不影響原有圖片順序）。"""
    results: dict[str, dict[str, Any]] = json.loads(INPUT_PATH.read_text("utf-8"))
    keys = sorted(results)

    def append(key: str, url: str) -> None:
        page = results[key]
        page["fit_markdown"] = page["fit_markdown"].rstrip("\n") + f"\n\n![x]({url})\n"
        page["images"].append({"url": url})

    for key in (keys[0], keys[5], keys[10]):  # 跨頁共用：成功／404 各三頁
        append(key, f"{INJECTED}/shared.png")
        append(key, f"{INJECTED}/gone.png")
    append(keys[15], f"{INJECTED}/page.png")
    append(keys[20], f"{INJECTED}/icon.svg")  # 排在最後，不影響描述對位
    return results


class _SnapshotDownloader:
    """依 _behavior 回傳結果的 fake 下載器（取代 HttpDownloader）。"""

    def __init__(self) -> None:
        self.flaky_seen: set[str] = set()

    def download(
        self,
        urls: Iterable[str],
        on_complete: Callable[[DownloadResult], None] | None = None,
    ) -> dict[str, DownloadResult]:
        results: dict[str, DownloadResult] = {}
        for url in dict.fromkeys(urls):
            results[url] = self._download_one(url)
            if on_complete is not None:
                on_complete(results[url])
        return results

    def _download_one(self, url: str) -> DownloadResult:
        behavior = _behavior(url)
        if behavior == "not_found":
            return failed_result(url, "HTTP 404", 404)
        if behavior == "flaky" and url not in self.flaky_seen:
            self.flaky_seen.add(url)
            return failed_result(url, "timeout")
        width, height, key = _image_spec(url)
        content_type = "text/html" if behavior == "wrong_type" else "image/png"
        return ok_result(url, content_type, png_bytes(width, height, key))


async def _fake_acompletion(*, model: str, messages: list, **_kwargs: Any) -> Any:
    data_url = messages[0]["content"][1]["image_url"]["url"]
    key = image_key(base64.standard_b64decode(data_url.split(",", 1)[1]))
    if _behavior(key) == "vlm_failure":
        raise RuntimeError("vlm error")
    message = SimpleNamespace(content=f"caption of {key}")
    return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=None)


@pytest.fixture
def fakes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(captioner_module, "acompletion", _fake_acompletion)
    monkeypatch.setattr(
        captioner_module, "completion_cost", lambda completion_response: 0.25
    )
    monkeypatch.setattr(augmenter_module.time, "sleep", lambda _seconds: None)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")


def _run() -> dict[str, dict[str, Any]]:
    augmenter = Augmenter(
        downloader=_SnapshotDownloader(), success_threshold=0.8, max_retries=3
    )
    return augmenter.augment(
        _load_input(),
        model="gpt-test",
        prompt="describe",
        image_max_concurrency=8,
        image_source="markdown",
        image_min_size=MIN_SIZE,
    )


def _dump(results: dict[str, dict[str, Any]]) -> str:
    """與 RunManager.save_results_as_json 相同的序列化。"""
    return json.dumps(results, ensure_ascii=False, indent=4)


def _write_snapshot(results: dict[str, dict[str, Any]]) -> None:
    EXPECTED_JSON.parent.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(EXPECTED_MD_DIR, ignore_errors=True)
    EXPECTED_MD_DIR.mkdir(parents=True)
    EXPECTED_JSON.write_text(_dump(results), encoding="utf-8")
    save_results_as_md(results, str(EXPECTED_MD_DIR), "enhanced_markdown")


def test_snapshot_matches_baseline(fakes: None, tmp_path: Path) -> None:
    results = _run()

    if os.environ.get("UPDATE_SNAPSHOT"):
        _write_snapshot(results)

    assert _dump(results) == EXPECTED_JSON.read_text(encoding="utf-8")

    actual_md_dir = tmp_path / "results"
    actual_md_dir.mkdir()
    save_results_as_md(results, str(actual_md_dir), "enhanced_markdown")
    expected_names = sorted(p.name for p in EXPECTED_MD_DIR.glob("*.md"))
    assert sorted(p.name for p in actual_md_dir.glob("*.md")) == expected_names
    for name in expected_names:
        assert (actual_md_dir / name).read_text("utf-8") == (
            EXPECTED_MD_DIR / name
        ).read_text("utf-8"), name


def test_snapshot_is_deterministic(fakes: None) -> None:
    assert _dump(_run()) == _dump(_run())


def test_snapshot_covers_expected_scenarios(fakes: None) -> None:
    """快照本身須涵蓋各情境，否則逐字一致無法證明這些行為不變。"""
    results = _run()
    markdown = {k: v["enhanced_markdown"] for k, v in results.items()}
    captioned = {
        image["url"]: image["caption"]
        for page in results.values()
        for image in page["images"]
        if image.get("caption")
    }
    behaviors = {
        url: _behavior(url)
        for page in _load_input().values()
        for url in (image["url"] for image in page["images"])
    }

    assert {"not_found", "wrong_type", "flaky", "vlm_failure", "ok"} <= set(
        behaviors.values()
    )
    # 下載成功、長邊 >= 門檻、VLM 未失敗（以內容 key 判斷）的圖片有描述；其餘沒有
    small = set()
    for url, behavior in behaviors.items():
        if url.endswith(".svg"):
            continue
        width, height, key = _image_spec(url)
        if behavior in ("ok", "flaky", "vlm_failure") and max(width, height) < MIN_SIZE:
            small.add(url)
        expected = (
            behavior in ("ok", "flaky", "vlm_failure")
            and max(width, height) >= MIN_SIZE
            and _behavior(key) != "vlm_failure"
        )
        assert (url in captioned) == expected, (url, behavior, key)
    # 兩項過濾都在快照中被觸發：小圖略過、內容相同的不同 URL 共用同一段描述
    assert small
    shared = [u for u in captioned if _image_spec(u)[2].startswith("shared-content-")]
    assert len(shared) >= 2
    assert len({captioned[u] for u in shared}) < len(shared)
    # svg 略過：沒有描述、markdown 不變
    assert f"{INJECTED}/icon.svg" not in captioned
    # 跨頁共用的圖片在三頁都有描述插入
    shared_caption = f"caption of {INJECTED}/shared.png"
    assert sum(shared_caption in md for md in markdown.values()) == 3
    # 沒有圖片的頁面 enhanced_markdown 等於 fit_markdown
    original = _load_input()
    plain = [k for k, v in original.items() if not v["images"]]
    assert plain
    for key in plain:
        assert markdown[key] == original[key]["fit_markdown"]


def test_input_fixture_untouched_by_run(fakes: None) -> None:
    before = copy.deepcopy(json.loads(INPUT_PATH.read_text("utf-8")))
    _run()
    assert json.loads(INPUT_PATH.read_text("utf-8")) == before
