import re

from crawl4ai import CrawlResult


class WebpageCleanerConstants:
    """Markdown 清理用常數：正文起點、要刪除的整行文字、頁尾片段、錯誤頁判斷。"""

    MAIN_CONTENT_HEADING = re.compile(r"^#+\s", re.MULTILINE)
    SKIP_LINE_PHRASES = (
        "Skip to main content",
        "Skip to navigation",
        "Search this site",
        "Embedded Files",
    )
    TRAILING_FOOTER_LINES = frozenset(
        {
            "Google Sites",
            "Report abuse",
            "Google 協作平台",
            "檢舉濫用情形",
            "",
        }
    )
    ERROR_STATUS_CODES = frozenset({404, 500, 502, 503})
    CONTENT_404_PATTERN = re.compile(
        r"#\s*404|page you have entered does not exist|does not exist", re.I
    )


class WebpageCleaner:
    Constants = WebpageCleanerConstants

    @staticmethod
    def _get_page_content(result: CrawlResult) -> str:
        """從 CrawlResult 取 Markdown 文字。"""
        md = getattr(result, "markdown", None)
        if md is None:
            return ""
        return md if isinstance(md, str) else getattr(md, "raw_markdown", str(md))

    # ----- 錯誤頁與內容清理-----
    @classmethod
    def _is_error_page(cls, result: CrawlResult, content: str) -> bool:
        """是否為讀取錯誤頁（success=False、404/5xx 或內容含 404 字樣）。"""
        if not getattr(result, "success", True):
            return True
        status = getattr(result, "status_code", None)
        if status is not None and status in cls.Constants.ERROR_STATUS_CODES:
            return True
        if content and cls.Constants.CONTENT_404_PATTERN.search(content):
            return True
        return False

    @classmethod
    def _clean_markdown_content(cls, content: str) -> str:
        """單一 markdown 字串清理：保留 frontmatter，切除導航與功能性連結。"""
        if not content or not content.strip():
            return content
        frontmatter = ""
        body = content
        if content.lstrip().startswith("---"):
            start = content.find("---")
            idx = content.find("\n---", start + 3)
            if idx != -1:
                fm_end = idx + len("\n---")
                frontmatter = content[:fm_end]
                body = content[fm_end:].lstrip()
        m = cls.Constants.MAIN_CONTENT_HEADING.search(body)
        if m is not None:
            body = body[m.start() :]
        skip_set = frozenset(cls.Constants.SKIP_LINE_PHRASES)
        body = "\n".join(
            line for line in body.split("\n") if line.strip() not in skip_set
        )
        tail_lines = body.split("\n")
        strip_count = 0
        for i in range(len(tail_lines) - 1, -1, -1):
            if tail_lines[i].strip() in cls.Constants.TRAILING_FOOTER_LINES:
                strip_count += 1
            else:
                break
        if strip_count:
            body = "\n".join(tail_lines[: len(tail_lines) - strip_count])
        body = re.sub(r"\n{3,}", "\n\n", body).strip()
        return (frontmatter + "\n\n" + body).strip() if frontmatter else body

    # ----- 對外 API -----
    @classmethod
    def clean_webpage_markdown(
        cls,
        results: list[CrawlResult],
        *,
        include_frontmatter: bool = True,
    ) -> list[str]:
        """取 content、過濾錯誤頁後清理，回傳通過的 cleaned markdown 列表。"""
        cleaned_markdown_list: list[str] = []
        for result in results:
            url = getattr(result, "url", "") or ""
            content = cls._get_page_content(result)
            if cls._is_error_page(result, content):
                continue
            if include_frontmatter:
                content = f"---\nsource: {url}\n---\n\n{content}"
            cleaned_markdown_list.append(cls._clean_markdown_content(content))
        return cleaned_markdown_list


if __name__ == "__main__":
    import logging
    import time

    from website_crawler.crawl4ai_crawler import WebsiteCrawler
    from webpage_content_extracter.md_file_manager import MdFileManager

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    log = logging.getLogger(__name__)
    t0 = time.perf_counter()

    start_url = "https://sites.google.com/site/nculab/labintro"
    webpage_markdowns = WebsiteCrawler.crawl_website(
        url=start_url,
        max_depth=3,
        include_external=False,
        # max_pages=100, # test
        url_prefix="https://sites.google.com/site/nculab",
        concurrent_requests=15,
        text_mode=False,
        light_mode=True,
        verbose=True,
    )
    t1 = time.perf_counter()
    log.info("爬取 %s 個網頁, 耗時 %.3f 秒", len(webpage_markdowns), t1 - t0)
    log.info("-" * 100)

    cleaned_webpage_markdowns = WebpageCleaner.clean_webpage_markdown(
        webpage_markdowns, include_frontmatter=True
    )
    t2 = time.perf_counter()
    log.info(
        "清理後剩餘 %s 個網頁, 耗時 %.3f 秒",
        len(cleaned_webpage_markdowns),
        t2 - t1,
    )
    log.info("-" * 100)

    md_file_paths = MdFileManager.save_md_files(
        directory="./data/webpage_markdown",
        markdown_contents=cleaned_webpage_markdowns,
    )
    t3 = time.perf_counter()
    log.info("已存成 %s 個 .md 檔, 耗時 %.3f 秒", len(md_file_paths), t3 - t2)
    log.info("-" * 100)

    log.info("總耗時 %.3f 秒", t3 - t0)
