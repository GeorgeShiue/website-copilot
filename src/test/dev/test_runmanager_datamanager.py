"""RunManager + DataManager 重構單元測試。"""

import json
import os
import shutil
import tempfile

import pytest

from app.workflow.data_manager import DataManager
from app.workflow.run_manager import RunManager


class TestRunManagerRefactor:
    """RunManager 重構測試。"""

    def setup_method(self):
        """每個測試前建立臨時目錄。"""
        self.temp_dir = tempfile.mkdtemp()
        self.runs_dir = os.path.join(self.temp_dir, "runs")
        self.chats_dir = os.path.join(self.temp_dir, "chats")
        os.makedirs(self.runs_dir)
        os.makedirs(self.chats_dir)

    def teardown_method(self):
        """每個測試後清理臨時目錄。"""
        shutil.rmtree(self.temp_dir)

    def test_filter_run_folders_with_base_folder(self):
        """測試 _filter_run_folders 使用 self.base_folder 而非硬編碼常數。"""
        # 在 runs/ 目錄建立測試資料夾
        test_folders = ["20260819_100000", "20260819_110000", "invalid_folder"]
        for folder in test_folders:
            os.makedirs(os.path.join(self.runs_dir, folder))

        # 建立 RunManager 但不提供 module_name，避免自動建立 timestamp 資料夾
        run_manager = RunManager(base_folder=self.runs_dir)
        # 清除自動建立的 timestamp 資料夾以避免干擾
        auto_created = os.path.join(self.runs_dir, run_manager.timestamp)
        if os.path.exists(auto_created):
            shutil.rmtree(auto_created)

        run_folders = run_manager._filter_run_folders()

        # 應該只回傳符合格式的資料夾
        assert len(run_folders) == 2
        assert "20260819_100000" in run_folders
        assert "20260819_110000" in run_folders
        assert "invalid_folder" not in run_folders

    def test_filter_run_folders_empty_raises(self):
        """測試 _filter_run_folders 在空目錄時拋出 FileNotFoundError。"""
        # 使用一個完全空的目錄（不含 RunManager 自動建立的 timestamp）
        empty_dir = os.path.join(self.temp_dir, "empty_runs")
        os.makedirs(empty_dir)
        run_manager = RunManager(base_folder=empty_dir)
        # 清除 RunManager 自動建立的 timestamp 資料夾
        auto_created = os.path.join(empty_dir, run_manager.timestamp)
        if os.path.exists(auto_created):
            shutil.rmtree(auto_created)

        with pytest.raises(FileNotFoundError, match="No run folders found"):
            run_manager._filter_run_folders()

    def test_load_latest_results_from_json_with_base_folder(self):
        """測試 load_latest_results_from_json 使用 self.base_folder。"""
        # 建立測試資料結構
        run_timestamp = "20260819_100000"
        run_dir = os.path.join(self.runs_dir, run_timestamp, "website_crawler")
        os.makedirs(run_dir)

        # 建立測試 results.json
        test_results = {"page1": {"url": "http://example.com", "content": "test"}}
        results_json_path = os.path.join(run_dir, "results.json")

        with open(results_json_path, "w") as f:
            json.dump(test_results, f)

        run_manager = RunManager(base_folder=self.runs_dir)
        loaded_results = run_manager.load_latest_results_from_json()

        assert loaded_results == test_results

    def test_load_latest_summarizer_run_path_with_base_folder(self):
        """測試 load_latest_summarizer_run_path 使用 self.base_folder。"""
        # 建立測試資料結構
        run_timestamp = "20260819_100000"
        summarizer_dir = os.path.join(
            self.runs_dir, run_timestamp, "webpage_image_summarizer", "results"
        )
        os.makedirs(summarizer_dir)

        run_manager = RunManager(base_folder=self.runs_dir)
        latest_run_path = run_manager.load_latest_summarizer_run_path()

        expected_path = os.path.join(
            self.runs_dir, run_timestamp, "webpage_image_summarizer"
        )
        assert latest_run_path == expected_path

    def test_set_site_path_creates_four_layer_structure(self):
        """測試 set_site_path 建立四層路徑結構。"""
        run_manager = RunManager(base_folder=self.runs_dir)
        run_manager.set_module_path("website_crawler")
        run_manager.set_site_path("nculab")
        run_manager.set_run_path("default")

        # 驗證路徑結構
        assert run_manager.site_id == "nculab"
        assert "nculab" in run_manager.site_path
        assert run_manager.site_path in run_manager.run_path

        # 驗證目錄已建立
        assert os.path.isdir(run_manager.site_path)
        assert os.path.isdir(run_manager.run_path)

    def test_agent_base_folder_discover(self):
        """測試 Agent 場景（base_folder="chats"）的 _filter_run_folders 功能。"""
        # 建立 chats/ 目錄下的測試資料
        run_timestamp = "20260819_100000"
        agent_dir = os.path.join(self.chats_dir, run_timestamp, "agent")
        os.makedirs(agent_dir)

        # 建立測試 results.json
        test_results = {"response": "test response"}
        results_json_path = os.path.join(agent_dir, "results.json")

        with open(results_json_path, "w") as f:
            json.dump(test_results, f)

        run_manager = RunManager("agent", base_folder=self.chats_dir)
        # 驗證 _filter_run_folders 能在 chats/ 目錄找到正確的 run 資料夾
        run_folders = run_manager._filter_run_folders()
        assert run_timestamp in run_folders


