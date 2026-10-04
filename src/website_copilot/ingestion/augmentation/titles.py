"""文件標題（規則產生，不用 LLM）。

優先序：連結文字（排除通用字，取各引用處最常出現者）> 連結的 title 屬性 >
非純數字的原始檔名 > 內文第一個 heading > 原始檔名（含純數字）。
PDF 內嵌 metadata 標題不採用（實測可能是多年前的舊範本標題）。
"""

import re
from collections import Counter
from pathlib import PurePosixPath

from website_copilot.ingestion.augmentation.assets import AssetRef
from website_copilot.utils.document_rules import DOCUMENT_EXTENSIONS

# 「按我取得詳細資訊」「附件」「下載」等不具標題意義的連結文字
GENERIC_PHRASES = tuple(
    sorted(
        (
            "按我取得詳細資訊",
            "取得詳細資訊",
            "詳細資訊",
            "另開新視窗",
            "點此下載",
            "按此下載",
            "點我下載",
            "下載",
            "附件",
            "檔案",
            "點此",
            "點我",
            "按此",
            "請按此",
            "連結",
            "更多",
            "download",
            "click here",
            "attachment",
            "more",
        ),
        key=len,
        reverse=True,
    )
)

_IMAGE_MARKDOWN = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_EXTENSION_SUFFIX = re.compile(
    rf"\.(?:{'|'.join(DOCUMENT_EXTENSIONS)})$", re.IGNORECASE
)
_PUNCTUATION_ONLY = re.compile(r"[\W_]*", re.UNICODE)
_HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)


def clean_link_text(text: str) -> str:
    """連結文字去掉圖示圖片、多餘空白、成對外的引號與副檔名。"""
    text = _IMAGE_MARKDOWN.sub(" ", text)
    text = re.sub(r"(\*\*|__|`)", "", text)  # 行內強調標記
    text = re.sub(r"\s+", " ", text).strip(" 　「」\"'")
    return _EXTENSION_SUFFIX.sub("", text).strip()


def is_generic(text: str) -> bool:
    """連結文字扣掉通用字與標點後沒有剩餘內容。"""
    remainder = text.lower()
    for phrase in GENERIC_PHRASES:
        remainder = remainder.replace(phrase, "")
    return _PUNCTUATION_ONLY.fullmatch(remainder) is not None


def _most_common(candidates: list[str]) -> str | None:
    usable = [c for c in candidates if c and not is_generic(c)]
    if not usable:
        return None
    counts = Counter(usable)
    best = max(counts.values())
    return next(c for c in usable if counts[c] == best)  # 並列時取最早出現者


def _file_stem(file_name: str | None) -> str | None:
    if not file_name:
        return None
    return PurePosixPath(file_name).stem or None


def choose_title(
    refs: list[AssetRef],
    *,
    file_name: str | None,
    markdown: str,
    fallback: str,
) -> str:
    """依優先序產生文件標題；fallback 為最後的保底（如 URL 檔名或 entry 鍵）。"""
    title = _most_common([clean_link_text(ref.text) for ref in refs])
    if title:
        return title

    title = _most_common([clean_link_text(ref.title) for ref in refs])
    if title:
        return title

    stem = _file_stem(file_name)
    if stem and not stem.isdigit():
        return stem

    match = _HEADING.search(markdown)
    if match:
        return match.group(1).strip()

    return stem or fallback
