"""RAGRegistry：多站 RAG 實例管理器（lazy + LRU 快取）。

此模組為 RAGRegistry 的唯一定義位置，避免 tool.py ↔ site_discovery / webpage_retriever 循環引用。
"""

import logging
import os
from collections import OrderedDict

from app.configs.rag_config import RAGConfig
from app.engines.rag import RAG, RAGBuilder

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

    def _site_exists(self, site_id: str) -> bool:
        """檢查指定 site_id 對應的目錄是否存在。"""
        return os.path.isdir(os.path.join(self.base_folder, "webpages", site_id))

    def list_sites(self) -> list[str]:
        """回傳所有可用的 site_id 列表（掃描 data/webpages/）。"""
        webpages_path = os.path.join(self.base_folder, "webpages")
        if not os.path.isdir(webpages_path):
            return []
        return sorted(
            item
            for item in os.listdir(webpages_path)
            if os.path.isdir(os.path.join(webpages_path, item))
        )

    def get(self, site_id: str) -> RAG:
        """取得指定 site_id 的 RAG 實例（cache hit 直接回傳，miss 則 lazy build）。

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

        logger.info("RAG cache miss, building: site_id=%s", site_id)

        config = RAGConfig.from_toml(self.config_name, site_id=site_id)
        assert config.webpages_data_folder_path is not None
        rag = RAG(webpages_data_folder_path=config.webpages_data_folder_path)
        RAGBuilder(config).build_to_retriever(rag, force_rebuild=False)

        self._cache[site_id] = rag
        self._evict_if_needed()

        return rag

    def __enter__(self) -> "RAGRegistry":
        """進入 context manager，回傳 self。"""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> bool:
        """離開 context manager，釋放資源並傳播例外。"""
        self.close()
        return False

    def close(self) -> None:
        """釋放所有快取中的 RAG 實例資源。"""
        for site_id, rag in self._cache.items():
            logger.info("Closing RAG for site_id=%s", site_id)
            rag.close()
        self._cache.clear()

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
