"""文件內嵌圖片：抽出與定位（anydoc／Docling）、描述插回文件、與頁面圖片共用過濾與重試。

解析以 monkeypatch 的 parse_document 提供（含佔位符與圖片），另以真實小檔驗證 anydoc 的圖片定位；
VLM 為 fake。不連網、不產生費用。
"""

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from augmentation_fakes import (
    COST_PER_CAPTION,
    FakeDownloader,
    FakeVLM,
    png_bytes,
)

from website_copilot.ingestion.augmentation import augmenter as augmenter_module
from website_copilot.ingestion.augmentation import documents as documents_module
from website_copilot.ingestion.augmentation.augmenter import Augmenter
from website_copilot.ingestion.augmentation.documents import (
    DocumentOptions,
    document_key,
)
from website_copilot.ingestion.augmentation.processors import (
    image_captioner as captioner_module,
)
from website_copilot.ingestion.augmentation.processors import pdf_parser
from website_copilot.ingestion.augmentation.processors.document_parser import (
    ParsedDocument,
    parse_document,
)
from website_copilot.ingestion.augmentation.processors.images import ParsedImage
from website_copilot.ingestion.augmentation.processors.office_parser import (
    office_to_markdown,
)

FIXTURES = Path("tests/fixtures/documents")
BASE = "https://www.csie.ncu.edu.tw"
PDF = b"%PDF-1.7\n%fake"
PLACEHOLDER = "<!-- image -->"


def _image(key: str, size: tuple[int, int] = (300, 200)) -> ParsedImage:
    return ParsedImage(content=png_bytes(*size, key), media_type="image/png")


# ----- anydoc：圖片位置 -----


def test_office_images_get_placeholders_at_their_positions() -> None:
    content = (FIXTURES / "form_with_images.doc").read_bytes()

    markdown, images = office_to_markdown(content, "doc", extract_images=True)

    assert markdown.count(PLACEHOLDER) == len(images) == 3
    assert all(i is not None and i.media_type == "image/png" for i in images)
    # 三張圖在表格之後、結尾說明文字之前
    assert markdown.index("離校系所同意書") < markdown.index(PLACEHOLDER)
    assert markdown.rindex(PLACEHOLDER) < markdown.index("完成表中簽名手續後")


def test_office_without_extraction_has_no_placeholders_or_images() -> None:
    content = (FIXTURES / "form_with_images.doc").read_bytes()

    markdown, images = office_to_markdown(content, "doc", extract_images=False)

    assert PLACEHOLDER not in markdown and images == []


def test_office_without_assets_is_plain_markdown() -> None:
    content = (FIXTURES / "form.odt").read_bytes()

    markdown, images = office_to_markdown(content, "odt", extract_images=True)

    assert PLACEHOLDER not in markdown and images == []


def test_parse_document_strips_placeholders_when_no_images(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "website_copilot.ingestion.augmentation.processors.document_parser.pdf_to_markdown",
        lambda content, extract_images: (f"# T\n\n{PLACEHOLDER}\n\n\n\n內文", []),
    )

    parsed = parse_document(PDF, "pdf", extract_images=False)

    assert parsed.markdown == "# T\n\n內文" and parsed.images == []


# ----- Docling：圖片與佔位符對位 -----


class _Picture:
    def __init__(self, image: Any) -> None:
        self._image = image

    def get_image(self, document: Any) -> Any:
        return self._image


def _converter_with(markdown: str, pictures: list[_Picture], monkeypatch) -> None:
    document = SimpleNamespace(export_to_markdown=lambda: markdown)
    monkeypatch.setattr(pdf_parser, "_pictures", lambda doc: pictures)
    monkeypatch.setattr(
        pdf_parser,
        "_converter",
        SimpleNamespace(convert=lambda stream: SimpleNamespace(document=document)),
    )


def test_pdf_pictures_are_encoded_in_placeholder_order(monkeypatch) -> None:
    from PIL import Image

    first, second = Image.new("RGB", (10, 20)), Image.new("RGB", (30, 40))
    _converter_with(
        f"文字\n\n{PLACEHOLDER}\n\n更多\n\n{PLACEHOLDER}\n",
        [
            _Picture(first),
            _Picture(second),
        ][:2],
        monkeypatch,
    )

    markdown, images = pdf_parser.pdf_to_markdown(PDF, extract_images=True)

    assert markdown.count(PLACEHOLDER) == 2
    assert [i.media_type for i in images if i] == ["image/png", "image/png"]
    from io import BytesIO

    assert [Image.open(BytesIO(i.content)).size for i in images if i] == [
        (10, 20),
        (30, 40),
    ]


def test_pdf_picture_count_mismatch_skips_images(monkeypatch) -> None:
    _converter_with(f"文字\n\n{PLACEHOLDER}\n", [], monkeypatch)

    _markdown, images = pdf_parser.pdf_to_markdown(PDF, extract_images=True)

    assert images == []
    assert parse_document(PDF, "pdf", extract_images=True).markdown == "文字"


