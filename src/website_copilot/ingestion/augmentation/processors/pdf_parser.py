"""PDF 解析：Docling（版面模型還原標題層級、條列與表格，並挑出有意義的圖片與位置）。

Docling 依賴很重（torch、版面／表格模型、OCR 模型），所以延遲到第一份 PDF 才載入；
converter 只建立一次並以鎖序列化呼叫（模型共用 GPU，且 DocumentConverter 不保證執行緒安全）。
首次載入會下載模型（HuggingFace 與 RapidOCR 的模型快取），之後每份約數秒。

圖片：Markdown 內以 `<!-- image -->` 佔位，與文件中的圖片（`PictureItem`，依閱讀順序）一一對應；
版面模型只挑有意義的圖（實測 36 張內嵌圖只辨識出 7 張系統截圖），含整頁校徽底圖與遮罩的圖不會被選到。
掃描版 PDF（沒有文字層、整頁是一張圖）抽不到文字：視為解析失敗並略過，OCR 另案處理。
"""

import io
import logging
import threading
from typing import Any

from website_copilot.ingestion.augmentation.processors.images import (
    IMAGE_PLACEHOLDER_PATTERN,
    ParsedImage,
)

logger = logging.getLogger(__name__)

# 圖片以 2 倍解析度裁切，描述（VLM）才看得清楚截圖中的小字
IMAGES_SCALE = 2.0

_lock = threading.Lock()
_converter: Any = None


def _get_converter() -> Any:
    """延遲建立 DocumentConverter（呼叫端須持有 _lock）。OCR 維持 Docling 預設（開啟）。"""
    global _converter
    if _converter is None:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption

        logger.info("Loading Docling models (first PDF; may download models)...")
        options = PdfPipelineOptions()
        options.generate_picture_images = True
        options.images_scale = IMAGES_SCALE
        _converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
        )
    return _converter


def _pictures(document: Any) -> list[Any]:
    """文件中的圖片，依閱讀順序（與 Markdown 的佔位符順序相同）。"""
    from docling_core.types.doc import PictureItem  # pyright: ignore[reportPrivateImportUsage]

    return [
        item
        for item, _level in document.iterate_items()
        if isinstance(item, PictureItem)
    ]


def _encode_png(image: Any) -> ParsedImage:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return ParsedImage(content=buffer.getvalue(), media_type="image/png")


def pdf_to_markdown(
    content: bytes, extract_images: bool
) -> tuple[str, list[ParsedImage | None]]:
    """PDF 位元組 → (Markdown, 圖片)。

    Markdown 內的 `<!-- image -->` 佔位符與圖片依順序對應（extract_images 為 False 時圖片為空，
    佔位符由呼叫端移除）；圖片數與佔位符數不一致時（無法對位）不回傳圖片。

    Raises:
        ValueError: 抽不到任何文字（掃描版或只有圖片）。
        Exception: Docling 的轉換錯誤（呼叫端統一包成 DocumentParseError）。
    """
    from docling.datamodel.base_models import DocumentStream

    with _lock:
        converter = _get_converter()
        result = converter.convert(
            DocumentStream(name="document.pdf", stream=io.BytesIO(content))
        )
        document = result.document
        markdown: str = document.export_to_markdown()
        images: list[ParsedImage | None] = []
        if extract_images:
            pictures = _pictures(document)
            placeholders = len(IMAGE_PLACEHOLDER_PATTERN.findall(markdown))
            if len(pictures) == placeholders:
                images = [_picture_image(picture, document) for picture in pictures]
            elif placeholders:
                logger.warning(
                    "PDF has %s image placeholders but %s pictures; skipping images",
                    placeholders,
                    len(pictures),
                )

    if not IMAGE_PLACEHOLDER_PATTERN.sub("", markdown).strip():
        raise ValueError("no text layer (scanned or image-only PDF)")
    return markdown, images


def _picture_image(picture: Any, document: Any) -> ParsedImage | None:
    image = picture.get_image(document)
    return _encode_png(image) if image is not None else None
