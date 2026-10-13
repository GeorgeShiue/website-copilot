"""Augmenter 處理的資源（圖片、文件）：跨頁去重後的單位。"""

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class AssetRef:
    """一次引用：哪一頁、以什麼文字引用（圖片的 alt／連結文字）。"""

    page_key: str
    text: str = ""
    title: str = ""  # 連結的 title 屬性（圖片無則為空）


@dataclass
class Asset:
    url: str  # 去重鍵
    kind: Literal["image", "document"]
    refs: list[AssetRef] = field(
        default_factory=list
    )  # 依頁面順序，第一筆即第一個引用頁面

    @property
    def first_page(self) -> str:
        if not self.refs:
            raise ValueError(f"資源尚未有任何引用，無法取得第一個引用頁面：{self.url}")
        return self.refs[0].page_key