def test_pdf_picture_without_image_keeps_its_position(monkeypatch) -> None:
    from PIL import Image

    _converter_with(
        f"{PLACEHOLDER}\n\n字\n\n{PLACEHOLDER}",
        [_Picture(None), _Picture(Image.new("RGB", (5, 5)))],
        monkeypatch,
    )

    _, images = pdf_parser.pdf_to_markdown(PDF, extract_images=True)

    assert images[0] is None and images[1] is not None


# ----- Augmenter：描述插回文件 -----


@pytest.fixture
def vlm(monkeypatch: pytest.MonkeyPatch):
    fake = FakeVLM()
    sleeps: list[float] = []
    monkeypatch.setattr(captioner_module, "acompletion", fake.acompletion)
    monkeypatch.setattr(
        captioner_module,
        "completion_cost",
        lambda completion_response: COST_PER_CAPTION,
    )
    monkeypatch.setattr(augmenter_module.time, "sleep", sleeps.append)
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    return fake, sleeps


def _parse_with(monkeypatch, outputs: dict[bytes, ParsedDocument]) -> list[bool]:
    """以內容為鍵提供解析結果；回傳每次呼叫的 extract_images。"""
    seen: list[bool] = []

    def fake_parse(content: bytes, file_format: str, extract_images: bool = False):
        seen.append(extract_images)
        parsed = outputs[content]
        if not extract_images:
            return ParsedDocument(
                markdown=parsed.markdown.replace(PLACEHOLDER, "").strip()
            )
        return parsed

    monkeypatch.setattr(documents_module, "parse_document", fake_parse)
    return seen


def _run(
    web: FakeDownloader,
    crawl_results: dict[str, dict[str, Any]],
    *,
    images_enabled: bool = True,
    caption_images: bool = True,
    max_retries: int = 3,
    min_size: int = 100,
):
    augmenter = Augmenter(
        downloader=web, success_threshold=0.8, max_retries=max_retries
    )
    results = augmenter.augment(
        crawl_results,
        model="gpt-test",
        prompt="describe",
        image_max_concurrency=4,
        image_source="markdown",
        image_min_size=min_size,
        images_enabled=images_enabled,
        documents=DocumentOptions(formats=("pdf",), caption_images=caption_images),
    )
    return augmenter, results


def _page(*links: str) -> dict[str, Any]:
    return {"url": f"{BASE}/p", "fit_markdown": "\n".join(links), "images": []}


def test_captions_replace_placeholders_in_document_markdown(monkeypatch, vlm) -> None:
    fake_vlm, _ = vlm
    url = f"{BASE}/a.pdf"
    markdown = f"# 報名流程\n\n{PLACEHOLDER}\n\n繳費說明\n\n{PLACEHOLDER}\n"
    content = PDF + b"1"
    _parse_with(
        monkeypatch,
        {content: ParsedDocument(markdown, [_image("flow"), _image("table")])},
    )
    web = FakeDownloader(contents={url: content})

    _augmenter, results = _run(web, {"p": _page(f"[報名]({url})")})

    entry = results[document_key(url)]
    assert entry["enhanced_markdown"] == (
        "# 報名流程\n\n> # Image-1\n>\n> caption of flow\n\n"
        "繳費說明\n\n> # Image-2\n>\n> caption of table"
    )
    assert sorted(fake_vlm.calls) == ["flow", "table"]
    assert entry["images"] == []  # 文件 entry 的 images 欄位維持空，描述已在內文
    assert results["p"]["enhanced_markdown"] == results["p"]["fit_markdown"]


def test_small_failed_and_unsupported_images_leave_no_placeholder(
    monkeypatch, vlm
) -> None:
    fake_vlm, _ = vlm
    fake_vlm.failing.add("broken")
    url = f"{BASE}/a.pdf"
    markdown = f"文字\n\n{PLACEHOLDER}\n\n{PLACEHOLDER}\n\n{PLACEHOLDER}\n\n{PLACEHOLDER}\n\n尾"
    content = PDF + b"2"
    unsupported = ParsedImage(content=b"not an image", media_type="image/x-emf")
    _parse_with(
        monkeypatch,
        {
            content: ParsedDocument(
                markdown,
                [_image("icon", (16, 16)), _image("broken"), unsupported, None],
            )
        },
    )
    web = FakeDownloader(contents={url: content})

    _, results = _run(web, {"p": _page(f"[文件]({url})")}, max_retries=1)

    assert results[document_key(url)]["enhanced_markdown"] == "文字\n\n尾"


