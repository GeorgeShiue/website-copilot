import time
import logging

from website_crawler.crawl4ai_crawler import WebsiteCrawler
from webpage_cleaner import WebpageCleaner


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    log = logging.getLogger(__name__)

    t0 = time.perf_counter()
    start_url = "https://sites.google.com/site/nculab/labintro"
    webpage_markdowns = WebsiteCrawler.crawl_website(
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


if __name__ == "__main__":
    main()
