"""建庫來源：prepare 產出的 webpages 資料夾（results.json + results/*.md）。"""

import json
import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Source:
    """建 nodes 所需的來源資料。

    Attributes:
        md_folder_path: Markdown 文件目錄（{webpages}/results）。
        results_json: 頁面 metadata（{webpages}/results.json）。
    """

    md_folder_path: str
    results_json: dict[str, Any]


def load_source(webpages_data_folder_path: str) -> Source:
    """載入 webpages 資料夾的建庫來源。

    Raises:
        FileNotFoundError: results.json 不存在時。
    """
    results_json_path = os.path.join(webpages_data_folder_path, "results.json")
    if not os.path.exists(results_json_path):
        raise FileNotFoundError(f"Results JSON file not found at {results_json_path}")
    with open(results_json_path, "r", encoding="utf-8") as f:
        results_json = json.load(f)
    return Source(
        md_folder_path=os.path.join(webpages_data_folder_path, "results"),
        results_json=results_json,
    )
