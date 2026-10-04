"""文件：格式判斷、連結收集、標題規則，以及 Augmenter 的文件流程（下載 → 解析 → 獨立 entry）。

下載以 FakeDownloader 取代（不連網）；docx／doc／odt 解析使用 tests/fixtures/documents 的真實小檔
（anydoc 在本機解析，不產生費用）。
"""

import hashlib
from pathlib import Path
from typing import Any

import pytest
from augmentation_fakes import COST_PER_CAPTION, FakeDownloader, FakeVLM

from website_copilot.ingestion.augmentation import augmenter as augmenter_module
from website_copilot.ingestion.augmentation.assets import AssetRef
from website_copilot.ingestion.augmentation.augmenter import Augmenter
from website_copilot.ingestion.augmentation.collectors import (
    DocumentCollector,
    iter_markdown_links,
)
from website_copilot.ingestion.augmentation.document_format import (
    detect_format,
    disposition_file_name,
)
from website_copilot.ingestion.augmentation.documents import (
    DocumentOptions,
    document_key,
)
from website_copilot.ingestion.augmentation.processors import (
    image_captioner as captioner_module,
)
from website_copilot.ingestion.augmentation.titles import (
    choose_title,
    clean_link_text,
    is_generic,
)
from website_copilot.utils.document_rules import normalize_url

FIXTURES = Path("tests/fixtures/documents")
DOCX = (FIXTURES / "form.docx").read_bytes()
DOC = (FIXTURES / "form.doc").read_bytes()
ODT = (FIXTURES / "form.odt").read_bytes()

BASE = "https://www.csie.ncu.edu.tw"
API = f"{BASE}/app/index.php?Action=downloadfile&file="
SITE_PATTERNS = ("*Action=downloadfile*",)
FORMATS = ("docx", "doc", "odt")


# ----- 格式判斷 -----


def test_magic_bytes_win_over_misleading_headers() -> None:
    """下載 API 回 octet-stream、URL 無副檔名；內容才是依據（即使標頭／URL 說是 pdf）。"""
    headers = {
        "content-type": "application/pdf",
        "content-disposition": 'attachment; filename="a.pdf"',
    }
    assert detect_format(DOCX, headers, f"{API}x.pdf") == "docx"
    assert detect_format(ODT, {}, f"{API}x") == "odt"
    assert detect_format(DOC, {}, f"{API}x") == "doc"
    assert detect_format(b"%PDF-1.7\n%...", {}, f"{API}x") == "pdf"


def test_format_falls_back_to_disposition_then_content_type_then_url() -> None:
    junk = b"not a document"
    disposition = {"content-disposition": 'attachment; filename="a.odt"'}
    assert detect_format(junk, disposition, "https://ex.com/x") == "odt"
    content_type = {"content-type": "application/msword; charset=binary"}
    assert detect_format(junk, content_type, "https://ex.com/x") == "doc"
    assert detect_format(junk, {}, "https://ex.com/files/a.DOCX?v=1") == "docx"
    # Content-Disposition 先於 Content-Type 與 URL
    both = {**disposition, "content-type": "application/msword"}
    assert detect_format(junk, both, "https://ex.com/a.docx") == "odt"
    assert detect_format(junk, {}, "https://ex.com/app/index.php") is None
    assert detect_format(junk, {"content-type": "text/html"}, "https://ex.com/") is None


@pytest.mark.parametrize(
    ("disposition", "expected"),
    [
        ('attachment; filename="%E6%B7%A1.pdf";', "淡.pdf"),
        ("attachment; filename*=UTF-8''%E8%A1%A8.docx", "表.docx"),
        ("attachment; filename=plain.odt", "plain.odt"),
        ("inline", None),
    ],
)
def test_disposition_file_name(disposition: str, expected: str | None) -> None:
    assert disposition_file_name({"content-disposition": disposition}) == expected


# ----- 連結與收集 -----


def test_iter_markdown_links_text_title_and_icon_images() -> None:
    markdown = (
        '[表單](https://ex.com/a.odt "(另開新視窗)[下載]") '
        "[![](https://ex.com/icon.gif%20)\n檔名.pdf](https://ex.com/b.pdf) "
        "![img](https://ex.com/c.png)"
    )

    links = list(iter_markdown_links(markdown))

    assert links == [
        ("表單", "https://ex.com/a.odt", "(另開新視窗)[下載]"),
        ("![](https://ex.com/icon.gif%20)\n檔名.pdf", "https://ex.com/b.pdf", ""),
    ]


def _page(*links: str) -> dict[str, Any]:
    return {"url": f"{BASE}/p", "fit_markdown": "\n".join(links), "images": []}


