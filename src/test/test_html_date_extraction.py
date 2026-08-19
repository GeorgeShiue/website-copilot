"""extract_date_from_html 及相關輔助函數的單元測試。"""

from bs4 import BeautifulSoup

from utils.html_date_extractor import (
    _extract_from_jsonld,
    _extract_meta_name,
    _extract_meta_property,
    _extract_time_element,
    _normalize_to_iso8601,
    _parse_http_date,
    extract_date_from_html,
)

# ── _extract_from_jsonld ──────────────────────────────────────────────


class TestExtractFromJsonld:
    def test_date_published_and_modified(self):
        html = """
        <html><head>
        <script type="application/ld+json">
        {"@type":"Article","datePublished":"2024-01-15T10:00:00Z","dateModified":"2024-06-20T14:30:00Z"}
        </script>
        </head></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        pub, mod = _extract_from_jsonld(soup)
        assert pub == "2024-01-15T10:00:00Z"
        assert mod == "2024-06-20T14:30:00Z"

    def test_date_created_fallback(self):
        html = """
        <html><head>
        <script type="application/ld+json">
        {"@type":"Article","dateCreated":"2023-12-01"}
        </script>
        </head></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        pub, mod = _extract_from_jsonld(soup)
        assert pub == "2023-12-01"
        assert mod is None

    def test_jsonld_list_format(self):
        html = """
        <html><head>
        <script type="application/ld+json">
        [{"@type":"Article","datePublished":"2024-03-10"}]
        </script>
        </head></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        pub, mod = _extract_from_jsonld(soup)
        assert pub == "2024-03-10"

    def test_no_jsonld(self):
        html = "<html><head></head><body></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        pub, mod = _extract_from_jsonld(soup)
        assert pub is None
        assert mod is None

    def test_invalid_jsonld(self):
        html = """
        <html><head>
        <script type="application/ld+json">NOT VALID JSON</script>
        </head></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        pub, mod = _extract_from_jsonld(soup)
        assert pub is None
        assert mod is None


# ── _extract_meta_property ────────────────────────────────────────────


class TestExtractMetaProperty:
    def test_article_published_time(self):
        html = '<html><head><meta property="article:published_time" content="2024-03-20T08:30:00+08:00"></head></html>'
        soup = BeautifulSoup(html, "html.parser")
        assert (
            _extract_meta_property(soup, "article:published_time")
            == "2024-03-20T08:30:00+08:00"
        )

    def test_missing_property(self):
        html = "<html><head></head></html>"
        soup = BeautifulSoup(html, "html.parser")
        assert _extract_meta_property(soup, "article:published_time") is None


# ── _extract_time_element ─────────────────────────────────────────────


class TestExtractTimeElement:
    def test_itemprop_date_published(self):
        html = '<html><body><time datetime="2024-05-10" itemprop="datePublished">May 10, 2024</time></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        assert _extract_time_element(soup) == "2024-05-10"

    def test_plain_datetime(self):
        html = '<html><body><time datetime="2024-07-01T12:00:00">July 1, 2024</time></body></html>'
        soup = BeautifulSoup(html, "html.parser")
        assert _extract_time_element(soup) == "2024-07-01T12:00:00"

    def test_no_time_element(self):
        html = "<html><body><p>No time</p></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        assert _extract_time_element(soup) is None


# ── _extract_meta_name ────────────────────────────────────────────────


class TestExtractMetaName:
    def test_date_meta(self):
        html = '<html><head><meta name="date" content="2024-01-20"></head></html>'
        soup = BeautifulSoup(html, "html.parser")
        assert _extract_meta_name(soup, ("date",)) == "2024-01-20"

    def test_case_insensitive(self):
        html = '<html><head><meta name="DC.date" content="2024-02-15"></head></html>'
        soup = BeautifulSoup(html, "html.parser")
        assert _extract_meta_name(soup, ("dc.date",)) == "2024-02-15"

    def test_pubdate(self):
        html = '<html><head><meta name="pubdate" content="2024-06-01"></head></html>'
        soup = BeautifulSoup(html, "html.parser")
        assert (
            _extract_meta_name(soup, ("date", "pubdate", "publish_date"))
            == "2024-06-01"
        )

    def test_no_match(self):
        html = "<html><head></head></html>"
        soup = BeautifulSoup(html, "html.parser")
        assert _extract_meta_name(soup, ("date",)) is None


# ── _parse_http_date ──────────────────────────────────────────────────


