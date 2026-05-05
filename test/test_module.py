from run import run_webpage_image_summarizer, run_website_crawler


def test_website_crawler():
    run_website_crawler(config_names=["test"])


def test_webpage_image_summarizer():
    run_webpage_image_summarizer(config_names=["test"])
