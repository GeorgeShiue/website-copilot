import asyncio
import os

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CrawlResult
from crawl4ai import PruningContentFilter
from crawl4ai import DefaultMarkdownGenerator
from crawl4ai import BFSDeepCrawlStrategy, DomainFilter, FilterChain
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

from crawl4ai.deep_crawling.filters import URLPatternFilter


MARKDOWN_PATH = "/home/george/website-copilot/data/test/crawl4ai_example"


async def fit_markdown():
    webpage_name = "nculab_labintro"
    thresholds = [0.55, 0.48, 0.4, 0.35, 0.3, 0.25] # 0.25才會出現網頁圖片
    url = "https://sites.google.com/site/nculab/labintro"

    for threshold in thresholds:
        prune_filter = PruningContentFilter(
            threshold=threshold, # Lower → more content retained, higher → more content pruned
            threshold_type="dynamic", # "fixed" or "dynamic"
            # min_word_threshold=5 # Ignore nodes with <5 words
        )

        async with AsyncWebCrawler() as crawler:
            result: CrawlResult = await crawler.arun(
                url=url,
                config=CrawlerRunConfig(
                    markdown_generator=DefaultMarkdownGenerator(
                        content_filter=prune_filter,
                    )
                ),
            )

            # Print stats and save the fit markdown
            print(f"Threshold: {threshold}")
            print(f"Fit markdown: {len(result.markdown.fit_markdown)} chars")

            result_path = f"{MARKDOWN_PATH}/{webpage_name}"
            os.makedirs(result_path, exist_ok=True)

            with open(f"{result_path}/fit_markdown_{threshold}.md", "w") as f:
                f.write(result.markdown.fit_markdown)


async def advanced_deep_crawl():
    # Create a chain of filters
    filter_chain = FilterChain([
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
    ])

    # # Create a scorer
    # scorer = KeywordRelevanceScorer(
    #     keywords=["crawl", "example", "async", "configuration"],
    #     weight=0.7
    # )

    # # Configure the strategy
    # deep_crawl_strategy = BestFirstCrawlingStrategy(
    #     max_depth=2,
    #     include_external=False,
    #     url_scorer=scorer,
    #     max_pages=25,              # Maximum number of pages to crawl (optional)
    # )

    deep_crawl_strategy = BFSDeepCrawlStrategy(
        max_depth=2,               
        filter_chain=filter_chain,
        include_external=False,    # Stay within the same domain
        # max_pages=10,              
        # score_threshold=0.3,       # Minimum score for URLs to be crawled (optional)
    )

    config = CrawlerRunConfig(
        deep_crawl_strategy=deep_crawl_strategy,
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
        # stream=True
    )

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun("https://sites.google.com/site/nculab", config=config)

        print(f"Crawled {len(results)} pages in total")

        # Access individual results
        for result in results:
            print(f"URL: {result.url}")
            print(f"Depth: {result.metadata.get('depth', 0)}")

    # async with AsyncWebCrawler() as crawler:
    #     # Returns an async iterator
    #     async for result in await crawler.arun("https://sites.google.com/site/nculab", config=config):
    #         # Process each result as it becomes available
    #         print(f"URL: {result.url}")
    #         print(f"Depth: {result.metadata.get('depth', 0)}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(fit_markdown())
    # asyncio.run(advanced_deep_crawl())
