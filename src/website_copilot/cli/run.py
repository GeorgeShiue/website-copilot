"""`website-copilot run <module>`：單模組執行（爬蟲／圖片摘要／RAG 建置／RAG 查詢／Agent）。

`--run.*` 為執行參數（RunConfig）；`--module.*` 為 module config 的覆寫值，由
`make_overrides_model()` 從各 module config 自動產生，巢狀結構與設定檔相同，如
`--module.retriever.similarity-top-k 20`。
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

import tyro

from website_copilot.config.agent_config import AgentConfig
from website_copilot.config.augmenter_config import AugmenterConfig
from website_copilot.config.overrides import make_overrides_model, overrides_to_dict
from website_copilot.config.pipeline_config import (
    AgentRunConfig,
    AugmenterRunConfig,
    RAGBuildRunConfig,
    RAGQueryRunConfig,
    WebsiteCrawlerRunConfig,
)
from website_copilot.config.rag_config import RAGConfig
from website_copilot.config.website_crawler_config import WebsiteCrawlerConfig

# 動態產生的 model 無法作為靜態型別，型別檢查時以 BaseModel 代替
if TYPE_CHECKING:
    from pydantic import BaseModel

    WebsiteCrawlerOverrides = BaseModel
    AugmenterOverrides = BaseModel
    RAGOverrides = BaseModel
    AgentOverrides = BaseModel
else:
    WebsiteCrawlerOverrides = make_overrides_model(WebsiteCrawlerConfig)
    AugmenterOverrides = make_overrides_model(AugmenterConfig)
    RAGOverrides = make_overrides_model(RAGConfig)
    AgentOverrides = make_overrides_model(AgentConfig)


@dataclass
class WebsiteCrawlerCLI:
    run: WebsiteCrawlerRunConfig
    module: WebsiteCrawlerOverrides
    """覆寫 configs/website_crawler/<config>.yml 的設定值；(default: ...) 為 config class 的預設值，--run.config 設定檔的值優先"""


@dataclass
class AugmenterCLI:
    run: AugmenterRunConfig
    module: AugmenterOverrides
    """覆寫 configs/augmenter/<config>.yml 的設定值；(default: ...) 為 config class 的預設值，--run.config 設定檔的值優先"""


@dataclass
class RAGBuildCLI:
    run: RAGBuildRunConfig
    module: RAGOverrides
    """覆寫 configs/rag/<config>.yml 的設定值；(default: ...) 為 config class 的預設值，--run.config 設定檔的值優先"""


@dataclass
class RAGQueryCLI:
    run: RAGQueryRunConfig
    module: RAGOverrides
    """覆寫 configs/rag/<config>.yml 的設定值；(default: ...) 為 config class 的預設值，--run.config 設定檔的值優先"""


@dataclass
class AgentCLI:
    run: AgentRunConfig
    module: AgentOverrides
    """覆寫 configs/agent/<config>.yml 的設定值；(default: ...) 為 config class 的預設值，--run.config 設定檔的值優先"""


ModuleCommand = (
    Annotated[WebsiteCrawlerCLI, tyro.conf.subcommand("website-crawler")]
    | Annotated[AugmenterCLI, tyro.conf.subcommand("augmenter")]
    | Annotated[RAGBuildCLI, tyro.conf.subcommand("rag-build")]
    | Annotated[RAGQueryCLI, tyro.conf.subcommand("rag-query")]
    | Annotated[AgentCLI, tyro.conf.subcommand("agent")]
)


@dataclass
class RunCLI:
    command: Annotated[ModuleCommand, tyro.conf.arg(name="")]


def main(cli: RunCLI) -> None:
    from website_copilot.utils.log_helper import setup_logging

    setup_logging("debug")

    command = cli.command
    overrides = overrides_to_dict(command.module)

    # 各分支才 import 對應階段的 workflow，避免載入用不到的依賴（如 server 不需爬蟲）
    if isinstance(command, WebsiteCrawlerCLI):
        from website_copilot.pipelines.prepare import run_website_crawler

        run_website_crawler(command.run, overrides)
    elif isinstance(command, AugmenterCLI):
        from website_copilot.pipelines.prepare import run_augmenter

        run_augmenter(command.run, overrides)
    elif isinstance(command, RAGBuildCLI):
        from website_copilot.pipelines.prepare import run_rag_build

        run_rag_build(command.run, overrides)
    elif isinstance(command, RAGQueryCLI):
        from website_copilot.pipelines.exp import run_rag_query

        run_rag_query(command.run, overrides)
    elif isinstance(command, AgentCLI):
        from website_copilot.pipelines.exp import run_agent_query

        run_agent_query(command.run, overrides)
