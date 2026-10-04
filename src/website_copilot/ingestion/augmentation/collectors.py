"""篩選：從爬取結果收集待處理的資源，跨頁去重。"""

from typing import Any, Literal
from urllib.parse import urlparse

from website_copilot.ingestion.augmentation.assets import Asset, AssetRef
from website_copilot.utils.text_helper import MARKDOWN_IMAGE_PATTERN

# VLM（OpenAI）僅支援 png / jpeg / gif / webp，其他格式（如 svg、avif）直接略過
UNSUPPORTED_IMAGE_SUFFIXES = (".svg", ".avif", ".bmp", ".ico", ".tif", ".tiff")


class ImageCollector:
    def __init__(self, source: Literal["images", "markdown"]) -> None:
        """source：圖片來源，爬蟲結果的 images 欄位或 fit_markdown 中的圖片連結。"""
        self.source = source

    def collect(self, crawl_results: dict[str, dict[str, Any]]) -> list[Asset]:
        """回傳不重複的圖片資源（依首次出現順序），refs 依頁面與頁內順序記錄所有引用。"""
        assets: dict[str, Asset] = {}
        for page_key, crawl_result in crawl_results.items():
            for url in self._page_image_urls(crawl_result):
                asset = assets.setdefault(url, Asset(url=url, kind="image"))
                asset.refs.append(AssetRef(page_key=page_key))
        return list(assets.values())

    def _page_image_urls(self, crawl_result: dict[str, Any]) -> list[str]:
        """單頁的圖片 URL（含重複，已排除 VLM 不支援的副檔名）。"""
        image_urls: list[str] = []
        if self.source == "markdown":
            image_urls = MARKDOWN_IMAGE_PATTERN.findall(
                crawl_result.get("fit_markdown", "")
            )
        elif self.source == "images":
            images = crawl_result.get("images", [])
            image_urls = [image.get("url", "") for image in images if image.get("url")]

        return [
            url
            for url in image_urls
            if not urlparse(url).path.lower().endswith(UNSUPPORTED_IMAGE_SUFFIXES)
        ]
