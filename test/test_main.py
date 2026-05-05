from run import run_webpage_image_summarizer, run_website_crawler
from utils.log_helper import setup_logging

setup_logging("debug")


def test_main():
    crawl_results = run_website_crawler(config_names=["test"])
    if crawl_results is None:
        return
    run_webpage_image_summarizer(config_names=["test"], crawl_results=crawl_results)
