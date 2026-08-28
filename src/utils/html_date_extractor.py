"""HTML 日期擷取模組 — 從 HTML 原始碼 + HTTP 標頭解析發佈/修改日期。

解析優先級：
  1. JSON-LD datePublished
  2. <meta property="article:published_time">
  3. <time datetime> with itemprop="datePublished"
  4. Generic meta name="date" / "pubdate"
  5. Dublin Core dc.date
  6. HTTP Last-Modified

回傳 ISO 8601 格式（YYYY-MM-DD）。無法擷取時對應值為 None。
"""

import json
import logging
import re
from datetime import datetime
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def _extract_from_jsonld(soup: BeautifulSoup) -> tuple[str | None, str | None]:
    """從 JSON-LD 擷取 datePublished / dateModified。"""
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.string or "")
            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict):
                    pub = item.get("datePublished") or item.get("dateCreated")
                    mod = item.get("dateModified")
                    if pub or mod:
                        return pub, mod
        except (json.JSONDecodeError, TypeError):
            continue
    return None, None


def _extract_meta_property(soup: BeautifulSoup, prop: str) -> str | None:
    """從 `<meta property="...">` 擷取 content 屬性。"""
    tag = soup.select_one(f'meta[property="{prop}"]')
    content = tag.get("content") if tag else None
    return str(content) if content is not None else None


def _extract_time_element(soup: BeautifulSoup) -> str | None:
    """從 `<time>` 元素擷取 datetime 屬性。"""
    for selector in (
        'time[itemprop="datePublished"]',
        "time[datetime]",
    ):
        tag = soup.select_one(selector)
        if tag:
            dt = tag.get("datetime")
            if dt is not None:
                return str(dt)
    return None


def _extract_meta_name(soup: BeautifulSoup, names: tuple[str, ...]) -> str | None:
    """從 `<meta name="...">` 擷取 content 屬性（不區分大小寫）。"""
    for name in names:
        tag = soup.select_one(f'meta[name="{name}" i]')
        if tag:
            content = tag.get("content")
            if content is not None:
                return str(content)
    return None


def _parse_http_date(date_str: str | None) -> str | None:
    """解析 HTTP 日期格式（RFC 7231），回傳 ISO 8601。"""
    if not date_str:
        return None
    try:
        return parsedate_to_datetime(date_str).isoformat()
    except (ValueError, TypeError):
        return None


def _normalize_to_iso8601(date_str: str | None) -> str | None:
    """嘗試將各種日期格式標準化為 ISO 8601（YYYY-MM-DD）。"""
    if not date_str:
        return None
    if re.match(r"\d{4}-\d{2}-\d{2}", date_str):
        return date_str[:10]
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def extract_date_from_html(
    html: str,
    response_headers: dict[str, str] | None = None,
) -> dict[str, str | None]:
    """從 HTML 原始碼 + HTTP 標頭擷取發佈/修改日期。

    回傳 ISO 8601 格式（YYYY-MM-DD）。無法擷取時對應值為 None。
    """
    published_date: str | None = None
    modified_date: str | None = None

    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        logger.warning(
            "BeautifulSoup parsing failed, skipping HTML date extraction",
            exc_info=True,
        )
        return {"published_date": None, "modified_date": None}

    # --- Priority 1: JSON-LD datePublished / dateModified ---
    published_date, modified_date = _extract_from_jsonld(soup)

    # --- Priority 2: <meta property="article:published_time"> ---
    if published_date is None:
        published_date = _extract_meta_property(soup, "article:published_time")

    # --- Priority 3: <time datetime> elements ---
    if published_date is None:
        published_date = _extract_time_element(soup)

    # --- Priority 4: Generic meta date tags ---
    if published_date is None:
        published_date = _extract_meta_name(soup, ("date", "pubdate", "publish_date"))

    # --- Priority 5: Dublin Core dc.date ---
    if published_date is None:
        published_date = _extract_meta_name(soup, ("dc.date", "dc.date.created"))

    # --- Priority 6: HTTP Last-Modified ---
    if published_date is None and response_headers:
        published_date = _parse_http_date(response_headers.get("Last-Modified"))

    # modified_date 從 article:modified_time 補充
    if modified_date is None:
        modified_date = _extract_meta_property(soup, "article:modified_time")

    return {
        "published_date": _normalize_to_iso8601(published_date),
        "modified_date": _normalize_to_iso8601(modified_date),
    }
