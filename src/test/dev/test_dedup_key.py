"""WebsiteCrawler 去重邏輯與 path_prefix 的單元測試。"""

from unittest.mock import MagicMock
from urllib.parse import urlparse

from app.engines.website_crawler import WebsiteCrawler


def _make_crawler(url: str, path_prefix: str | None = None) -> WebsiteCrawler:
    crawler = WebsiteCrawler()
    crawler.url = url
    if path_prefix is not None:
        crawler.path_prefix = path_prefix.rstrip("/")
    else:
        start_path = urlparse(url).path.rstrip("/")
        crawler.path_prefix = start_path.rsplit("/", 1)[0] or "/"
    return crawler


def _make_result(url: str, title: str = "Page") -> MagicMock:
    r = MagicMock()
    r.url = url
    r.status_code = 200
    r.metadata = {"title": title}
    r.markdown.fit_markdown = f"# {title}"
    return r


# ── resolve_dedup_key ────────────────────────────────────────────────


class TestResolveDedupKey:
    def test_nculab_child_page(self):
        c = _make_crawler(
            "https://sites.google.com/site/nculab/labintro",
            path_prefix="/site/nculab",
        )
        assert (
            WebsiteCrawler._resolve_dedup_key(
                "https://sites.google.com/site/nculab/news/校內奬項", c.path_prefix
            )
            == "news_校內奬項"
        )

    def test_nculab_root(self):
        c = _make_crawler(
            "https://sites.google.com/site/nculab/labintro",
            path_prefix="/site/nculab",
        )
        # /site/nculab/labintro 截去 /site/nculab → labintro
        assert (
            WebsiteCrawler._resolve_dedup_key(
                "https://sites.google.com/site/nculab/labintro", c.path_prefix
            )
            == "labintro"
        )

    def test_csie_child_page(self):
        c = _make_crawler("https://www.csie.ncu.edu.tw/", path_prefix="/")
        assert (
            WebsiteCrawler._resolve_dedup_key(
                "https://www.csie.ncu.edu.tw/department/member", c.path_prefix
            )
            == "department_member"
        )

    def test_csie_root(self):
        c = _make_crawler("https://www.csie.ncu.edu.tw/", path_prefix="/")
        assert (
            WebsiteCrawler._resolve_dedup_key(
                "https://www.csie.ncu.edu.tw/", c.path_prefix
            )
            == "index"
        )

    def test_csie_deep_path(self):
        c = _make_crawler("https://www.csie.ncu.edu.tw/", path_prefix="/")
        key = WebsiteCrawler._resolve_dedup_key(
            "https://www.csie.ncu.edu.tw/announcement/abc123", c.path_prefix
        )
        assert key == "announcement_abc123"

    def test_no_path_prefix_fallback(self):
        """path_prefix 為 None 時 fallback 到起始 URL 父路徑。"""
        c = _make_crawler("https://example.com/blog/post1")
        # parent of /blog/post1 is /blog
        assert c.path_prefix == "/blog"
        assert (
            WebsiteCrawler._resolve_dedup_key(
                "https://example.com/blog/post2", c.path_prefix
            )
            == "post2"
        )

    def test_no_path_prefix_domain_root(self):
        """起始 URL 在 domain 根時，fallback 到 /"""
        c = _make_crawler("https://example.com/")
        assert c.path_prefix == "/"
        assert (
            WebsiteCrawler._resolve_dedup_key(
                "https://example.com/about", c.path_prefix
            )
            == "about"
        )

    def test_percent_encoded_matches_decoded(self):
        """百分比編碼與原文 URL 應得到相同的鍵。"""
        prefix = "/site/nculab"
        encoded = WebsiteCrawler._resolve_dedup_key(
            "https://sites.google.com/site/nculab/news/%E7%A2%A9%E8%AB%96%E5%8F%A3%E8%A9%A6",
            prefix,
        )
        decoded = WebsiteCrawler._resolve_dedup_key(
            "https://sites.google.com/site/nculab/news/碩論口試", prefix
        )
        assert encoded == decoded == "news_碩論口試"

    def test_percent_encoding_hex_case_insensitive(self):
        """%e7 與 %E7 為同一編碼，應得到相同的鍵。"""
        lower = WebsiteCrawler._resolve_dedup_key(
            "https://example.com/news/%e7%a2%a9", "/"
        )
        upper = WebsiteCrawler._resolve_dedup_key(
            "https://example.com/news/%E7%A2%A9", "/"
        )
        assert lower == upper == "news_碩"

    def test_percent_encoded_path_prefix(self):
        """path_prefix 為編碼形式時仍能正確截去。"""
        key = WebsiteCrawler._resolve_dedup_key(
            "https://example.com/site/實驗室/news/a",
            "/site/%E5%AF%A6%E9%A9%97%E5%AE%A4",
        )
        assert key == "news_a"

    def test_encoded_slash_becomes_underscore(self):
        """%2F 解碼後轉為 `_`，鍵不得含路徑分隔符。"""
        key = WebsiteCrawler._resolve_dedup_key("https://example.com/news/a%2Fb", "/")
        assert key == "news_a_b"
        assert "/" not in key


