"""ImageSummarizer：VLM 並行數、快取、下載失敗、重試、markdown 插入與統計。

下載（urlopen）與 VLM（acompletion／completion_cost）皆以 fake 取代，不連網、不產生費用。
fake 圖片內容即其 url，fake caption 為 "caption of <url>"，可由 caption 反推來源圖片。
"""

import asyncio
import base64
import threading
import time
from dataclasses import asdict
from types import SimpleNamespace
from typing import Any
from urllib.error import URLError

import pytest

from website_copilot.ingestion.augmentation import image_summarizer as module
from website_copilot.ingestion.augmentation.image_summarizer import ImageSummarizer

COST_PER_CAPTION = 0.25
DOWNLOAD_ERROR = str(URLError("connection refused"))


def _make_summarizer(
    success_threshold: float = 0.8,
    max_retries: int = 0,
    download_max_workers: int = 4,
) -> ImageSummarizer:
    return ImageSummarizer(
        download_timeout=1.0,
        download_max_workers=download_max_workers,
        success_threshold=success_threshold,
        max_retries=max_retries,
    )


class _FakeResponse:
    def __init__(self, data: bytes, content_type: str) -> None:
        self._data = data
        self.headers = {"Content-Type": content_type}

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *_exc: object) -> None:
        return None

    def read(self) -> bytes:
        return self._data


class _FakeWeb:
    """依 url 回傳圖片；failures[url] 為剩餘的下載失敗次數，content_types 可指定 Content-Type。"""

    def __init__(
        self,
        failures: dict[str, int] | None = None,
        content_types: dict[str, str] | None = None,
    ) -> None:
        self.failures = dict(failures or {})
        self.content_types = content_types or {}
        self.downloads: list[str] = []

    def urlopen(self, req: Any, timeout: float) -> _FakeResponse:
        url = req.full_url
        self.downloads.append(url)
        if self.failures.get(url, 0) > 0:
            self.failures[url] -= 1
            raise URLError("connection refused")
        return _FakeResponse(url.encode(), self.content_types.get(url, "image/png"))


class _FakeVLM:
    """caption 為 "caption of <url>"；failing 中的 url 回傳例外（summarize 失敗）。"""

    def __init__(self, failing: set[str] | None = None) -> None:
        self.failing = failing or set()
        self.calls: list[str] = []

    async def acompletion(self, *, model: str, messages: list, **_kwargs: Any) -> Any:
        data_url = messages[0]["content"][1]["image_url"]["url"]
        url = base64.standard_b64decode(data_url.split(",", 1)[1]).decode()
        self.calls.append(url)
        if url in self.failing:
            raise RuntimeError("vlm error")
        message = SimpleNamespace(content=f"caption of {url}")
        return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=None)


@pytest.fixture
def fakes(monkeypatch: pytest.MonkeyPatch):
    """安裝 fake 下載／VLM／sleep；回傳 (web, vlm, sleeps) 供測試調整與斷言。"""
    web = _FakeWeb()
    vlm = _FakeVLM()
    sleeps: list[float] = []
    monkeypatch.setattr(module, "urlopen", web.urlopen)
    monkeypatch.setattr(module, "acompletion", vlm.acompletion)
    monkeypatch.setattr(
        module, "completion_cost", lambda completion_response: COST_PER_CAPTION
    )
    monkeypatch.setattr(module.time, "sleep", sleeps.append)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    return web, vlm, sleeps


def _page(*urls: str) -> dict[str, Any]:
    markdown = "".join(f"line ![img]({url})\n" for url in urls)
    return {"fit_markdown": markdown, "images": [{"url": url} for url in urls]}


def _summarize(
    summarizer: ImageSummarizer, crawl_results: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    return summarizer.summarize_crawl_results_images(
        crawl_results,
        model="gpt-test",
        prompt="describe",
        summary_max_workers=4,
        image_source="markdown",
    )


def _stats(stats: Any) -> dict[str, Any]:
    return asdict(stats)


def _page_stats(summarizer: ImageSummarizer) -> dict[str, dict[str, Any]]:
    return {title: _stats(s) for title, s in summarizer._page_stats_by_page}


# ----- 並行數（C2） -----


@pytest.mark.parametrize(
    ("workers", "n_images", "expected_peak"),
    [(3, 10, 3), (20, 5, 5)],
)
def test_caption_concurrency_is_limited_by_summary_max_workers(
    monkeypatch: pytest.MonkeyPatch, workers: int, n_images: int, expected_peak: int
) -> None:
    summarizer = _make_summarizer()
    summarizer.summary_max_workers = workers
    in_flight = 0
    peak = 0

    async def fake_caption(_image_base64_url: str) -> tuple[str, str, float]:
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.01)
        in_flight -= 1
        return "caption", "success", 0.0

    monkeypatch.setattr(summarizer, "_agenerate_image_caption", fake_caption)
    images = {f"https://example.com/{i}.png": "data" for i in range(n_images)}

    results = asyncio.run(summarizer._agenerate_image_captions(images))

    assert peak == expected_peak
    assert len(results) == n_images


