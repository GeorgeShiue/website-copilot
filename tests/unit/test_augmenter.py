"""Augmenter（圖片）：並行數、快取與跨頁去重、下載失敗、可恢復／永久錯誤與重試、markdown 插入與統計。

下載（FakeDownloader／httpx.MockTransport）與 VLM（acompletion／completion_cost）皆以 fake 取代，
不連網、不產生費用。fake 圖片內容即其 url，fake caption 為 "caption of <url>"。
"""

import asyncio
from dataclasses import asdict
from typing import Any

import httpx
import pytest
from augmentation_fakes import (
    COST_PER_CAPTION,
    FakeDownloader,
    FakeVLM,
    failed_result,
    png_bytes,
)

from website_copilot.ingestion.augmentation import augmenter as augmenter_module
from website_copilot.ingestion.augmentation.augmenter import Augmenter, Downloader
from website_copilot.ingestion.augmentation.processors import (
    image_captioner as captioner_module,
)
from website_copilot.ingestion.augmentation.processors.image_captioner import (
    ImageCaptioner,
)
from website_copilot.utils.http_downloader import HttpDownloader

CONNECTION_ERROR = "connection error: refused"


def _make_augmenter(
    downloader: Downloader,
    success_threshold: float = 0.8,
    max_retries: int = 0,
) -> Augmenter:
    return Augmenter(
        downloader=downloader,
        success_threshold=success_threshold,
        max_retries=max_retries,
    )


@pytest.fixture
def fakes(monkeypatch: pytest.MonkeyPatch):
    """安裝 fake 下載器／VLM／sleep；回傳 (web, vlm, sleeps) 供測試調整與斷言。"""
    web = FakeDownloader()
    vlm = FakeVLM()
    sleeps: list[float] = []
    monkeypatch.setattr(captioner_module, "acompletion", vlm.acompletion)
    monkeypatch.setattr(
        captioner_module,
        "completion_cost",
        lambda completion_response: COST_PER_CAPTION,
    )
    monkeypatch.setattr(augmenter_module.time, "sleep", sleeps.append)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    return web, vlm, sleeps


def _page(*urls: str) -> dict[str, Any]:
    markdown = "".join(f"line ![img]({url})\n" for url in urls)
    return {"fit_markdown": markdown, "images": [{"url": url} for url in urls]}


def _augment(
    augmenter: Augmenter,
    crawl_results: dict[str, dict[str, Any]],
    image_max_concurrency: int = 4,
    image_min_size: int = 100,
) -> dict[str, dict[str, Any]]:
    return augmenter.augment(
        crawl_results,
        model="gpt-test",
        prompt="describe",
        image_max_concurrency=image_max_concurrency,
        image_source="markdown",
        image_min_size=image_min_size,
    )


def _stats(stats: Any) -> dict[str, Any]:
    return asdict(stats)


def _page_stats(augmenter: Augmenter) -> dict[str, dict[str, Any]]:
    return {title: _stats(s) for title, s in augmenter._page_stats_by_page}


# ----- 並行數 -----


@pytest.mark.parametrize(
    ("workers", "n_images", "expected_peak"),
    [(3, 10, 3), (20, 5, 5)],
)
def test_caption_concurrency_is_limited_by_max_concurrency(
    monkeypatch: pytest.MonkeyPatch,
    fakes,
    workers: int,
    n_images: int,
    expected_peak: int,
) -> None:
    captioner = ImageCaptioner(
        model="gpt-test", prompt="describe", max_concurrency=workers
    )
    in_flight = 0
    peak = 0

    async def fake_caption(_image_base64_url: str) -> tuple[str, str, float]:
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.01)
        in_flight -= 1
        return "caption", "success", 0.0

    monkeypatch.setattr(captioner, "_agenerate_image_caption", fake_caption)
    images = {f"https://example.com/{i}.png": "data" for i in range(n_images)}

    results = asyncio.run(captioner._agenerate_image_captions(images))

    assert peak == expected_peak
    assert len(results) == n_images


class _ConcurrencyProbe:
    """MockTransport handler：記錄同時進行的請求數。"""

    def __init__(self) -> None:
        self.in_flight = 0
        self.peak = 0

    async def __call__(self, request: httpx.Request) -> httpx.Response:
        self.in_flight += 1
        self.peak = max(self.peak, self.in_flight)
        await asyncio.sleep(0.02)
        self.in_flight -= 1
        return httpx.Response(
            200,
            content=str(request.url).encode(),
            headers={"Content-Type": "image/png"},
        )


