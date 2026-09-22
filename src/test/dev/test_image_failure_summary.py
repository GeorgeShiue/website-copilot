"""WebpageImageSummarizer 失敗圖片追蹤與彙整輸出的單元測試。"""

from unittest.mock import patch
from urllib.error import URLError

from app.engines.webpage_image_summarizer import WebpageImageSummarizer

LONG_URL = "https://sites.google.com/sitesv-images-rt/" + "A" * 300 + "=w1280"


def test_log_failed_images_prints_nothing_when_empty(capsys):
    WebpageImageSummarizer()._log_failed_images()

    assert capsys.readouterr().out == ""


def test_log_failed_images_prints_full_url_on_a_single_line(capsys):
    summarizer = WebpageImageSummarizer()
    summarizer._failed_images = {
        LONG_URL: ("members", "HTTP Error 403: Forbidden"),
    }

    summarizer._log_failed_images()

    out = capsys.readouterr().out
    assert "Failed Images (1)" in out
    assert f"[members] HTTP Error 403: Forbidden: {LONG_URL}" in out


def test_download_image_records_failure_reason():
    summarizer = WebpageImageSummarizer()

    with patch(
        "app.engines.webpage_image_summarizer.urlopen",
        side_effect=URLError("HTTP Error 403: Forbidden"),
    ):
        image_data, status = summarizer._download_image(LONG_URL)

    assert image_data is None
    assert status == "failed"
    assert "403" in summarizer._download_failure_reasons[LONG_URL]
