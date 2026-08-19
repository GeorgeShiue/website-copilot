import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from rich import box
from rich.table import Table

from utils.log_helper import print_log

RUNS_FOLDER_PATH = "./runs"
os.makedirs(RUNS_FOLDER_PATH, exist_ok=True)
RESULTS_JSON_NAME = "results.json"
QUERY_MD_FILE_PREFIX = "query_"
RUN_PATH_COMPLETE = [
    "Results json",
    "Module config toml",
    "Run config toml",
    "Log file",
]

logger = logging.getLogger(__name__)


# TODO: 為每個模組客製化 RunManager
class RunManager:
    def __init__(
        self,
        module_name: str = "",
        base_folder: str = "runs",
    ) -> None:
        """初始化 RunManager。

        Args:
            module_name: 模組名稱（可選，之後可再 set_module_path）。
            base_folder: 執行結果的根資料夾（預設 runs/）。
                聊天記錄等非實驗資料可傳入其他資料夾（如 chats/）。
        """
        self.timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.base_folder = base_folder
        self.base_path = self._set_base_path()

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

        self.latest_results_json_path: str = ""
        self.latest_run_path: str = ""

        # 預先檢查允許初始化時不用提供 module_name
        if module_name:
            self.set_module_path(module_name)

    def _set_base_path(self) -> str:
        """設定基本路徑並回傳 Markdown 檔案夾路徑。"""
        base_path = os.path.join(self.base_folder, self.timestamp)
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

    def set_site_path(self, site_id: str) -> None:
        """設定站點路徑（可選，建立四層結構）。"""
        if not self.module_name:
            raise ValueError("Module name must be set before setting site path.")
        if not site_id:
            raise ValueError("Site ID must be provided to set site path.")

        self.site_id = site_id
        site_path = os.path.join(self.module_path, site_id)
        os.makedirs(site_path, exist_ok=True)
        self.site_path = site_path

    def clear_site_path(self) -> None:
        """清除站點路徑，回到三層結構。"""
        self.site_id = ""
        self.site_path = ""

    def set_run_path(self, run_name: str) -> None:
        """設定實驗路徑（支援 site_path）。"""
        if not self.module_name:
            raise ValueError("Module name must be set before setting run path.")
        if not run_name:
            raise ValueError("Run name must be provided to set run path.")

        self.run_name = run_name
        # 優先使用 site_path（四層結構），否則使用 module_path（三層結構）
        base_for_run = self.site_path if self.site_path else self.module_path
        run_path = os.path.join(base_for_run, self.run_name)
        os.makedirs(run_path, exist_ok=True)
        self.run_path = run_path

    def init_module_run_paths(self) -> None:
        if not self.module_name:
            raise ValueError("Module name must be set to initialize module run paths.")
        if not self.run_name:
            raise ValueError("Run name must be set to initialize module run paths.")

        self._set_results_json_path()
        self._set_results_folder_path()
        self._set_module_config_toml_path()
        self._set_run_config_toml_path()
        self._set_log_path()

    def log_run_paths(self, usage: str) -> None:
        """以 Rich 表格紀錄目前的實驗路徑設定（內部使用）。"""
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

            if usage == "init":
                path_value, status = self._log_run_path_init(raw_path, path_key)
            elif usage == "complete":
                path_value, status = self._log_run_path_complete(raw_path, path_key)

            if path_value and status:
                table.add_row(path_key, path_value, status)

        print_log(table)

    def _log_run_path_init(self, raw_path: str, path_key: str) -> tuple[str, str]:
        """以 Rich 表格紀錄路徑初始化狀態（內部使用）。"""
        path_obj = Path(raw_path)
        if path_key in RUN_PATH_COMPLETE:
            path_value = str(path_obj)
            status = "[yellow]wait for saving[/yellow]"
        elif not path_obj.exists():
            raise NotADirectoryError(f"{path_key}:{raw_path} has not been created.")
        else:
            path_value = str(path_obj)
            status = "[green]created[/green]"

        return path_value, status

    def _log_run_path_complete(self, raw_path: str, path_key: str) -> tuple[str, str]:
        """以 Rich 表格紀錄路徑已建立狀態（內部使用）。"""
        if path_key not in RUN_PATH_COMPLETE:
            return "", ""

        path_obj = Path(raw_path)
        if not path_obj.exists():
            path_value = "..."
            status = "[red]not saved[/red]"
        else:
            path_value = str(path_obj)
            status = "[green]saved[/green]"

        return path_value, status

    def _set_results_json_path(self) -> None:
        """設定爬取結果 JSON 路徑並回傳。"""
        results_json_path = os.path.join(self.run_path, RESULTS_JSON_NAME)
        self.results_json_path = results_json_path

    def _set_results_folder_path(self) -> None:
        """設定執行結果檔案夾路徑。"""
        results_folder_path = os.path.join(self.run_path, "results")
        os.makedirs(results_folder_path, exist_ok=True)
        self.results_folder_path = results_folder_path

    def _set_module_config_toml_path(self) -> None:
        """設定 module TOML 設定檔路徑。"""
        module_config_toml_path = os.path.join(self.run_path, "module_config.toml")
        self.module_config_toml_path = module_config_toml_path

    def _set_run_config_toml_path(self) -> None:
        """設定 run TOML 設定檔路徑。"""
        run_config_toml_path = os.path.join(self.run_path, "run_config.toml")
        self.run_config_toml_path = run_config_toml_path

    def _set_log_path(self) -> None:
        """設定實驗 log 檔案路徑。"""
        log_path = os.path.join(self.run_path, "terminal.log")
        self.log_path = log_path

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
        self.latest_results_json_path = file_path

    def save_results_as_md(
        self,
        results: dict[str, dict],
        markdown_type: str,
        save_images: bool = False,
    ) -> None:
        """將爬取結果寫入 Markdown 檔案。"""
        for page_title, result in results.items():
            md_file_path = page_title + ".md"
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

    def save_query_results_as_md(self, query_results: dict) -> None:
        """將每次 query 與回覆各寫為一份 Markdown 檔案。"""
        for result in query_results.get("results", []):
            index = result.get("index", 1)
            markdown = self._render_query_result_md(result)
            md_file_name = f"{QUERY_MD_FILE_PREFIX}{index}.md"
            md_file_path = os.path.join(self.results_folder_path, md_file_name)
            os.makedirs(os.path.dirname(md_file_path), exist_ok=True)
            with open(md_file_path, "w", encoding="utf-8") as f:
                f.write(markdown)

    def _render_query_result_md(self, result: dict) -> str:
        """將單次 query 的結果渲染為獨立的 Markdown 檔案（內部使用）。"""
        lines: list[str] = []
        lines.append(f"# Query #{result.get('index')}: {result.get('query', '')}")
        timestamp = result.get("timestamp")
        if timestamp:
            lines.append("")
            lines.append(f"> {timestamp}")
        lines.append("")
        lines.append("# Response")
        lines.append("")
        lines.append(str(result.get("response", "")))
        lines.append("")

        evaluation = result.get("evaluation")
        if evaluation:
            lines.append("# Evaluation")
            lines.append("")
            lines.append("| Metric | Passing | Score | Reason |")
            lines.append("|--------|:-------:|:-----:|--------|")
            for metric in ("faithfulness", "relevancy"):
                ev = evaluation.get(metric)
                if ev is None:
                    continue
                passing = ev.get("passing")
                mark = ":white_check_mark:" if passing else ":x:"
                score = ev.get("score")
                score_text = self._format_score(score)
                reason = self._escape_md_cell(
                    (ev.get("feedback") or "").replace("\n", " ")
                )
                lines.append(
                    f"| {metric.capitalize()} | {mark} | {score_text} | {reason} |"
                )
            lines.append("")

        sources = result.get("sources", [])
        lines.append(f"# Sources ({len(sources)})")
        lines.append("")
        if sources:
            lines.append("| # | Page | Type | Score | URL |")
            lines.append("|---|------|------|:-----:|-----|")
            for i, source in enumerate(sources, start=1):
                lines.append(
                    f"| {i} | {self._escape_md_cell(source.get('page_title', ''))} "
                    f"| {self._escape_md_cell(source.get('page_type', ''))} "
                    f"| {self._format_score(source.get('score'))} "
                    f"| {self._escape_md_cell(source.get('url', ''))} |"
                )
            lines.append("")
            for i, source in enumerate(sources, start=1):
                content = source.get("content", "")
                lines.append(f"**#{i} 內容片段：**")
                lines.append("")
                lines.append(self._to_blockquote(content))
                lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _format_score(score: object) -> str:
        return f"{score:.4f}" if isinstance(score, (int, float)) else "-"

    @staticmethod
    def _escape_md_cell(text: object) -> str:
        return str(text).replace("|", "\\|").replace("\n", " ")

    @staticmethod
    def _to_blockquote(text: object) -> str:
        """將多行文字轉為每行皆為引用區塊的 Markdown。"""
        return "\n".join(f"> {line}" for line in str(text).splitlines())

    def load_latest_results_from_json(self) -> dict[str, dict]:
        """從 JSON 檔案讀取爬取結果列表。"""
        latest_results = self._load_latest_results_json()
        if latest_results is not None:
            return latest_results

        logger.info(f"Looking for run folders in {self.base_folder}...")
        run_folder_names = self._filter_run_folders()

        # 由新到舊尋找第一份位於 website_crawler 子目錄中的 results.json
        latest_results_json_path = ""
        for folder_name in sorted(run_folder_names, reverse=True):
            website_crawler_folder_path = os.path.join(
                self.base_folder, folder_name, "website_crawler"
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
        latest_results = self._load_latest_results_json()
        if latest_results is None:
            self.latest_results_json_path = ""
            raise FileNotFoundError(
                f"Failed to load crawl results from {latest_results_json_path}."
            )

        return latest_results

    def load_latest_summarizer_run_path(self) -> str:
        """回傳最新 webpage_image_summarizer 的 run path（results 的上一層）。"""
        # 1. 若 latest_run_path 已指向 webpage_image_summarizer 則直接回傳
        if self.latest_run_path and "webpage_image_summarizer" in self.latest_run_path:
            logger.info(
                f"Latest summarizer run path already set: {self.latest_run_path}"
            )
            return self.latest_run_path

        # 2. 由新到舊尋找第一份 webpage_image_summarizer 子目錄中的 results 資料夾，回傳其 parent
        logger.info(
            f"Looking for webpage_image_summarizer run path in {self.base_folder}..."
        )
        run_folder_names = self._filter_run_folders()

        latest_run_path = ""
        for folder_name in sorted(run_folder_names, reverse=True):
            webpage_image_summarizer_folder_path = os.path.join(
                self.base_folder, folder_name, "webpage_image_summarizer"
            )
            if not os.path.isdir(webpage_image_summarizer_folder_path):
                continue

            for root, dirs, files in os.walk(webpage_image_summarizer_folder_path):
                dirs.sort()
                files.sort()
                if os.path.basename(root) == "results":
                    latest_run_path = os.path.dirname(root)
                    break

            if latest_run_path:
                break

        if not latest_run_path:
            raise FileNotFoundError(
                "No webpage_image_summarizer run path found in any run."
            )

        self.latest_run_path = latest_run_path
        logger.info(f"Found latest summarizer run path at: {self.latest_run_path}")

        return self.latest_run_path

    def _load_latest_results_json(self) -> dict[str, dict] | None:
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

    def _filter_run_folders(self) -> list[str]:
        """篩選出符合實驗資料夾命名規則的資料夾名稱列表。"""
        folder_names = os.listdir(self.base_folder)
        run_folder_names = []
        for folder_name in folder_names:
            if folder_name.startswith("20") and len(folder_name) == 15:
                run_folder_names.append(folder_name)
        if not run_folder_names:
            raise FileNotFoundError(f"No run folders found in {self.base_folder}.")
        return run_folder_names
