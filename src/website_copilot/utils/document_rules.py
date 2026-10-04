"""文件 URL 規則：爬蟲（排除文件 URL）與 augmenter 的 DocumentCollector 共用。

通用副檔名為程式常數；站點專屬樣式（如下載 API）由 `SiteConfig.documents.url_patterns` 提供。
"""

import re
from collections.abc import Iterable
from fnmatch import fnmatchcase
from urllib.parse import urlsplit, urlunsplit

DOCUMENT_EXTENSIONS: tuple[str, ...] = (
    "pdf",
    "doc",
    "docx",
    "odt",
    "xls",
    "xlsx",
    "ods",
    "ppt",
    "pptx",
    "odp",
)

# 只比對 path 的副檔名（不分大小寫，query／fragment 之後不算），`pdf.gif%20` 之類不會命中
DOCUMENT_EXTENSION_PATTERN = re.compile(
    rf"^[^?#]*\.(?:{'|'.join(DOCUMENT_EXTENSIONS)})(?:[?#]|$)", re.IGNORECASE
)


def is_document_url(url: str, site_patterns: Iterable[str] = ()) -> bool:
    """URL 是否為文件：副檔名屬於通用清單，或符合站點樣式（glob，全 URL 比對）。"""
    if DOCUMENT_EXTENSION_PATTERN.match(url):
        return True
    return any(fnmatchcase(url, pattern) for pattern in site_patterns)


def normalize_url(url: str) -> str:
    """文件 URL 的去重鍵：scheme／host 轉小寫、去掉 fragment；path 與 query 原樣保留
    （站點的下載 API 以 query 區分檔案）。"""
    parts = urlsplit(url.strip())
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path, parts.query, "")
    )