def test_collector_dedups_across_pages_and_records_refs() -> None:
    crawl_results = {
        "p1": _page("[A](https://ex.com/a.odt#top)", "[B](https://ex.com/b.docx)"),
        "p2": _page('[A2](https://EX.com/a.odt "t")'),
    }

    collected = DocumentCollector(formats=FORMATS).collect(crawl_results)

    assert [a.url for a in collected.assets] == [
        "https://ex.com/a.odt",
        "https://ex.com/b.docx",
    ]
    assert collected.assets[0].refs == [
        AssetRef("p1", "A", ""),
        AssetRef("p2", "A2", "t"),
    ]


def test_collector_skips_disabled_formats_by_url_extension_only() -> None:
    crawl_results = {
        "p": _page(
            "[pdf](https://ex.com/a.pdf)",
            "[xls](https://ex.com/b.xlsx)",
            "[api](https://ex.com/app/index.php?Action=downloadfile&file=Zg)",
            "[page](https://ex.com/news)",
            "[icon](https://ex.com/pdf.gif%20)",
        )
    }

    collected = DocumentCollector(formats=FORMATS, site_patterns=SITE_PATTERNS).collect(
        crawl_results
    )

    assert collected.skipped_format == {
        "https://ex.com/a.pdf": "pdf",
        "https://ex.com/b.xlsx": "xlsx",
    }
    # 下載 API 沒有副檔名：先收進來，下載後依內容判斷
    assert [a.url for a in collected.assets] == [
        "https://ex.com/app/index.php?Action=downloadfile&file=Zg"
    ]


def test_collector_without_site_pattern_ignores_download_api() -> None:
    crawl_results = {"p": _page("[api](https://ex.com/index.php?Action=downloadfile)")}

    assert DocumentCollector(formats=FORMATS).collect(crawl_results).assets == []


def test_collector_respects_allowed_domains() -> None:
    crawl_results = {
        "p": _page(
            f"[in]({BASE}/a.odt)",
            "[sub](https://sub.csie.ncu.edu.tw/b.odt)",
            "[out](https://other.example.com/c.odt)",
        )
    }

    collected = DocumentCollector(
        formats=FORMATS, allowed_domains=["www.csie.ncu.edu.tw", "csie.ncu.edu.tw"]
    ).collect(crawl_results)

    assert [a.url for a in collected.assets] == [
        f"{BASE}/a.odt",
        "https://sub.csie.ncu.edu.tw/b.odt",
    ]
    assert collected.skipped_domain == 1
    unrestricted = DocumentCollector(formats=FORMATS).collect(crawl_results)
    assert len(unrestricted.assets) == 3


def test_collector_reads_links_from_all_pages_regardless_of_depth() -> None:
    crawl_results = {
        "p1": {**_page("[a](https://ex.com/a.odt)"), "crawl_info": {"depth": 0}},
        "deep": {**_page("[b](https://ex.com/b.odt)"), "crawl_info": {"depth": 2}},
    }

    collected = DocumentCollector(formats=FORMATS).collect(crawl_results)

    assert [a.first_page for a in collected.assets] == ["p1", "deep"]


def test_normalize_url_and_document_key() -> None:
    assert normalize_url("HTTPS://Ex.COM/A.odt#frag") == "https://ex.com/A.odt"
    assert normalize_url("https://ex.com/a?x=1&y=2") == "https://ex.com/a?x=1&y=2"
    key = document_key("https://ex.com/a.odt")
    assert key == "doc_" + hashlib.sha1(b"https://ex.com/a.odt").hexdigest()[:12]
    # 下載 API 的連結只差 query：鍵不會撞名
    assert document_key(f"{API}a") != document_key(f"{API}b")


# ----- 標題 -----


@pytest.mark.parametrize(
    "text",
    ["按我取得詳細資訊", "(另開新視窗)[下載]", "下載", "附件", "Download", "  "],
)
def test_generic_link_texts(text: str) -> None:
    assert is_generic(clean_link_text(text))


@pytest.mark.parametrize("text", ["表單下載", "碩士班修業辦法", "著作審查申請表"])
def test_meaningful_link_texts_are_not_generic(text: str) -> None:
    assert not is_generic(clean_link_text(text))


def test_clean_link_text_strips_icon_images_extension_and_quotes() -> None:
    raw = "![](https://ex.com/pdf.gif%20)\n淡江大學誠徵專任教師公告.pdf"
    assert clean_link_text(raw) == "淡江大學誠徵專任教師公告"
    assert clean_link_text("抵免資格考申請表」") == "抵免資格考申請表"
    assert clean_link_text("**獎學金申請表**") == "獎學金申請表"