@pytest.mark.parametrize(
    ("limit", "n_pages", "expected_peak"),
    [(3, 6, 3), (50, 4, 8)],
)
def test_download_concurrency_is_shared_across_pages(
    fakes, limit: int, n_pages: int, expected_peak: int
) -> None:
    """上限對整批下載生效：跨頁的圖片共用同一個上限（原本每頁各自計算）。"""
    probe = _ConcurrencyProbe()
    downloader = HttpDownloader(
        max_concurrency=limit,
        timeout=1.0,
        max_retries=0,
        max_bytes=None,
        transport=httpx.MockTransport(probe),
    )
    crawl_results = {
        f"page{p}": _page(*(f"https://ex.com/{p}-{i}.png" for i in range(2)))
        for p in range(n_pages)
    }

    results = _augment(_make_augmenter(downloader), crawl_results)

    assert probe.peak == expected_peak
    assert all(page["images"][0]["caption"] for page in results.values())


def test_download_and_caption_concurrency_are_independent_and_shared_across_pages(
    fakes, monkeypatch: pytest.MonkeyPatch
) -> None:
    """下載 2 條、摘要 5 條：兩個上限各自生效、跨頁共用，互不影響。"""
    _, vlm, _ = fakes
    probe = _ConcurrencyProbe()
    downloader = HttpDownloader(
        max_concurrency=2,
        timeout=1.0,
        max_retries=0,
        max_bytes=None,
        transport=httpx.MockTransport(probe),
    )
    summary = {"in_flight": 0, "peak": 0}
    real_acompletion = vlm.acompletion

    async def slow_acompletion(**kwargs: Any) -> Any:
        summary["in_flight"] += 1
        summary["peak"] = max(summary["peak"], summary["in_flight"])
        await asyncio.sleep(0.05)
        summary["in_flight"] -= 1
        return await real_acompletion(**kwargs)

    monkeypatch.setattr(captioner_module, "acompletion", slow_acompletion)
    crawl_results = {
        f"page{p}": _page(*(f"https://ex.com/{p}-{i}.png" for i in range(5)))
        for p in range(4)
    }

    _augment(_make_augmenter(downloader), crawl_results, image_max_concurrency=5)

    assert probe.peak == 2
    assert summary["peak"] == 5


# ----- 快取 -----


def test_same_image_on_multiple_pages_is_downloaded_and_captioned_once(fakes) -> None:
    web, vlm, _ = fakes
    shared, own = "https://ex.com/logo.png", "https://ex.com/a.png"
    crawl_results = {"page1": _page(shared, own), "page2": _page(shared)}

    results = _augment(_make_augmenter(web), crawl_results)

    assert web.downloads.count(shared) == 1
    assert vlm.calls.count(shared) == 1
    assert f"caption of {shared}" in results["page2"]["enhanced_markdown"]
    assert results["page2"]["images"][0]["caption"] == f"caption of {shared}"


def test_duplicate_url_within_page_is_downloaded_and_captioned_once(fakes) -> None:
    web, vlm, _ = fakes
    url = "https://ex.com/a.png"

    results = _augment(_make_augmenter(web), {"page": _page(url, url)})

    assert web.downloads == [url]
    assert vlm.calls == [url]
    assert results["page"]["enhanced_markdown"].count(f"caption of {url}") == 2


# ----- 下載失敗 -----


def test_download_failure_is_not_sent_to_vlm(fakes) -> None:
    web, vlm, _ = fakes
    bad, good = "https://ex.com/bad.png", "https://ex.com/good.png"
    web.failures[bad] = 99

    augmenter = _make_augmenter(web)
    results = _augment(augmenter, {"page": _page(bad, good)})

    assert bad not in vlm.calls
    assert results["page"]["images"][0]["caption"] == ""
    assert results["page"]["images"][1]["caption"] == f"caption of {good}"
    assert augmenter._failed_images == {bad: ("page", CONNECTION_ERROR)}


