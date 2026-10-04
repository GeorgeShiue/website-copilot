"""篩選：從爬取結果收集待處理的資源，跨頁去重。"""

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from typing import Any, Literal
from urllib.parse import urlparse

from website_copilot.ingestion.augmentation.assets import Asset, AssetRef
from website_copilot.utils.document_rules import is_document_url, normalize_url
from website_copilot.utils.text_helper import MARKDOWN_IMAGE_PATTERN

# VLM（OpenAI）僅支援 png / jpeg / gif / webp，其他格式（如 svg、avif）直接略過
UNSUPPORTED_IMAGE_SUFFIXES = (".svg", ".avif", ".bmp", ".ico", ".tif", ".tiff")


class ImageCollector:
    def __init__(self, source: Literal["images", "markdown"]) -> None:
        """source：圖片來源，爬蟲結果的 images 欄位或 fit_markdown 中的圖片連結。"""
        self.source = source

    def collect(self, crawl_results: dict[str, dict[str, Any]]) -> list[Asset]:
        """回傳不重複的圖片資源（依首次出現順序），refs 依頁面與頁內順序記錄所有引用。"""
        assets: dict[str, Asset] = {}
        for page_key, crawl_result in crawl_results.items():
            for url in self._page_image_urls(crawl_result):
                asset = assets.setdefault(url, Asset(url=url, kind="image"))
                asset.refs.append(AssetRef(page_key=page_key))
        return list(assets.values())

    def _page_image_urls(self, crawl_result: dict[str, Any]) -> list[str]:
        """單頁的圖片 URL（含重複，已排除 VLM 不支援的副檔名）。"""
        image_urls: list[str] = []
        if self.source == "markdown":
            image_urls = MARKDOWN_IMAGE_PATTERN.findall(
                crawl_result.get("fit_markdown", "")
            )
        elif self.source == "images":
            images = crawl_result.get("images", [])
            image_urls = [image.get("url", "") for image in images if image.get("url")]

        return [
            url
            for url in image_urls
            if not urlparse(url).path.lower().endswith(UNSUPPORTED_IMAGE_SUFFIXES)
        ]


# Markdown 連結 [文字](url "title")；文字可含圖示圖片 ![alt](src)（不含以 ! 開頭的圖片本身）
MARKDOWN_LINK_PATTERN = re.compile(
    r"(?<!!)\[((?:[^\[\]]|!\[[^\]]*\]\([^)]*\))*)\]"
    r"\((https?://[^)\s]+)(?:\s+\"([^\"]*)\")?\)"
)


def iter_markdown_links(markdown: str) -> Iterator[tuple[str, str, str]]:
    """依出現順序產生 (連結文字, URL, title 屬性)。"""
    for match in MARKDOWN_LINK_PATTERN.finditer(markdown):
        yield match.group(1), match.group(2), match.group(3) or ""


@dataclass
class CollectedDocuments:
    assets: list[Asset] = field(default_factory=list)
    # 副檔名可判斷、但格式未啟用而不下載的文件：URL → 副檔名（小寫）
    skipped_format: dict[str, str] = field(default_factory=dict)
    # 不在 allowed_domains 的文件連結數（不重複 URL）
    skipped_domain: int = 0


class DocumentCollector:
    def __init__(
        self,
        *,
        formats: Iterable[str],
        site_patterns: Iterable[str] = (),
        allowed_domains: Iterable[str] | None = None,
    ) -> None:
        """formats：要解析的格式（副檔名）；site_patterns：站點專屬的文件 URL 樣式；
        allowed_domains：None 為不限制網域。"""
        self.formats = frozenset(f.lower() for f in formats)
        self.site_patterns = tuple(site_patterns)
        self.allowed_domains = (
            None
            if allowed_domains is None
            else tuple(d.lower() for d in allowed_domains)
        )

    def collect(self, crawl_results: dict[str, dict[str, Any]]) -> CollectedDocuments:
        """從所有已爬頁面（含深度 2）的連結收集文件，不受 max_depth 限制；依正規化 URL 去重。

        副檔名可判斷且不在 formats 的不下載（記入 skipped_format）；副檔名無法判斷的
        （如下載 API）先收進來，下載後依內容判斷格式。
        """
        collected = CollectedDocuments()
        assets: dict[str, Asset] = {}
        off_domain: set[str] = set()
        for page_key, crawl_result in crawl_results.items():
            for text, raw_url, title in iter_markdown_links(
                crawl_result.get("fit_markdown", "")
            ):
                if not is_document_url(raw_url, self.site_patterns):
                    continue
                url = normalize_url(raw_url)
                if not self._domain_allowed(url):
                    off_domain.add(url)
                    continue
                extension = self._url_extension(url)
                if extension is not None and extension not in self.formats:
                    collected.skipped_format[url] = extension
                    continue
                asset = assets.setdefault(url, Asset(url=url, kind="document"))
                asset.refs.append(AssetRef(page_key=page_key, text=text, title=title))

        collected.assets = list(assets.values())
        collected.skipped_domain = len(off_domain)
        return collected

    def _domain_allowed(self, url: str) -> bool:
        if self.allowed_domains is None:
            return True
        host = (urlparse(url).hostname or "").lower()
        return any(host == d or host.endswith(f".{d}") for d in self.allowed_domains)

    @staticmethod
    def _url_extension(url: str) -> str | None:
        """URL path 的副檔名（僅限已知的文件副檔名；下載 API 等無副檔名者回傳 None）。"""
        name = urlparse(url).path.rsplit("/", 1)[-1]
        if "." not in name:
            return None
        extension = name.rsplit(".", 1)[1].lower()
        return extension if is_document_url(f"https://x/a.{extension}") else None
