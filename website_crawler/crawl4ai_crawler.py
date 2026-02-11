import asyncio
from collections.abc import AsyncIterator
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse, urlunparse

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlResult, CrawlerRunConfig
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, FilterChain, URLPatternFilter


class WebsiteCrawler:
    """Crawl4AI BFS 網站爬蟲，提供 crawl_website 等類別方法。"""

    _DROP_QUERY_PARAMS = frozenset(
        {"authuser", "utm_source", "utm_medium", "utm_campaign", "ref", "fbclid"}
    )

    # ----- URL 正規化與過濾（內部用） -----
    @staticmethod
    def _normalize_url(url: str) -> str:
        """URL 正規化供去重用：scheme/host 統一、path 解碼再編碼、去掉無關 query、統一尾端斜線。"""
        if not url or not url.strip():
            return url
        parsed = urlparse(url.strip())
        scheme = "https" if parsed.scheme == "http" else (parsed.scheme or "https")
        netloc = (parsed.netloc or "").lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        path = quote(unquote(parsed.path), safe="/~").rstrip("/") or "/"
        query = parsed.query
        if query:
            params = parse_qs(query, keep_blank_values=False)
            params = {
                k: v
                for k, v in params.items()
                if k.lower() not in WebsiteCrawler._DROP_QUERY_PARAMS
            }
            query = urlencode(sorted(params.items()), doseq=True) if params else ""
        return urlunparse((scheme, netloc, path, "", query, ""))

    @classmethod
    def _dedupe_results_by_normalized_url(
        cls, results: list[CrawlResult]
    ) -> list[CrawlResult]:
        """依正規化 URL 去重，同一正規化 URL 只保留第一筆。"""
        seen: set[str] = set()
        out: list[CrawlResult] = []
        for r in results:
            norm = cls._normalize_url(getattr(r, "url", "") or "")
            if norm in seen:
                continue
            seen.add(norm)
            out.append(r)
        return out

    @staticmethod
    def _filter_chain(url_prefix: str | list[str] | None) -> FilterChain | None:
        """依 url_prefix 建立 FilterChain，僅爬取符合前綴的網址。"""
        if url_prefix is None:
            return None
        prefixes = [url_prefix] if isinstance(url_prefix, str) else list(url_prefix)
        patterns = [
            p.rstrip("/") + "/*" if not p.endswith("/*") else p
            for p in prefixes
            if p and (p.startswith("http://") or p.startswith("https://"))
        ]
        return (
            FilterChain([URLPatternFilter(patterns=patterns, use_glob=True)])
            if patterns
            else None
        )

    # ----- 對外 API -----
    @classmethod
    async def crawl_website_async(
        cls,
        url: str,
        *,
        max_depth: int = 3,
        include_external: bool = False,
        max_pages: int | None = None,
        url_prefix: str | list[str] | None = None,
        concurrent_requests: int = 15,
        text_mode: bool = False,
        light_mode: bool = False,
        stream: bool = False,
        verbose: bool = False,
        page_timeout: int | None = None,
    ) -> list[CrawlResult] | AsyncIterator[CrawlResult]:
        """非同步 BFS 爬整站。stream=True 回傳 AsyncIterator，否則 list[CrawlResult]。"""
        strategy_kw: dict[str, Any] = {
            "max_depth": max_depth,
            "include_external": include_external,
        }

        if max_pages is not None:
            strategy_kw["max_pages"] = max_pages
        filter_chain = cls._filter_chain(url_prefix)
        if filter_chain is not None:
            strategy_kw["filter_chain"] = filter_chain

        run_config = CrawlerRunConfig(
            deep_crawl_strategy=BFSDeepCrawlStrategy(**strategy_kw),
            scraping_strategy=LXMLWebScrapingStrategy(),
            stream=stream,
            verbose=verbose,
            semaphore_count=concurrent_requests,
        )
        if page_timeout is not None:
            run_config.page_timeout = page_timeout

        browser_config = BrowserConfig(
            headless=True,
            text_mode=text_mode,
            light_mode=light_mode,
            java_script_enabled=not text_mode,
            verbose=verbose,
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            run_result = await crawler.arun(url, config=run_config)
            if stream:
                return run_result
            raw_list = list(run_result) if run_result else []
            return cls._dedupe_results_by_normalized_url(raw_list)

    @classmethod
    def crawl_website(
        cls,
        url: str,
        *,
        max_depth: int = 3,
        include_external: bool = False,
        max_pages: int | None = None,
        url_prefix: str | list[str] | None = None,
        concurrent_requests: int = 15,
        text_mode: bool = False,
        light_mode: bool = False,
        verbose: bool = False,
        page_timeout: int | None = None,
    ) -> list[CrawlResult]:
        """同步爬整站，回傳 list[CrawlResult]。"""
        return asyncio.run(
            cls.crawl_website_async(
                url,
                max_depth=max_depth,
                include_external=include_external,
                max_pages=max_pages,
                url_prefix=url_prefix,
                concurrent_requests=concurrent_requests,
                text_mode=text_mode,
                light_mode=light_mode,
                stream=False,
                verbose=verbose,
                page_timeout=page_timeout,
            )
        )


if __name__ == "__main__":
    import logging
    import time

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    log = logging.getLogger(__name__)

    t0 = time.perf_counter()
    start_url = "https://sites.google.com/site/nculab/labintro"
    results = WebsiteCrawler.crawl_website(
        url=start_url,
        max_depth=3,
        include_external=False,
        url_prefix="https://sites.google.com/site/nculab",
        concurrent_requests=15,
        text_mode=False,
        light_mode=True,
        verbose=True,
    )

    t1 = time.perf_counter()
    log.info("爬取 %s 個網頁，耗時 %.1f 秒", len(results), t1 - t0)
