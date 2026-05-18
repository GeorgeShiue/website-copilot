from run import run_webpage_image_summarizer, run_website_crawler, run_rag
from utils.log_helper import setup_logging

setup_logging("debug")


def test_website_crawler():
    run_website_crawler(config_names=["test"])


def test_webpage_image_summarizer():
    run_webpage_image_summarizer(config_names=["test"])


def test_rag():
    run_rag()
