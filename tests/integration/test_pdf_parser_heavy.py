"""PDF 解析：實際呼叫 Docling（heavy：載入版面／OCR 模型，首次會下載模型，較慢；不產生費用）。"""

from pathlib import Path

import pytest

from website_copilot.ingestion.augmentation.processors.document_parser import (
    parse_document,
)

LECTURE_PDF = Path("tests/fixtures/documents/lecture.pdf")


@pytest.mark.heavy
def test_docling_extracts_text_from_small_pdf() -> None:
    parsed = parse_document(LECTURE_PDF.read_bytes(), "pdf")

    assert "Toward B5G/6G Mobile Edge Intelligence" in parsed.markdown
    assert "Abstract" in parsed.markdown


@pytest.mark.heavy
def test_docling_extracts_meaningful_pictures_in_placeholder_order() -> None:
    """報名流程通知：版面模型挑出 7 張有意義的圖（流程圖與系統截圖），與佔位符一一對應。"""
    content = Path("tests/fixtures/documents/notice_with_images.pdf").read_bytes()

    parsed = parse_document(content, "pdf", extract_images=True)

    assert parsed.markdown.count("<!-- image -->") == len(parsed.images) == 7
    assert all(image is not None for image in parsed.images)
    assert all(image.media_type == "image/png" for image in parsed.images if image)
    assert max(len(image.content) for image in parsed.images if image) > 10_000
