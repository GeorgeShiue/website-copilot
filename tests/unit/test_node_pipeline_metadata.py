"""NodePipelineBuilder 的 metadata 清洗，以及 DataManager 發布時清空舊 .md。"""

import json

import pytest

from website_copilot.ingestion.crawling.website_crawler import WebsiteCrawler
from website_copilot.ingestion.indexing.node_pipeline import NodePipelineBuilder
from website_copilot.storage.data_manager import DataManager
from website_copilot.utils.text_helper import MAX_DESCRIPTION_CHARS, clean_description


def test_clean_description_strips_html_and_truncates() -> None:
    raw = '<p>Hello <a href="x" attributionsrc="' + "a" * 5000 + '">world</a></p>'
    assert clean_description(raw) == "Hello world"
    long = clean_description("字" * 5000)
    assert len(long) == MAX_DESCRIPTION_CHARS + 1 and long.endswith("…")
    assert clean_description(None) == ""
    assert clean_description("A &amp; B&nbsp;C") == "A & B C"


def test_crawler_extract_metadata_cleans_description() -> None:
    raw = {"og:description": "<p>" + "x" * 6000 + "</p>"}
    metadata = WebsiteCrawler._extract_metadata("https://example.com/a", raw)
    assert len(metadata["description"]) == MAX_DESCRIPTION_CHARS + 1
    assert "<" not in metadata["description"]


def test_build_with_huge_description_does_not_exceed_chunk_size(tmp_path) -> None:
    md = tmp_path / "results"
    md.mkdir()
    (md / "page.md").write_text("# Title\n\n內容 " * 20, encoding="utf-8")
    results_json = {
        "page": {
            "url": "https://example.com/page",
            "metadata": {"description": "<p>" + "x" * 6000 + "</p>"},
        }
    }
    builder = NodePipelineBuilder(
        chunk_size=800, chunk_overlap=100, paragraph_separator="\n\n"
    )
    nodes = builder.build(str(md), results_json, "site")
    assert nodes
    assert all(
        len(n.metadata["description"]) <= MAX_DESCRIPTION_CHARS + 1 for n in nodes
    )


@pytest.mark.parametrize("publisher", ["publish_crawl_results", "publish_markdown"])
def test_publish_removes_stale_markdown(tmp_path, publisher: str) -> None:
    dm = DataManager(base_folder=str(tmp_path))
    category = (
        "raw_webpages" if publisher == "publish_crawl_results" else "aug_webpages"
    )
    results_dir = tmp_path / category / "site" / "results"
    results_dir.mkdir(parents=True)
    (results_dir / "stale.md").write_text("old", encoding="utf-8")
    (results_dir / "keep.txt").write_text("not markdown", encoding="utf-8")

    key = (
        "fit_markdown" if publisher == "publish_crawl_results" else "enhanced_markdown"
    )
    getattr(dm, publisher)("site", {"fresh": {key: "new"}})

    assert not (results_dir / "stale.md").exists()
    assert (results_dir / "fresh.md").read_text(encoding="utf-8") == "new"
    assert (results_dir / "keep.txt").exists()
    results_json = json.loads(
        (results_dir.parent / "results.json").read_text(encoding="utf-8")
    )
    assert list(results_json) == ["fresh"]