class TestParseHttpDate:
    def test_rfc7231_format(self):
        assert _parse_http_date("Wed, 15 Jan 2025 12:00:00 GMT") is not None

    def test_none_input(self):
        assert _parse_http_date(None) is None

    def test_empty_string(self):
        assert _parse_http_date("") is None

    def test_invalid_format(self):
        assert _parse_http_date("not-a-date") is None


# ── _normalize_to_iso8601 ─────────────────────────────────────────────


class TestNormalizeToIso8601:
    def test_already_iso(self):
        assert _normalize_to_iso8601("2024-01-15") == "2024-01-15"

    def test_iso_with_time(self):
        assert _normalize_to_iso8601("2024-01-15T10:00:00Z") == "2024-01-15"

    def test_iso_with_timezone(self):
        assert _normalize_to_iso8601("2024-03-20T08:30:00+08:00") == "2024-03-20"

    def test_none(self):
        assert _normalize_to_iso8601(None) is None

    def test_empty(self):
        assert _normalize_to_iso8601("") is None

    def test_invalid(self):
        assert _normalize_to_iso8601("not-a-date") is None


# ── extract_date_from_html（整合測試）────────────────────────────────


class TestExtractDateFromHtml:
    def test_jsonld_priority(self):
        """JSON-LD 應優先於 OG meta。"""
        html = """
        <html><head>
        <meta property="article:published_time" content="2024-06-01">
        <script type="application/ld+json">
        {"datePublished":"2024-01-15"}
        </script>
        </head></html>
        """
        result = extract_date_from_html(html)
        assert result["published_date"] == "2024-01-15"

    def test_og_meta_fallback(self):
        """無 JSON-LD 時應使用 article:published_time。"""
        html = """
        <html><head>
        <meta property="article:published_time" content="2024-03-20T08:30:00+08:00">
        </head></html>
        """
        result = extract_date_from_html(html)
        assert result["published_date"] == "2024-03-20"

    def test_time_element_fallback(self):
        """無 JSON-LD 和 OG 時應使用 <time> 元素。"""
        html = """
        <html><body>
        <time datetime="2024-05-10" itemprop="datePublished">May 10, 2024</time>
        </body></html>
        """
        result = extract_date_from_html(html)
        assert result["published_date"] == "2024-05-10"

    def test_generic_meta_date(self):
        """使用 generic meta name="date"。"""
        html = '<html><head><meta name="date" content="2024-02-15"></head></html>'
        result = extract_date_from_html(html)
        assert result["published_date"] == "2024-02-15"

    def test_dublin_core(self):
        """使用 Dublin Core dc.date。"""
        html = '<html><head><meta name="dc.date" content="2024-04-10"></head></html>'
        result = extract_date_from_html(html)
        assert result["published_date"] == "2024-04-10"

    def test_http_last_modified(self):
        """所有 HTML 來源都沒有時，fallback 到 Last-Modified。"""
        html = "<html><head></head><body></body></html>"
        headers = {"Last-Modified": "Wed, 15 Jan 2025 12:00:00 GMT"}
        result = extract_date_from_html(html, response_headers=headers)
        assert result["published_date"] is not None

    def test_no_date_anywhere(self):
        """完全無日期來源時回傳 None。"""
        html = "<html><head></head><body>No dates</body></html>"
        result = extract_date_from_html(html)
        assert result["published_date"] is None
        assert result["modified_date"] is None

    def test_modified_date_from_jsonld(self):
        """JSON-LD 同時提供 datePublished 和 dateModified。"""
        html = """
        <html><head>
        <script type="application/ld+json">
        {"datePublished":"2024-01-15","dateModified":"2024-06-20"}
        </script>
        </head></html>
        """
        result = extract_date_from_html(html)
        assert result["published_date"] == "2024-01-15"
        assert result["modified_date"] == "2024-06-20"

    def test_modified_date_from_og(self):
        """article:modified_time 作為 modified_date 來源。"""
        html = """
        <html><head>
        <meta property="article:published_time" content="2024-01-15">
        <meta property="article:modified_time" content="2024-06-20">
        </head></html>
        """
        result = extract_date_from_html(html)
        assert result["published_date"] == "2024-01-15"
        assert result["modified_date"] == "2024-06-20"

    def test_invalid_html_graceful(self):
        """損壞的 HTML 不應拋出異常。"""
        result = extract_date_from_html("<<<NOT VALID>>>")
        assert result["published_date"] is None

    def test_none_headers(self):
        """response_headers 為 None 時不應拋出異常。"""
        html = '<html><head><meta name="date" content="2024-01-15"></head></html>'
        result = extract_date_from_html(html, response_headers=None)
        assert result["published_date"] == "2024-01-15"
