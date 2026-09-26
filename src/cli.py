from dataclasses import dataclass

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


if __name__ == "__main__":
    import tyro

    from website_copilot.utils.log_helper import (
        setup_logging,
    )

    setup_logging("debug")

    cli_args_type = (
        WebsiteCrawlerCLI
        | WebpageImageSummarizerCLI
        | RAGBuildCLI
        | RAGQueryCLI
        | AgentCLI
    )
    cli_arg = tyro.cli(cli_args_type)
    module_config_overrides = {}
    for key, value in vars(cli_arg.module).items():
        if value is not None:
            if key == "weights":
                module_config_overrides["hybrid_ranker_params"] = {"weights": value}
            else:
                module_config_overrides[key] = value

    # 從 RunConfig 提前取出 publish／save，避免洩漏進 **config_overrides
    run_kwargs = vars(cli_arg.run)
    save = run_kwargs.pop("save", True)
    publish = run_kwargs.pop("publish", False)

    # 各分支才 import 對應階段的 workflow，避免載入用不到的依賴（如 server 不需爬蟲）
    if isinstance(cli_arg, WebsiteCrawlerCLI):
        from website_copilot.pipelines.prepare import run_website_crawler

        run_website_crawler(
            **run_kwargs,
            **module_config_overrides,
            save=save,
            publish=publish,
            run_config=cli_arg.run,
        )
    elif isinstance(cli_arg, WebpageImageSummarizerCLI):
        from website_copilot.pipelines.prepare import (
            run_webpage_image_summarizer,
        )

        run_webpage_image_summarizer(
            **run_kwargs,
            **module_config_overrides,
            save=save,
            publish=publish,
            run_config=cli_arg.run,
        )
    elif isinstance(cli_arg, RAGBuildCLI):
        from website_copilot.pipelines.prepare import run_rag_build

        run_rag_build(
            **run_kwargs,
            **module_config_overrides,
            save=save,
            publish=publish,
            run_config=cli_arg.run,
        )
    elif isinstance(cli_arg, RAGQueryCLI):
        from website_copilot.pipelines.eval import run_rag_query

        run_rag_query(
            **run_kwargs,
            **module_config_overrides,
            run_config=cli_arg.run,
        )
    elif isinstance(cli_arg, AgentCLI):
        from website_copilot.server.bootstrap import run_agent_query

        run_agent_query(
            config_name=cli_arg.run.config_name,
            query=cli_arg.run.query,
            thread_id=cli_arg.run.thread_id,
            stream=cli_arg.run.stream,
            run_config=cli_arg.run,
            **module_config_overrides,
        )
