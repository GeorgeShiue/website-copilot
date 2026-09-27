"""`website-copilot run <module>`：單模組執行（爬蟲／圖片摘要／RAG 建置／RAG 查詢／Agent）。"""

from dataclasses import dataclass
from typing import Annotated

import tyro

from website_copilot.config.pipeline_config import (
    AgentModuleConfig,
    AgentRunConfig,
    RAGBuildRunConfig,
    RAGModuleConfig,
    RAGQueryRunConfig,
    WebpageImageSummarizerModuleConfig,
    WebpageImageSummarizerRunConfig,
    WebsiteCrawlerModuleConfig,
    WebsiteCrawlerRunConfig,
)


@dataclass
class WebsiteCrawlerCLI:
    run: WebsiteCrawlerRunConfig
    module: WebsiteCrawlerModuleConfig


@dataclass
class WebpageImageSummarizerCLI:
    run: WebpageImageSummarizerRunConfig
    module: WebpageImageSummarizerModuleConfig


@dataclass
class RAGBuildCLI:
    run: RAGBuildRunConfig
    module: RAGModuleConfig


@dataclass
class RAGQueryCLI:
    run: RAGQueryRunConfig
    module: RAGModuleConfig


@dataclass
class AgentCLI:
    run: AgentRunConfig
    module: AgentModuleConfig


ModuleCommand = (
    Annotated[WebsiteCrawlerCLI, tyro.conf.subcommand("website-crawler")]
    | Annotated[WebpageImageSummarizerCLI, tyro.conf.subcommand("image-summarizer")]
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
    module_config_overrides = {}
    for key, value in vars(command.module).items():
        if value is not None:
            if key == "weights":
                module_config_overrides["hybrid_ranker_params"] = {"weights": value}
            else:
                module_config_overrides[key] = value

    # 從 RunConfig 提前取出 publish／save，避免洩漏進 **config_overrides；
    # 複製一份再 pop，保留 command.run 本身的欄位，讓 run_config.toml 完整記錄
    run_kwargs = dict(vars(command.run))
    save = run_kwargs.pop("save", True)
    publish = run_kwargs.pop("publish", False)

    # 各分支才 import 對應階段的 workflow，避免載入用不到的依賴（如 server 不需爬蟲）
    if isinstance(command, WebsiteCrawlerCLI):
        from website_copilot.pipelines.prepare import run_website_crawler

        run_website_crawler(
            **run_kwargs,
            **module_config_overrides,
            save=save,
            publish=publish,
            run_config=command.run,
        )
    elif isinstance(command, WebpageImageSummarizerCLI):
        from website_copilot.pipelines.prepare import run_webpage_image_summarizer

        run_webpage_image_summarizer(
            **run_kwargs,
            **module_config_overrides,
            save=save,
            publish=publish,
            run_config=command.run,
        )
    elif isinstance(command, RAGBuildCLI):
        from website_copilot.pipelines.prepare import run_rag_build

        run_rag_build(
            **run_kwargs,
            **module_config_overrides,
            save=save,
            publish=publish,
            run_config=command.run,
        )
    elif isinstance(command, RAGQueryCLI):
        from website_copilot.pipelines.exp import run_rag_query

        run_rag_query(
            **run_kwargs,
            **module_config_overrides,
            run_config=command.run,
        )
    elif isinstance(command, AgentCLI):
        from website_copilot.pipelines.exp import run_agent_query

        run_agent_query(
            config_name=command.run.config_name,
            query=command.run.query,
            thread_id=command.run.thread_id,
            stream=command.run.stream,
            run_config=command.run,
            **module_config_overrides,
        )
