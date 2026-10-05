import json
import os
import time
from pathlib import Path
from typing import Any

from rich import box
from rich.table import Table

from website_copilot.config.agent_config import AgentConfig
from website_copilot.storage.run_persistence import RESULTS_JSON_NAME, is_run_folder
from website_copilot.utils.config_helper import (
    MODULE_CONFIG_FILE,
    RUN_CONFIG_FILE,
    SITE_CONFIG_FILE,
)
from website_copilot.utils.log_helper import print_log


class RunManager:
    def __init__(
        self,
        module_name: str,
        base_folder: str = "runs",
    ) -> None:
        """初始化 RunManager。

        Args:
            module_name: 模組名稱（由 for_run / for_run_no_site 傳入）。
            base_folder: 執行結果的根資料夾（預設 runs/）。
        """
        self.timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.base_folder = base_folder
        self.base_path = os.path.join(self.base_folder, self.timestamp)
        os.makedirs(self.base_path, exist_ok=True)

        self.module_name = module_name
        self.module_path = os.path.join(self.base_path, module_name)
        os.makedirs(self.module_path, exist_ok=True)

        self.site_id: str = ""
        self.site_path: str = ""
        self.run_name: str = ""
        self.run_path: str = ""

        self.results_folder_path: str = ""
        self.results_json_path: str = ""
        self.module_config_path: str = ""
        self.run_config_path: str = ""
        self.site_config_path: str = ""
        self.log_path: str = ""

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
        if not self.run_name:
            raise ValueError("Run name must be set to initialize module run paths.")

        self.results_json_path = os.path.join(self.run_path, RESULTS_JSON_NAME)
        self.results_folder_path = os.path.join(self.run_path, "results")
        os.makedirs(self.results_folder_path, exist_ok=True)
        self.module_config_path = os.path.join(self.run_path, MODULE_CONFIG_FILE)
        self.run_config_path = os.path.join(self.run_path, RUN_CONFIG_FILE)
        self.site_config_path = os.path.join(self.run_path, SITE_CONFIG_FILE)
        self.log_path = os.path.join(self.run_path, "terminal.log")

    def log_run_paths(self, usage: str) -> None:
        """以 Rich 表格紀錄目前的實驗路徑設定（內部使用）。"""
        run_path_complete = [
            "Results json",
            "Module config",
            "Run config",
            "Site config",
            "Log file",
        ]

        rows = [
            ("Base", self.base_path),
            ("Module", self.module_path),
            ("Run", self.run_path),
            ("Results folder", self.results_folder_path),
            ("Results json", self.results_json_path),
            ("Module config", self.module_config_path),
            ("Run config", self.run_config_path),
            ("Log file", self.log_path),
        ]
        # 有站點的 run 另存 site_config.yml（agent／server 為多站，無此檔）
        if self.site_id:
            rows.insert(-1, ("Site config", self.site_config_path))

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
            elif usage == "complete" and path_key in run_path_complete:
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

    def save_agent_results_as_json(
        self,
        thread_id: str,
        results: list[dict[str, Any]],
        agent_config: AgentConfig,
    ) -> None:
        """將 Agent 對話結果落盤（分檔：results_{thread_id}.json）。

        合併邏輯：讀取既有歷史（含跨 run 目錄搜尋）→ extend 新結果 → 寫回。
        本方法與 save_results_as_json()（crawler / rag 模組）完全獨立。

        Args:
            thread_id: session 識別（檔名的一部分，'/' 會置換為 '_'）。
            results: 本輪新增的對話結果。
            agent_config: Agent 設定，由此組出檔案的 config 摘要
                （落盤責任上移後，呼叫端只需傳入 agent 自帶的設定）。

        Returns:
            None。檔案由 RunManager 內部管理，呼叫端無需持有路徑。
        """
        safe_id = thread_id.replace("/", "_")
        history_filename = f"results_{safe_id}.json"
        history_path = os.path.join(self.run_path, history_filename)

        existing_results: list[dict[str, Any]] = []
        if not os.path.isfile(history_path):
            found = RunManager.find_thread_history_path(
                self.base_folder,
                self.module_name,
                history_filename,
            )
            if found:
                history_path = found
        if os.path.isfile(history_path):
            try:
                with open(history_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                # CR S5：合法 JSON 但結構非預期（非 dict／results 非 list）時視為無歷史，
                # 避免 AttributeError 中斷落盤。
                if isinstance(existing, dict):
                    stored = existing.get("results", [])
                    existing_results = stored if isinstance(stored, list) else []
            except (json.JSONDecodeError, OSError):
                existing_results = []

        existing_results.extend(results)
        # config 摘要欄位與順序為落盤格式的一部分，重構前後須逐欄位等價（R3）
        config_summary = {
            "config_name": agent_config.config_name,
            "run_name": self.run_name,
            "llm_name": agent_config.llm_name,
            "system_prompt": agent_config.system_prompt,
        }
        results_dict = {
            "config": config_summary,
            "results": existing_results,
        }
        self.save_results_as_json(results_dict, file_path=history_path)

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
            base_folder: runs/ 根目錄。
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
            if not is_run_folder(entry):
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
