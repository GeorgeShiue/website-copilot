"""WebsiteCrawler 去重邏輯與 path_prefix 的單元測試。"""

from unittest.mock import MagicMock

from app.engines.website_crawler import WebsiteCrawler, resolve_dedup_key


def _make_crawler(url: str, path_prefix: str | None = None) -> WebsiteCrawler:
    crawler = WebsiteCrawler()
    crawler.url = url
    if path_prefix is not None:
        crawler.path_prefix = path_prefix.rstrip("/")
    else:
        from urllib.parse import urlparse

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
            resolve_dedup_key(
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
            resolve_dedup_key(
                "https://sites.google.com/site/nculab/labintro", c.path_prefix
            )
            == "labintro"
        )

    def test_csie_child_page(self):
        c = _make_crawler("https://www.csie.ncu.edu.tw/", path_prefix="/")
        assert (
            resolve_dedup_key(
                "https://www.csie.ncu.edu.tw/department/member", c.path_prefix
            )
            == "department_member"
        )

    def test_csie_root(self):
        c = _make_crawler("https://www.csie.ncu.edu.tw/", path_prefix="/")
        assert (
            resolve_dedup_key("https://www.csie.ncu.edu.tw/", c.path_prefix) == "index"
        )

    def test_csie_deep_path(self):
        c = _make_crawler("https://www.csie.ncu.edu.tw/", path_prefix="/")
        key = resolve_dedup_key(
            "https://www.csie.ncu.edu.tw/announcement/abc123", c.path_prefix
        )
        assert key == "announcement_abc123"

    def test_no_path_prefix_fallback(self):
        """path_prefix 為 None 時 fallback 到起始 URL 父路徑。"""
        c = _make_crawler("https://example.com/blog/post1")
        # parent of /blog/post1 is /blog
        assert c.path_prefix == "/blog"
        assert (
            resolve_dedup_key("https://example.com/blog/post2", c.path_prefix)
            == "post2"
        )

    def test_no_path_prefix_domain_root(self):
        """起始 URL 在 domain 根時，fallback 到 /"""
        c = _make_crawler("https://example.com/")
        assert c.path_prefix == "/"
        assert resolve_dedup_key("https://example.com/about", c.path_prefix) == "about"


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
