import json
import logging
import os
import time

TEST_DATA_FOLDER_PATH = "./data/test"
RESULTS_JSON_NAME = "results.json"

logger = logging.getLogger(__name__)


class ExperimentManager:
    def __init__(self, module_name: str = "") -> None:
        self.timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.base_path = self._set_base_path()

        self.module_name: str = ""
        self.module_path: str = ""
        self.run_name: str = ""
        self.run_path: str = ""

        self.results_json_path = ""
        self.results_folder_path: str = ""
        self.config_toml_path: str = ""
        self.latest_results_json_path: str = ""

        # 預先檢查允許初始化時不用提供 module_name
        if module_name:
            self.set_module_path(module_name)

    def _set_base_path(self) -> str:
        """設定基本路徑並回傳 Markdown 檔案夾路徑。"""
        base_path = os.path.join(TEST_DATA_FOLDER_PATH, self.timestamp)
        os.makedirs(base_path, exist_ok=True)
        return base_path

    def set_module_path(self, module_name: str) -> None:
        """設定模組路徑並回傳。"""
        if not module_name:
            raise ValueError("Module name must be provided to set module path.")

        self.module_name = module_name
        module_path = os.path.join(self.base_path, module_name)
        os.makedirs(module_path, exist_ok=True)
        self.module_path = module_path

    def set_run_path(self, run_name: str) -> None:
        """設定實驗路徑並回傳。"""
        if not self.module_name:
            raise ValueError("Module name must be set before setting run path.")
        if not run_name:
            raise ValueError("Run name must be provided to set run path.")

        self.run_name = run_name
        run_path = os.path.join(self.module_path, self.run_name)
        os.makedirs(run_path, exist_ok=True)
        self.run_path = run_path

    def init_module_run_paths(self) -> None:
        if not self.module_name:
            raise ValueError("Module name must be set to initialize module run paths.")
        if not self.run_name:
            raise ValueError("Run name must be set to initialize module run paths.")

        self._set_results_json_path()
        self._set_results_folder_path()
        self._set_config_toml_path()

    def _log_paths(self) -> None:
        """紀錄目前的實驗路徑設定（內部使用）。"""
        logger.info(
            f"Experiment paths for module '{self.module_name}' run '{self.run_name}':"
        )
        logger.info(f"  * Base path: {self.base_path}")
        logger.info(f"  * Module path: {self.module_path}")
        logger.info(f"  * Run path: {self.run_path}")
        logger.info(f"  * Results json path: {self.results_json_path}")
        logger.info(f"  * Results folder path: {self.results_folder_path}")
        logger.info(f"  * Config toml path: {self.config_toml_path}")

    def _set_results_json_path(self) -> None:
        """設定爬取結果 JSON 路徑並回傳。"""
        results_json_path = os.path.join(self.run_path, RESULTS_JSON_NAME)
        self.results_json_path = results_json_path

    def _set_results_folder_path(self) -> None:
        """設定執行結果檔案夾路徑。"""
        results_folder_path = os.path.join(self.run_path, "results")
        os.makedirs(results_folder_path, exist_ok=True)
        self.results_folder_path = results_folder_path

    def _set_config_toml_path(self) -> None:
        """設定 TOML 設定檔路徑。"""
        config_toml_path = os.path.join(self.run_path, "config.toml")
        self.config_toml_path = config_toml_path

    def save_results_as_json(self, results: list[dict]) -> None:
        """將爬取結果列表寫入 JSON 檔案。"""
        os.makedirs(os.path.dirname(self.results_json_path), exist_ok=True)
        with open(self.results_json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        self.latest_results_json_path = self.results_json_path

    def save_results_as_md(
        self,
        results: list[dict],
        markdown_type: str,
        save_images: bool = False,
    ) -> None:
        """將爬取結果寫入 Markdown 檔案。"""
        for result in results:
            md_file_path = result["md_file_name"] + ".md"
            markdown_file_path = os.path.join(self.results_folder_path, md_file_path)
            markdown = result[markdown_type]
            images = result["images"]

            with open(markdown_file_path, "w", encoding="utf-8") as f:
                f.write(markdown)
                if images and save_images:
                    f.write("\n" + "-" * 5 + "\n")
                    f.write("Images:\n\n")
                    for image in images:
                        f.write(f"![]({image['src']})\n")
                    f.write("\n" + "-" * 5 + "\n")

    def load_latest_results_from_json(self) -> list[dict]:
        """從 JSON 檔案讀取爬取結果列表。"""
        latest_results = self._load_latest_results()
        if latest_results is not None:
            return latest_results

        logger.info(f"Looking for experiment folders in {TEST_DATA_FOLDER_PATH}...")
        exp_folder_names = self._filter_exp_folders()

        # 由新到舊尋找第一份位於 website_crawler 子目錄中的 results.json
        latest_results_json_path = ""
        for folder_name in sorted(exp_folder_names, reverse=True):
            website_crawler_folder_path = os.path.join(
                TEST_DATA_FOLDER_PATH, folder_name, "website_crawler"
            )
            if not os.path.isdir(website_crawler_folder_path):
                continue

            for root, dirs, files in os.walk(website_crawler_folder_path):
                dirs.sort()
                files.sort()
                if RESULTS_JSON_NAME in files:
                    latest_results_json_path = os.path.join(root, RESULTS_JSON_NAME)
                    break

            if latest_results_json_path:
                break

        if not latest_results_json_path:
            raise FileNotFoundError("No crawl results found")

        self.latest_results_json_path = latest_results_json_path
        latest_results = self._load_latest_results()
        if latest_results is None:
            raise FileNotFoundError(
                f"Failed to load crawl results from {latest_results_json_path}."
            )

        return latest_results

    def _load_latest_results(self) -> list[dict] | None:
        """載入最新的爬取結果 JSON。"""
        if not self.latest_results_json_path:
            logger.warning("Latest results JSON path is not set.")
            return None
        if not os.path.isfile(self.latest_results_json_path):
            logger.warning(f"{self.latest_results_json_path} not found.")
            return None

        logger.info(f"Latest crawl results found at: {self.latest_results_json_path}")
        with open(self.latest_results_json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _filter_exp_folders(self) -> list[str]:
        """篩選出符合實驗資料夾命名規則的資料夾名稱列表。"""
        folder_names = os.listdir(TEST_DATA_FOLDER_PATH)
        exp_folder_names = []
        for folder_name in folder_names:
            if folder_name.startswith("20") and len(folder_name) == 15:
                exp_folder_names.append(folder_name)
        if not exp_folder_names:
            raise FileNotFoundError(
                f"No experiment folders found in {TEST_DATA_FOLDER_PATH}."
            )
        return exp_folder_names
