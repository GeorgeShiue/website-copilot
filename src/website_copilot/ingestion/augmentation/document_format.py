"""文件格式判斷與原始檔名。

格式優先序：檔頭 magic bytes（anydoc 依 PDF 標頭、OLE stream 名稱、ZIP 套件內容判斷）>
Content-Disposition 檔名 > Content-Type > URL 副檔名。站點的下載 API 回
`application/octet-stream` 且 URL 無副檔名，必須靠前兩者。
"""

import re
from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit

import anydoc

CONTENT_TYPE_FORMATS = {
    "application/pdf": "pdf",
    "application/msword": "doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.oasis.opendocument.text": "odt",
    "application/vnd.ms-excel": "xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.ms-powerpoint": "ppt",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
}

_FILENAME_STAR = re.compile(r"filename\*\s*=\s*(?:[\w-]+)'[^']*'([^;]+)", re.IGNORECASE)
_FILENAME = re.compile(r'filename\s*=\s*(?:"([^"]*)"|([^;]+))', re.IGNORECASE)


def disposition_file_name(headers: dict[str, str]) -> str | None:
    """Content-Disposition 的檔名（支援 filename*= 與百分比編碼的 filename=）。"""
    disposition = headers.get("content-disposition", "")
    match = _FILENAME_STAR.search(disposition)
    if match:
        return unquote(match.group(1).strip().strip('"')) or None
    match = _FILENAME.search(disposition)
    if match:
        return unquote((match.group(1) or match.group(2)).strip()) or None
    return None


def url_file_name(url: str) -> str | None:
    """URL path 的最後一段（含副檔名者才算檔名）。"""
    name = PurePosixPath(unquote(urlsplit(url).path)).name
    return name if "." in name else None


def _format_from_name(name: str | None) -> str | None:
    if not name or "." not in name:
        return None
    return anydoc.format_from_extension(name.rsplit(".", 1)[1].strip().lower())


def detect_format(content: bytes, headers: dict[str, str], url: str) -> str | None:
    """依優先序判斷文件格式（anydoc 的格式名稱，如 pdf、docx、doc、odt）；無法判斷回傳 None。"""
    detected = anydoc.format_from_bytes(content)
    if detected is not None:
        return detected

    from_disposition = _format_from_name(disposition_file_name(headers))
    if from_disposition is not None:
        return from_disposition

    content_type = headers.get("content-type", "").split(";")[0].strip().lower()
    if content_type in CONTENT_TYPE_FORMATS:
        return CONTENT_TYPE_FORMATS[content_type]

    return _format_from_name(url_file_name(url))
