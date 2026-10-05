"""文件階段：下載 → 格式判斷 → 解析 → 回寫成獨立 entry。

DocumentStage 由 Augmenter 在每一輪呼叫（與圖片共用整輪退避重試）：
- 下載：共用下載器；下載後以內容判斷格式，格式未啟用者不存檔、不建 entry，只記統計。
- 去重：內容 sha1 相同的不同 URL 只建一筆 entry（鍵取第一個 URL），引用頁面合併。
- 解析：每份不重複的內容解析一次（執行緒池）；解析失敗為永久失敗。
- 回寫：每份文件成為 results 的獨立 entry（`doc_<url sha1 前 12 碼>`），原檔另存於 files。
"""

import hashlib
import logging
import os
import re
from collections import Counter
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from rich.table import Table

from website_copilot.ingestion.augmentation.assets import Asset, AssetRef
from website_copilot.ingestion.augmentation.collectors import DocumentCollector
from website_copilot.ingestion.augmentation.document_format import (
    detect_format,
    disposition_file_name,
    url_file_name,
)
from website_copilot.ingestion.augmentation.processors.document_parser import (
    DocumentParseError,
    ParsedDocument,
    parse_document,
)
from website_copilot.ingestion.augmentation.processors.image_captioner import (
    caption_block,
)
from website_copilot.ingestion.augmentation.processors.images import (
    IMAGE_PLACEHOLDER_PATTERN,
    ParsedImage,
)
from website_copilot.ingestion.augmentation.titles import (
    choose_title,
    clean_link_text,
    is_generic,
)
from website_copilot.utils.http_downloader import DownloadResult
from website_copilot.utils.log_helper import TaskCountProgress, log_session, print_log

logger = logging.getLogger(__name__)

PARSE_MAX_WORKERS = 8


@dataclass
class DocumentOptions:
    formats: tuple[str, ...]  # 要解析的格式（副檔名）
    url_patterns: tuple[str, ...] = ()  # 站點專屬的文件 URL 樣式
    allowed_domains: tuple[str, ...] | None = None  # None 為不限制網域
    caption_images: bool = True  # 文件內嵌圖片是否交給 VLM 描述


@dataclass
class DocumentFile:
    """要隨結果發布的原檔。"""

    file_name: str  # 存檔名稱：<key>.<ext>
    content: bytes


@dataclass
class DocumentEntry:
    """單一文件 URL 的下載結果。"""

    download_status: str = ""  # "success"／"failed"
    content: bytes = b""
    content_sha1: str = ""
    file_format: str = ""
    file_name: str = ""  # 原始檔名（Content-Disposition 或 URL）
    content_type: str = ""
    downloaded_at: str = ""
    skip_reason: str = ""  # 下載後判斷格式未啟用或無法判斷：不存檔、不建 entry
    failure_reason: str = ""
    recoverable: bool = False


@dataclass
class DocumentStats:
    collected: int = 0
    skipped_format: int = 0  # 副檔名判斷出格式未啟用，未下載
    skipped_domain: int = 0
    download_failure: int = 0
    format_skipped: int = 0  # 下載後判斷出格式未啟用或無法判斷
    parse_failure: int = 0
    duplicate_content: int = 0  # 內容與其他 URL 相同而合併
    success: int = 0
    skipped_by_format: Counter[str] = field(default_factory=Counter)


