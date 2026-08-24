"""Run config 與 module config（CLI override 欄位）統一定義。

Run config 控制 workflow 執行參數（config_name、publish 等）。
Module config 定義 CLI 可覆寫的模組設定欄位（從 TOML 載入後可被 CLI 覆蓋）。
"""

from dataclasses import dataclass

# ════════════════════════════════════════════════════════════════════
#  Run Config
# ════════════════════════════════════════════════════════════════════


@dataclass
class BaseRunConfig:
    config_name: str = "default"
    run_name_use_config_name: bool = False
    publish: bool = False


@dataclass
class WebsiteCrawlerRunConfig(BaseRunConfig):
    pass


@dataclass
class WebpageImageSummarizerRunConfig(BaseRunConfig):
    pass


@dataclass
class RAGBuildRunConfig(BaseRunConfig):
    webpages_data_use_latest_results: bool = False
    save_vector_store_to_runs: bool = False


@dataclass
class RAGQueryRunConfig(BaseRunConfig):
    force_rebuild: bool = False
    query_times: int = 1


@dataclass
class AgentRunConfig:
    query: str
    config_name: str = "default"
    thread_id: str | None = None
    stream: bool = False


@dataclass
class ServerRunConfig:
    config_name: str = "default"
    host: str = "127.0.0.1"
    port: int = 8000
    allowed_origins: list[str] | None = None


# ════════════════════════════════════════════════════════════════════
#  Module Config（CLI override 欄位）
# ════════════════════════════════════════════════════════════════════


@dataclass
class WebsiteCrawlerModuleConfig:
    max_pages: int | None = None


@dataclass
class WebpageImageSummarizerModuleConfig:
    model: str | None = None


@dataclass
class RAGModuleConfig:
    hybrid_ranker: str | None = None
    weights: list[float] | None = None
    similarity_top_k: int | None = None
    query_mode: str | None = None
    hybrid_top_k: int | None = None
    alpha: float | None = None
    cutoff: float | None = None
    query: str | None = None


@dataclass
class AgentModuleConfig:
    site_id: str | None = None
    llm_name: str | None = None
    system_prompt: str | None = None
