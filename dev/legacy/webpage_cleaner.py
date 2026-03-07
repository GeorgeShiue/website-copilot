import re

from crawl4ai import CrawlResult


class WebpageCleanerConstants:
    """Markdown 清理用常數：正文起點、要刪除的整行文字、頁尾片段、錯誤頁判斷。"""

    MAIN_CONTENT_HEADING = re.compile(r"^#+\s", re.MULTILINE)
    SKIP_LINE_PHRASES = frozenset(
        {
            "Skip to main content",
            "Skip to navigation",
            "Search this site",
            "Embedded Files",
        }
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
    HTML_AND_XML_TAGS = frozenset(
        {
            "<NE>",
            "<Separator>",
            "<Input Corpus>",
            "<Seed File>",
            "<Output Corpus>",
            "<Labeled Corpus>",
            "<Labeled Matrix>",
            "<Model Name>",
            "<Method>",
            "<Folder Name>",
            "<Output File>",
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
        # 步驟 1: 檢查內容是否為空或僅包含空白字元
        # 若為空則直接返回，避免後續處理
        if not content or not content.strip():
            return content

        # 步驟 2: 初始化 frontmatter（前置元數據）和 body（正文內容）
        frontmatter = ""
        body = content

        # 步驟 3: 提取並分離 YAML frontmatter
        # frontmatter 格式為 ---\nkey: value\n---，常見於 Jekyll、Hugo 等靜態網站
        if content.lstrip().startswith("---"):
            start = content.find("---")  # 找到第一個 ---
            idx = content.find("\n---", start + 3)  # 找到結束的 ---（必須在換行後）
            if idx != -1:
                fm_end = idx + len("\n---")  # 計算 frontmatter 結束位置
                frontmatter = content[:fm_end]  # 提取 frontmatter
                body = content[fm_end:].lstrip()  # 提取正文並移除前導空白

        # 步驟 4: 尋找正文起點（第一個 Markdown 標題）
        # 使用正則表達式 MAIN_CONTENT_HEADING（匹配 # 開頭的標題）
        # 從該標題開始截取，以去除標題前的導航或其他無關內容
        m = cls.Constants.MAIN_CONTENT_HEADING.search(body)
        if m is not None:
            body = body[m.start() :]

        # 步驟 5: 移除特定的功能性行
        # 過濾掉像 "Skip to main content"、"Search this site" 等導航輔助文字
        skip_set = frozenset(cls.Constants.SKIP_LINE_PHRASES)
        body = "\n".join(
            line for line in body.split("\n") if line.strip() not in skip_set
        )

        # 步驟 6: 從後往前掃描並移除頁尾行
        # 頁尾通常包含 "Google Sites"、"Report abuse" 等固定文字
        tail_lines = body.split("\n")
        strip_count = 0
        for i in range(len(tail_lines) - 1, -1, -1):  # 反向遍歷
            if tail_lines[i].strip() in cls.Constants.TRAILING_FOOTER_LINES:
                strip_count += 1  # 計算需要移除的行數
            else:
                break  # 遇到非頁尾行則停止
        if strip_count:
            body = "\n".join(tail_lines[: len(tail_lines) - strip_count])

        # 步驟 7: 移除特定的 XML 或 HTML 標籤
        # 移除像 <NE>, </NE> 等在轉換過程中可能殘留的標籤
        for tag in cls.Constants.HTML_AND_XML_TAGS:
            body = body.replace(tag, "")

        # 步驟 8: 清理多餘的空行
        # 將連續 3 個以上的換行符（\n\n\n...）替換為 2 個（\n\n），保持段落分隔清晰
        body = re.sub(r"\n{3,}", "\n\n", body).strip()

        # 步驟 9: 組合並返回最終結果
        # 若有 frontmatter 則將其與正文用兩個換行符連接，否則只返回正文
        result = (frontmatter + "\n\n" + body).strip() if frontmatter else body

        return result

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
    log.info("爬取%s個網頁, 耗時%.3f秒", len(webpage_markdowns), t1 - t0)
    log.info("-" * 50)

    cleaned_webpage_markdowns = WebpageCleaner.clean_webpage_markdown(
        webpage_markdowns, include_frontmatter=True
    )
    t2 = time.perf_counter()
    log.info(
        "清理後剩餘%s個網頁, 耗時%.3f秒",
        len(cleaned_webpage_markdowns),
        t2 - t1,
    )
    log.info("-" * 50)

    md_file_paths = MdFileManager.save_md_files(
        directory="./data/webpage_markdown",
        markdown_contents=cleaned_webpage_markdowns,
    )
    t3 = time.perf_counter()
    log.info("已存成%s個 .md 檔, 耗時%.3f秒", len(md_file_paths), t3 - t2)
    log.info("-" * 50)

    log.info("總耗時%.3f秒", t3 - t0)
