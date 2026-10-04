"""PDF 解析：以 fake converter 測試（不載入 Docling 模型）。

延遲載入、converter 只建立一次且呼叫序列化、佔位符保留、無文字層（掃描版）視為失敗、
解析器分派與整個 PDF 文件流程。實際呼叫 Docling 的測試見 tests/integration/test_pdf_parser_heavy.py（heavy）。
"""

import threading
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from augmentation_fakes import FakeDownloader

from website_copilot.ingestion.augmentation.augmenter import Augmenter
from website_copilot.ingestion.augmentation.documents import (
    DocumentOptions,
    document_key,
)
from website_copilot.ingestion.augmentation.processors import (
    document_parser,
    pdf_parser,
)
from website_copilot.ingestion.augmentation.processors.document_parser import (
    DocumentParseError,
    parse_document,
)

BASE = "https://www.csie.ncu.edu.tw"
PDF_BYTES = b"%PDF-1.7\n%fake pdf body"
ODT = Path("tests/fixtures/documents/form.odt").read_bytes()


class _FakeConverter:
    def __init__(self, markdown: str = "# 標題\n\n內文\n\n<!-- image -->\n") -> None:
        self.markdown = markdown
        self.calls = 0
        self.in_flight = 0
        self.peak = 0

    def convert(self, stream: Any) -> Any:
        self.calls += 1
        self.in_flight += 1
        self.peak = max(self.peak, self.in_flight)
        time.sleep(0.02)
        self.in_flight -= 1
        return SimpleNamespace(
            document=SimpleNamespace(export_to_markdown=lambda: self.markdown)
        )


@pytest.fixture
def converter(monkeypatch: pytest.MonkeyPatch) -> _FakeConverter:
    fake = _FakeConverter()
    monkeypatch.setattr(pdf_parser, "_converter", fake)
    return fake


def test_pdf_markdown_keeps_image_placeholder(converter: _FakeConverter) -> None:
    markdown, images = pdf_parser.pdf_to_markdown(PDF_BYTES, extract_images=False)

    assert markdown == "# 標題\n\n內文\n\n<!-- image -->\n"
    assert images == []
    assert converter.calls == 1


@pytest.mark.parametrize("markdown", ["", "   \n", "<!-- image -->\n\n<!-- image -->"])
def test_pdf_without_text_layer_fails(
    monkeypatch: pytest.MonkeyPatch, markdown: str
) -> None:
    monkeypatch.setattr(pdf_parser, "_converter", _FakeConverter(markdown))

    with pytest.raises(DocumentParseError, match="no text layer|no text content"):
        parse_document(PDF_BYTES, "pdf")


def test_conversion_errors_become_parse_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    class Broken:
        def convert(self, stream: Any) -> Any:
            raise RuntimeError("corrupt pdf")

    monkeypatch.setattr(pdf_parser, "_converter", Broken())

    with pytest.raises(DocumentParseError, match="RuntimeError: corrupt pdf"):
        parse_document(PDF_BYTES, "pdf")


def test_converter_is_created_lazily_once_and_calls_are_serialized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    created: list[_FakeConverter] = []

    def fake_get() -> _FakeConverter:
        if not created:
            created.append(_FakeConverter())
        return created[0]

    monkeypatch.setattr(pdf_parser, "_get_converter", fake_get)
    assert created == []  # 匯入與設定時不建立（Docling 延遲到第一份 PDF 才載入）

    threads = [
        threading.Thread(target=pdf_parser.pdf_to_markdown, args=(PDF_BYTES, False))
        for _ in range(6)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(created) == 1
    assert created[0].calls == 6
    assert created[0].peak == 1  # 鎖：同一時間只有一個轉換


def test_dispatcher_sends_pdf_to_docling_and_office_to_anydoc(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: list[str] = []
    monkeypatch.setattr(
        document_parser,
        "pdf_to_markdown",
        lambda content, extract_images: called.append("pdf") or ("# pdf text", []),
    )

    assert parse_document(PDF_BYTES, "pdf").markdown == "# pdf text"
    assert "研究生論文指導變更申請表" in parse_document(ODT, "odt").markdown
    assert called == ["pdf"]


def test_pdf_documents_become_entries_and_scanned_pdf_is_recorded_as_failed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    text_pdf, scanned_pdf = f"{BASE}/rules.pdf", f"{BASE}/scan.pdf"
    contents = {text_pdf: PDF_BYTES + b"A", scanned_pdf: PDF_BYTES + b"B"}

    def fake_pdf_to_markdown(content: bytes, extract_images: bool) -> tuple[str, list]:
        if content.endswith(b"B"):
            raise ValueError("no text layer (scanned or image-only PDF)")
        return "# 辦法\n\n第一條", []

    monkeypatch.setattr(document_parser, "pdf_to_markdown", fake_pdf_to_markdown)
    web = FakeDownloader(contents=contents)
    crawl_results = {
        "p": {
            "url": f"{BASE}/p",
            "fit_markdown": f"[修業辦法]({text_pdf})\n[掃描檔]({scanned_pdf})",
            "images": [],
        }
    }
    augmenter = Augmenter(downloader=web, success_threshold=0.8, max_retries=2)

    results = augmenter.augment(
        crawl_results,
        model="gpt-test",
        prompt="describe",
        image_max_concurrency=1,
        image_source="markdown",
        image_min_size=100,
        images_enabled=False,
        documents=DocumentOptions(formats=("pdf", "odt")),
    )

    key = document_key(text_pdf)
    assert results[key]["metadata"]["file_format"] == "pdf"
    assert results[key]["title"] == "修業辦法"
    assert results[key]["enhanced_markdown"] == "# 辦法\n\n第一條"
    assert augmenter.document_files[key].file_name == f"{key}.pdf"
    assert document_key(scanned_pdf) not in results
    reason = augmenter._failed_documents[scanned_pdf][1]
    assert reason.startswith("parse failed") and "no text layer" in reason
    assert web.downloads.count(scanned_pdf) == 1  # 解析失敗不重試