class TestDataManager:
    """DataManager 測試。"""

    def setup_method(self):
        """每個測試前建立臨時目錄。"""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, "data")
        os.makedirs(self.data_dir)

    def teardown_method(self):
        """每個測試後清理臨時目錄。"""
        shutil.rmtree(self.temp_dir)

    def test_list_sites_empty(self):
        """測試 list_sites 在空目錄時回傳空列表。"""
        data_manager = DataManager(base_folder=self.data_dir)
        sites = data_manager.list_sites()
        assert sites == []

    def test_list_sites_with_sites(self):
        """測試 list_sites 回傳正確的站點列表。"""
        # 建立測試站點目錄
        sites = ["nculab", "ncucsie", "test_site"]
        for site in sites:
            os.makedirs(os.path.join(self.data_dir, "webpages", site))

        data_manager = DataManager(base_folder=self.data_dir)
        listed_sites = data_manager.list_sites()

        assert sorted(listed_sites) == sorted(sites)

    def test_site_exists(self):
        """測試 site_exists 判斷正確。"""
        data_manager = DataManager(base_folder=self.data_dir)

        # 站點不存在
        assert not data_manager.site_exists("nculab")

        # 建立站點
        os.makedirs(os.path.join(self.data_dir, "webpages", "nculab"))
        assert data_manager.site_exists("nculab")

    def test_get_webpages_path(self):
        """測試 get_webpages_path 回傳正確路徑。"""
        data_manager = DataManager(base_folder=self.data_dir)
        path = data_manager.get_webpages_path("nculab")
        expected = os.path.join(self.data_dir, "webpages", "nculab")
        assert path == expected

    def test_get_vector_store_path(self):
        """測試 get_vector_store_path 回傳正確路徑。"""
        data_manager = DataManager(base_folder=self.data_dir)
        path = data_manager.get_vector_store_path("nculab")
        expected = os.path.join(self.data_dir, "rag", "nculab")
        assert path == expected

    def test_publish_crawl_results(self):
        """測試 publish_crawl_results 正確複製檔案。"""
        data_manager = DataManager(base_folder=self.data_dir)

        # 建立來源資料
        source_dir = os.path.join(self.temp_dir, "source")
        os.makedirs(source_dir)
        results_json_path = os.path.join(source_dir, "results.json")
        results_folder_path = os.path.join(source_dir, "results")
        os.makedirs(results_folder_path)

        # 寫入測試資料
        test_results = {"page1": {"url": "http://example.com"}}
        with open(results_json_path, "w") as f:
            json.dump(test_results, f)

        # 寫入測試 Markdown
        with open(os.path.join(results_folder_path, "page1.md"), "w") as f:
            f.write("# Page 1")

        # 發布
        published_path = data_manager.publish_crawl_results(
            site_id="nculab",
            results=test_results,
            results_json_path=results_json_path,
            results_folder_path=results_folder_path,
        )

        # 驗證發布結果
        assert os.path.isdir(published_path)
        assert os.path.isfile(os.path.join(published_path, "results.json"))
        assert os.path.isdir(os.path.join(published_path, "results"))

        # 驗證內容
        with open(os.path.join(published_path, "results.json")) as f:
            published_results = json.load(f)
        assert published_results == test_results

    def test_publish_vector_store_milvus(self):
        """測試 publish_vector_store 正確複製 Milvus 向量庫。"""
        data_manager = DataManager(base_folder=self.data_dir)

        # 建立來源 Milvus 資料夾
        source_dir = os.path.join(self.temp_dir, "source_milvus")
        os.makedirs(source_dir)

        # 寫入測試資料
        with open(os.path.join(source_dir, "test.db"), "w") as f:
            f.write("test")

        # 發布
        published_path = data_manager.publish_vector_store(
            site_id="nculab",
            source_path=source_dir,
        )

        # 驗證發布結果
        dest_path = os.path.join(published_path, "milvus.db")
        assert os.path.isdir(dest_path)
        assert os.path.isfile(os.path.join(dest_path, "test.db"))
