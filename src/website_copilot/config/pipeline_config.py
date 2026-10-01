"""Run config 定義：控制 workflow 執行參數（config 名稱、save、publish 等）。

pipeline 函式一律接收 run_config（必填）與 overrides；CLI 的 module 覆寫參數由
`config/overrides.py` 從各 module config 自動產生，不在此定義。

`config_name` 在 CLI 上為 `--run.config`（Python 屬性維持 config_name，避免與 config 物件混淆）。
`site` 為必填的位置參數（如 `website-copilot prepare ncucsie`），對應 configs/sites/{site}.yml；
agent／serve 為多站，不需要 site。
"""

from dataclasses import dataclass
from typing import Annotated

import tyro

ConfigName = Annotated[str, tyro.conf.arg(name="config")]
Site = Annotated[str, tyro.conf.Positional, tyro.conf.arg(metavar="SITE")]


@dataclass
class BaseRunConfig:
    site: Site
    """站點名稱，對應 configs/sites/{site}.yml"""
    config_name: ConfigName = "default"
    run_name_use_config_name: bool = False
    publish: bool = False
    save: bool = True


@dataclass
class WebsiteCrawlerRunConfig(BaseRunConfig):
    pass


@dataclass
class ImageSummarizerRunConfig(BaseRunConfig):
    pass


@dataclass
class RAGBuildRunConfig(BaseRunConfig):
    webpages_data_use_latest_results: bool = False


@dataclass
class RAGQueryRunConfig(BaseRunConfig):
    vector_store_run: str | None = None
    """rag-build 的 run 資料夾（如 runs/<ts>/rag_build/<site>/<run_name>）；查詢其 results/milvus.db。
    未指定時查詢 data/ 中已 publish 的向量庫"""
    query_times: int = 1
    query: str | None = None
    """查詢問題；未指定時使用站點設定的 sample_query"""


@dataclass
class AgentRunConfig:
    query: str
    config_name: ConfigName = "default"
    thread_id: str | None = None
    stream: bool = False
    publish: bool = False


@dataclass
class PrepareRunConfig:
    """Prepare 階段（website-copilot prepare）的執行參數；site 與 config_name 同時決定各階段的設定。

    publish=True 時各階段結果 publish 到 data/（不存 runs/）；False（`--run.no-publish`）時
    只存到 runs/，RAG 以 runs/ 中本次的圖片摘要結果建庫。
    """

    site: Site
    """站點名稱，對應 configs/sites/{site}.yml"""
    config_name: ConfigName = "default"
    publish: bool = True


@dataclass
class ServeRunConfig:
    """Serve 階段（website-copilot serve）的執行參數；config_name 對應 configs/agent/{name}.yml。"""

    config_name: ConfigName = "default"
    host: str = "127.0.0.1"
    port: int = 8000
    allowed_origins: list[str] | None = None
