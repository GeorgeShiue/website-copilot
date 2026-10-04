"""ImageCollector：圖片來源、副檔名過濾、跨頁去重與引用順序。"""

from website_copilot.ingestion.augmentation.assets import Asset, AssetRef
from website_copilot.ingestion.augmentation.collectors import ImageCollector

A, B, SVG = "https://ex.com/a.png", "https://ex.com/b.png", "https://ex.com/i.svg"

CRAWL_RESULTS = {
    "p1": {
        "fit_markdown": f"![x]({A})\n![y]({SVG})\n![z]({B})\n![x2]({A})",
        "images": [{"url": B}, {"url": A}, {"url": ""}],
    },
    "p2": {"fit_markdown": f"![x]({A})", "images": [{"url": A}]},
    "p3": {"fit_markdown": "no images"},
}


def test_markdown_source_dedups_across_pages_and_keeps_all_refs() -> None:
    assets = ImageCollector("markdown").collect(CRAWL_RESULTS)

    assert assets == [
        Asset(
            url=A,
            kind="image",
            refs=[AssetRef("p1"), AssetRef("p1"), AssetRef("p2")],
        ),
        Asset(url=B, kind="image", refs=[AssetRef("p1")]),
    ]
    assert assets[0].first_page == "p1"


def test_images_source_uses_images_field_in_order() -> None:
    assets = ImageCollector("images").collect(CRAWL_RESULTS)

    assert [(a.url, [r.page_key for r in a.refs]) for a in assets] == [
        (B, ["p1"]),
        (A, ["p1", "p2"]),
    ]


def test_unsupported_suffix_is_filtered_case_insensitively_ignoring_query() -> None:
    results = {
        "p": {
            "fit_markdown": "![a](https://ex.com/A.SVG?v=1) ![b](https://ex.com/b.avif)"
            " ![c](https://ex.com/c.png?x=.svg)"
        }
    }

    assets = ImageCollector("markdown").collect(results)

    assert [a.url for a in assets] == ["https://ex.com/c.png?x=.svg"]


def test_empty_results() -> None:
    assert ImageCollector("markdown").collect({}) == []
