"""HttpDownloader：去重、並行上限、重試條件、max_bytes、重新導向、錯誤訊息（httpx.MockTransport，不連網）。"""

import asyncio
from collections.abc import Callable

import httpx
import pytest

from website_copilot.utils.http_downloader import (
    DEFAULT_USER_AGENT,
    DownloadResult,
    HttpDownloader,
)

Handler = Callable[[httpx.Request], httpx.Response]


def _downloader(
    handler: Callable,
    *,
    max_concurrency: int = 4,
    max_retries: int = 2,
    max_bytes: int | None = None,
    headers: dict[str, str] | None = None,
) -> HttpDownloader:
    return HttpDownloader(
        max_concurrency=max_concurrency,
        timeout=1.0,
        max_retries=max_retries,
        max_bytes=max_bytes,
        headers=headers,
        retry_backoff=0.0,
        transport=httpx.MockTransport(handler),
    )


def _ok(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, content=str(request.url).encode())


def test_success_result_fields() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=b"data",
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": 'attachment; filename="a.pdf"',
            },
        )

    url = "https://ex.com/a"
    result = _downloader(handler).download([url])[url]

    assert result.ok
    assert result == DownloadResult(
        url=url,
        final_url=url,
        status_code=200,
        headers={
            "content-type": "application/pdf",
            "content-disposition": 'attachment; filename="a.pdf"',
            "content-length": "4",
        },
        content=b"data",
        error=None,
        attempts=1,
    )


def test_empty_input() -> None:
    assert _downloader(_ok).download([]) == {}


def test_duplicate_urls_requested_once_and_order_preserved() -> None:
    requests: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        return _ok(request)

    urls = ["https://ex.com/b", "https://ex.com/a", "https://ex.com/b"]
    results = _downloader(handler).download(urls)

    assert list(results) == ["https://ex.com/b", "https://ex.com/a"]
    assert sorted(requests) == ["https://ex.com/a", "https://ex.com/b"]


@pytest.mark.parametrize(("limit", "n_urls"), [(3, 12), (20, 5)])
def test_concurrency_limited_across_all_urls(limit: int, n_urls: int) -> None:
    in_flight = 0
    peak = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.01)
        in_flight -= 1
        return _ok(request)

    urls = [f"https://ex.com/{i}" for i in range(n_urls)]
    results = _downloader(handler, max_concurrency=limit).download(urls)

    assert peak == min(limit, n_urls)
    assert all(r.ok for r in results.values())


def test_retry_on_5xx_then_success() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(503) if calls < 3 else _ok(request)

    result = _downloader(handler, max_retries=2).download(["https://ex.com/a"])[
        "https://ex.com/a"
    ]

    assert result.ok
    assert result.attempts == 3


def test_retry_on_429() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(429) if calls == 1 else _ok(request)

    result = _downloader(handler).download(["https://ex.com/a"])["https://ex.com/a"]

    assert result.ok
    assert result.attempts == 2


def test_retries_exhausted_reports_last_error() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(502)

    result = _downloader(handler, max_retries=2).download(["https://ex.com/a"])[
        "https://ex.com/a"
    ]

    assert not result.ok
    assert (result.error, result.status_code, result.content) == ("HTTP 502", 502, None)
    assert result.attempts == calls == 3


@pytest.mark.parametrize("status", [400, 403, 404, 410])
def test_4xx_not_retried(status: int) -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(status)

    result = _downloader(handler, max_retries=5).download(["https://ex.com/a"])[
        "https://ex.com/a"
    ]

    assert (result.error, result.status_code, result.attempts) == (
        f"HTTP {status}",
        status,
        1,
    )
    assert calls == 1


def test_timeout_is_retried_and_reported() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout("slow", request=request)

    result = _downloader(handler, max_retries=1).download(["https://ex.com/a"])[
        "https://ex.com/a"
    ]

    assert (result.error, result.status_code, result.attempts) == ("timeout", None, 2)
    assert calls == 2