@pytest.mark.parametrize(
    ("workers", "n_images", "expected_peak"),
    [(2, 8, 2), (20, 5, 5)],
)
def test_download_concurrency_is_limited_by_download_max_workers(
    monkeypatch: pytest.MonkeyPatch, workers: int, n_images: int, expected_peak: int
) -> None:
    summarizer = _make_summarizer(download_max_workers=workers)
    lock = threading.Lock()
    in_flight = 0
    peak = 0

    def fake_download(_url: str) -> str:
        nonlocal in_flight, peak
        with lock:
            in_flight += 1
            peak = max(peak, in_flight)
        time.sleep(0.05)
        with lock:
            in_flight -= 1
        return "data:image/png;base64,AA=="

    monkeypatch.setattr(summarizer, "_download_image", fake_download)

    summarizer._download_images(
        [f"https://example.com/{i}.png" for i in range(n_images)]
    )

    assert peak == expected_peak


def test_download_and_summary_concurrency_are_independent(
    fakes, monkeypatch: pytest.MonkeyPatch
) -> None:
    """下載 2 條、摘要 5 條：兩個上限各自生效，互不影響。"""
    web, vlm, _ = fakes
    lock = threading.Lock()
    counters = {"download": 0, "download_peak": 0, "summary": 0, "summary_peak": 0}
    real_urlopen, real_acompletion = web.urlopen, vlm.acompletion

    def slow_urlopen(req: Any, timeout: float) -> Any:
        with lock:
            counters["download"] += 1
            counters["download_peak"] = max(
                counters["download_peak"], counters["download"]
            )
        threading.Event().wait(0.05)  # fakes 已把 time.sleep 換成 no-op
        with lock:
            counters["download"] -= 1
        return real_urlopen(req, timeout)

    async def slow_acompletion(**kwargs: Any) -> Any:
        counters["summary"] += 1
        counters["summary_peak"] = max(counters["summary_peak"], counters["summary"])
        await asyncio.sleep(0.05)
        counters["summary"] -= 1
        return await real_acompletion(**kwargs)

    monkeypatch.setattr(module, "urlopen", slow_urlopen)
    monkeypatch.setattr(module, "acompletion", slow_acompletion)

    summarizer = _make_summarizer(download_max_workers=2)
    urls = [f"https://ex.com/{i}.png" for i in range(10)]
    summarizer.summarize_crawl_results_images(
        {"page": _page(*urls)},
        model="gpt-test",
        prompt="describe",
        summary_max_workers=5,
        image_source="markdown",
    )

    assert counters["download_peak"] == 2
    assert counters["summary_peak"] == 5


# ----- 快取 -----


def test_same_image_on_multiple_pages_is_downloaded_and_captioned_once(fakes) -> None:
    web, vlm, _ = fakes
    shared, own = "https://ex.com/logo.png", "https://ex.com/a.png"
    crawl_results = {"page1": _page(shared, own), "page2": _page(shared)}

    results = _summarize(_make_summarizer(), crawl_results)

    assert web.downloads.count(shared) == 1
    assert vlm.calls.count(shared) == 1
    assert f"caption of {shared}" in results["page2"]["enhanced_markdown"]
    assert results["page2"]["images"][0]["caption"] == f"caption of {shared}"


# ----- 下載失敗 -----


def test_download_failure_is_not_sent_to_vlm(fakes) -> None:
    web, vlm, _ = fakes
    bad, good = "https://ex.com/bad.png", "https://ex.com/good.png"
    web.failures[bad] = 99

    summarizer = _make_summarizer()
    results = _summarize(summarizer, {"page": _page(bad, good)})

    assert bad not in vlm.calls
    assert results["page"]["images"][0]["caption"] == ""
    assert results["page"]["images"][1]["caption"] == f"caption of {good}"
    assert summarizer._failed_images == {bad: ("page", DOWNLOAD_ERROR)}


def test_unsupported_content_type_counts_as_download_failure(fakes) -> None:
    web, vlm, _ = fakes
    svg = "https://ex.com/icon"
    web.content_types[svg] = "image/svg+xml; charset=utf-8"

    summarizer = _make_summarizer()
    _summarize(summarizer, {"page": _page(svg)})

    assert vlm.calls == []
    assert summarizer._failed_images == {
        svg: ("page", "unsupported content-type image/svg+xml")
    }


def test_unsupported_suffix_is_skipped_without_download(fakes) -> None:
    web, _, _ = fakes
    crawl_results = {"page": _page("https://ex.com/icon.svg")}

    results = _summarize(_make_summarizer(), crawl_results)

    assert web.downloads == []
    assert results["page"]["enhanced_markdown"] == crawl_results["page"]["fit_markdown"]


