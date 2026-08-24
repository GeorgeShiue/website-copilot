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

    from app.server.app import run_server
    from app.workflow.data_manager import DataManager
    from app.workflow.run_manager import RunManager
    from app.workflow.workflow import (
        run_agent,
        run_rag_build,
        run_rag_query,
        run_webpage_image_summarizer,
        run_website_crawler,
    )
    from utils.config_helper import save_run_config_as_toml
    from utils.log_helper import (
        setup_logging,
    )

    setup_logging("debug")

    run_manager = RunManager()

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
        run_manager.set_module_path("website_crawler")
        run_website_crawler(
            run_manager,
            **run_kwargs,
            **module_config_overrides,
            data_manager=data_manager,
        )
    elif isinstance(cli_arg, WebpageImageSummarizerCLI):
        run_manager.set_module_path("webpage_image_summarizer")
        run_webpage_image_summarizer(
            run_manager,
            **run_kwargs,
            **module_config_overrides,
            data_manager=data_manager,
        )
    elif isinstance(cli_arg, RAGBuildCLI):
        run_manager.set_module_path("rag_build")
        run_rag_build(
            run_manager,
            **run_kwargs,
            **module_config_overrides,
            data_manager=data_manager,
        )
    elif isinstance(cli_arg, RAGQueryCLI):
        run_manager.set_module_path("rag_query")
        run_rag_query(
            run_manager,
            **run_kwargs,
            **module_config_overrides,
        )
    elif isinstance(cli_arg, AgentCLI):
        # 聊天記錄與實驗分離：agent 使用獨立 RunManager（base_folder="chats"）
        agent_run_manager = RunManager("agent", base_folder="chats")
        run_agent(
            agent_run_manager=agent_run_manager,
            **run_kwargs,
            **module_config_overrides,
        )
        save_run_config_as_toml(cli_arg.run, agent_run_manager.run_config_toml_path)
        agent_run_manager.log_run_paths("complete")
    elif isinstance(cli_arg, ServerCLI):
        # 常駐服務：不落盤 run config（無 run_manager），由 run_server blocking 執行
        run_server(**vars(cli_arg.run))

    if not isinstance(cli_arg, (AgentCLI, ServerCLI)):
        save_run_config_as_toml(cli_arg.run, run_manager.run_config_toml_path)
        run_manager.log_run_paths("complete")
