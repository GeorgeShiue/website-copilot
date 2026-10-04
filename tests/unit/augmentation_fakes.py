"""Augmenter 測試共用的 fake：下載器與 VLM（不連網、不產生費用）。

fake 圖片內容即其 url，fake caption 為 "caption of <url>"，可由 caption 反推來源圖片。
"""

import base64
import hashlib
import io
from collections.abc import Callable, Iterable
from types import SimpleNamespace
from typing import Any

from PIL import Image, PngImagePlugin

from website_copilot.utils.http_downloader import DownloadResult

COST_PER_CAPTION = 0.25


def png_bytes(width: int, height: int, key: str = "") -> bytes:
    """指定尺寸的 PNG；key 決定顏色並寫入 tEXt（同 key、同尺寸的位元組完全相同，fake VLM 由它得知描述對象）。"""
    digest = hashlib.sha1(key.encode()).digest()
    image = Image.new("RGB", (width, height), (digest[0], digest[1], digest[2]))
    info = PngImagePlugin.PngInfo()
    info.add_text("key", key)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", pnginfo=info)
    return buffer.getvalue()


def image_key(content: bytes) -> str:
    """fake 圖片內容的描述對象：PNG 取 tEXt 的 key，否則內容即 url。"""
    try:
        with Image.open(io.BytesIO(content)) as image:
            return str(image.info["key"])
    except (OSError, KeyError):
        try:
            return content.decode()
        except UnicodeDecodeError:  # 沒有 key 的真實圖片：以內容雜湊代表
            return hashlib.sha1(content).hexdigest()[:8]


def ok_result(
    url: str,
    content_type: str = "image/png",
    content: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> DownloadResult:
    return DownloadResult(
        url=url,
        final_url=url,
        status_code=200,
        headers={"content-type": content_type, **(headers or {})},
        content=url.encode() if content is None else content,
        error=None,
        attempts=1,
    )


def failed_result(
    url: str, error: str = "connection error: refused", status_code: int | None = None
) -> DownloadResult:
    return DownloadResult(
        url=url,
        final_url=url,
        status_code=status_code,
        headers={},
        content=None,
        error=error,
        attempts=1,
    )


class FakeDownloader:
    """依 url 回傳圖片。

    - failures[url]：剩餘的失敗次數（失敗內容由 errors[url] 指定，預設連線錯誤）。
    - errors[url]：(error, status_code)，如 ("HTTP 404", 404)。
    - content_types[url]：回應的 Content-Type。
    - contents[url]：回應內容（預設為 url 的位元組，不是有效圖片）。
    - headers[url]：額外的回應標頭（如 content-disposition）。
    """

    def __init__(
        self,
        failures: dict[str, int] | None = None,
        content_types: dict[str, str] | None = None,
        errors: dict[str, tuple[str, int | None]] | None = None,
        contents: dict[str, bytes] | None = None,
        headers: dict[str, dict[str, str]] | None = None,
    ) -> None:
        self.failures = dict(failures or {})
        self.content_types = content_types or {}
        self.errors = errors or {}
        self.contents = contents or {}
        self.headers = headers or {}
        self.downloads: list[str] = []

    def download(
        self,
        urls: Iterable[str],
        on_complete: Callable[[DownloadResult], None] | None = None,
    ) -> dict[str, DownloadResult]:
        results: dict[str, DownloadResult] = {}
        for url in dict.fromkeys(urls):
            self.downloads.append(url)
            if self.failures.get(url, 0) > 0:
                self.failures[url] -= 1
                error, status = self.errors.get(
                    url, ("connection error: refused", None)
                )
                result = failed_result(url, error, status)
            else:
                result = ok_result(
                    url,
                    self.content_types.get(url, "image/png"),
                    self.contents.get(url),
                    self.headers.get(url),
                )
            results[url] = result
            if on_complete is not None:
                on_complete(result)
        return results


class FakeVLM:
    """caption 為 "caption of <url>"；failing 中的 url 永遠失敗，failures[url] 為剩餘的失敗次數。"""

    def __init__(
        self, failing: set[str] | None = None, failures: dict[str, int] | None = None
    ) -> None:
        self.failing = failing or set()
        self.failures = dict(failures or {})
        self.calls: list[str] = []

    async def acompletion(self, *, model: str, messages: list, **_kwargs: Any) -> Any:
        data_url = messages[0]["content"][1]["image_url"]["url"]
        url = image_key(base64.standard_b64decode(data_url.split(",", 1)[1]))
        self.calls.append(url)
        if url in self.failing:
            raise RuntimeError("vlm error")
        if self.failures.get(url, 0) > 0:
            self.failures[url] -= 1
            raise RuntimeError("vlm error")
        message = SimpleNamespace(content=f"caption of {url}")
        return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=None)
