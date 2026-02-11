import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

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
    TRAILING_FOOTER_LINES = frozenset({"Google Sites", "Report abuse", ""})
    ERROR_STATUS_CODES = frozenset({404, 500, 502, 503})
    CONTENT_404_PATTERN = re.compile(
        r"#\s*404|page you have entered does not exist|does not exist", re.I
    )


class WebpageCleaner:
    # ----- 內容取得 -----
    @staticmethod
    def _get_page_content(result: CrawlResult) -> str:
        """從 CrawlResult 取 Markdown 文字。"""
        md = getattr(result, "markdown", None)
        if md is None:
            return ""
        return md if isinstance(md, str) else getattr(md, "raw_markdown", str(md))

    # ----- 檔名：安全 basename -----
    @staticmethod
    def _safe_suffix(s: str, index: int, max_length: int = 80) -> str:
        """將字串截斷並加上編號前綴，作為檔名後半段。"""
        s = (s[:max_length].rstrip("_") if len(s) > max_length else s) or "page"
        return f"{index:03d}_{s}"

    @classmethod
    def _title_to_safe_basename(cls, raw: str, index: int, max_length: int = 80) -> str:
        """將標題轉成可作為檔名的安全字串。"""
        s = (raw or "").strip()
        s = re.sub(r"[^\w\s\-.]", "", s)
        s = re.sub(r"_+", "_", re.sub(r"\s+", "_", s).strip("_"))
        return cls._safe_suffix(s, index, max_length)

    @classmethod
    def _url_to_safe_basename(cls, url: str, index: int, max_length: int = 80) -> str:
        """從 URL path 產生可作為檔名的安全字串。"""
        path = (urlparse(url).path or "/").strip("/") or "index"
        path = re.sub(r"_+", "_", re.sub(r"[^\w\-.]", "_", path)).strip("_")
        return cls._safe_suffix(path, index, max_length)

    @classmethod
    def _first_heading_from_md(cls, content: str) -> str | None:
        """從 markdown 內容取第一個 ATX 標題（# 開頭）文字，無則回傳 None。"""
        for line in content.split("\n"):
            s = line.strip()
            if s.startswith("#"):
                return re.sub(r"^#+\s*", "", s).strip() or None
        return None

    # ----- 錯誤頁與內容清理（內部用） -----
    @classmethod
    def _is_error_page(cls, result: CrawlResult, content: str) -> bool:
        """是否為讀取錯誤頁（success=False、404/5xx 或內容含 404 字樣）。"""
        if not getattr(result, "success", True):
            return True
        status = getattr(result, "status_code", None)
        C = WebpageCleanerConstants
        if status is not None and status in C.ERROR_STATUS_CODES:
            return True
        if content and C.CONTENT_404_PATTERN.search(content):
            return True
        return False

    @classmethod
    def _clean_markdown_content(cls, content: str) -> str:
        """單一 markdown 字串清理：保留 frontmatter，切除導航與功能性連結。"""
        if not content or not content.strip():
            return content
        C = WebpageCleanerConstants
        frontmatter = ""
        body = content
        if content.lstrip().startswith("---"):
            start = content.find("---")
            idx = content.find("\n---", start + 3)
            if idx != -1:
                fm_end = idx + len("\n---")
                frontmatter = content[:fm_end]
                body = content[fm_end:].lstrip()
        m = C.MAIN_CONTENT_HEADING.search(body)
        if m is not None:
            body = body[m.start() :]
        skip_set = frozenset(C.SKIP_LINE_PHRASES)
        body = "\n".join(
            line for line in body.split("\n") if line.strip() not in skip_set
        )
        tail_lines = body.split("\n")
        strip_count = 0
        for i in range(len(tail_lines) - 1, -1, -1):
            if tail_lines[i].strip() in C.TRAILING_FOOTER_LINES:
                strip_count += 1
            else:
                break
        if strip_count:
            body = "\n".join(tail_lines[: len(tail_lines) - strip_count])
        body = re.sub(r"\n{3,}", "\n\n", body).strip()
        return (frontmatter + "\n\n" + body).strip() if frontmatter else body

    # ----- 對外 API -----
    @classmethod
    def save_md_files(
        cls,
        cleaned_markdown_contents: list[str] | None = None,
        directory: str = "./website_crawler/webpage_markdown",
        *,
        filename_prefix: str = "",
    ) -> list[Path]:
        """將清理後的 markdown 字串列表存成 .md；檔名由各則內容的首個標題或索引產生。"""
        md_file_paths: list[Path] = []
        if not cleaned_markdown_contents:
            return md_file_paths
        out_dir = Path(directory)
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for i, content in enumerate(cleaned_markdown_contents):
            title = cls._first_heading_from_md(content)
            basename = (
                cls._title_to_safe_basename(title, i)
                if title
                else cls._safe_suffix("page", i)
            )
            path = (out_dir / f"{filename_prefix}{basename}").with_suffix(".md")
            path.write_text(content, encoding="utf-8")
            md_file_paths.append(path)
        return md_file_paths

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

    cleaned_webpage_markdowns = WebpageCleaner.clean_webpage_markdown(
        webpage_markdowns, include_frontmatter=True
    )
    t2 = time.perf_counter()
    log.info(
        "清理後剩餘 %s 個網頁, 耗時 %.3f 秒",
        len(cleaned_webpage_markdowns),
        t2 - t1,
    )

    md_file_paths = WebpageCleaner.save_md_files(
        cleaned_webpage_markdowns,
    )
    t3 = time.perf_counter()
    log.info("已存成 %s 個 .md 檔, 耗時 %.3f 秒", len(md_file_paths), t3 - t2)

    log.info("總耗時 %.3f 秒", t3 - t0)
