"""Office 文件（docx／doc／odt…）→ Markdown：anydoc，並在內嵌圖片的位置放 `<!-- image -->` 佔位符。

anydoc 的 Markdown 輸出不含內嵌圖片，所以從文件模型（blocks）找出圖片所在的頂層 block，
再以該 block 的第一段文字為錨點，在 Markdown 中定位其結尾，把佔位符插在後面
（圖片在表格或清單中時，放在整個表格／該項目之後）。找不到錨點的圖片放在目前位置。
"""

import logging
from typing import Any

import anydoc

from website_copilot.ingestion.augmentation.processors.images import (
    IMAGE_PLACEHOLDER,
    ParsedImage,
)

logger = logging.getLogger(__name__)

ANCHOR_CHARS = 30


def office_to_markdown(
    content: bytes, file_format: str, extract_images: bool
) -> tuple[str, list[ParsedImage | None]]:
    """回傳 (Markdown, 圖片)；圖片依佔位符出現順序排列（extract_images 為 False 時為空、無佔位符）。"""
    markdown = anydoc.to_markdown_bytes(content, file_format)  # type: ignore[arg-type]
    if not extract_images:
        return markdown, []

    document = anydoc.to_document(content, file_format)  # type: ignore[arg-type]
    if not document.assets:
        return markdown, []
    try:
        return _insert_placeholders(markdown, document)
    except Exception:  # 定位失敗不影響文字：退回不含圖片
        logger.warning("Failed to place embedded images; skipping them", exc_info=True)
        return markdown, []


def _insert_placeholders(
    markdown: str, document: Any
) -> tuple[str, list[ParsedImage | None]]:
    insertions: list[tuple[int, int]] = []  # (插入位置, asset id)
    cursor = 0
    for block in document.blocks:
        anchor = _first_text(block)
        if anchor:
            found = markdown.find(anchor[:ANCHOR_CHARS], cursor)
            if found >= 0:
                end = markdown.find("\n\n", found)
                cursor = len(markdown) if end < 0 else end
        for asset_id in _image_asset_ids(block):
            insertions.append((cursor, asset_id))

    images: list[ParsedImage | None] = []
    parts: list[str] = []
    position = 0
    for at, asset_id in insertions:
        parts.append(markdown[position:at])
        parts.append(f"\n\n{IMAGE_PLACEHOLDER}")
        position = at
        asset = document.assets[asset_id]
        images.append(
            ParsedImage(content=bytes(asset.data), media_type=asset.media_type)
        )
    parts.append(markdown[position:])
    return "".join(parts), images


def _first_text(block: Any) -> str:
    """block 內第一段非空白文字（錨點）。"""
    for text in _texts(block):
        stripped = text.strip()
        if stripped:
            return stripped
    return ""


def _texts(block: Any) -> Any:
    if block.content:
        for inline in block.content:
            yield from _inline_texts(inline)
    if block.text:
        yield block.text
    if block.list:
        for item in block.list.items:
            for child in item.blocks:
                yield from _texts(child)
    if block.table:
        for row in block.table.grid:
            for slot in row:
                if slot.cell:
                    for child in slot.cell.blocks:
                        yield from _texts(child)
    if block.blocks:
        for child in block.blocks:
            yield from _texts(child)


def _inline_texts(inline: Any) -> Any:
    if inline.kind == "text" and inline.text:
        yield inline.text
    elif inline.kind == "link" and inline.content:
        for child in inline.content:
            yield from _inline_texts(child)


def _image_asset_ids(block: Any) -> list[int]:
    """block 內（含清單、表格、引言中）依出現順序的內嵌圖片 asset id。"""
    ids: list[int] = []
    for inline in block.content or []:
        ids.extend(_inline_image_ids(inline))
    for item in block.list.items if block.list else []:
        for child in item.blocks:
            ids.extend(_image_asset_ids(child))
    if block.table:
        for row in block.table.grid:
            for slot in row:
                if slot.cell:
                    for child in slot.cell.blocks:
                        ids.extend(_image_asset_ids(child))
    for child in block.blocks or []:
        ids.extend(_image_asset_ids(child))
    return ids


def _inline_image_ids(inline: Any) -> list[int]:
    if inline.kind == "image":
        source = inline.source
        if (
            source is not None
            and source.kind == "asset"
            and source.asset_id is not None
        ):
            return [source.asset_id]
        return []
    ids: list[int] = []
    for child in inline.content or []:
        ids.extend(_inline_image_ids(child))
    return ids
