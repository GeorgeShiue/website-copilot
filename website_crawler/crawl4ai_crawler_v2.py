import re
from crawl4ai import (
    AsyncWebCrawler,
    CrawlResult,
    CrawlerRunConfig,
    PruningContentFilter,
    DefaultMarkdownGenerator,
)
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

from crawl4ai.deep_crawling.filters import (
    FilterChain,
    URLPatternFilter,
    DomainFilter,
)

MARKDOWN_PATH = "/home/george/website-copilot/data/test/webpage_markdown"


async def main():
    # Create a chain of filters
    filter_chain = FilterChain(
        [
            # Only follow URLs with specific patterns
            URLPatternFilter(patterns=["*nculab*"]),
            # Only crawl specific domains
            DomainFilter(
                allowed_domains=["sites.google.com"],
                # blocked_domains=["old.docs.example.com"]
            ),
            # Only include specific content types
            # ContentTypeFilter(allowed_types=["text/html"])
            # Create an SEO filter that looks for specific keywords in page metadata
            # seo_filter = SEOFilter(
            #     threshold=0.5,  # Minimum score (0.0 to 1.0)
            #     keywords=["tutorial", "guide", "documentation"]
            # )
            # Create a content relevance filter
            # relevance_filter = ContentRelevanceFilter(
            #     query="Web crawling and data extraction with Python",
            #     threshold=0.7  # Minimum similarity score (0.0 to 1.0)
            # )
        ]
    )

    deep_crawl_strategy = BFSDeepCrawlStrategy(
        max_depth=2,
        filter_chain=filter_chain,
        include_external=False,  # Stay within the same domain
        # max_pages=10,
        # score_threshold=0.3,       # Minimum score for URLs to be crawled (optional)
    )

    prune_content_filter = PruningContentFilter(
        threshold=0.45,  # 0.45可以顯示所有標題，0.25以下才會出現網頁圖片
        # threshold_type="dynamic",
    )

    config = CrawlerRunConfig(
        deep_crawl_strategy=deep_crawl_strategy,
        # stream=True
        # excluded_tags=["header"],
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=prune_content_filter
        ),
    )

    async with AsyncWebCrawler() as crawler:
        results: list[CrawlResult] = await crawler.arun(
            "https://sites.google.com/site/nculab",
            config=config,
        )

        success_unique_count = 0
        error_count = 0
        repeat_count = 0
        # Access individual results
        for result in results:
            # 排除 404 頁面
            if result.status_code == 404:
                error_count += 1
                # results.remove(result)
                print(f"Webpage {result.url} status code is 404, skipping...")
                print("-" * 50)
                continue

            # 刪除網頁多餘文字
            exclude_words = (
                "Search this site",
                "Embedded Files",
                "Skip to main content",
                "Skip to navigation",
                "Google Sites",
                "Report abuse",
            )
            original_lines = result.markdown.fit_markdown.splitlines(keepends=True)
            filtered_lines = []
            for line in original_lines:
                if not any(word in line for word in exclude_words):
                    filtered_lines.append(line)
            fit_markdown = "".join(filtered_lines)

            # 取內文的第一個標題作為檔名，若無則使用 URL 的最後一段
            heading_match = re.search(r"^#+\s*(.+)", fit_markdown, flags=re.MULTILINE)
            if heading_match:
                title = heading_match.group(1).strip()
                safe_title = re.sub(r"[\\/:\"\*\?<>\|]", "", title)
                safe_title = re.sub(r"\s+", "_", safe_title)
                markdown_file_name = f"{safe_title}.md"
            else:
                markdown_file_name = f"{result.url.split('/')[-1]}.md"

            markdown_file_path = os.path.join(MARKDOWN_PATH, markdown_file_name)

            # 避免存取相同網頁多次，若網頁已存在則跳過
            if os.path.exists(markdown_file_path):
                repeat_count += 1
                print(f"Webpage {markdown_file_name} already exists, skipping...")
                print("-" * 50)
                continue

            images = result.media.get("images", [])
            
            success_unique_count += 1
            with open(markdown_file_path, "w", encoding="utf-8") as f:
                f.write("-" * 5 + "\n")
                f.write(f"URL: {result.url}\n")
                
                f.write("-" * 5 + "\n")
                f.write(fit_markdown)
                
                if images:
                    f.write("\n" + "-" * 5 + "\n")
                    f.write("Images: \n")
                    for image in images:
                        f.write(f"* {image['src']}\n")
                    f.write("\n" + "-" * 5 + "\n")

            print(f"URL: {result.url}")
            print(f"Depth: {result.metadata.get('depth', 0)}")
            print("Images:")
            for image in images:
                print(image)
            print("-" * 50)

        print("Webpage crawling stats:")
        print(f"  - Successful unique pages: {success_unique_count}")
        print(f"  - Error pages: {error_count}")
        print(f"  - Repeat pages: {repeat_count}")


if __name__ == "__main__":
    import asyncio
    import shutil
    import os

    shutil.rmtree(MARKDOWN_PATH, ignore_errors=True)
    os.makedirs(MARKDOWN_PATH, exist_ok=True)

    asyncio.run(main())