def test_connection_error_is_retried_then_recovers() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ConnectError("refused", request=request)
        return _ok(request)

    result = _downloader(handler).download(["https://ex.com/a"])["https://ex.com/a"]

    assert result.ok
    assert result.attempts == 2


def test_connection_error_message() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    result = _downloader(handler, max_retries=0).download(["https://ex.com/a"])[
        "https://ex.com/a"
    ]

    assert result.error == "connection error: refused"


def test_unsupported_protocol_not_retried() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("not reached")

    url = "ftp://ex.com/a"
    result = HttpDownloader(
        max_concurrency=1, timeout=1.0, max_retries=3, max_bytes=None, retry_backoff=0.0
    ).download([url])[url]

    assert result.error is not None
    assert result.error.startswith("invalid url")
    assert result.attempts == 1


def test_failure_does_not_affect_other_urls() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404) if request.url.path == "/bad" else _ok(request)

    results = _downloader(handler).download(
        ["https://ex.com/bad", "https://ex.com/good"]
    )

    assert not results["https://ex.com/bad"].ok
    assert results["https://ex.com/good"].ok


def test_max_bytes_aborts_streaming_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"x" * 100)

    results = _downloader(handler, max_bytes=50).download(["https://ex.com/a"])
    result = results["https://ex.com/a"]

    assert (result.ok, result.error, result.content) == (
        False,
        "exceeds max_bytes",
        None,
    )
    assert result.status_code == 200
    assert result.attempts == 1  # 超過上限不重試


def test_max_bytes_rejects_by_content_length_without_reading() -> None:
    class Body(httpx.AsyncByteStream):
        consumed = False

        async def __aiter__(self):
            Body.consumed = True
            yield b"x" * 100

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"Content-Length": "100"}, stream=Body())

    result = _downloader(handler, max_bytes=50).download(["https://ex.com/a"])[
        "https://ex.com/a"
    ]

    assert result.error == "exceeds max_bytes"
    assert not Body.consumed


@pytest.mark.parametrize("max_bytes", [100, None])
def test_within_max_bytes_succeeds(max_bytes: int | None) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"x" * 100)

    result = _downloader(handler, max_bytes=max_bytes).download(["https://ex.com/a"])[
        "https://ex.com/a"
    ]

    assert result.ok
    assert result.content == b"x" * 100


def test_redirect_reports_final_url() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/old":
            return httpx.Response(302, headers={"Location": "https://cdn.ex.com/new"})
        return _ok(request)

    result = _downloader(handler).download(["https://ex.com/old"])["https://ex.com/old"]

    assert result.ok
    assert result.url == "https://ex.com/old"
    assert result.final_url == "https://cdn.ex.com/new"
    assert result.content == b"https://cdn.ex.com/new"


def test_default_user_agent_and_custom_headers() -> None:
    seen: list[httpx.Headers] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.headers)
        return _ok(request)

    _downloader(handler).download(["https://ex.com/a"])
    _downloader(handler, headers={"User-Agent": "custom", "X-Test": "1"}).download(
        ["https://ex.com/b"]
    )

    assert seen[0]["user-agent"] == DEFAULT_USER_AGENT
    assert (seen[1]["user-agent"], seen[1]["x-test"]) == ("custom", "1")


def test_on_complete_called_once_per_unique_url() -> None:
    completed: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404) if request.url.path == "/bad" else _ok(request)

    urls = ["https://ex.com/a", "https://ex.com/bad", "https://ex.com/a"]
    _downloader(handler).download(urls, on_complete=lambda r: completed.append(r.url))

    assert sorted(completed) == ["https://ex.com/a", "https://ex.com/bad"]


def test_async_api() -> None:
    results = asyncio.run(_downloader(_ok).adownload(["https://ex.com/a"]))

    assert results["https://ex.com/a"].ok
