from run import run_webpage_image_summarizer, run_website_crawler
from utils.log_helper import setup_logging
from utils.run_manager import RunManager

setup_logging("debug")


def test_main():
    run_manager = RunManager()

    run_manager.set_module_path("website_crawler")
    crawl_results = run_website_crawler(run_manager=run_manager, config_name="test")
    if crawl_results is None:
        return

    run_manager.set_module_path("webpage_image_summarizer")
    run_webpage_image_summarizer(
        run_manager=run_manager, config_name="test", crawl_results=crawl_results
    )
