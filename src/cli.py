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
        run_agent,
        run_rag_build,
        run_rag_query,
        run_server,
        run_webpage_image_summarizer,
        run_website_crawler,
    )
    from utils.config_helper import save_run_config_as_toml
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

    run_manager = None
    if isinstance(cli_arg, WebsiteCrawlerCLI):
        _, run_manager = run_website_crawler(
            **run_kwargs,
            **module_config_overrides,
            data_manager=data_manager,
        )
    elif isinstance(cli_arg, WebpageImageSummarizerCLI):
        _, run_manager = run_webpage_image_summarizer(
            **run_kwargs,
            **module_config_overrides,
            data_manager=data_manager,
        )
    elif isinstance(cli_arg, RAGBuildCLI):
        run_manager = run_rag_build(
            **run_kwargs,
            **module_config_overrides,
            data_manager=data_manager,
        )
    elif isinstance(cli_arg, RAGQueryCLI):
        run_manager = run_rag_query(
            **run_kwargs,
            **module_config_overrides,
        )
    elif isinstance(cli_arg, AgentCLI):
        # run_agent 建立 agent_run_manager 並回傳
        agent_run_manager = run_agent(
            **run_kwargs,
            **module_config_overrides,
        )
        save_run_config_as_toml(cli_arg.run, agent_run_manager.run_config_toml_path)
        agent_run_manager.log_run_paths("complete")
        if data_manager is not None:
            data_manager.publish_run_metadata(
                site_id=cli_arg.run.config_name,
                category="agent",
                module_config_path=agent_run_manager.module_config_toml_path,
                run_config_path=agent_run_manager.run_config_toml_path,
                log_path=agent_run_manager.log_path,
            )
    elif isinstance(cli_arg, ServerCLI):
        # 常駐服務：不落盤 run config（無 run_manager），由 run_server blocking 執行
        run_server(**vars(cli_arg.run), mode="block")

    if run_manager is not None and not isinstance(cli_arg, ServerCLI):
        save_run_config_as_toml(cli_arg.run, run_manager.run_config_toml_path)
        run_manager.log_run_paths("complete")

    if (
        isinstance(cli_arg, RAGQueryCLI)
        and data_manager is not None
        and run_manager is not None
    ):
        data_manager.publish_run_metadata(
            site_id=run_manager.site_id,
            category="rag",
            module_config_path=run_manager.module_config_toml_path,
            run_config_path=run_manager.run_config_toml_path,
            log_path=run_manager.log_path,
        )
