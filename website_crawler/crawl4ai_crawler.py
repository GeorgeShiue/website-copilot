import asyncio
import re
import shutil
import time
from pathlib import Path
from urllib.parse import urlparse

from collections.abc import AsyncIterator
from typing import Any

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, FilterChain, URLPatternFilter


class WebsiteCrawler:
    """Crawl4AI BFS 網站爬蟲，提供 crawl_website / save_results_to_md 等類別方法。"""

    @staticmethod
    def _get_page_content(result: Any) -> str:
        """從 CrawlResult 取 Markdown 文字。"""
        md = getattr(result, "markdown", None)
        if md is None:
            return ""
        return md if isinstance(md, str) else getattr(md, "raw_markdown", str(md))

    @staticmethod
    def _safe_suffix(s: str, index: int, max_length: int = 80) -> str:
        s = (s[:max_length].rstrip("_") if len(s) > max_length else s) or "page"
        return f"{index:03d}_{s}"

    @classmethod
    def _title_to_safe_basename(cls, raw: str, index: int, max_length: int = 80) -> str:
        s = (raw or "").strip()
        s = re.sub(r"[^\w\s\-.]", "", s)
        s = re.sub(r"_+", "_", re.sub(r"\s+", "_", s).strip("_"))
        return cls._safe_suffix(s, index, max_length)

    @classmethod
    def _url_to_safe_basename(cls, url: str, index: int, max_length: int = 80) -> str:
        path = (urlparse(url).path or "/").strip("/") or "index"
        path = re.sub(r"_+", "_", re.sub(r"[^\w\-.]", "_", path)).strip("_")
        return cls._safe_suffix(path, index, max_length)

    @staticmethod
    def _filter_chain(url_prefix: str | list[str] | None) -> FilterChain | None:
        if url_prefix is None:
            return None
        prefixes = [url_prefix] if isinstance(url_prefix, str) else list(url_prefix)
        patterns = [
            p.rstrip("/") + "/*" if not p.endswith("/*") else p
            for p in prefixes
            if p and (p.startswith("http://") or p.startswith("https://"))
        ]
        return FilterChain([URLPatternFilter(patterns=patterns, use_glob=True)]) if patterns else None

    @classmethod
    def save_results_to_md(
        cls,
        results: list[Any],
        directory: str = "./website_crawler/webpage_markdown",
        *,
        include_frontmatter: bool = True,
        filename_prefix: str = "",
    ) -> list[Path]:
        """將 CrawlResult 列表存成 .md 檔。"""
        out_dir = Path(directory)
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        written: list[Path] = []
        for i, result in enumerate(results):
            url = getattr(result, "url", "") or ""
            meta = getattr(result, "metadata", None) or {}
            depth = meta.get("depth", "")
            title = meta.get("title") or getattr(result, "title", None)
            content = cls._get_page_content(result)
            if include_frontmatter:
                content = f"---\nsource: {url}\ndepth: {depth}\n---\n\n{content}"
            basename = cls._title_to_safe_basename(title, i) if title else cls._url_to_safe_basename(url, i)
            path = (out_dir / f"{filename_prefix}{basename}").with_suffix(".md")
            path.write_text(content, encoding="utf-8")
            written.append(path)
        
        return written

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
    ) -> list[Any] | AsyncIterator[Any]:
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
            return list(run_result) if run_result else []

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
    ) -> list[Any]:
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
    t0 = time.perf_counter()
    results = WebsiteCrawler.crawl_website(
        "https://sites.google.com/site/nculab/labintro",
        max_depth=1,
        include_external=False,
        url_prefix="https://sites.google.com/site/nculab",
        concurrent_requests=15,
        light_mode=True,
        verbose=True,
    )
    WebsiteCrawler.save_results_to_md(results, include_frontmatter=True)
    print(f"爬取 {len(results)} 個網頁，耗時 {time.perf_counter() - t0:.1f} 秒")