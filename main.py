from run import run_webpage_image_summarizer, run_website_crawler
from utils.log_helper import setup_logging

setup_logging("info")


def main() -> None:
    crawl_results = run_website_crawler()
    if crawl_results is None:
        return
    run_webpage_image_summarizer(crawl_results=crawl_results)


if __name__ == "__main__":
    main()