# ── _filter_crawl_results ─────────────────────────────────────────────


class TestFilterCrawlResults:
    def test_different_pages_not_deduped(self):
        """不同 URL path 的頁面不應被去重。"""
        c = _make_crawler("https://www.csie.ncu.edu.tw/", path_prefix="/")
        results = c._filter_crawl_results(
            [
                _make_result(
                    "https://www.csie.ncu.edu.tw/", "國立中央大學資訊工程學系"
                ),
                _make_result(
                    "https://www.csie.ncu.edu.tw/department", "國立中央大學資訊工程學系"
                ),
                _make_result(
                    "https://www.csie.ncu.edu.tw/department/member",
                    "國立中央大學資訊工程學系",
                ),
            ]
        )
        assert len(results) == 3
        assert "index" in results
        assert "department" in results
        assert "department_member" in results

    def test_same_url_deduped(self):
        """相同 URL 的頁面應被去重。"""
        c = _make_crawler("https://www.csie.ncu.edu.tw/", path_prefix="/")
        results = c._filter_crawl_results(
            [
                _make_result("https://www.csie.ncu.edu.tw/department"),
                _make_result("https://www.csie.ncu.edu.tw/department"),
            ]
        )
        assert len(results) == 1

    def test_404_skipped(self):
        """404 頁面應被跳過。"""
        c = _make_crawler("https://www.csie.ncu.edu.tw/", path_prefix="/")
        r = _make_result("https://www.csie.ncu.edu.tw/missing")
        r.status_code = 404
        results = c._filter_crawl_results([r])
        assert len(results) == 0

    def test_nculab_pages_not_deduped(self):
        """nculab 不同子頁面不應被去重。"""
        c = _make_crawler(
            "https://sites.google.com/site/nculab/labintro",
            path_prefix="/site/nculab",
        )
        results = c._filter_crawl_results(
            [
                _make_result("https://sites.google.com/site/nculab/labintro"),
                _make_result("https://sites.google.com/site/nculab/news/校內奬項"),
                _make_result("https://sites.google.com/site/nculab/advisor"),
            ]
        )
        assert len(results) == 3
        assert "labintro" in results
        assert "news_校內奬項" in results
        assert "advisor" in results

    def test_encoded_and_decoded_url_deduped(self):
        """同一頁的編碼／原文 URL 只保留先出現的一筆，鍵為解碼後中文。"""
        c = _make_crawler(
            "https://sites.google.com/site/nculab/labintro",
            path_prefix="/site/nculab",
        )
        first = "https://sites.google.com/site/nculab/news/碩論口試"
        second = "https://sites.google.com/site/nculab/news/%E7%A2%A9%E8%AB%96%E5%8F%A3%E8%A9%A6"
        results = c._filter_crawl_results([_make_result(first), _make_result(second)])
        assert list(results) == ["news_碩論口試"]
        assert results["news_碩論口試"]["url"] == first
        assert c._crawl_stats["repeat_pages"] == 1
        assert c._crawl_stats["success_pages"] == 1

    def test_different_encoded_pages_not_deduped(self):
        """不同的編碼頁不應被誤判為重複。"""
        c = _make_crawler(
            "https://sites.google.com/site/nculab/labintro",
            path_prefix="/site/nculab",
        )
        results = c._filter_crawl_results(
            [
                _make_result(
                    "https://sites.google.com/site/nculab/news/%E6%A0%A1%E5%85%A7%E5%A5%AC%E9%A0%85"
                ),
                _make_result(
                    "https://sites.google.com/site/nculab/news/%E7%A2%A9%E8%AB%96%E5%8F%A3%E8%A9%A6"
                ),
            ]
        )
        assert sorted(results) == ["news_校內奬項", "news_碩論口試"]
        assert c._crawl_stats["repeat_pages"] == 0

    def test_stats_tracking(self):
        """重複頁面應正確計入 repeat_pages。"""
        c = _make_crawler("https://www.csie.ncu.edu.tw/", path_prefix="/")
        c._filter_crawl_results(
            [
                _make_result("https://www.csie.ncu.edu.tw/"),
                _make_result("https://www.csie.ncu.edu.tw/"),
                _make_result("https://www.csie.ncu.edu.tw/"),
            ]
        )
        assert c._crawl_stats["success_pages"] == 1
        assert c._crawl_stats["repeat_pages"] == 2
