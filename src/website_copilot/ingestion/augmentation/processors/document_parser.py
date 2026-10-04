"""文件解析：原始檔位元組 → Markdown（依實際格式選擇解析器）。

PDF 以 Docling 轉換（processors/pdf_parser.py）；docx／doc／odt 等 Office 格式以 anydoc 轉換
（Rust，不需 LibreOffice，processors/office_parser.py）。內嵌圖片以 `<!-- image -->` 佔位，
`ParsedDocument.images` 依佔位符順序提供圖片本身（描述由圖片階段產生後取代佔位符）。
"""

import re
from dataclasses import dataclass, field

from website_copilot.ingestion.augmentation.processors.images import (
    IMAGE_PLACEHOLDER_PATTERN,
    ParsedImage,
)
from website_copilot.ingestion.augmentation.processors.office_parser import (
    office_to_markdown,
)
from website_copilot.ingestion.augmentation.processors.pdf_parser import (
    pdf_to_markdown,
)


class DocumentParseError(Exception):
    """文件無法解析成有內容的 Markdown（永久失敗，重試不會改變結果）。"""


@dataclass
class ParsedDocument:
    markdown: str
    # 依佔位符順序；None 表示該位置的圖片取不到。沒有抽圖（或無法對位）時為空，
    # 此時 markdown 內已沒有佔位符
    images: list[ParsedImage | None] = field(default_factory=list)


def parse_document(
    content: bytes, file_format: str, extract_images: bool = False
) -> ParsedDocument:
    """解析文件；失敗（損毀、加密、需 OCR、沒有文字）時拋出 DocumentParseError。"""
    try:
        markdown, images = _parse(content, file_format, extract_images)
    except DocumentParseError:
        raise
    except Exception as e:  # anydoc 的 ConvertError／OSError、Docling 的轉換錯誤等
        raise DocumentParseError(f"{type(e).__name__}: {e}") from e

    if not images:  # 沒有可用的圖片：移除佔位符，避免雜訊進入文件內容
        markdown = _strip_placeholders(markdown)
    markdown = markdown.strip()
    if not markdown:
        raise DocumentParseError("no text content")
    return ParsedDocument(markdown=markdown, images=images)


def _parse(
    content: bytes, file_format: str, extract_images: bool
) -> tuple[str, list[ParsedImage | None]]:
    if file_format == "pdf":
        return pdf_to_markdown(content, extract_images)
    return office_to_markdown(content, file_format, extract_images)


def _strip_placeholders(markdown: str) -> str:
    markdown = IMAGE_PLACEHOLDER_PATTERN.sub("", markdown)
    return re.sub(r"\n{3,}", "\n\n", markdown)
