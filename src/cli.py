from dataclasses import dataclass

from app.workflow.workflow_config import (
    RAGBuildRunConfig,
    RAGQueryRunConfig,
    WebpageImageSummarizerRunConfig,
    WebsiteCrawlerRunConfig,
)


@dataclass
class WebsiteCrawlerConfigCLI:
    # ----- init config -----
    max_pages: int | None = None


@dataclass
class WebpageImageSummarizerConfigCLI:
    # ----- init config -----
    model: str | None = None


@dataclass
class RAGConfigCLI:
    # ----- vector store config -----
    hybrid_ranker: str | None = None
    weights: list[float] | None = None
    # ----- retriever config -----
    similarity_top_k: int | None = None
    query_mode: str | None = None
    hybrid_top_k: int | None = None
    alpha: float | None = None
    # ----- query engine config -----
    cutoff: float | None = None
    query: str | None = None


@dataclass
class WebsiteCrawlerCLI:
    run: WebsiteCrawlerRunConfig
    module: WebsiteCrawlerConfigCLI


@dataclass
class WebpageImageSummarizerCLI:
    run: WebpageImageSummarizerRunConfig
    module: WebpageImageSummarizerConfigCLI


@dataclass
class RAGBuildCLI:
    run: RAGBuildRunConfig
    module: RAGConfigCLI


@dataclass
class RAGQueryCLI:
    run: RAGQueryRunConfig
    module: RAGConfigCLI


@dataclass
class AgentConfigCLI:
    # ----- agent config -----
    llm_name: str | None = None
    system_prompt: str | None = None


@dataclass
class AgentRunConfig:
    # ----- run config -----
    query: str
    config_name: str = "test"
    thread_id: str | None = None  # 多輪記憶 session 識別（相同 id 記得上下文）
    stream: bool = False  # True 時逐 token 串流顯示回答


@dataclass
class AgentCLI:
    run: AgentRunConfig
    module: AgentConfigCLI


if __name__ == "__main__":
    import tyro

    from app.workflow.workflow import (
        run_agent,
        run_rag_build,
        run_rag_query,
        run_webpage_image_summarizer,
        run_website_crawler,
    )
    from app.workflow.workflow_manager import RunManager
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
    )
    cli_arg = tyro.cli(cli_args_type)
    module_config_overrides = {}
    for key, value in vars(cli_arg.module).items():
        if value is not None:
            if key == "weights":
                module_config_overrides["hybrid_ranker_params"] = {"weights": value}
            else:
                module_config_overrides[key] = value

    if isinstance(cli_arg, WebsiteCrawlerCLI):
        run_manager.set_module_path("website_crawler")
        run_website_crawler(
            run_manager,
            **vars(cli_arg.run),
            **module_config_overrides,
        )
    elif isinstance(cli_arg, WebpageImageSummarizerCLI):
        run_manager.set_module_path("webpage_image_summarizer")
        run_webpage_image_summarizer(
            run_manager,
            **vars(cli_arg.run),
            **module_config_overrides,
        )
    elif isinstance(cli_arg, RAGBuildCLI):
        run_manager.set_module_path("rag_build")
        run_rag_build(
            run_manager,
            **vars(cli_arg.run),
            **module_config_overrides,
        )
    elif isinstance(cli_arg, RAGQueryCLI):
        run_manager.set_module_path("rag_query")
        run_rag_query(
            run_manager,
            **vars(cli_arg.run),
            **module_config_overrides,
        )
    elif isinstance(cli_arg, AgentCLI):
        # 聊天記錄與實驗分離：agent 使用獨立 RunManager（base_folder="chats"）
        agent_run_manager = RunManager("agent", base_folder="chats")
        run_agent(
            agent_run_manager=agent_run_manager,
            **vars(cli_arg.run),
            **module_config_overrides,
        )
        save_run_config_as_toml(cli_arg.run, agent_run_manager.run_config_toml_path)
        agent_run_manager.log_run_paths("complete")

    if not isinstance(cli_arg, AgentCLI):
        save_run_config_as_toml(cli_arg.run, run_manager.run_config_toml_path)
        run_manager.log_run_paths("complete")
