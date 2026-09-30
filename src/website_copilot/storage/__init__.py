"""Storage 模組：資料與 run 產物的管理及持久化。"""

from website_copilot.storage.data_manager import DataManager
from website_copilot.storage.run_manager import RunManager
from website_copilot.storage.run_persistence import (
    load_latest_results,
    load_latest_run_path,
    save_query_results_as_md,
    save_results_as_md,
)

__all__ = [
    "DataManager",
    "RunManager",
    "load_latest_results",
    "load_latest_run_path",
    "save_query_results_as_md",
    "save_results_as_md",
]
