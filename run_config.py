from dataclasses import dataclass


# TODO: 移除 run_config 的 config_name 參數
# TODO: cli args 分兩大類：run_config, module_config
@dataclass
class BaseRun:
    config_name: str = "default"
    run_name_use_config_name: bool = False


@dataclass
class RunWebsiteCrawler(BaseRun):
    max_pages: int | None = None


@dataclass
class RunWebpageImageSummarizer(BaseRun):
    model: str = "gemini-3.1-flash-lite"


@dataclass
class RunRagBuild(BaseRun):
    chunk_size: int = 800


@dataclass
class RunRagQuery(BaseRun):
    force_rebuild: bool = False
    query_iterations: int = 1

    top_k: int = 5
