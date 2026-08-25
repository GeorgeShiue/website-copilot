"""DataManager: 專管 data/ 目錄的持久化資料管理模組。

與 RunManager 職責分離：
- RunManager: 專管 runs/ 目錄（歷史執行紀錄）
- DataManager: 專管 data/ 目錄（持久化發布區）
"""

import logging
import os
import shutil
from typing import Any

logger = logging.getLogger(__name__)


class DataManager:
    """管理 data/ 目錄的持久化資料。"""

    def __init__(self, base_folder: str = "data") -> None:
        """初始化 DataManager。

        Args:
            base_folder: 持久化資料的根資料夾（預設 data/）。
        """
        self.base_folder = base_folder
        os.makedirs(base_folder, exist_ok=True)

    # ----- Publish 方法 -----

    def publish_crawl_results(
        self,
        site_id: str,
        results: dict[str, Any],
        results_json_path: str | None = None,
        results_folder_path: str | None = None,
    ) -> str:
        """將爬取結果發布到 data/webpages/{site_id}/。

        Args:
            site_id: 站點識別碼。
            results: 爬取結果 dict。
            results_json_path: 原始 results.json 路徑（可選）。
            results_folder_path: 原始 results/ 資料夾路徑（可選）。

        Returns:
            發布後的 webpages 資料夾路徑。
        """
        webpages_path = os.path.join(self.base_folder, "webpages", site_id)
        os.makedirs(webpages_path, exist_ok=True)

        # 複製 results.json
        if results_json_path and os.path.isfile(results_json_path):
            dest_json = os.path.join(webpages_path, "results.json")
            shutil.copy2(results_json_path, dest_json)
            logger.info(f"Published results.json to {dest_json}")

        # 複製 results/ 資料夾（Markdown 檔案）
        if results_folder_path and os.path.isdir(results_folder_path):
            dest_results = os.path.join(webpages_path, "results")
            if os.path.exists(dest_results):
                shutil.rmtree(dest_results)
            shutil.copytree(results_folder_path, dest_results)
            logger.info(f"Published results folder to {dest_results}")

        return webpages_path

    def publish_markdown(
        self,
        site_id: str,
        enhanced_results: dict[str, dict],
        results_folder_path: str | None = None,
    ) -> str:
        """發布增強後的 Markdown 到 data/webpages/{site_id}/results/。

        Args:
            site_id: 站點識別碼。
            enhanced_results: 增強後的爬取結果 dict。
            results_folder_path: 原始 results/ 資料夾路徑（可選）。

        Returns:
            發布後的 webpages 資料夾路徑。
        """
        webpages_path = os.path.join(self.base_folder, "webpages", site_id)
        os.makedirs(webpages_path, exist_ok=True)

        # 更新 results/ 資料夾中的 Markdown 檔案
        if results_folder_path and os.path.isdir(results_folder_path):
            dest_results = os.path.join(webpages_path, "results")
            os.makedirs(dest_results, exist_ok=True)

            # 寫入增強後的 Markdown
            for page_title, result in enhanced_results.items():
                md_file_path = os.path.join(dest_results, f"{page_title}.md")
                markdown = result.get("enhanced_markdown", "")
                with open(md_file_path, "w", encoding="utf-8") as f:
                    f.write(markdown)

            logger.info(f"Published enhanced markdown to {dest_results}")

        return webpages_path

    def publish_vector_store(
        self,
        site_id: str,
        vector_store_type: str,
        source_path: str,
    ) -> str:
        """發布向量庫到 data/rag/{site_id}/。

        Args:
            site_id: 站點識別碼。
            vector_store_type: 向量庫類型（milvus 或 qdrant）。
            source_path: 原始向量庫路徑。

        Returns:
            發布後的向量庫路徑。
        """
        rag_path = os.path.join(self.base_folder, "rag", site_id)
        os.makedirs(rag_path, exist_ok=True)

        if vector_store_type == "milvus":
            dest_path = os.path.join(rag_path, "milvus.db")
            # source == dest 時跳過，避免 rmtree 銷毀 source 後 copytree 失敗
            if os.path.realpath(source_path) == os.path.realpath(dest_path):
                logger.info(
                    f"Milvus vector store already at {dest_path}, skipping publish"
                )
            elif os.path.isdir(source_path):
                # Milvus 資料夾結構
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)
                logger.info(f"Published Milvus vector store to {dest_path}")
            elif os.path.isfile(source_path):
                shutil.copy2(source_path, dest_path)
                logger.info(f"Published Milvus vector store to {dest_path}")
        elif vector_store_type == "qdrant":
            dest_path = os.path.join(rag_path, "qdrant_db")
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(source_path, dest_path)
            logger.info(f"Published Qdrant vector store to {dest_path}")
        else:
            raise ValueError(f"Unsupported vector_store_type: {vector_store_type}")

        return rag_path

    # ----- Discover 方法 -----

    def list_sites(self) -> list[str]:
        """回傳所有可用的 site_id 列表。"""
        webpages_path = os.path.join(self.base_folder, "webpages")
        if not os.path.isdir(webpages_path):
            return []

        sites = []
        for item in os.listdir(webpages_path):
            item_path = os.path.join(webpages_path, item)
            if os.path.isdir(item_path):
                sites.append(item)
        return sorted(sites)

    def get_webpages_path(self, site_id: str) -> str:
        """回傳指定 site 的 webpages 路徑。"""
        return os.path.join(self.base_folder, "webpages", site_id)

    def get_vector_store_path(self, site_id: str) -> str:
        """回傳指定 site 的向量庫路徑。"""
        return os.path.join(self.base_folder, "rag", site_id)

    def site_exists(self, site_id: str) -> bool:
        """檢查 site 是否存在。"""
        webpages_path = self.get_webpages_path(site_id)
        return os.path.isdir(webpages_path)