def test_summarize_failure_is_recorded(fakes) -> None:
    _, vlm, _ = fakes
    url = "https://ex.com/a.png"
    vlm.failing.add(url)

    summarizer = _make_summarizer()
    results = _summarize(summarizer, {"page": _page(url)})

    assert results["page"]["images"][0]["caption"] == ""
    assert summarizer._failed_images == {url: ("page", "caption generation failed")}


# ----- 重試 -----


def test_retry_redoes_only_failed_images(fakes) -> None:
    web, vlm, sleeps = fakes
    flaky, good = "https://ex.com/flaky.png", "https://ex.com/good.png"
    other = "https://ex.com/other.png"
    web.failures[flaky] = 1  # 第一輪下載失敗，重試成功
    crawl_results = {"page1": _page(flaky, good), "page2": _page(other)}

    summarizer = _make_summarizer(success_threshold=0.8, max_retries=3)
    results = _summarize(summarizer, crawl_results)

    assert len(sleeps) == 1
    assert web.downloads.count(flaky) == 2
    assert web.downloads.count(good) == 1  # 第一輪已成功，重試時沿用快取
    assert web.downloads.count(other) == 1  # 不含失敗圖片的頁面不重做
    assert vlm.calls.count(good) == 1
    assert summarizer._failed_images == {}
    assert f"caption of {flaky}" in results["page1"]["enhanced_markdown"]
    assert results["page1"]["images"][0]["caption"] == f"caption of {flaky}"
    assert _stats(summarizer._all_round_stats) == {
        "cost_usd": 3 * COST_PER_CAPTION,
        "success": 3,
        "failure": 1,
        "retries": 2,
    }
    # 重試輪只處理 page1：good 沿用快取（cache_reuse），flaky 這次成功
    assert _page_stats(summarizer) == {
        "page1": {
            "cost_usd": COST_PER_CAPTION,
            "success": 1,
            "download_failure": 0,
            "summarize_failure": 0,
            "cache_reuse": 1,
        }
    }


def test_no_retry_when_success_rate_meets_threshold(fakes) -> None:
    web, _, sleeps = fakes
    bad = "https://ex.com/bad.png"
    web.failures[bad] = 99
    urls = [bad] + [f"https://ex.com/{i}.png" for i in range(4)]  # 成功率 0.8

    summarizer = _make_summarizer(success_threshold=0.8, max_retries=3)
    _summarize(summarizer, {"page": _page(*urls)})

    assert sleeps == []
    assert web.downloads.count(bad) == 1


def test_retry_stops_at_max_retries(fakes) -> None:
    web, _, sleeps = fakes
    bad = "https://ex.com/bad.png"
    web.failures[bad] = 99

    summarizer = _make_summarizer(success_threshold=0.8, max_retries=2)
    _summarize(summarizer, {"page": _page(bad)})

    assert len(sleeps) == 1
    assert web.downloads.count(bad) == 2
    assert summarizer._failed_images == {bad: ("page", DOWNLOAD_ERROR)}
    assert _stats(summarizer._all_round_stats)["retries"] == 2


# ----- markdown 插入與統計 -----


def test_enhanced_markdown_inserts_numbered_captions(fakes) -> None:
    web, _, _ = fakes
    a, b, bad = "https://ex.com/a.png", "https://ex.com/b.png", "https://ex.com/x.png"
    web.failures[bad] = 99
    page = {
        "fit_markdown": f"# Title\n![a]({a}) ![b]({b})\ntext\n![x]({bad})\n\n",
        "images": [],
    }

    results = _summarize(_make_summarizer(), {"page": page})

    assert results["page"]["enhanced_markdown"] == (
        "# Title\n"
        f"![a]({a}) ![b]({b})\n"
        f"> # Image-1\n>\n> caption of {a}\n"
        f"> # Image-2\n>\n> caption of {b}\n"
        "text\n"
        f"![x]({bad})"
    )


def test_page_stats(fakes) -> None:
    web, vlm, _ = fakes
    shared, bad, broken = (
        "https://ex.com/logo.png",
        "https://ex.com/bad.png",
        "https://ex.com/broken.png",
    )
    web.failures[bad] = 99
    vlm.failing.add(broken)
    crawl_results = {"page1": _page(shared, bad, broken), "page2": _page(shared)}

    summarizer = _make_summarizer()
    _summarize(summarizer, crawl_results)

    assert _page_stats(summarizer) == {
        "page1": {
            "cost_usd": COST_PER_CAPTION,
            "success": 1,
            "download_failure": 1,
            "summarize_failure": 1,
            "cache_reuse": 0,
        },
        "page2": {
            "cost_usd": 0.0,
            "success": 0,
            "download_failure": 0,
            "summarize_failure": 0,
            "cache_reuse": 1,
        },
    }
    assert _stats(summarizer._all_round_stats) == {
        "cost_usd": COST_PER_CAPTION,
        "success": 1,
        "failure": 2,
        "retries": 1,
    }