def test_unsupported_content_type_counts_as_download_failure(fakes) -> None:
    web, vlm, _ = fakes
    svg = "https://ex.com/icon"
    web.content_types[svg] = "image/svg+xml; charset=utf-8"

    augmenter = _make_augmenter(web)
    _augment(augmenter, {"page": _page(svg)})

    assert vlm.calls == []
    assert augmenter._failed_images == {
        svg: ("page", "unsupported content-type image/svg+xml")
    }


def test_unsupported_suffix_is_skipped_without_download(fakes) -> None:
    web, _, _ = fakes
    crawl_results = {"page": _page("https://ex.com/icon.svg")}

    results = _augment(_make_augmenter(web), crawl_results)

    assert web.downloads == []
    assert results["page"]["enhanced_markdown"] == crawl_results["page"]["fit_markdown"]


def test_summarize_failure_is_recorded(fakes) -> None:
    _, vlm, _ = fakes
    web = FakeDownloader()
    url = "https://ex.com/a.png"
    vlm.failing.add(url)

    augmenter = _make_augmenter(web)
    results = _augment(augmenter, {"page": _page(url)})

    assert results["page"]["images"][0]["caption"] == ""
    assert augmenter._failed_images == {url: ("page", "caption generation failed")}


def test_failed_resource_on_many_pages_is_downloaded_and_counted_once(fakes) -> None:
    """失敗資源跨多頁出現：只下載一次、只計一次失敗（記在第一個引用頁面，其餘為 cache_reuse）。"""
    web, _vlm, _ = fakes
    bad = "https://ex.com/bad.png"
    web.failures[bad] = 99
    crawl_results = {f"page{i}": _page(bad) for i in range(3)}

    augmenter = _make_augmenter(web)
    _augment(augmenter, crawl_results)

    assert web.downloads == [bad]
    assert augmenter._failed_images == {bad: ("page0", CONNECTION_ERROR)}
    stats = _page_stats(augmenter)
    assert [s["download_failure"] for s in stats.values()] == [1, 0, 0]
    assert [s["cache_reuse"] for s in stats.values()] == [0, 1, 1]
    assert _stats(augmenter._all_round_stats)["failure"] == 1


# ----- 重試 -----


def test_retry_redoes_only_failed_images(fakes) -> None:
    web, vlm, sleeps = fakes
    flaky, good = "https://ex.com/flaky.png", "https://ex.com/good.png"
    other = "https://ex.com/other.png"
    web.failures[flaky] = 1  # 第一輪下載失敗，重試成功
    crawl_results = {"page1": _page(flaky, good), "page2": _page(other)}

    augmenter = _make_augmenter(web, success_threshold=0.8, max_retries=3)
    results = _augment(augmenter, crawl_results)

    assert len(sleeps) == 1
    assert web.downloads.count(flaky) == 2
    assert web.downloads.count(good) == 1  # 第一輪已成功，重試時沿用快取
    assert web.downloads.count(other) == 1  # 不含失敗圖片的頁面不重做
    assert vlm.calls.count(good) == 1
    assert augmenter._failed_images == {}
    assert f"caption of {flaky}" in results["page1"]["enhanced_markdown"]
    assert results["page1"]["images"][0]["caption"] == f"caption of {flaky}"
    assert _stats(augmenter._all_round_stats) == {
        "cost_usd": 3 * COST_PER_CAPTION,
        "success": 3,
        "failure": 1,
        "retries": 2,
    }
    # 重試輪只處理 page1：good 沿用快取（cache_reuse），flaky 這次成功
    assert _page_stats(augmenter) == {
        "page1": {
            "cost_usd": COST_PER_CAPTION,
            "success": 1,
            "download_failure": 0,
            "summarize_failure": 0,
            "skipped": 0,
            "cache_reuse": 1,
        }
    }


def test_no_retry_when_success_rate_meets_threshold(fakes) -> None:
    web, _, sleeps = fakes
    bad = "https://ex.com/bad.png"
    web.failures[bad] = 99
    urls = [bad] + [f"https://ex.com/{i}.png" for i in range(4)]  # 成功率 0.8

    augmenter = _make_augmenter(web, success_threshold=0.8, max_retries=3)
    _augment(augmenter, {"page": _page(*urls)})

    assert sleeps == []
    assert web.downloads.count(bad) == 1


