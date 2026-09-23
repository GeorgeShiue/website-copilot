"""DataManager: 專管 data/ 目錄的持久化資料管理模組。

與 RunManager 職責分離：
- RunManager: 專管 runs/ 目錄（歷史執行紀錄）
- DataManager: 專管 data/ 目錄（持久化發布區）
"""

import json
import logging
import os
import shutil
from typing import Any

from app.engines.webpage_markdown_cleaner import GenerationResult
from app.workflow.run_persistence import save_generated_exclude_words
from utils.config_helper import save_module_config_as_toml, save_run_config_as_toml

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

    def publish_crawl_results(self, site_id: str, results: dict[str, Any]) -> str:
        """將爬取結果發布到 data/raw_webpages/{site_id}/（crawler 自己的原始輸出）。

        跟 publish_markdown() 寫入的 data/webpages/{site_id}/ 完全分開存放——後者
        才是 image summarizer 產生、RAG 建庫實際讀取的最終版本
        （見 RAG.md_docs_folder_path），避免 webpage_image_summarizer 執行後
        覆蓋掉 crawler 自己的原始輸出。

        Args:
            site_id: 站點識別碼。
            results: 爬取結果 dict。

        Returns:
            發布後的 raw_webpages 資料夾路徑。
        """
        raw_webpages_path = os.path.join(self.base_folder, "raw_webpages", site_id)
        os.makedirs(raw_webpages_path, exist_ok=True)

        results_json_path = os.path.join(raw_webpages_path, "results.json")
        with open(results_json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        dest_results = os.path.join(raw_webpages_path, "results")
        os.makedirs(dest_results, exist_ok=True)
        self._write_markdown_files(dest_results, results, "fit_markdown")

        return raw_webpages_path

    def publish_markdown(self, site_id: str, enhanced_results: dict[str, dict]) -> str:
        """發布增強後的結果到 data/webpages/{site_id}/（RAG 建庫實際讀取的最終版本）。

        enhanced_results 是 webpage_image_summarizer 就地在 crawl_results 上疊加
        enhanced_markdown 欄位後回傳的完整結果（每頁仍保留 url／images／metadata／
        crawl_info 等原始欄位），所以這裡連同 results.json 一起發布，讓
        data/webpages/{site_id}/ 維持跟 RAG 目前預期的結構一致（results.json +
        results/*.md），RAG 端完全不用改。crawler 自己的原始輸出另外存在
        data/raw_webpages/{site_id}/（見 publish_crawl_results）。

        Args:
            site_id: 站點識別碼。
            enhanced_results: 增強後的爬取結果 dict（含原始欄位 + enhanced_markdown）。

        Returns:
            發布後的 webpages 資料夾路徑。
        """
        webpages_path = os.path.join(self.base_folder, "webpages", site_id)
        os.makedirs(webpages_path, exist_ok=True)

        results_json_path = os.path.join(webpages_path, "results.json")
        with open(results_json_path, "w", encoding="utf-8") as f:
            json.dump(enhanced_results, f, ensure_ascii=False, indent=4)

        dest_results = os.path.join(webpages_path, "results")
        os.makedirs(dest_results, exist_ok=True)
        self._write_markdown_files(dest_results, enhanced_results, "enhanced_markdown")
        logger.info(f"Published enhanced markdown to {dest_results}")

        return webpages_path

    def _write_markdown_files(
        self,
        dest_folder: str,
        results: dict[str, dict],
        markdown_key: str,
    ) -> None:
        """把 results 逐頁寫成 {page_title}.md（publish_crawl_results／publish_markdown 共用）。"""
        for page_title, result in results.items():
            markdown = result.get(markdown_key, "")
            md_file_path = os.path.join(dest_folder, f"{page_title}.md")
            with open(md_file_path, "w", encoding="utf-8") as f:
                f.write(markdown)

    def publish_generated_exclude_words(
        self,
        site_id: str,
        generation_result: GenerationResult,
        raw_pages: dict[str, str],
    ) -> str:
        """發布 LLM 產生的 exclude_words 與報告到 data/raw_webpages/{site_id}/（crawler 自己的輸出）。

        Args:
            site_id: 站點識別碼。
            generation_result: LLM 產生的 exclude words 結果。
            raw_pages: 原始頁面內容 dict。

        Returns:
            發布後的 raw_webpages 資料夾路徑。
        """
        raw_webpages_path = os.path.join(self.base_folder, "raw_webpages", site_id)
        os.makedirs(raw_webpages_path, exist_ok=True)
        save_generated_exclude_words(generation_result, raw_pages, raw_webpages_path)
        return raw_webpages_path

    def publish_vector_store(
        self,
        site_id: str,
        source_path: str,
    ) -> str:
        """發布 Milvus 向量庫到 data/rag/{site_id}/。

        Args:
            site_id: 站點識別碼。
            source_path: 原始向量庫路徑。

        Returns:
            發布後的向量庫所在資料夾路徑。
        """
        rag_path = os.path.join(self.base_folder, "rag", site_id)
        os.makedirs(rag_path, exist_ok=True)

        dest_path = os.path.join(rag_path, "milvus.db")
        # source == dest 時跳過，避免 rmtree 銷毀 source 後 copytree 失敗
        if os.path.realpath(source_path) == os.path.realpath(dest_path):
            logger.info(f"Milvus vector store already at {dest_path}, skipping publish")
        elif os.path.isdir(source_path):
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(source_path, dest_path)
            logger.info(f"Published Milvus vector store to {dest_path}")
        elif os.path.isfile(source_path):
            shutil.copy2(source_path, dest_path)
            logger.info(f"Published Milvus vector store to {dest_path}")

        return rag_path

    # ----- Publish 元資料方法 -----

    def _copy_single_file(
        self,
        source_path: str | None,
        dest_folder: str,
        filename: str,
    ) -> None:
        """複製單一檔案到目標資料夾。"""
        if not source_path or not os.path.isfile(source_path):
            return
        dest_path = os.path.join(dest_folder, filename)
        shutil.copy2(source_path, dest_path)
        logger.info(f"Published {filename} to {dest_path}")

    def publish_run_metadata(
        self,
        site_id: str,
        category: str,
        config: object,
        run_config: object | None = None,
        log_path: str | None = None,
    ) -> str:
        """一次發布 module_config.toml／run_config.toml／terminal.log 到 data/{category}/{site_id}/。

        module_config／run_config 直接從物件序列化（不依賴 runs/ 已寫好的檔案）；
        log_path 仍是複製既有實體檔案（log 是執行期間寫入的，沒有記憶體物件可序列化）。

        Args:
            site_id: 站點識別碼。
            category: 目標子目錄（"webpages" 或 "rag"）。
            config: 模組設定物件（用於序列化 module_config.toml）。
            run_config: Run 設定物件（可選，用於序列化 run_config.toml）。
            log_path: 原始 terminal.log 路徑（可選）。

        Returns:
            發布後的目標資料夾路徑。
        """
        dest_folder = os.path.join(self.base_folder, category, site_id)
        os.makedirs(dest_folder, exist_ok=True)

        save_module_config_as_toml(
            config, os.path.join(dest_folder, "module_config.toml")
        )
        if run_config is not None:
            save_run_config_as_toml(
                run_config, os.path.join(dest_folder, "run_config.toml")
            )
        self._copy_single_file(log_path, dest_folder, "terminal.log")
        return dest_folder

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
