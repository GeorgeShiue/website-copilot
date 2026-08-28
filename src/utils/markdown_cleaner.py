"""Markdown 清洗模組 — 純函數式的 Markdown 內容清理與格式化。

提供 clean_markdown / promote_empty_heading_line 兩個公開函數，
以及所有相關正則常數。無任何類別狀態依賴。
"""

import logging
import re

import mdformat

logger = logging.getLogger(__name__)


# ── 正則常數 ─────────────────────────────────────────────────────────

EMPTY_ANCHOR_LINK_PATTERN = re.compile(r"\[\]\(.*?#h\.[a-z0-9]+\)")
EMPTY_LIST_NOISE_PATTERN = re.compile(r"^\s*\*\s*#{1,6}\s*$", flags=re.MULTILINE)
EMPTY_HEADING_LINE_PATTERN = re.compile(r"^(\s{0,3}#{1,6})\s*$")
SKIP_AS_HEADING_PATTERN = re.compile(r"^\s*!?\[.*?\]\(.*?\)\s*$")
IMAGE_ABOVE_SPACING_PATTERN = re.compile(
    r"([^\n])\n(?=[ \t]*!\[.*?\]\()", flags=re.MULTILINE
)
IMAGE_FOLLOW_TEXT_PATTERN = re.compile(r"(!\[.*?\]\(.*?\))\s*(?=\S)")


# ── 公開函數 ─────────────────────────────────────────────────────────


def promote_empty_heading_line(fit_markdown: str) -> str:
    """將空標題行提升為下一個可用文字標題，並保留中間內容。"""
    lines = fit_markdown.splitlines(keepends=True)
    fixed_lines: list[str] = []
    i = 0

    while i < len(lines):
        current_line = lines[i]
        heading_match = EMPTY_HEADING_LINE_PATTERN.match(current_line.rstrip("\r\n"))
        if heading_match:
            j = i + 1
            while j < len(lines):
                candidate = lines[j].strip()
                if candidate and not SKIP_AS_HEADING_PATTERN.match(candidate):
                    fixed_lines.append(f"{heading_match.group(1)} {candidate}\n")
                    fixed_lines.extend(lines[i + 1 : j])
                    i = j + 1
                    break
                j += 1
            else:
                fixed_lines.append(current_line)
                i += 1
        else:
            fixed_lines.append(current_line)
            i += 1

    return "".join(fixed_lines)


def clean_markdown(
    markdown: str,
    exclude_words: list[str] | None = None,
) -> str:
    """Markdown 清理：Regex 預處理 + mdformat 格式化 + 結構修復。

    Args:
        markdown: 原始 Markdown 文字。
        exclude_words: 要排除的關鍵字列表（行級過濾）。
    """
    # --- 資料清洗 ---
    if exclude_words is not None:
        markdown = "".join(
            line
            for line in markdown.splitlines(keepends=True)
            if not any(word in line for word in exclude_words)
        )
    markdown = EMPTY_ANCHOR_LINK_PATTERN.sub("", markdown)
    markdown = EMPTY_LIST_NOISE_PATTERN.sub("", markdown)

    # ----- 結構修復 (前) -----
    markdown = promote_empty_heading_line(markdown)
    markdown = IMAGE_ABOVE_SPACING_PATTERN.sub(r"\1\n\n", markdown)

    # ----- 格式化 -----
    try:
        markdown = mdformat.text(
            markdown,
            options={"wrap": "no"},
            extensions={"gfm"},
        )
    except (ValueError, KeyError) as e:
        logger.warning("mdformat failed, using unformatted markdown: %s", e)

    # ----- 結構修復 (後) -----
    markdown = IMAGE_FOLLOW_TEXT_PATTERN.sub(r"\1\n", markdown)
    markdown = IMAGE_ABOVE_SPACING_PATTERN.sub(r"\1\n\n", markdown)

    return markdown