def test_retry_stops_at_max_retries(fakes) -> None:
    web, _, sleeps = fakes
    bad = "https://ex.com/bad.png"
    web.failures[bad] = 99

    augmenter = _make_augmenter(web, success_threshold=0.8, max_retries=2)
    _augment(augmenter, {"page": _page(bad)})

    assert len(sleeps) == 1
    assert web.downloads.count(bad) == 2
    assert augmenter._failed_images == {bad: ("page", CONNECTION_ERROR)}
    assert _stats(augmenter._all_round_stats)["retries"] == 2


def test_success_rate_counts_unique_resources(fakes) -> None:
    """壞圖跨多頁重複出現不會把成功率拉低：4 張好圖 + 1 張壞圖（出現在 5 頁）= 80%，不重試。"""
    web, _, sleeps = fakes
    bad = "https://ex.com/bad.png"
    web.failures[bad] = 99
    crawl_results = {f"bad{i}": _page(bad) for i in range(5)}
    crawl_results["good"] = _page(*(f"https://ex.com/{i}.png" for i in range(4)))

    _augment(_make_augmenter(web, success_threshold=0.8, max_retries=3), crawl_results)

    assert sleeps == []
    assert web.downloads.count(bad) == 1


@pytest.mark.parametrize(
    ("error", "status"),
    [
        ("HTTP 404", 404),
        ("HTTP 410", 410),
        ("HTTP 400", 400),
        ("exceeds max_bytes", 200),
        ("invalid url: x", None),
    ],
)
def test_permanent_download_errors_are_not_retried(
    fakes, error: str, status: int | None
) -> None:
    web, _, sleeps = fakes
    bad = "https://ex.com/bad.png"
    web.failures[bad] = 99
    web.errors[bad] = (error, status)

    augmenter = _make_augmenter(web, success_threshold=0.8, max_retries=5)
    _augment(augmenter, {"page": _page(bad, "https://ex.com/good.png")})

    assert sleeps == []
    assert web.downloads.count(bad) == 1
    assert augmenter._failed_images == {bad: ("page", error)}


def test_unsupported_content_type_is_not_retried(fakes) -> None:
    web, vlm, sleeps = fakes
    html = "https://ex.com/page.png"
    web.content_types[html] = "text/html"

    augmenter = _make_augmenter(web, success_threshold=0.8, max_retries=5)
    _augment(augmenter, {"page": _page(html)})

    assert sleeps == []
    assert web.downloads == [html]
    assert vlm.calls == []


@pytest.mark.parametrize(
    ("error", "status"),
    [
        ("timeout", None),
        (CONNECTION_ERROR, None),
        ("HTTP 500", 500),
        ("HTTP 503", 503),
        ("HTTP 429", 429),
        ("HTTP 403", 403),
    ],
)
def test_recoverable_download_errors_trigger_retry(
    fakes, error: str, status: int | None
) -> None:
    web, _, sleeps = fakes
    bad = "https://ex.com/bad.png"
    web.failures[bad] = 1  # 第一輪失敗，重試成功
    web.errors[bad] = (error, status)

    augmenter = _make_augmenter(web, success_threshold=0.8, max_retries=3)
    results = _augment(augmenter, {"page": _page(bad)})

    assert len(sleeps) == 1
    assert web.downloads.count(bad) == 2
    assert results["page"]["images"][0]["caption"] == f"caption of {bad}"


def test_vlm_failure_triggers_retry_without_redownloading(fakes) -> None:
    web, vlm, sleeps = fakes
    url = "https://ex.com/a.png"
    vlm.failures[url] = 1

    augmenter = _make_augmenter(web, success_threshold=0.8, max_retries=3)
    results = _augment(augmenter, {"page": _page(url)})

    assert len(sleeps) == 1
    assert web.downloads == [url]  # 下載已成功，只重做摘要
    assert vlm.calls == [url, url]
    assert results["page"]["images"][0]["caption"] == f"caption of {url}"
    assert augmenter._failed_images == {}


def test_retry_failed_result_helper_is_recoverable() -> None:
    """Downloader 的未知失敗（無狀態碼）視為可恢復。"""
    assert Augmenter._is_recoverable(failed_result("u", "timeout"))
    assert not Augmenter._is_recoverable(failed_result("u", "HTTP 404", 404))


# ----- markdown 插入與統計 -----