def test_title_prefers_most_common_non_generic_link_text() -> None:
    refs = [
        AssetRef("p1", "按我取得詳細資訊", "(另開新視窗)[下載]"),
        AssetRef("p2", "修業辦法", ""),
        AssetRef("p3", "修業辦法", ""),
        AssetRef("p4", "辦法全文", ""),
    ]
    title = choose_title(refs, file_name="614882835.pdf", markdown="# H", fallback="x")
    assert title == "修業辦法"


def test_title_priority_chain() -> None:
    generic = AssetRef("p", "按我取得詳細資訊", "")
    # 2. title 屬性
    with_title = AssetRef("p", "下載", "獎學金申請表")
    assert choose_title([with_title], file_name="1.pdf", markdown="", fallback="f") == (
        "獎學金申請表"
    )
    # 3. 非純數字的檔名（去副檔名）
    assert choose_title(
        [generic], file_name="辦法.odt", markdown="# H", fallback="f"
    ) == ("辦法")
    # 4. 純數字檔名跳過，取內文第一個 heading
    assert (
        choose_title(
            [generic],
            file_name="614882835.pdf",
            markdown="x\n## 第一章\n",
            fallback="f",
        )
        == "第一章"
    )
    # 5. 沒有 heading：純數字檔名
    assert choose_title(
        [generic], file_name="614882835.pdf", markdown="x", fallback="f"
    ) == ("614882835")
    assert choose_title([generic], file_name=None, markdown="x", fallback="f") == "f"


# ----- Augmenter 的文件流程 -----


@pytest.fixture
def fakes(monkeypatch: pytest.MonkeyPatch):
    """安裝 fake VLM／sleep（圖片關閉的測試不需要 API key）。"""
    vlm = FakeVLM()
    sleeps: list[float] = []
    monkeypatch.setattr(captioner_module, "acompletion", vlm.acompletion)
    monkeypatch.setattr(
        captioner_module,
        "completion_cost",
        lambda completion_response: COST_PER_CAPTION,
    )
    monkeypatch.setattr(augmenter_module.time, "sleep", sleeps.append)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    return vlm, sleeps


def _augment(
    web: FakeDownloader,
    crawl_results: dict[str, dict[str, Any]],
    *,
    formats: tuple[str, ...] = FORMATS,
    images_enabled: bool = False,
    max_retries: int = 3,
) -> tuple[Augmenter, dict[str, dict[str, Any]]]:
    augmenter = Augmenter(
        downloader=web, success_threshold=0.8, max_retries=max_retries
    )
    results = augmenter.augment(
        crawl_results,
        model="gpt-test",
        prompt="describe",
        image_max_concurrency=4,
        image_source="markdown",
        image_min_size=100,
        images_enabled=images_enabled,
        documents=DocumentOptions(
            formats=formats,
            url_patterns=SITE_PATTERNS,
            allowed_domains=("www.csie.ncu.edu.tw",),
        ),
    )
    return augmenter, results


