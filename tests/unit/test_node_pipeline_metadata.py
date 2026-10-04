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


# ----- 文件 entry：page_title、file metadata、source_pages -----


def _document_results_json(n_pages: int = 12) -> dict:
    """一份被 n_pages 頁引用的文件（source_pages 很長）。"""
    return {
        "doc_abc123": {
            "url": "https://example.com/files/a.odt",
            "title": "研究生論文指導變更申請表",
            "metadata": {
                "page_type": "document",
                "description": "",
                "file_format": "odt",
                "file_name": "申請表.odt",
                "source_pages": [
                    {
                        "url": f"https://example.com/p/{'x' * 60}-{i}",
                        "title": f"p_412-1013-{i}.php",
                        "link_text": "研究生論文指導變更申請表" * 2,
                    }
                    for i in range(n_pages)
                ],
            },
        }
    }


def _build_document_nodes(tmp_path, results_json: dict, chunk_size: int = 800):
    md = tmp_path / "results"
    md.mkdir()
    (md / "doc_abc123.md").write_text("# 申請表\n\n內容 " * 30, encoding="utf-8")
    builder = NodePipelineBuilder(
        chunk_size=chunk_size, chunk_overlap=100, paragraph_separator="\n\n"
    )
    return builder.build(str(md), results_json, "site")


def test_document_page_title_comes_from_entry_title(tmp_path) -> None:
    nodes = _build_document_nodes(tmp_path, _document_results_json(1))

    assert nodes
    for node in nodes:
        assert node.metadata["page_title"] == "研究生論文指導變更申請表"
        assert node.metadata["page_url"] == "https://example.com/files/a.odt"
        assert node.metadata["page_type"] == "document"
        assert node.metadata["file_format"] == "odt"
        assert node.metadata["file_name"] == "申請表.odt"


def test_page_without_title_keeps_key_as_page_title(tmp_path) -> None:
    md = tmp_path / "results"
    md.mkdir()
    (md / "news_a.md").write_text("# T\n\n內容", encoding="utf-8")
    builder = NodePipelineBuilder(
        chunk_size=800, chunk_overlap=100, paragraph_separator="\n\n"
    )

    (node, *_) = builder.build(
        str(md), {"news_a": {"url": "https://example.com/a", "metadata": {}}}, "site"
    )

    assert node.metadata["page_title"] == "news_a"
    assert "file_format" not in node.metadata


def test_long_source_pages_do_not_exceed_chunk_size_and_are_excluded(tmp_path) -> None:
    """source_pages 在切塊之後才寫入：即使很長也不會觸發 metadata 超過 chunk size，
    且排除於 embedding 與 LLM 文字之外。"""
    results_json = _document_results_json(12)

    nodes = _build_document_nodes(tmp_path, results_json, chunk_size=300)

    assert nodes
    expected = results_json["doc_abc123"]["metadata"]["source_pages"]
    for node in nodes:
        assert node.metadata["source_pages"] == expected
        assert "source_pages" in node.excluded_embed_metadata_keys
        assert "source_pages" in node.excluded_llm_metadata_keys
        assert "source_pages" not in node.get_content(metadata_mode="embed")  # type: ignore[arg-type]
        assert "source_pages" not in node.get_content(metadata_mode="llm")  # type: ignore[arg-type]


# ----- 文件原檔隨 aug_webpages 發布 -----


class _File:
    def __init__(self, file_name: str, content: bytes) -> None:
        self.file_name = file_name
        self.content = content


def test_publish_markdown_writes_document_files_and_removes_stale(tmp_path) -> None:
    dm = DataManager(base_folder=str(tmp_path))
    files_dir = tmp_path / "aug_webpages" / "site" / "files"
    files_dir.mkdir(parents=True)
    (files_dir / "doc_old.pdf").write_bytes(b"stale")
    (files_dir / "doc_keep.odt").write_bytes(b"old content")
    results = {"doc_keep": {"enhanced_markdown": "md"}, "p": {"enhanced_markdown": "x"}}

    site_path = dm.publish_markdown(
        "site",
        results,
        document_files={"doc_keep": _File("doc_keep.odt", b"new content")},
    )

    assert sorted(p.name for p in files_dir.iterdir()) == ["doc_keep.odt"]
    assert (files_dir / "doc_keep.odt").read_bytes() == b"new content"
    assert site_path == str(tmp_path / "aug_webpages" / "site")


def test_publish_markdown_without_documents_clears_files(tmp_path) -> None:
    dm = DataManager(base_folder=str(tmp_path))
    files_dir = tmp_path / "aug_webpages" / "site" / "files"
    files_dir.mkdir(parents=True)
    (files_dir / "doc_old.pdf").write_bytes(b"stale")

    dm.publish_markdown("site", {"p": {"enhanced_markdown": "x"}})

    assert list(files_dir.iterdir()) == []
