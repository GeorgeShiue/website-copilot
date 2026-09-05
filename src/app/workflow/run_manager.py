import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from rich import box
from rich.table import Table

from utils.log_helper import print_log

RESULTS_JSON_NAME = "results.json"

logger = logging.getLogger(__name__)


class RunManager:
    def __init__(
        self,
        module_name: str = "",
        base_folder: str = "runs",
    ) -> None:
        """初始化 RunManager。

        Args:
            module_name: 模組名稱（可選，之後由 for_run / for_run_no_site 設定）。
            base_folder: 執行結果的根資料夾（預設 runs/）。
                聊天記錄等非實驗資料可傳入其他資料夾（如 chats/）。
        """
        self.timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.base_folder = base_folder
        self.base_path = os.path.join(self.base_folder, self.timestamp)
        os.makedirs(self.base_path, exist_ok=True)

        self.module_name: str = ""
        self.module_path: str = ""
        self.site_id: str = ""
        self.site_path: str = ""
        self.run_name: str = ""
        self.run_path: str = ""

        self.results_folder_path: str = ""
        self.results_json_path: str = ""
        self.module_config_toml_path: str = ""
        self.run_config_toml_path: str = ""
        self.log_path: str = ""

        if module_name:
            self.module_name = module_name
            self.module_path = os.path.join(self.base_path, module_name)
            os.makedirs(self.module_path, exist_ok=True)

    @classmethod
    def for_run(
        cls,
        module: str,
        site_id: str,
        run_name: str,
        base_folder: str = "runs",
    ) -> "RunManager":
        """Atomic 3-layer init: module → site → run."""
        rm = cls(module, base_folder)
        rm.site_id = site_id
        rm.site_path = os.path.join(rm.module_path, site_id)
        os.makedirs(rm.site_path, exist_ok=True)
        rm.run_name = run_name
        rm.run_path = os.path.join(rm.site_path, run_name)
        os.makedirs(rm.run_path, exist_ok=True)
        rm.init_module_run_paths()
        return rm

    @classmethod
    def for_run_no_site(
        cls,
        module: str,
        run_name: str,
        base_folder: str = "runs",
    ) -> "RunManager":
        """Atomic 2-layer init: module → run (no site). For Agent."""
        rm = cls(module, base_folder)
        rm.run_name = run_name
        rm.run_path = os.path.join(rm.module_path, run_name)
        os.makedirs(rm.run_path, exist_ok=True)
        rm.init_module_run_paths()
        return rm

    def init_module_run_paths(self) -> None:
        if not self.module_name:
            raise ValueError("Module name must be set to initialize module run paths.")
        if not self.run_name:
            raise ValueError("Run name must be set to initialize module run paths.")

        self.results_json_path = os.path.join(self.run_path, RESULTS_JSON_NAME)
        self.results_folder_path = os.path.join(self.run_path, "results")
        os.makedirs(self.results_folder_path, exist_ok=True)
        self.module_config_toml_path = os.path.join(self.run_path, "module_config.toml")
        self.run_config_toml_path = os.path.join(self.run_path, "run_config.toml")
        self.log_path = os.path.join(self.run_path, "terminal.log")

    def log_run_paths(self, usage: str) -> None:
        """以 Rich 表格紀錄目前的實驗路徑設定（內部使用）。"""
        run_path_complete = [
            "Results json",
            "Module config toml",
            "Run config toml",
            "Log file",
        ]

        rows = [
            ("Base", self.base_path),
            ("Module", self.module_path),
            ("Run", self.run_path),
            ("Results folder", self.results_folder_path),
            ("Results json", self.results_json_path),
            ("Module config toml", self.module_config_toml_path),
            ("Run config toml", self.run_config_toml_path),
            ("Log file", self.log_path),
        ]

        table = Table(
            box=box.SIMPLE_HEAVY,
            show_lines=False,
            header_style="bold cyan",
        )
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Directory", style="white")
        table.add_column("Status", no_wrap=True)

        for path_key, raw_path in rows:
            path_value = ""
            status = ""
            path_obj = Path(raw_path)

            if usage == "init":
                if path_key in run_path_complete:
                    path_value = str(path_obj)
                    status = "[yellow]wait for saving[/yellow]"
                elif not path_obj.exists():
                    raise NotADirectoryError(
                        f"{path_key}:{raw_path} has not been created."
                    )
                else:
                    path_value = str(path_obj)
                    status = "[green]created[/green]"
            elif usage == "complete":
                if path_key in run_path_complete:
                    if not path_obj.exists():
                        path_value = "..."
                        status = "[red]not saved[/red]"
                    else:
                        path_value = str(path_obj)
                        status = "[green]saved[/green]"

            if path_value and status:
                table.add_row(path_key, path_value, status)

        print_log(table)

    def save_results_as_json(
        self, results: dict[str, Any], file_path: str | None = None
    ) -> None:
        """將結果寫入 JSON 檔案（爬取結果或 query 結果皆可）。

        Args:
            results: 要寫入的 dict。
            file_path: 目標檔案路徑（預設 self.results_json_path；
                亦可傳入其他路徑做分檔落盤，如 results_<thread_id>.json）。
        """
        if file_path is None:
            file_path = self.results_json_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

    @staticmethod
    def find_thread_history_path(
        base_folder: str,
        module_name: str,
        history_filename: str,
    ) -> str | None:
        """跨 run 目錄搜尋 thread 歷史檔（結果為最新時間戳的那份）。

        CLI 每次執行建立新的 timestamped run 目錄，但 thread 歷史需跨 run 累積。
        從 base_folder 下所有 timestamped 子目錄搜尋符合的歷史檔，
        回傳時間戳最新（lexicographically last）的那一個完整路徑；找不到回傳 None。

        Args:
            base_folder: runs/ 或 chats/ 根目錄。
            module_name: 模組名稱（如 "agent"）。
            history_filename: 要搜尋的檔名（如 "results_auto-87d6ce91.json"）。
        """
        if not os.path.isdir(base_folder):
            return None

        latest_path: str | None = None
        for entry in sorted(os.listdir(base_folder), reverse=True):
            entry_path = os.path.join(base_folder, entry)
            if not os.path.isdir(entry_path):
                continue
            # timestamped folder: 20260830_172330 (15 chars, starts with 20)
            if not (entry.startswith("20") and len(entry) == 15):
                continue
            module_path = os.path.join(entry_path, module_name)
            if not os.path.isdir(module_path):
                continue
            # recursively search for the history file
            for root, _dirs, files in os.walk(module_path):
                if history_filename in files:
                    candidate = os.path.join(root, history_filename)
                    if latest_path is None or candidate > latest_path:
                        latest_path = candidate
            if latest_path is not None:
                break  # already got the latest timestamp
        return latest_path