def _doc_entries(results: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {k: v for k, v in results.items() if k.startswith("doc_")}


def test_documents_become_independent_entries_with_original_files(fakes) -> None:
    url_a, url_b = f"{BASE}/static/file/form.odt", f"{API}Zm9ybQ"
    web = FakeDownloader(
        contents={url_a: ODT, url_b: DOCX},
        content_types={url_a: "application/vnd.oasis.opendocument.text"},
        headers={
            url_b: {
                "content-disposition": 'attachment; filename="%E7%94%B3%E8%AB%8B%E8%A1%A8.docx"'
            }
        },
    )
    crawl_results = {
        "p1": _page(f'[論文指導變更申請表]({url_a} "(另開新視窗)[下載]")'),
        "p2": _page(f"[按我取得詳細資訊]({url_b})", f"[變更申請表]({url_a})"),
    }

    augmenter, results = _augment(web, crawl_results)

    docs = _doc_entries(results)
    key_a, key_b = document_key(url_a), document_key(url_b)
    assert list(docs) == [key_a, key_b]
    assert list(results)[:2] == ["p1", "p2"]  # 頁面在前，文件接在後面

    entry = docs[key_a]
    assert entry["url"] == url_a
    assert entry["title"] == "論文指導變更申請表"
    assert "研究生論文指導變更申請表" in entry["enhanced_markdown"]
    assert entry["images"] == []
    metadata = entry["metadata"]
    assert metadata["page_type"] == "document"
    assert metadata["file_format"] == "odt"
    assert metadata["file_size"] == len(ODT)
    assert metadata["content_type"] == "application/vnd.oasis.opendocument.text"
    assert metadata["file_path"] == f"files/{key_a}.odt"
    assert metadata["source_pages"] == [
        {"url": f"{BASE}/p", "title": "p1", "link_text": "論文指導變更申請表"},
        {"url": f"{BASE}/p", "title": "p2", "link_text": "變更申請表"},
    ]
    # 下載 API：原始檔名取自 Content-Disposition，格式取自內容
    assert docs[key_b]["metadata"]["file_name"] == "申請表.docx"
    assert docs[key_b]["metadata"]["file_format"] == "docx"
    assert docs[key_b]["title"] == "申請表"  # 連結文字為通用字 → 檔名

    files = augmenter.document_files
    assert {k: (f.file_name, f.content) for k, f in files.items()} == {
        key_a: (f"{key_a}.odt", ODT),
        key_b: (f"{key_b}.docx", DOCX),
    }
    # 頁面不被改動：不加註、不內嵌文件內容
    assert results["p1"]["enhanced_markdown"] == crawl_results["p1"]["fit_markdown"]


def test_doc_and_odt_formats_are_parsed_too(fakes) -> None:
    url_doc, url_odt = f"{BASE}/a.doc", f"{BASE}/b.odt"
    web = FakeDownloader(contents={url_doc: DOC, url_odt: ODT})
    crawl_results = {"p": _page(f"[a]({url_doc})", f"[b]({url_odt})")}

    _, results = _augment(web, crawl_results)

    docs = _doc_entries(results)
    assert "外賓參訪成果介紹規畫表" in docs[document_key(url_doc)]["enhanced_markdown"]
    assert docs[document_key(url_doc)]["metadata"]["file_format"] == "doc"


def test_disabled_format_is_skipped_by_extension_without_download(fakes) -> None:
    pdf_url = f"{BASE}/辦法.pdf"
    web = FakeDownloader()
    crawl_results = {"p": _page(f"[辦法]({pdf_url})")}

    augmenter, results = _augment(web, crawl_results)

    assert web.downloads == []
    assert _doc_entries(results) == {}
    assert augmenter.document_files == {}


def test_format_detected_after_download_and_not_enabled_creates_no_entry(fakes) -> None:
    """下載 API 回的是 pdf（P2a 未啟用）：下載後才發現，不存檔、不建 entry，也不算失敗。"""
    url = f"{API}cGRm"
    web = FakeDownloader(contents={url: b"%PDF-1.7\n%fake"})
    crawl_results = {"p": _page(f"[辦法]({url})")}

    augmenter, results = _augment(web, crawl_results)

    assert web.downloads == [url]
    assert _doc_entries(results) == {}
    assert augmenter.document_files == {}
    assert augmenter._failed_documents == {}
    assert augmenter._documents is not None
    stats = augmenter._documents.stats()
    assert (stats.collected, stats.format_skipped, stats.success) == (1, 1, 0)


def test_same_content_with_different_urls_creates_one_entry(fakes) -> None:
    first, second = f"{API}YQ", f"{BASE}/static/file/copy.docx"
    web = FakeDownloader(contents={first: DOCX, second: DOCX})
    crawl_results = {
        "p1": _page(f"[A]({first})"),
        "p2": _page(f"[B]({second})"),
    }

    augmenter, results = _augment(web, crawl_results)

    docs = _doc_entries(results)
    assert list(docs) == [document_key(first)]  # 鍵取第一個 URL
    entry = docs[document_key(first)]
    assert entry["metadata"]["alternate_urls"] == [second]
    assert [p["title"] for p in entry["metadata"]["source_pages"]] == ["p1", "p2"]
    assert entry["title"] == "A"  # 各引用處最常出現者並列時取最早
    assert len(augmenter.document_files) == 1
    assert augmenter._documents is not None
    assert augmenter._documents.stats().duplicate_content == 1


def test_parse_failure_is_permanent_and_creates_no_entry(fakes) -> None:
    bad = f"{BASE}/broken.docx"
    good = f"{BASE}/good.odt"
    web = FakeDownloader(contents={bad: b"PK\x03\x04 garbage", good: ODT})
    crawl_results = {"p": _page(f"[bad]({bad})", f"[good]({good})")}

    augmenter, results = _augment(web, crawl_results)

    assert list(_doc_entries(results)) == [document_key(good)]
    assert set(augmenter._failed_documents) == {bad}
    assert augmenter._failed_documents[bad][1].startswith("parse failed")
    assert web.downloads.count(bad) == 1  # 解析失敗不重試


def test_permanent_download_errors_are_not_retried(fakes) -> None:
    _, sleeps = fakes
    gone = f"{BASE}/gone.odt"
    web = FakeDownloader(
        failures={gone: 99},
        errors={gone: ("HTTP 404", 404)},
        contents={f"{BASE}/ok.odt": ODT},
    )
    crawl_results = {"p": _page(f"[gone]({gone})", f"[ok]({BASE}/ok.odt)")}

    augmenter, _ = _augment(web, crawl_results)

    assert sleeps == []
    assert web.downloads.count(gone) == 1
    assert augmenter._failed_documents == {gone: ("p", "HTTP 404")}


def test_recoverable_download_failures_are_retried(fakes) -> None:
    _, sleeps = fakes
    flaky = f"{BASE}/flaky.odt"
    web = FakeDownloader(failures={flaky: 1}, contents={flaky: ODT})
    crawl_results = {"p": _page(f"[flaky]({flaky})")}

    augmenter, results = _augment(web, crawl_results)

    assert len(sleeps) == 1
    assert web.downloads.count(flaky) == 2
    assert list(_doc_entries(results)) == [document_key(flaky)]
    assert augmenter._failed_documents == {}


def test_images_and_documents_share_one_retry_round(
    fakes, monkeypatch: pytest.MonkeyPatch
) -> None:
    """成功率合併兩種資源計算；重試時兩種資源的可恢復失敗一起重做。"""
    _, sleeps = fakes
    img_ok, img_flaky = f"{BASE}/ok.png", f"{BASE}/flaky.png"
    doc_ok, doc_flaky = f"{BASE}/ok.odt", f"{BASE}/flaky.odt"
    # 兩份文件內容不同（避免被當成重複內容）
    web = FakeDownloader(
        failures={img_flaky: 1, doc_flaky: 1}, contents={doc_ok: ODT, doc_flaky: DOC}
    )
    markdown = [
        f"![i]({img_ok})",
        f"![i]({img_flaky})",
        f"[d]({doc_ok})",
        f"[f]({doc_flaky})",
    ]
    crawl_results = {
        "p": {"url": f"{BASE}/p", "fit_markdown": "\n".join(markdown), "images": []}
    }

    monkeypatch.setenv("OPENAI_API_KEY", "test")
    augmenter, results = _augment(web, crawl_results, images_enabled=True)

    # 第一輪：成功 2（圖片 1 + 文件 1）、可恢復失敗 2 → 成功率 50% < 80% → 一起重試
    assert len(sleeps) == 1
    assert web.downloads.count(img_flaky) == 2 and web.downloads.count(doc_flaky) == 2
    assert web.downloads.count(img_ok) == 1 and web.downloads.count(doc_ok) == 1
    assert sorted(_doc_entries(results)) == sorted(
        [document_key(doc_ok), document_key(doc_flaky)]
    )
    assert f"caption of {img_flaky}" in results["p"]["enhanced_markdown"]


def test_documents_none_leaves_documents_alone(
    fakes, monkeypatch: pytest.MonkeyPatch
) -> None:
    img = f"{BASE}/a.png"
    web = FakeDownloader()
    crawl_results = {
        "p": {
            "url": f"{BASE}/p",
            "fit_markdown": f"![i]({img})\n[d]({BASE}/a.odt)",
            "images": [],
        }
    }

    monkeypatch.setenv("OPENAI_API_KEY", "test")
    augmenter = Augmenter(downloader=web, success_threshold=0.8, max_retries=1)
    results = augmenter.augment(
        crawl_results,
        model="gpt-test",
        prompt="describe",
        image_max_concurrency=4,
        image_source="markdown",
        image_min_size=100,
    )

    assert web.downloads == [img]  # documents=None：不處理文件
    assert _doc_entries(results) == {}
    assert augmenter.document_files == {}


def test_images_disabled_needs_no_api_key_and_leaves_pages_unchanged(fakes) -> None:
    vlm, _ = fakes
    img = f"{BASE}/a.png"
    web = FakeDownloader(contents={f"{BASE}/a.odt": ODT})
    crawl_results = {
        "p": {
            "url": f"{BASE}/p",
            "fit_markdown": f"![i]({img})\n[d]({BASE}/a.odt)",
            "images": [{"url": img}],
        }
    }

    _, results = _augment(web, crawl_results, images_enabled=False)

    assert img not in web.downloads and vlm.calls == []
    assert results["p"]["enhanced_markdown"] == crawl_results["p"]["fit_markdown"]
    assert "caption" not in results["p"]["images"][0]
