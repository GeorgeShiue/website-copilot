"""RAGRegistry：多站 RAG 實例管理（lazy + LRU 快取）。

M3 多站 RAG 檢索的核心模組。管理多個 site_id 對應的 RAG 實例，
支援延遲建立（首次查詢時 build）與 LRU 快取淘汰（max_cached 限制同時載入數量）。

設計原則：
- Registry 不建立 RunManager（Agent 問答指向正式 data/，非 runs/ 中間層）
- 使用 RAGConfig.from_toml("default", site_id=site_id) 動態產生路徑
- 利用 Milvus 重用機制（build_reusable + load_collection）加速載入
"""

import logging
from collections import OrderedDict

from app.configs.rag_config import RAGConfig
from app.engines.rag import RAG, RAGBuilder
from app.workflow.data_manager import DataManager

logger = logging.getLogger(__name__)


class RAGRegistry:
    """管理多站 RAG 實例（lazy + LRU 快取）。

    Attributes:
        _cache: site_id → RAG 的 LRU 快取（OrderedDict）。
        _data_manager: DataManager 實例，用於 site 存在性驗證。
        _default_config_name: RAG config 名稱（預設 "default"）。
        _max_cached: 快取上限，超出時淘汰最久未使用項。
    """

    def __init__(
        self,
        data_manager: DataManager | None = None,
        default_config_name: str = "default",
        max_cached: int = 5,
    ) -> None:
        self._cache: OrderedDict[str, RAG] = OrderedDict()
        self._data_manager = data_manager or DataManager()
        self._default_config_name = default_config_name
        self._max_cached = max_cached

    def list_sites(self) -> list[str]:
        """回傳所有可用的 site_id 列表（掃描 data/webpages/）。"""
        return self._data_manager.list_sites()

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

        if not self._data_manager.site_exists(site_id):
            raise ValueError(
                f"site_id '{site_id}' 不存在。"
                f"可用的站點：{', '.join(self.list_sites()) or '（無）'}"
            )

        logger.info("RAG cache miss, building: site_id=%s", site_id)

        config = RAGConfig.from_toml(self._default_config_name, site_id=site_id)
        assert config.webpages_data_folder_path is not None
        rag = RAG(webpages_data_folder_path=config.webpages_data_folder_path)
        RAGBuilder(config).build_reusable(rag, force_rebuild=False)

        self._cache[site_id] = rag
        self._evict_if_needed()

        return rag

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