def test_enhanced_markdown_inserts_numbered_captions(fakes) -> None:
    web, _, _ = fakes
    a, b, bad = "https://ex.com/a.png", "https://ex.com/b.png", "https://ex.com/x.png"
    web.failures[bad] = 99
    page = {
        "fit_markdown": f"# Title\n![a]({a}) ![b]({b})\ntext\n![x]({bad})\n\n",
        "images": [],
    }

    results = _augment(_make_augmenter(web), {"page": page})

    assert results["page"]["enhanced_markdown"] == (
        "# Title\n"
        f"![a]({a}) ![b]({b})\n"
        f"> # Image-1\n>\n> caption of {a}\n"
        f"> # Image-2\n>\n> caption of {b}\n"
        "text\n"
        f"![x]({bad})"
    )


def test_captions_land_on_correct_images_when_skipped_image_comes_first(fakes) -> None:
    """被略過的圖片（svg）排在前面時，描述依各圖片自己的 URL 對位；編號為頁內圖片序號。"""
    web, _, _ = fakes
    svg, a, b = (
        "https://ex.com/icon.svg",
        "https://ex.com/a.png",
        "https://ex.com/b.png",
    )
    page = {
        "fit_markdown": f"![i]({svg})\n![a]({a})\n![b]({b})\n",
        "images": [],
    }

    results = _augment(_make_augmenter(web), {"page": page})

    assert results["page"]["enhanced_markdown"] == (
        f"![i]({svg})\n"
        f"![a]({a})\n"
        f"> # Image-2\n>\n> caption of {a}\n"
        f"![b]({b})\n"
        f"> # Image-3\n>\n> caption of {b}"
    )
    assert web.downloads == [a, b]


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

    augmenter = _make_augmenter(web)
    _augment(augmenter, crawl_results)

    assert _page_stats(augmenter) == {
        "page1": {
            "cost_usd": COST_PER_CAPTION,
            "success": 1,
            "download_failure": 1,
            "summarize_failure": 1,
            "skipped": 0,
            "cache_reuse": 0,
        },
        "page2": {
            "cost_usd": 0.0,
            "success": 0,
            "download_failure": 0,
            "summarize_failure": 0,
            "skipped": 0,
            "cache_reuse": 1,
        },
    }
    assert _stats(augmenter._all_round_stats) == {
        "cost_usd": COST_PER_CAPTION,
        "success": 1,
        "failure": 2,
        "retries": 1,
    }


# ----- 圖片過濾：尺寸門檻、內容去重 -----


def test_small_image_is_not_sent_to_vlm_and_has_no_caption(fakes) -> None:
    """長邊 < min_size 不送 VLM、不產生描述（比照略過的 svg：沒有 caption 欄位、markdown 不變）。"""
    web, vlm, _ = fakes
    small, big = "https://ex.com/icon.png", "https://ex.com/photo.png"
    web.contents = {small: png_bytes(16, 99, "small"), big: png_bytes(300, 200, "big")}

    augmenter = _make_augmenter(web)
    results = _augment(augmenter, {"page": _page(small, big)})

    assert vlm.calls == ["big"]
    assert "caption" not in results["page"]["images"][0]
    assert results["page"]["images"][1]["caption"] == "caption of big"
    assert results["page"]["enhanced_markdown"] == (
        f"line ![img]({small})\nline ![img]({big})\n> # Image-2\n>\n> caption of big"
    )
    assert augmenter._failed_images == {}
    assert _page_stats(augmenter)["page"]["skipped"] == 1
    assert _page_stats(augmenter)["page"]["success"] == 1


@pytest.mark.parametrize(
    ("size", "min_size", "sent"),
    [
        ((100, 40), 100, True),  # 長邊剛好等於門檻：不略過
        ((40, 100), 100, True),  # 以長邊判斷，不是任一邊
        ((99, 99), 100, False),
        ((1, 1), 100, False),
        ((1, 1), 0, True),  # min_size = 0 不過濾
    ],
)
def test_min_size_uses_long_edge(
    fakes, size: tuple[int, int], min_size: int, sent: bool
) -> None:
    web, vlm, _ = fakes
    url = "https://ex.com/a.png"
    web.contents = {url: png_bytes(*size, "a")}

    _augment(_make_augmenter(web), {"page": _page(url)}, image_min_size=min_size)

    assert (vlm.calls == ["a"]) is sent


