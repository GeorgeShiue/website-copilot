"""Asset／AssetRef 與文件解析結果：不可變性與 first_page 的錯誤訊息。"""

from dataclasses import FrozenInstanceError

import pytest

from website_copilot.ingestion.augmentation.assets import Asset, AssetRef
from website_copilot.ingestion.augmentation.processors.document_parser import (
    ParsedDocument,
)
from website_copilot.ingestion.augmentation.processors.images import ParsedImage


def test_asset_ref_is_immutable() -> None:
    ref = AssetRef("p1", "text")

    with pytest.raises(FrozenInstanceError):
        ref.page_key = "p2"  # type: ignore[misc]


def test_parsed_results_are_immutable() -> None:
    document = ParsedDocument(markdown="# h")
    image = ParsedImage(content=b"x", media_type="image/png")

    with pytest.raises(FrozenInstanceError):
        document.markdown = "other"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        image.media_type = "image/jpeg"  # type: ignore[misc]


def test_first_page_is_the_first_reference() -> None:
    asset = Asset(url="https://ex.com/a.png", kind="image")
    asset.refs.append(AssetRef("p1"))
    asset.refs.append(AssetRef("p2"))

    assert asset.first_page == "p1"


def test_first_page_without_refs_raises_value_error_with_url() -> None:
    asset = Asset(url="https://ex.com/a.png", kind="image")

    with pytest.raises(ValueError, match="https://ex.com/a.png"):
        _ = asset.first_page
