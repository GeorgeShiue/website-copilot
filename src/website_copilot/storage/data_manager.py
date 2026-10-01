"""DataManager: 專管 data/ 目錄的持久化資料管理模組。

與 RunManager 職責分離：
- RunManager: 專管 runs/ 目錄（歷史執行紀錄）
- DataManager: 專管 data/ 目錄（持久化發布區）
"""

import json
import logging
import os
import shutil
import tempfile
from collections.abc import Callable
from typing import Any

from website_copilot.config.base_config import BaseModuleConfig
from website_copilot.config.site_config import SiteConfig
from website_copilot.schemas import GenerationResult
from website_copilot.storage.run_persistence import save_generated_exclude_words
from website_copilot.utils.config_helper import (
    save_module_config,
    save_run_config,
    save_site_config,
)

logger = logging.getLogger(__name__)

# 已發布向量庫（data/vector_db/{site_id}.db）內存放設定紀錄的資料夾
META_FOLDER_NAME = "meta"


def _remove_path(path: str) -> None:
    """刪除檔案或資料夾（不存在時略過）。"""
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)


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

        跟 publish_markdown() 寫入的 data/aug_webpages/{site_id}/ 完全分開存放——後者
        才是 image summarizer 產生、RAG 建庫實際讀取的最終版本
        （見 indexing.source.load_source），避免 image_summarizer 執行後
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
        """發布增強後的結果到 data/aug_webpages/{site_id}/（RAG 建庫實際讀取的最終版本）。

        enhanced_results 是 image_summarizer 就地在 crawl_results 上疊加
        enhanced_markdown 欄位後回傳的完整結果（每頁仍保留 url／images／metadata／
        crawl_info 等原始欄位），所以這裡連同 results.json 一起發布，讓
        data/aug_webpages/{site_id}/ 維持跟 RAG 目前預期的結構一致（results.json +
        results/*.md），RAG 端完全不用改。crawler 自己的原始輸出另外存在
        data/raw_webpages/{site_id}/（見 publish_crawl_results）。

        Args:
            site_id: 站點識別碼。
            enhanced_results: 增強後的爬取結果 dict（含原始欄位 + enhanced_markdown）。

        Returns:
            發布後的 aug_webpages 資料夾路徑。
        """
        aug_webpages_path = os.path.join(self.base_folder, "aug_webpages", site_id)
        os.makedirs(aug_webpages_path, exist_ok=True)

        results_json_path = os.path.join(aug_webpages_path, "results.json")
        with open(results_json_path, "w", encoding="utf-8") as f:
            json.dump(enhanced_results, f, ensure_ascii=False, indent=4)

        dest_results = os.path.join(aug_webpages_path, "results")
        os.makedirs(dest_results, exist_ok=True)
        self._write_markdown_files(dest_results, enhanced_results, "enhanced_markdown")
        logger.info(f"Published enhanced markdown to {dest_results}")

        return aug_webpages_path

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

    def vector_store_path(self, site_id: str) -> str:
        """已發布向量庫的位置 data/vector_db/{site_id}.db（Milvus Lite 要求資料夾名稱以 .db 結尾）。

        向量庫資料與設定紀錄（meta/）都在這個資料夾內，publish 時一起原子替換。
        """
        return os.path.join(self.base_folder, "vector_db", f"{site_id}.db")

    def create_vector_store_staging(self, site_id: str) -> str:
        """在 data/vector_db/ 下建立暫存資料夾（.staging-*），供建庫後原子替換。

        與正式向量庫位於同一檔案系統，publish 時可直接以 rename 移入；
        呼叫端負責在結束時刪除（無論成功或失敗）。向量庫應建在其中的 {site_id}.db。
        """
        rag_path = os.path.join(self.base_folder, "vector_db")
        os.makedirs(rag_path, exist_ok=True)
        return tempfile.mkdtemp(prefix=".staging-", dir=rag_path)

    def publish_vector_store(
        self,
        site_id: str,
        source_path: str,
        move: bool = False,
        write_meta: Callable[[str], None] | None = None,
    ) -> str:
        """以原子替換發布 Milvus 向量庫到 data/vector_db/{site_id}.db。

        先將新向量庫放到同目錄的 {site_id}.db.tmp，寫入 meta/ 後再以 rename 替換：
        舊 {site_id}.db → .old、.tmp → {site_id}.db，最後刪除 .old。
        正式路徑不會出現複製到一半的內容，向量庫與設定紀錄一定同版；已開啟舊向量庫的
        server 不受影響。

        Args:
            site_id: 站點識別碼。
            source_path: 原始向量庫路徑。
            move: True 時以 rename 移入（來源為同檔案系統的 staging，不保留來源）；
                False 時複製（來源為 runs/，保留來源）。
            write_meta: 以 meta 資料夾路徑呼叫，寫入設定紀錄（module_config.yml 等）；
                在替換前執行，失敗時不影響正式路徑。

        Returns:
            發布後的向量庫資料夾路徑。
        """
        os.makedirs(os.path.join(self.base_folder, "vector_db"), exist_ok=True)
        dest_path = self.vector_store_path(site_id)

        # source == dest 時跳過，避免清掉 dest 時連同 source 一起刪除
        if os.path.realpath(source_path) == os.path.realpath(dest_path):
            logger.info(f"Milvus vector store already at {dest_path}, skipping publish")
            return dest_path

        tmp_path = f"{dest_path}.tmp"
        old_path = f"{dest_path}.old"
        # 清掉前次中斷殘留的 .tmp／.old
        _remove_path(tmp_path)
        _remove_path(old_path)

        try:
            if move:
                shutil.move(source_path, tmp_path)
            elif os.path.isdir(source_path):
                shutil.copytree(source_path, tmp_path)
            else:
                raise NotADirectoryError(f"向量庫應為資料夾: {source_path}")

            if write_meta is not None:
                meta_path = os.path.join(tmp_path, META_FOLDER_NAME)
                os.makedirs(meta_path, exist_ok=True)
                write_meta(meta_path)

            if os.path.exists(dest_path):
                os.replace(dest_path, old_path)
            os.replace(tmp_path, dest_path)
        except BaseException:
            # 替換中途失敗：舊向量庫已移成 .old 時還原，確保正式路徑維持舊版
            if os.path.exists(old_path) and not os.path.exists(dest_path):
                os.replace(old_path, dest_path)
            raise
        finally:
            _remove_path(tmp_path)
        _remove_path(old_path)

        logger.info(f"Published Milvus vector store to {dest_path}")
        return dest_path

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
        config: BaseModuleConfig,
        site: SiteConfig,
        run_config: object | None = None,
        log_path: str | None = None,
    ) -> str:
        """一次發布 module_config.yml／site_config.yml／run_config.yml／terminal.log 到 data/{category}/{site_id}/。

        module_config／run_config 直接從物件序列化（不依賴 runs/ 已寫好的檔案）；
        log_path 仍是複製既有實體檔案（log 是執行期間寫入的，沒有記憶體物件可序列化）。

        Args:
            site_id: 站點識別碼。
            category: 目標子目錄（"raw_webpages" 或 "aug_webpages"）。
            config: 模組設定物件（用於序列化 module_config.yml）。
            site: 站點設定（用於序列化 site_config.yml）。
            run_config: Run 設定物件（可選，用於序列化 run_config.yml）。
            log_path: 原始 terminal.log 路徑（可選）。

        Returns:
            發布後的目標資料夾路徑。
        """
        dest_folder = os.path.join(self.base_folder, category, site_id)
        os.makedirs(dest_folder, exist_ok=True)
        self.write_run_metadata(dest_folder, config, site, run_config, log_path)
        return dest_folder

    def write_run_metadata(
        self,
        dest_folder: str,
        config: BaseModuleConfig,
        site: SiteConfig,
        run_config: object | None = None,
        log_path: str | None = None,
    ) -> None:
        """把 module_config.yml／site_config.yml／run_config.yml／terminal.log 寫入 dest_folder。"""
        save_module_config(config, os.path.join(dest_folder, "module_config.yml"))
        save_site_config(site, os.path.join(dest_folder, "site_config.yml"))
        if run_config is not None:
            save_run_config(run_config, os.path.join(dest_folder, "run_config.yml"))
        self._copy_single_file(log_path, dest_folder, "terminal.log")

    # ----- Discover 方法 -----

    def list_sites(self) -> list[str]:
        """回傳所有可用的 site_id 列表。"""
        aug_webpages_path = os.path.join(self.base_folder, "aug_webpages")
        if not os.path.isdir(aug_webpages_path):
            return []

        sites = []
        for item in os.listdir(aug_webpages_path):
            item_path = os.path.join(aug_webpages_path, item)
            if os.path.isdir(item_path):
                sites.append(item)
        return sorted(sites)

    def get_webpages_path(self, site_id: str) -> str:
        """回傳指定 site 的 aug_webpages 路徑。"""
        return os.path.join(self.base_folder, "aug_webpages", site_id)

    def get_vector_store_path(self, site_id: str) -> str:
        """回傳指定 site 的向量庫路徑（data/vector_db/{site_id}.db）。"""
        return self.vector_store_path(site_id)

    def site_exists(self, site_id: str) -> bool:
        """檢查 site 是否存在。"""
        aug_webpages_path = self.get_webpages_path(site_id)
        return os.path.isdir(aug_webpages_path)
