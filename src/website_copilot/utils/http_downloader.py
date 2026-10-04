"""共用下載器：URL 清單 → HTTP 回應（圖片與文件共用）。

只負責下載：並行上限、單一請求層級的重試、大小上限、重新導向。格式判斷、存檔與 log 呈現
由呼叫端處理（失敗原因以 `DownloadResult.error` 回傳）。這一層的重試（逾時、連線錯誤、5xx、429）
與 Augmenter 的整輪退避重試（對付封鎖）是不同層次，可疊加。
"""

import asyncio
import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
RETRY_BACKOFF_SECONDS = 0.5  # 第 n 次重試前等待 base * 2^(n-1)
RETRYABLE_STATUS_CODES = frozenset({429})  # 另含所有 5xx
# 403 常為封鎖：單一請求不重試，但整輪退避重試時視為可恢復
RECOVERABLE_STATUS_CODES = frozenset({403, 429})


@dataclass(frozen=True)
class DownloadResult:
    url: str  # 請求的 URL
    final_url: str  # 跟隨重新導向後的 URL（未取得回應時同 url）
    status_code: int | None  # 未取得回應（逾時、連線失敗）時為 None
    headers: dict[
        str, str
    ]  # 回應標頭，key 一律小寫（content-type、content-disposition…）
    content: bytes | None  # 失敗時為 None
    error: str | None  # 失敗原因，如 "HTTP 404"、"timeout"、"exceeds max_bytes"
    attempts: int  # 實際嘗試次數

    @property
    def ok(self) -> bool:
        return self.error is None and self.content is not None

    @property
    def recoverable(self) -> bool:
        """失敗是否可能因重試或等待而恢復：逾時、連線錯誤、5xx、429、403（常為封鎖或限流）。

        其餘 4xx、超過大小上限與無效 URL 為永久錯誤。成功的結果回傳 False。
        """
        if self.ok or self.error is None:
            return False
        if self.error.startswith(("invalid url", "exceeds max_bytes")):
            return False
        status = self.status_code
        if status is None:
            return True
        return status >= 500 or status in RECOVERABLE_STATUS_CODES


class _ExceedsMaxBytes(Exception):
    pass


class HttpDownloader:
    def __init__(
        self,
        *,
        max_concurrency: int,  # 一次下載呼叫內所有 URL 共用的同時請求數
        timeout: float,  # 單次請求的連線／讀取逾時秒數
        max_retries: int,  # 逾時、連線錯誤、5xx、429 的最大重試次數（不含第一次）
        max_bytes: int | None,  # 單一回應的大小上限，None 為不限制
        headers: dict[str, str] | None = None,  # 額外請求標頭（覆蓋預設 User-Agent）
        retry_backoff: float = RETRY_BACKOFF_SECONDS,
        transport: httpx.AsyncBaseTransport | None = None,  # 測試用
    ) -> None:
        self.max_concurrency = max_concurrency
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_bytes = max_bytes
        self.headers = {"User-Agent": DEFAULT_USER_AGENT, **(headers or {})}
        self.retry_backoff = retry_backoff
        self._transport = transport

    def download(
        self,
        urls: Iterable[str],
        on_complete: Callable[[DownloadResult], None] | None = None,
    ) -> dict[str, DownloadResult]:
        """同步版（asyncio.run 包裝），供同步呼叫端使用。"""
        return asyncio.run(self.adownload(urls, on_complete))

    async def adownload(
        self,
        urls: Iterable[str],
        on_complete: Callable[[DownloadResult], None] | None = None,
    ) -> dict[str, DownloadResult]:
        """下載所有 URL，回傳 url → 結果（依輸入順序；重複的 URL 只請求一次）。

        on_complete 於每個 URL 完成（成功或最終失敗）時呼叫一次，供呼叫端更新進度條。
        """
        unique_urls = list(dict.fromkeys(urls))
        if not unique_urls:
            return {}

        semaphore = asyncio.Semaphore(self.max_concurrency)
        async with httpx.AsyncClient(
            transport=self._transport,
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
            headers=self.headers,
            limits=httpx.Limits(max_connections=self.max_concurrency),
        ) as client:

            async def fetch(url: str) -> DownloadResult:
                result = await self._fetch_with_retries(client, semaphore, url)
                if on_complete is not None:
                    on_complete(result)
                return result

            results = await asyncio.gather(*(fetch(url) for url in unique_urls))

        return dict(zip(unique_urls, results, strict=True))

    async def _fetch_with_retries(
        self,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        url: str,
    ) -> DownloadResult:
        attempts = 0
        while True:
            attempts += 1
            async with semaphore:
                result, retryable = await self._fetch_once(client, url, attempts)
            if result.ok or not retryable or attempts > self.max_retries:
                if not result.ok:
                    logger.debug(
                        "Download failed (url=%s, error=%s)", url, result.error
                    )
                return result
            # 退避期間不佔用並行名額
            await asyncio.sleep(self.retry_backoff * 2 ** (attempts - 1))

    async def _fetch_once(
        self, client: httpx.AsyncClient, url: str, attempts: int
    ) -> tuple[DownloadResult, bool]:
        """單次請求，回傳 (結果, 失敗時是否值得重試)。"""

        def failure(
            error: str,
            *,
            retryable: bool,
            status_code: int | None = None,
            final_url: str | None = None,
            headers: dict[str, str] | None = None,
        ) -> tuple[DownloadResult, bool]:
            result = DownloadResult(
                url=url,
                final_url=final_url or url,
                status_code=status_code,
                headers=headers or {},
                content=None,
                error=error,
                attempts=attempts,
            )
            return result, retryable

        try:
            async with client.stream("GET", url) as response:
                final_url = str(response.url)
                headers = {k.lower(): v for k, v in response.headers.items()}
                status_code = response.status_code
                if status_code >= 400:
                    retryable = (
                        status_code >= 500 or status_code in RETRYABLE_STATUS_CODES
                    )
                    return failure(
                        f"HTTP {status_code}",
                        retryable=retryable,
                        status_code=status_code,
                        final_url=final_url,
                        headers=headers,
                    )

                content = await self._read_limited(response)
        except _ExceedsMaxBytes:
            return failure(
                "exceeds max_bytes",
                retryable=False,
                status_code=status_code,
                final_url=final_url,
                headers=headers,
            )
        except httpx.TimeoutException:
            return failure("timeout", retryable=True)
        except (httpx.UnsupportedProtocol, httpx.InvalidURL) as e:
            return failure(f"invalid url: {e}", retryable=False)
        except httpx.TransportError as e:
            return failure(f"connection error: {e or type(e).__name__}", retryable=True)

        return (
            DownloadResult(
                url=url,
                final_url=final_url,
                status_code=status_code,
                headers=headers,
                content=content,
                error=None,
                attempts=attempts,
            ),
            False,
        )

    async def _read_limited(self, response: httpx.Response) -> bytes:
        """串流讀取回應內容；超過 max_bytes 即中止，避免誤抓大檔吃光記憶體。"""
        max_bytes = self.max_bytes
        if max_bytes is None:
            return await response.aread()

        declared = response.headers.get("content-length")
        if declared is not None and declared.isdigit() and int(declared) > max_bytes:
            raise _ExceedsMaxBytes
        chunks: list[bytes] = []
        size = 0
        async for chunk in response.aiter_bytes():
            size += len(chunk)
            if size > max_bytes:
                raise _ExceedsMaxBytes
            chunks.append(chunk)
        return b"".join(chunks)
