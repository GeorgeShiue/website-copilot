from dataclasses import dataclass


@dataclass
class BaseRunConfig:
    config_name: str = "default"
    run_name_use_config_name: bool = False


@dataclass
class WebsiteCrawlerRunConfig(BaseRunConfig):
    pass


@dataclass
class WebpageImageSummarizerRunConfig(BaseRunConfig):
    pass


@dataclass
class RagBuildRunConfig(BaseRunConfig):
    webpages_data_use_latest_results: bool = False


@dataclass
class RagQueryRunConfig(BaseRunConfig):
    force_rebuild: bool = False
    query_times: int = 1
