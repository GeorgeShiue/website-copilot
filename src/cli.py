from dataclasses import dataclass

from app.configs.workflow_config import (
    AgentModuleConfig,
    AgentRunConfig,
    RAGBuildRunConfig,
    RAGModuleConfig,
    RAGQueryRunConfig,
    ServerRunConfig,
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


@dataclass
class ServerCLI:
    run: ServerRunConfig


if __name__ == "__main__":
    import tyro

    from app.workflow.data_manager import DataManager
    from app.workflow.workflow import (
        run_agent_query,
        run_app,
        run_rag_build,
        run_rag_query,
        run_webpage_image_summarizer,
        run_website_crawler,
    )
    from utils.log_helper import (
        setup_logging,
    )

    setup_logging("debug")

    cli_args_type = (
        WebsiteCrawlerCLI
        | WebpageImageSummarizerCLI
        | RAGBuildCLI
        | RAGQueryCLI
        | AgentCLI
        | ServerCLI
    )
    cli_arg = tyro.cli(cli_args_type)
    module_config_overrides = {}
    if not isinstance(cli_arg, ServerCLI):
        for key, value in vars(cli_arg.module).items():
            if value is not None:
                if key == "weights":
                    module_config_overrides["hybrid_ranker_params"] = {"weights": value}
                else:
                    module_config_overrides[key] = value

    # 從 RunConfig 提前取出 publish，避免洩漏進 **config_overrides
    run_kwargs = vars(cli_arg.run) if not isinstance(cli_arg, ServerCLI) else {}
    publish = run_kwargs.pop("publish", False) if run_kwargs else False
    data_manager = DataManager() if publish else None

    if isinstance(cli_arg, WebsiteCrawlerCLI):
        run_website_crawler(
            **run_kwargs,
            **module_config_overrides,
            data_manager=data_manager,
            run_config=cli_arg.run,
        )
    elif isinstance(cli_arg, WebpageImageSummarizerCLI):
        run_webpage_image_summarizer(
            **run_kwargs,
            **module_config_overrides,
            data_manager=data_manager,
            run_config=cli_arg.run,
        )
    elif isinstance(cli_arg, RAGBuildCLI):
        run_rag_build(
            **run_kwargs,
            **module_config_overrides,
            data_manager=data_manager,
            run_config=cli_arg.run,
        )
    elif isinstance(cli_arg, RAGQueryCLI):
        run_rag_query(
            **run_kwargs,
            **module_config_overrides,
            run_config=cli_arg.run,
        )
    elif isinstance(cli_arg, AgentCLI):
        run_agent_query(
            config_name=cli_arg.run.config_name,
            query=cli_arg.run.query,
            thread_id=cli_arg.run.thread_id,
            stream=cli_arg.run.stream,
            run_config=cli_arg.run,
            **module_config_overrides,
        )
    elif isinstance(cli_arg, ServerCLI):
        server, chat_app = run_app(
            config_name=cli_arg.run.config_name,
            run_config=cli_arg.run,
            allowed_origins=cli_arg.run.allowed_origins,
            host=cli_arg.run.host,
            port=cli_arg.run.port,
        )
        try:
            server.run()
        finally:
            chat_app.close()
