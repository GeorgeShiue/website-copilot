"""Run config 定義：控制 workflow 執行參數（config 名稱、save、publish 等）。

pipeline 函式一律接收 run_config（必填）與 overrides；CLI 的 module 覆寫參數由
`config/overrides.py` 從各 module config 自動產生，不在此定義。

`config_name` 在 CLI 上為 `--run.config`（Python 屬性維持 config_name，避免與 config 物件混淆）。
"""

from dataclasses import dataclass
from typing import Annotated

import tyro

ConfigName = Annotated[str, tyro.conf.arg(name="config")]


@dataclass
class BaseRunConfig:
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
    force_rebuild: bool = False
    query_times: int = 1


@dataclass
class AgentRunConfig:
    query: str
    config_name: ConfigName = "default"
    thread_id: str | None = None
    stream: bool = False
    publish: bool = False


@dataclass
class PrepareRunConfig:
    """Prepare 階段（website-copilot prepare）的執行參數；config_name 同時決定各階段使用的 config。

    publish=True 時各階段結果 publish 到 data/（不存 runs/）；False（`--run.no-publish`）時
    只存到 runs/，RAG 以 runs/ 中本次的圖片摘要結果建庫。
    """

    config_name: ConfigName = "default"
    publish: bool = True


@dataclass
class ServeRunConfig:
    """Serve 階段（website-copilot serve）的執行參數；config_name 對應 configs/agent/{name}.yml。"""

    config_name: ConfigName = "default"
    host: str = "127.0.0.1"
    port: int = 8000
    allowed_origins: list[str] | None = None
