"""文件 URL 規則與爬蟲排除文件的測試。

- is_document_url：副檔名（大小寫、query）、站點樣式；非文件 URL 不誤判。
- WebsiteCrawler 的 FilterChain：文件 URL 被排除、一般頁面通過。
- _filter_crawl_results：success=False 記錄實際錯誤訊息。
"""

import asyncio
import logging
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from website_copilot.config.site_config import SiteConfig, SiteDocumentsConfig
from website_copilot.ingestion.crawling.website_crawler import WebsiteCrawler
from website_copilot.utils.document_rules import is_document_url

BASE = "https://www.csie.ncu.edu.tw"
DOWNLOAD_API = f"{BASE}/app/index.php?Action=downloadfile&file=WVhSMFlXTm9"
SITE_PATTERNS = ["*Action=downloadfile*"]

DOCUMENT_URLS = [
    f"{BASE}/static/file/13/1013/img/a.pdf",
    f"{BASE}/static/file/a.PDF",
    f"{BASE}/static/file/a.Docx",
    f"{BASE}/static/file/a.odt",
    f"{BASE}/static/file/a.xlsx",
    f"{BASE}/static/file/a.pptx",
    f"{BASE}/static/file/a.pdf?download=1",
    f"{BASE}/static/file/a.pdf#page=2",
]
NON_DOCUMENT_URLS = [
    f"{BASE}/",
    f"{BASE}/app/index.php?Action=mobileloadmod&Type=mobile_rcg_mstr&Nbr=1013",
    f"{BASE}/static/file/pdf.gif%20",
    f"{BASE}/static/file/doc.gif",
    f"{BASE}/index.php",
    f"{BASE}/pdf/list",
    f"{BASE}/news?file=a.pdf",
]


@pytest.mark.parametrize("url", DOCUMENT_URLS)
def test_document_by_extension(url: str) -> None:
    assert is_document_url(url)


@pytest.mark.parametrize("url", NON_DOCUMENT_URLS)
def test_non_document_not_matched(url: str) -> None:
    assert not is_document_url(url, SITE_PATTERNS)


def test_site_pattern_matches_download_api_only_when_given() -> None:
    assert is_document_url(DOWNLOAD_API, SITE_PATTERNS)
    assert not is_document_url(DOWNLOAD_API)


def test_site_documents_default_and_ncucsie() -> None:
    assert SiteDocumentsConfig().url_patterns == []
    assert SiteConfig.from_yaml("ncucsie").documents.url_patterns == SITE_PATTERNS
    assert SiteConfig.from_yaml("nculab").documents.url_patterns == []


def _crawler(**kwargs) -> WebsiteCrawler:
    crawler = WebsiteCrawler(
        max_depth=2,
        max_pages=None,
        content_threshold=0.5,
        light_mode=False,
        wait_for_images=False,
        cleaner=MagicMock(),
    )
    crawler.url_patterns = ["*csie.ncu.edu.tw*"]
    crawler.allowed_domains = ["www.csie.ncu.edu.tw"]
    crawler.document_url_patterns = SITE_PATTERNS
    for key, value in kwargs.items():
        setattr(crawler, key, value)
    return crawler


def _passes(crawler: WebsiteCrawler, url: str) -> bool:
    return asyncio.run(crawler._build_filter_chain().apply(url))


@pytest.mark.parametrize("url", [*DOCUMENT_URLS, DOWNLOAD_API])
def test_filter_chain_excludes_documents(url: str) -> None:
    assert not _passes(_crawler(), url)


@pytest.mark.parametrize("url", NON_DOCUMENT_URLS)
def test_filter_chain_keeps_pages(url: str) -> None:
    assert _passes(_crawler(), url)


def test_filter_chain_without_site_filters_still_excludes_documents() -> None:
    crawler = _crawler(
        url_patterns=None, allowed_domains=None, document_url_patterns=[]
    )

    assert not _passes(crawler, DOCUMENT_URLS[0])
    assert _passes(crawler, "https://other.example.com/page")


def _result(url: str, *, success: bool, markdown=None, error_message=None, status=200):
    return SimpleNamespace(
        url=url,
        success=success,
        markdown=markdown,
        error_message=error_message,
        status_code=status,
    )


def test_failed_result_logs_actual_error(caplog: pytest.LogCaptureFixture) -> None:
    crawler = _crawler()
    crawler.path_prefix = ""
    ok = _result(
        f"{BASE}/a", success=True, markdown=SimpleNamespace(fit_markdown="# a")
    )
    failed = _result(
        f"{BASE}/b",
        success=False,
        error_message="Page.goto: net::ERR_CONNECTION_RESET",
    )

    with caplog.at_level(logging.INFO):
        filtered = crawler._filter_crawl_results([ok, failed])

    assert list(filtered) == ["a"]
    assert crawler._crawl_stats["error_failed"] == 1
    assert crawler._crawl_stats["error_no_markdown"] == 0
    assert "net::ERR_CONNECTION_RESET" in caplog.text
    assert "no markdown" not in caplog.text


def test_success_without_markdown_still_counted_as_no_markdown() -> None:
    crawler = _crawler()
    crawler.path_prefix = ""

    crawler._filter_crawl_results([_result(f"{BASE}/c", success=True)])

    assert crawler._crawl_stats["error_no_markdown"] == 1