def test_same_image_in_two_documents_is_captioned_once(monkeypatch, vlm) -> None:
    fake_vlm, _ = vlm
    url_a, url_b = f"{BASE}/a.pdf", f"{BASE}/b.pdf"
    content_a, content_b = PDF + b"A", PDF + b"B"
    logo = _image("logo")
    _parse_with(
        monkeypatch,
        {
            content_a: ParsedDocument(f"甲\n\n{PLACEHOLDER}", [logo]),
            content_b: ParsedDocument(f"乙\n\n{PLACEHOLDER}", [logo]),
        },
    )
    web = FakeDownloader(contents={url_a: content_a, url_b: content_b})

    _, results = _run(web, {"p": _page(f"[a]({url_a})", f"[b]({url_b})")})

    assert fake_vlm.calls == ["logo"]
    for url in (url_a, url_b):
        assert "caption of logo" in results[document_key(url)]["enhanced_markdown"]


def test_document_image_shares_description_with_identical_page_image(
    monkeypatch, vlm
) -> None:
    fake_vlm, _ = vlm
    url = f"{BASE}/a.pdf"
    page_image = f"{BASE}/same.png"
    shared = _image("same")
    content = PDF + b"3"
    _parse_with(
        monkeypatch, {content: ParsedDocument(f"文\n\n{PLACEHOLDER}", [shared])}
    )
    web = FakeDownloader(contents={url: content, page_image: shared.content})
    crawl_results = {
        "p": {
            "url": f"{BASE}/p",
            "fit_markdown": f"![x]({page_image})\n[doc]({url})",
            "images": [],
        }
    }

    _, results = _run(web, crawl_results)

    assert fake_vlm.calls == ["same"]  # 頁面圖片與文件內嵌圖片內容相同：只描述一次
    assert "caption of same" in results[document_key(url)]["enhanced_markdown"]
    assert "caption of same" in results["p"]["enhanced_markdown"]


def test_document_image_vlm_failure_is_retried(monkeypatch, vlm) -> None:
    fake_vlm, sleeps = vlm
    fake_vlm.failures["flow"] = 1
    url = f"{BASE}/a.pdf"
    content = PDF + b"4"
    _parse_with(
        monkeypatch, {content: ParsedDocument(f"文\n\n{PLACEHOLDER}", [_image("flow")])}
    )
    web = FakeDownloader(contents={url: content})

    augmenter, results = _run(web, {"p": _page(f"[a]({url})")})

    assert len(sleeps) == 1
    assert fake_vlm.calls == ["flow", "flow"]
    assert "caption of flow" in results[document_key(url)]["enhanced_markdown"]
    assert augmenter._failed_images == {}


def test_images_disabled_does_not_extract_or_caption(monkeypatch, vlm) -> None:
    fake_vlm, _ = vlm
    url = f"{BASE}/a.pdf"
    content = PDF + b"5"
    seen = _parse_with(
        monkeypatch, {content: ParsedDocument(f"文\n\n{PLACEHOLDER}", [_image("x")])}
    )
    web = FakeDownloader(contents={url: content})

    _, results = _run(web, {"p": _page(f"[a]({url})")}, images_enabled=False)

    assert seen == [False] and fake_vlm.calls == []
    assert results[document_key(url)]["enhanced_markdown"] == "文"


def test_caption_images_false_does_not_extract(monkeypatch, vlm) -> None:
    fake_vlm, _ = vlm
    url = f"{BASE}/a.pdf"
    content = PDF + b"6"
    seen = _parse_with(
        monkeypatch, {content: ParsedDocument(f"文\n\n{PLACEHOLDER}", [_image("x")])}
    )
    web = FakeDownloader(contents={url: content})

    _, results = _run(web, {"p": _page(f"[a]({url})")}, caption_images=False)

    assert seen == [False] and fake_vlm.calls == []
    assert results[document_key(url)]["enhanced_markdown"] == "文"


def test_real_office_images_are_described_end_to_end(vlm) -> None:
    """真實 .doc（3 張內嵌圖片）：以 anydoc 抽圖定位，描述插在對應位置。"""
    fake_vlm, _ = vlm
    url = f"{BASE}/form.doc"
    web = FakeDownloader(
        contents={url: (FIXTURES / "form_with_images.doc").read_bytes()}
    )
    augmenter = Augmenter(downloader=web, success_threshold=0.8, max_retries=1)

    results = augmenter.augment(
        {"p": _page(f"[離校同意書]({url})")},
        model="gpt-test",
        prompt="describe",
        image_max_concurrency=2,
        image_source="markdown",
        image_min_size=0,
        documents=DocumentOptions(formats=("doc",)),
    )

    markdown = results[document_key(url)]["enhanced_markdown"]
    assert len(fake_vlm.calls) == 3
    assert markdown.count("> # Image-") == 3
    assert PLACEHOLDER not in markdown
    assert markdown.index("> # Image-1") < markdown.index("完成表中簽名手續後")