def test_small_image_on_many_pages_counted_once_and_not_retried(fakes) -> None:
    web, vlm, sleeps = fakes
    icon = "https://ex.com/icon.png"
    web.contents = {icon: png_bytes(8, 8, "icon")}
    crawl_results = {f"page{i}": _page(icon) for i in range(3)}

    augmenter = _make_augmenter(web, max_retries=3)
    _augment(augmenter, crawl_results)

    assert web.downloads == [icon] and vlm.calls == [] and sleeps == []
    stats = _page_stats(augmenter)
    assert [s["skipped"] for s in stats.values()] == [1, 0, 0]
    assert [s["cache_reuse"] for s in stats.values()] == [0, 1, 1]


def test_same_content_with_different_urls_is_captioned_once(fakes) -> None:
    web, vlm, _ = fakes
    first, second, other = (
        "https://ex.com/a.png",
        "https://cdn.ex.com/copy-of-a.png",
        "https://ex.com/b.png",
    )
    same = png_bytes(300, 200, "same")
    web.contents = {
        first: same,
        second: same,
        other: png_bytes(300, 200, "other"),
    }
    crawl_results = {"page1": _page(first, other), "page2": _page(second)}

    augmenter = _make_augmenter(web)
    results = _augment(augmenter, crawl_results)

    assert sorted(vlm.calls) == ["other", "same"]  # 內容相同的只描述一次
    assert results["page1"]["images"][0]["caption"] == "caption of same"
    assert results["page2"]["images"][0]["caption"] == "caption of same"
    assert "caption of same" in results["page2"]["enhanced_markdown"]
    # 描述只計一次花費；內容共用的圖片記為 cache_reuse
    stats = _page_stats(augmenter)
    assert stats["page1"]["success"] == 2
    assert stats["page2"] == {
        "cost_usd": 0.0,
        "success": 0,
        "download_failure": 0,
        "summarize_failure": 0,
        "skipped": 0,
        "cache_reuse": 1,
    }
    assert _stats(augmenter._all_round_stats)["cost_usd"] == 2 * COST_PER_CAPTION


def test_shared_content_follows_representative_through_retry(fakes) -> None:
    """代表圖片的 VLM 失敗後重試成功，內容相同的圖片跟著得到描述。"""
    web, vlm, sleeps = fakes
    first, second = "https://ex.com/a.png", "https://ex.com/copy.png"
    same = png_bytes(300, 200, "same")
    web.contents = {first: same, second: same}
    vlm.failures["same"] = 1

    augmenter = _make_augmenter(web, max_retries=3)
    results = _augment(augmenter, {"page": _page(first, second)})

    assert len(sleeps) == 1
    assert vlm.calls == ["same", "same"]
    assert [i["caption"] for i in results["page"]["images"]] == ["caption of same"] * 2
    assert augmenter._failed_images == {}


def test_shared_content_without_description_when_representative_fails(fakes) -> None:
    web, vlm, _ = fakes
    first, second = "https://ex.com/a.png", "https://ex.com/copy.png"
    same = png_bytes(300, 200, "same")
    web.contents = {first: same, second: same}
    vlm.failing.add("same")

    augmenter = _make_augmenter(web)
    results = _augment(augmenter, {"page": _page(first, second)})

    assert [i["caption"] for i in results["page"]["images"]] == ["", ""]
    assert augmenter._failed_images == {first: ("page", "caption generation failed")}


def test_small_image_with_same_content_is_skipped_not_shared(fakes) -> None:
    """尺寸門檻先於內容去重：小圖不會成為共用描述的代表。"""
    web, vlm, _ = fakes
    first, second = "https://ex.com/a.png", "https://ex.com/b.png"
    tiny = png_bytes(1, 1, "tiny")
    web.contents = {first: tiny, second: tiny}

    results = _augment(_make_augmenter(web), {"page": _page(first, second)})

    assert vlm.calls == []
    assert all("caption" not in i for i in results["page"]["images"])


def test_undecodable_image_is_not_filtered(fakes) -> None:
    """無法解碼尺寸的圖片不依尺寸過濾（交給 VLM）。"""
    web, vlm, _ = fakes
    url = "https://ex.com/a.png"

    _augment(_make_augmenter(web), {"page": _page(url)})

    assert vlm.calls == [url]
