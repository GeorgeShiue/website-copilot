"""RAGRegistry：多站 RAG 實例管理器（lazy 載入 + LRU 快取，唯讀）。

只載入 prepare 階段已 publish 的向量庫（data/vector_db/{site_id}.db），不做任何建置。

此模組為 RAGRegistry 的唯一定義位置，避免 tool.py ↔ site_discovery / webpage_retriever 循環引用。
"""

import logging
import os
from collections import OrderedDict
from types import TracebackType
from typing import Self

from website_copilot.config.rag_config import RAGConfig
from website_copilot.retrieval.factory import load_rag, published_target
from website_copilot.retrieval.rag import RAG
from website_copilot.storage.data_paths import (
    site_id_from_vector_store_name,
    vector_db_folder,
    vector_store_path,
)

logger = logging.getLogger(__name__)


class RAGRegistry:
    """管理多站 RAG 實例（lazy + LRU 快取）。

    Attributes:
        _cache: site_id → RAG 的 LRU 快取（OrderedDict）。
        base_folder: 資料根目錄（預設 "data"）。
        config_name: RAG config 名稱（預設 "default"）。
        _max_cached: 快取上限，超出時淘汰最久未使用項。
    """

    def __init__(
        self,
        config_name: str = "default",
        base_folder: str = "data",
        max_cached: int = 5,
    ) -> None:
        self._cache: OrderedDict[str, RAG] = OrderedDict()
        self.base_folder = base_folder
        self.config_name = config_name
        self._max_cached = max_cached

    def __enter__(self) -> Self:
        """進入 context manager，回傳 self。"""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """離開 context manager，釋放資源並傳播例外。"""
        self.close()
        return False

    def list_sites(self) -> list[str]:
        """回傳所有可查詢的 site_id 列表（掃描 data/vector_db/ 下已 publish 向量庫的站點）。

        以向量庫而非 data/aug_webpages/ 判斷，避免列出 prepare 尚未完成 RAG 建置的站點。
        """
        vector_db_path = vector_db_folder(self.base_folder)
        if not os.path.isdir(vector_db_path):
            return []
        # 只認 {site_id}.db；.staging-*／.db.tmp／.db.old 等 publish 中間產物不是站點
        site_ids = (
            site_id_from_vector_store_name(item) for item in os.listdir(vector_db_path)
        )
        return sorted(
            site_id for site_id in site_ids if site_id and self._site_exists(site_id)
        )

    def get(self, site_id: str) -> RAG:
        """取得指定 site_id 的 RAG 實例（cache hit 直接回傳，miss 則載入已 publish 的向量庫）。

        Args:
            site_id: 目標知識庫的 site_id。

        Returns:
            已初始化至 retriever 層級的 RAG 實例。

        Raises:
            ValueError: site_id 不存在時。
        """
        if site_id in self._cache:
            self._cache.move_to_end(site_id)
            logger.info("RAG cache hit: site_id=%s", site_id)
            return self._cache[site_id]

        if not self._site_exists(site_id):
            raise ValueError(
                f"site_id '{site_id}' 不存在。"
                f"可用的站點：{', '.join(self.list_sites()) or '（無）'}"
            )

        logger.info("RAG cache miss, loading: site_id=%s", site_id)

        config = RAGConfig.from_yaml(self.config_name)
        # serve 階段唯讀：只載入 prepare 已 publish 的向量庫，不在 request 中建庫
        rag = load_rag(config, published_target(site_id, self.base_folder))

        self._cache[site_id] = rag
        self._evict_if_needed()

        return rag

    def close(self) -> None:
        """釋放所有快取中的 RAG 實例資源。"""
        for site_id, rag in self._cache.items():
            logger.info("Closing RAG for site_id=%s", site_id)
            rag.close()
        self._cache.clear()

    def _site_exists(self, site_id: str) -> bool:
        """檢查指定 site_id 是否已 publish 向量庫（data/vector_db/{site_id}.db 資料夾）。"""
        return os.path.isdir(vector_store_path(site_id, self.base_folder))

    def _evict_if_needed(self) -> None:
        """若快取超出上限，淘汰最久未使用的 RAG 實例。"""
        while len(self._cache) > self._max_cached:
            evicted_site_id, evicted_rag = self._cache.popitem(last=False)
            logger.info(
                "LRU eviction: site_id=%s (cache size=%d)",
                evicted_site_id,
                len(self._cache),
            )
            evicted_rag.close()