class DocumentStage:
    def __init__(self, options: DocumentOptions, downloader: Any) -> None:
        self.options = options
        self.downloader = downloader
        self.assets: list[Asset] = []
        self.skipped_format: dict[str, str] = {}
        self.skipped_domain = 0
        self.files: dict[str, DocumentFile] = {}
        self._entries: dict[str, DocumentEntry] = {}
        self._parsed: dict[str, ParsedDocument | DocumentParseError] = {}
        # 是否抽出文件內嵌圖片（由 Augmenter 依 VLM 是否可用設定）
        self.extract_images = False
        # 文件內嵌圖片：資源 URL（doc-image:<sha1>）→ 圖片；內容 sha1 → 該文件各佔位符對應的資源 URL
        self.image_contents: dict[str, ParsedImage] = {}
        self._image_urls: dict[str, list[str | None]] = {}

    # ===== 收集 =====

    def collect(self, crawl_results: dict[str, dict[str, Any]]) -> list[Asset]:
        collected = DocumentCollector(
            formats=self.options.formats,
            site_patterns=self.options.url_patterns,
            allowed_domains=self.options.allowed_domains,
        ).collect(crawl_results)
        self.assets = collected.assets
        self.skipped_format = collected.skipped_format
        self.skipped_domain = collected.skipped_domain
        self._entries = {}
        self._parsed = {}
        self.files = {}
        self.image_contents = {}
        self._image_urls = {}
        return self.assets

    # ===== 下載 =====

    def download(self, pending: list[Asset]) -> None:
        """下載尚未成功的文件；下載後判斷格式，格式未啟用者標記略過。"""
        urls = [
            asset.url
            for asset in pending
            if self._entries.get(asset.url, DocumentEntry()).download_status
            != "success"
        ]
        if not urls:
            return

        with TaskCountProgress() as progress:
            task_id = progress.add_task("Downloading documents...", total=len(urls))
            results = self.downloader.download(
                urls, on_complete=lambda _result: progress.update(task_id, advance=1)
            )

        for url in urls:
            self._entries[url] = self._to_entry(url, results[url])

    def _to_entry(self, url: str, result: DownloadResult) -> DocumentEntry:
        if not result.ok:
            reason = result.error or "download failed"
            logger.warning("Document download failed - %s (url=%s)", reason, url)
            return DocumentEntry(
                download_status="failed",
                failure_reason=reason,
                recoverable=result.recoverable,
            )

        assert result.content is not None
        file_format = detect_format(result.content, result.headers, result.final_url)
        file_name = (
            disposition_file_name(result.headers)
            or url_file_name(result.final_url)
            or url_file_name(url)
            or ""
        )
        entry = DocumentEntry(
            download_status="success",
            file_name=file_name,
            content_type=result.headers.get("content-type", "").split(";")[0].strip(),
            downloaded_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )
        if file_format is None or file_format not in self.options.formats:
            entry.skip_reason = f"format {file_format or 'unknown'} not enabled"
            logger.info("Document skipped (%s): %s", entry.skip_reason, url)
            return entry

        entry.file_format = file_format
        entry.content = result.content
        entry.content_sha1 = hashlib.sha1(result.content).hexdigest()
        return entry

    # ===== 解析 =====

    def parse(self) -> list[Asset]:
        """解析尚未解析的不重複內容（以第一個 URL 的檔案為代表）。

        回傳本輪新產生的文件內嵌圖片資源（kind="image"，不需下載；URL 為 doc-image:<內容 sha1>，
        同一張圖在多份文件中只有一個資源，引用處依文件記錄）。
        """
        to_parse = {
            sha: entry
            for sha, (_, entry) in self._representatives().items()
            if sha not in self._parsed
        }
        if not to_parse:
            return []

        def parse_one(
            item: tuple[str, DocumentEntry],
        ) -> tuple[str, ParsedDocument | DocumentParseError]:
            sha, entry = item
            try:
                return sha, parse_document(
                    entry.content, entry.file_format, self.extract_images
                )
            except DocumentParseError as e:
                return sha, e

        with TaskCountProgress() as progress:
            task_id = progress.add_task("Parsing documents...", total=len(to_parse))
            workers = min(PARSE_MAX_WORKERS, os.cpu_count() or 1)
            with ThreadPoolExecutor(max_workers=workers) as executor:
                for sha, outcome in executor.map(parse_one, to_parse.items()):
                    self._parsed[sha] = outcome
                    progress.update(task_id, advance=1)

        new_images: dict[str, Asset] = {}
        for sha in to_parse:
            outcome = self._parsed[sha]
            if isinstance(outcome, DocumentParseError):
                logger.warning("Document parse failed - %s", outcome)
                continue
            self._register_images(sha, outcome, new_images)
        return list(new_images.values())

    def _register_images(
        self, document_sha: str, outcome: ParsedDocument, new_images: dict[str, Asset]
    ) -> None:
        """把文件內嵌圖片登記為圖片資源（同一張圖只一個資源，引用處記錄所在文件）。"""
        label = document_label(document_sha)
        urls: list[str | None] = []
        for index, image in enumerate(outcome.images, 1):
            if image is None:
                urls.append(None)
                continue
            url = "doc-image:" + hashlib.sha1(image.content).hexdigest()
            urls.append(url)
            if url not in self.image_contents:
                self.image_contents[url] = image
                new_images[url] = Asset(url=url, kind="image")
            asset = new_images.get(url)
            if asset is not None:
                asset.refs.append(AssetRef(page_key=label, text=f"Image-{index}"))
        self._image_urls[document_sha] = urls

    def _representatives(self) -> dict[str, tuple[Asset, DocumentEntry]]:
        """已下載且格式啟用的文件，依內容 sha1 分組後的代表（資源順序中的第一個）。"""
        representatives: dict[str, tuple[Asset, DocumentEntry]] = {}
        for asset in self.assets:
            entry = self._entries.get(asset.url)
            if entry is None or not entry.content_sha1:
                continue
            representatives.setdefault(entry.content_sha1, (asset, entry))
        return representatives

    # ===== 本輪結果與重試 =====

    def is_success(self, asset: Asset) -> bool:
        """代表圖片以外的重複內容不單獨計成功；成功 = 下載成功且解析成功的不重複內容。"""
        entry = self._entries.get(asset.url)
        if entry is None or not entry.content_sha1:
            return False
        representative, _ = self._representatives()[entry.content_sha1]
        return representative.url == asset.url and isinstance(
            self._parsed.get(entry.content_sha1), ParsedDocument
        )

    def recoverable_failures(self, pending: Iterable[Asset]) -> list[Asset]:
        """可恢復的失敗（只有下載的逾時、連線錯誤、5xx、429、403）；解析失敗與格式不符為永久失敗。"""
        return [
            asset
            for asset in pending
            if (entry := self._entries.get(asset.url)) is not None
            and entry.download_status == "failed"
            and entry.recoverable
        ]

    def reset(self, assets: Iterable[Asset]) -> None:
        """重試前清除失敗的下載記錄。"""
        for asset in assets:
            self._entries.pop(asset.url, None)

    # ===== 回寫 =====

    def write_back(
        self,
        crawl_results: dict[str, dict[str, Any]],
        caption_for: Callable[[str], str] | None = None,
    ) -> None:
        """每份不重複的文件寫成 crawl_results 的獨立 entry，原檔記入 self.files。

        caption_for：圖片資源 URL → 描述（空字串為沒有描述）；文件內的圖片佔位符以與頁面圖片
        相同的格式取代為描述，沒有描述者移除。"""
        groups: dict[str, list[Asset]] = {}
        for asset in self.assets:
            entry = self._entries.get(asset.url)
            if entry is not None and entry.content_sha1:
                groups.setdefault(entry.content_sha1, []).append(asset)

        self.files = {}
        page_urls = {key: page.get("url", "") for key, page in crawl_results.items()}
        for sha, members in groups.items():
            outcome = self._parsed.get(sha)
            if not isinstance(outcome, ParsedDocument):
                continue

            representative = members[0]
            entry = self._entries[representative.url]
            key = document_key(representative.url)
            refs = [ref for member in members for ref in member.refs]
            markdown = self._insert_captions(sha, outcome.markdown, caption_for)
            title = choose_title(
                refs,
                file_name=entry.file_name,
                markdown=markdown,
                fallback=url_file_name(representative.url) or key,
            )
            file_name = f"{key}.{entry.file_format}"
            self.files[key] = DocumentFile(file_name=file_name, content=entry.content)
            crawl_results[key] = {
                "url": representative.url,
                "title": title,
                "enhanced_markdown": markdown,
                "images": [],
                "metadata": {
                    "description": "",
                    "page_type": "document",
                    "file_format": entry.file_format,
                    "file_name": entry.file_name,
                    "file_size": len(entry.content),
                    "content_type": entry.content_type,
                    "downloaded_at": entry.downloaded_at,
                    "file_path": f"files/{file_name}",
                    "alternate_urls": [m.url for m in members[1:]],
                    "source_pages": _source_pages(refs, page_urls),
                },
                "crawl_info": {},
            }

    def _insert_captions(
        self,
        document_sha: str,
        markdown: str,
        caption_for: Callable[[str], str] | None,
    ) -> str:
        """第 n 個佔位符取代為第 n 張圖片的描述區塊（`Image-{n}` 為文件內圖片序號）。"""
        urls = self._image_urls.get(document_sha, [])
        counter = iter(range(1, len(urls) + 1))

        def replace(_match: re.Match[str]) -> str:
            index = next(counter, None)
            if index is None:  # 佔位符比圖片多：無法對位，移除
                return ""
            url = urls[index - 1]
            caption = caption_for(url) if url and caption_for else ""
            return caption_block(index, caption).rstrip("\n") if caption else ""

        markdown = IMAGE_PLACEHOLDER_PATTERN.sub(replace, markdown)
        markdown = re.sub(r"^\s*[-*]\s*$", "", markdown, flags=re.MULTILINE)
        return re.sub(r"\n{3,}", "\n\n", markdown).strip()

    # ===== 統計與 log =====

    def stats(self) -> DocumentStats:
        stats = DocumentStats(
            collected=len(self.assets),
            skipped_format=len(self.skipped_format),
            skipped_domain=self.skipped_domain,
            skipped_by_format=Counter(self.skipped_format.values()),
        )
        for asset in self.assets:
            entry = self._entries.get(asset.url)
            if entry is None or entry.download_status == "failed":
                stats.download_failure += 1
            elif entry.skip_reason:
                stats.format_skipped += 1
        for sha, (_, entry) in self._representatives().items():
            if isinstance(self._parsed.get(sha), ParsedDocument):
                stats.success += 1
            else:
                stats.parse_failure += 1
        stats.duplicate_content = sum(
            1
            for a in self.assets
            if self._entries.get(a.url, DocumentEntry()).content_sha1
        ) - len(self._representatives())
        return stats

    def failed_documents(self) -> dict[str, tuple[str, str]]:
        """最終仍失敗的文件：url → (第一個引用頁面, 原因)；格式未啟用不算失敗。"""
        failed: dict[str, tuple[str, str]] = {}
        for asset in self.assets:
            entry = self._entries.get(asset.url)
            if entry is not None and entry.download_status == "failed":
                failed[asset.url] = (asset.first_page, entry.failure_reason)
        for asset, entry in self._representatives().values():
            outcome = self._parsed.get(entry.content_sha1)
            if isinstance(outcome, DocumentParseError):
                failed[asset.url] = (asset.first_page, f"parse failed: {outcome}")
        return failed

    def log_summary(self) -> None:
        stats = self.stats()
        log_session("Document Stats", style="green")
        table = Table(show_header=True, header_style="bold green")
        table.add_column("Metric", style="green", no_wrap=True)
        table.add_column("Value", style="white")
        rows = {
            "collected": stats.collected,
            "skipped (format not enabled, by URL)": stats.skipped_format,
            "skipped (outside allowed domains)": stats.skipped_domain,
            "download_failure": stats.download_failure,
            "skipped (format not enabled, by content)": stats.format_skipped,
            "parse_failure": stats.parse_failure,
            "duplicate_content": stats.duplicate_content,
            "success": stats.success,
        }
        for metric, value in rows.items():
            table.add_row(metric, str(value))
        print_log(table)
        if stats.skipped_by_format:
            logger.info(
                "Skipped by URL extension: %s",
                ", ".join(
                    f"{k}={v}" for k, v in sorted(stats.skipped_by_format.items())
                ),
            )


def document_label(document_sha: str) -> str:
    """文件內嵌圖片在統計表中的「頁面」名稱（以內容 sha1 為準，不受代表 URL 變動影響）。"""
    return f"doc-{document_sha[:12]}"


def document_key(url: str) -> str:
    """文件 entry 的鍵（即 md 檔名）：`doc_` + 正規化 URL sha1 前 12 碼。

    穩定、不撞名、與頁面鍵可區分（頁面鍵規則會丟棄 query，下載 API 的連結會全部撞成同一個鍵）。
    """
    return "doc_" + hashlib.sha1(url.encode()).hexdigest()[:12]


def _source_pages(
    refs: list[AssetRef], page_urls: dict[str, str]
) -> list[dict[str, str]]:
    """引用頁面（依首次引用順序、不重複）：URL、頁面標題（頁面鍵）、該頁的連結文字。"""
    pages: dict[str, dict[str, str]] = {}
    for ref in refs:
        page = pages.setdefault(
            ref.page_key,
            {
                "url": page_urls.get(ref.page_key, ""),
                "title": ref.page_key,
                "link_text": "",
            },
        )
        text = clean_link_text(ref.text)
        if not page["link_text"] and text and not is_generic(text):
            page["link_text"] = text
    return list(pages.values())
