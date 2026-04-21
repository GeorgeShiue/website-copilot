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
        self.results_json_path = self._set_results_json_path()
        logger.info("Paths initialized for experiment:")
        logger.info(f"  * Base path: {self.base_path}")
        logger.info(f"  * Results json path: {self.results_json_path}")
        logger.info("-" * 30)

        self.module_name = ""
        self.module_path: str = ""
        self.results_folder_path: str = ""
        self.config_toml_path: str = ""
        self.latest_results_json_path: str = ""

        if module_name:
            self.init_module_paths(module_name)

    def _set_base_path(self) -> str:
        """設定基本路徑並回傳 Markdown 檔案夾路徑。"""
        base_path = os.path.join(TEST_DATA_FOLDER_PATH, self.timestamp)
        os.makedirs(base_path, exist_ok=True)
        return base_path

    def _set_results_json_path(self) -> str:
        """設定爬取結果 JSON 路徑並回傳。"""
        results_json_path = os.path.join(self.base_path, RESULTS_JSON_NAME)
        return results_json_path

    def init_module_paths(self, module_name: str) -> None:
        """設定模組相關路徑。"""
        self.module_name = module_name
        self.module_path = self._set_module_path()
        self.results_folder_path = self._set_results_folder_path()
        self.config_toml_path = self._set_config_toml_path()

        logger.info(f"Paths initialized for module '{module_name}':")
        logger.info(f"  * Module path: {self.module_path}")
        logger.info(f"  * Results folder path: {self.results_folder_path}")
        logger.info(f"  * Config toml path: {self.config_toml_path}")
        logger.info("-" * 30)

    def _set_module_path(self) -> str:
        """設定模組路徑並回傳。"""
        module_path = os.path.join(self.base_path, self.module_name)
        os.makedirs(module_path, exist_ok=True)
        return module_path

    def _set_results_folder_path(self) -> str:
        """設定執行結果檔案夾路徑。"""
        results_folder_path = os.path.join(self.module_path, "results")
        os.makedirs(results_folder_path, exist_ok=True)
        return results_folder_path

    def _set_config_toml_path(self) -> str:
        """設定 TOML 設定檔路徑。"""
        config_path = os.path.join(self.module_path, "config.toml")
        return config_path

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
            markdown_file_name = result["markdown_file_name"]
            markdown_file_path = os.path.join(
                self.results_folder_path, markdown_file_name
            )
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

        # 篩選出包含爬取結果 JSON 的實驗資料夾
        exp_with_results_folder_names = []
        for folder_name in exp_folder_names:
            results_json_path = os.path.join(
                TEST_DATA_FOLDER_PATH, folder_name, RESULTS_JSON_NAME
            )
            if os.path.isfile(results_json_path):
                exp_with_results_folder_names.append(folder_name)
        if not exp_with_results_folder_names:
            raise FileNotFoundError(
                f"No experiment folders with crawl results found in {TEST_DATA_FOLDER_PATH}."
            )

        latest_exp_with_results_folder_name = sorted(exp_with_results_folder_names)[-1]
        latest_results_json_path = os.path.join(
            TEST_DATA_FOLDER_PATH,
            latest_exp_with_results_folder_name,
            RESULTS_JSON_NAME,
        )
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
            logger.error("Latest results JSON path is not set.")
            return None
        if not os.path.isfile(self.latest_results_json_path):
            logger.error(f"{self.latest_results_json_path} not found.")
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
