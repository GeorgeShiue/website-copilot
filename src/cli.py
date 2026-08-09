import time
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
    import asyncio

    import tyro

    from app.agent.agent import (
        ask_agent,
        astream_agent,
        create_rag_agent,
        save_conversation_results,
    )
    from app.configs.agent_config import AgentConfig
    from app.workflow.workflow import (
        run_rag_build,
        run_rag_query,
        run_webpage_image_summarizer,
        run_website_crawler,
    )
    from app.workflow.workflow_manager import RunManager
    from utils.config_helper import save_run_config_as_toml
    from utils.log_helper import (
        log_session,
        print_log,
        save_logging_file,
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

    def stream_agent(agent, run_config) -> dict:
        """以 astream 逐 token 串流回答（sources 於 M2 暫不擷取，M3 前端處理）。"""

        async def _astream() -> dict:
            chunks: list[str] = []
            async for token in astream_agent(
                agent, run_config.query, run_config.thread_id
            ):
                chunks.append(token)
                print(token, end="", flush=True)
            print()
            return {
                "query": run_config.query,
                "response": "".join(chunks),
                "sources": [],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

        return asyncio.run(_astream())

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
        agent = create_rag_agent(
            config=AgentConfig(
                config_name=cli_arg.run.config_name,
                **module_config_overrides,
            ),
            run_manager=agent_run_manager,
        )
        try:
            # 問答過程也寫入 log 檔（append 至 agent 建立時開啟的同一個 terminal.log）
            with save_logging_file(agent.run_manager.log_path):
                if cli_arg.run.stream:
                    result = stream_agent(agent, cli_arg.run)
                else:
                    result = ask_agent(agent, cli_arg.run.query, cli_arg.run.thread_id)
                log_session("Agent Response", style="green")
                print_log(result["response"])
                log_session("Sources", style="cyan")
                for i, url in enumerate(result["sources"], 1):
                    print(f"{i}. {url}")
                save_conversation_results(agent, [result])
                save_run_config_as_toml(
                    cli_arg.run, agent_run_manager.run_config_toml_path
                )
                log_session("Conversation Saved", style="green")
                print(f"Results json: {agent.run_manager.results_json_path}")
                agent_run_manager.log_run_paths("complete")
        finally:
            agent.close()

    if not isinstance(cli_arg, AgentCLI):
        save_run_config_as_toml(cli_arg.run, run_manager.run_config_toml_path)
        run_manager.log_run_paths("complete")
