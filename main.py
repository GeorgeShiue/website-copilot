import time
from website_crawler.crawl4ai_crawler import WebsiteCrawler

def main():
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
    WebsiteCrawler.save_results_to_md(
        results=results,
        include_frontmatter=True,
    )
    
    for result in results:
        print(result.url)
    print(f"爬取 {len(results)} 個網頁，耗時 {time.perf_counter() - t0:.1f} 秒")



if __name__ == "__main__":
    main()
