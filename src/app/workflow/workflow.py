import asyncio
import os
import time
import uuid
from contextlib import ExitStack

import uvicorn

from app.agent.agent import create_agent
from app.configs.agent_config import AgentConfig
from app.configs.rag_config import (
    RAGConfig,
)
from app.configs.webpage_image_summarizer_config import WebpageImageSummarizerConfig
from app.configs.website_crawler_config import WebsiteCrawlerConfig
from app.configs.workflow_config import (
    AgentRunConfig,
    RAGBuildRunConfig,
    RAGQueryRunConfig,
    ServerRunConfig,
    WebpageImageSummarizerRunConfig,
    WebsiteCrawlerRunConfig,
)
from app.engines.rag import RAG, RAGBuilder
from app.engines.webpage_image_summarizer import WebpageImageSummarizer
from app.engines.website_crawler import WebsiteCrawler
from app.server.app import create_app
from app.tools.tool import Tool
from app.workflow.data_manager import DataManager
from app.workflow.run_manager import RunManager
from app.workflow.run_persistence import (
    load_latest_results,
    save_query_results_as_md,
    save_results_as_md,
)
from utils.config_helper import (
    log_config,
    save_module_config_as_toml,
    save_run_config_as_toml,
)
from utils.log_helper import (
    log_run_time,
    log_session,
    print_log,
    save_logging_file,
)
from utils.rag_helper import response_to_dict


def _create_run_context(
    module: str,
    config_name: str,
    config,
    run_name_use_config_name: bool = False,
) -> tuple[RunManager, str]:
    """共用初始化：建立 RunManager 與 run_title。

    Returns:
        (RunManager, run_title)。
    """
    run_name = config.config_name if run_name_use_config_name else config.run_name
    run_manager = RunManager.for_run(
        module=module,
        site_id=config.site_id,
        run_name=run_name,
    )
    run_title = f"{module.replace('_', ' ').title()} ({config_name})"
    return run_manager, run_title


def _create_run_no_site_context(
    module: str,
    config_name: str,
    run_name: str | None = None,
    base_folder: str = "runs",
) -> tuple[RunManager, str]:
    """建立不需要 site_id 的 RunManager 與 run title。"""
    run_title = f"{module.replace('_', ' ').title()} ({config_name})"
    run_manager = RunManager.for_run_no_site(
        module=module,
        run_name=run_name or config_name,
        base_folder=base_folder,
    )
    return run_manager, run_title


def _run_workflow_context(
    run_title: str,
    config,
    log_path: str,
    run_time_title: str | None = None,
):
    """共用 logging preamble context manager。

    取代 run_* 函式中重複的 logging pattern：
    save_logging_file + log_run_time + log_session + log_config。
    """

    stack = ExitStack()
    stack.enter_context(save_logging_file(log_path))
    stack.enter_context(log_run_time(run_time_title or run_title))
    log_session(run_title, style="purple")
    log_config(f"{config.__class__.__name__} Loaded from toml", config)

    return stack


def create_rag(
    config_name: str = "default",
    force_rebuild: bool = False,
    webpages_data_use_latest_results: bool = False,
    save_vector_store_to_runs: bool = False,
    data_manager: DataManager | None = None,
    **config_overrides,
) -> RAG:
    """建立並建構 RAG 實例。僅執行建構流程，不包含 query 步驟。

    Args:
        config_name: RAGConfig 名稱（對應 configs/rag/{name}.toml）。
        force_rebuild: 是否強制重建向量庫。
        webpages_data_use_latest_results: 是否使用最新的 webpage 資料。
        save_vector_store_to_runs: 是否將向量庫儲存到 runs/ 目錄。
        data_manager: DataManager 實例（可選，用於解決 webpages 資料路徑）。
        **config_overrides: RAGConfig 覆寫值（含 site_id）。

    Returns:
        已建構的 RAG 實例（呼叫端負責 close）。
    """
    config = RAGConfig.from_toml(config_name, **config_overrides)

    # ----- 解決 webpages 資料路徑（如有需要可覆蓋 config 預設值）-----
    if webpages_data_use_latest_results:
        if data_manager is None:
            raise ValueError(
                "data_manager is required when webpages_data_use_latest_results=True"
            )
        log_session("Finding Latest Webpages Data", style="cyan")
        webpages_data_folder_path = data_manager.get_webpages_path(config.site_id)
        config.webpages_data_folder_path = webpages_data_folder_path

    # ----- 解決向量庫存放位置（預設位置 vs 本次 run 的 results/）-----
    if save_vector_store_to_runs:
        run_manager = RunManager.for_run(
            module="rag_build",
            site_id=config.site_id,
            run_name=config.config_name,
        )
        config.milvus_uri = os.path.join(run_manager.results_folder_path, "milvus.db")

    log_session("Building RAG", style="cyan")
    rag = RAG(webpages_data_folder_path=config.webpages_data_folder_path or "")
    builder = RAGBuilder(config)
    builder.build_reusable(rag, force_rebuild=force_rebuild)

    return rag


def run_website_crawler(
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    data_manager: DataManager | None = None,
    run_config: WebsiteCrawlerRunConfig | None = None,
    **config_overrides,
) -> dict[str, dict] | None:
    """執行網站爬蟲工作流程。

    Args:
        config_name: WebsiteCrawlerConfig 名稱（對應 configs/website_crawler/{name}.toml）。
        run_name_use_config_name: 是否使用 config_name 作為 run_name。
        data_manager: DataManager 實例（可選，用於發布結果到 data/）。
        run_config: RunConfig 實例（可選，用於落盤 run config toml）。
        **config_overrides: WebsiteCrawlerConfig 覆寫值（含 site_id）。

    Returns:
        爬取結果 dict | None。
    """
    # ----- 初始化設定和路徑 -----
    website_crawler = WebsiteCrawler()
    config = WebsiteCrawlerConfig.from_toml(config_name, **config_overrides)
    run_manager, run_title = _create_run_context(
        module="website_crawler",
        config_name=config_name,
        config=config,
        run_name_use_config_name=run_name_use_config_name,
    )

    crawl_results = None
    with _run_workflow_context(run_title, config, run_manager.log_path):
        log_session("Run Paths", style="cyan")
        run_manager.log_run_paths("init")

        # ----- 初始化物件 -----
        website_crawler.override_init_config(
            max_depth=config.max_depth,
            max_pages=config.max_pages,
            content_threshold=config.content_threshold,
            light_mode=config.light_mode,
            wait_for_images=config.wait_for_images,
        )

        # ---- 執行網站爬蟲 -----
        log_session("Website Crawling", style="cyan")
        crawl_results = website_crawler.crawl_website(
            url=config.url,
            url_patterns=config.url_patterns,
            allowed_domains=config.allowed_domains,
            exclude_words=config.exclude_words,
            path_prefix=config.path_prefix,
        )

        if crawl_results is None:
            log_session("Website Crawling Failed", style="red")
            return None

        # ---- 儲存結果 -----
        run_manager.save_results_as_json(crawl_results)
        save_results_as_md(
            crawl_results, run_manager.results_folder_path, "fit_markdown"
        )

        if data_manager is not None:
            data_manager.publish_crawl_results(
                site_id=config.site_id,
                results=crawl_results,
                results_json_path=run_manager.results_json_path,
                results_folder_path=run_manager.results_folder_path,
            )
            data_manager.publish_run_metadata(
                site_id=run_manager.site_id,
                category="webpages",
                module_config_path=run_manager.module_config_toml_path,
                run_config_path=run_manager.run_config_toml_path,
                log_path=run_manager.log_path,
            )

        # ----- 儲存設定 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)
        if run_config is not None:
            save_run_config_as_toml(run_config, run_manager.run_config_toml_path)

        # ----- 輸出完成訊息 -----
        log_session("Website Crawling Completed", style="cyan")
        run_manager.log_run_paths("complete")

    return crawl_results


def run_webpage_image_summarizer(
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    crawl_results: dict[str, dict] | None = None,
    data_manager: DataManager | None = None,
    run_config: WebpageImageSummarizerRunConfig | None = None,
    **config_overrides,
) -> dict[str, dict] | None:
    """執行網頁圖片摘要工作流程。

    Args:
        config_name: WebpageImageSummarizerConfig 名稱。
        run_name_use_config_name: 是否使用 config_name 作為 run_name。
        crawl_results: 爬取結果 dict（可選，None 時從最新結果載入）。
        data_manager: DataManager 實例（可選，用於發布結果到 data/）。
        run_config: RunConfig 實例（可選，用於落盤 run config toml）。
        **config_overrides: WebpageImageSummarizerConfig 覆寫值（含 site_id）。

    Returns:
        增強後的爬取結果 dict | None。
    """
    # ----- 初始化設定和路徑 -----
    webpage_image_summarizer = WebpageImageSummarizer()
    config = WebpageImageSummarizerConfig.from_toml(config_name, **config_overrides)
    run_manager, run_title = _create_run_context(
        module="webpage_image_summarizer",
        config_name=config_name,
        config=config,
        run_name_use_config_name=run_name_use_config_name,
    )

    with _run_workflow_context(run_title, config, run_manager.log_path):
        log_session("Run Paths", style="cyan")
        run_manager.log_run_paths("init")

        # ----- 初始化物件 -----
        webpage_image_summarizer.override_init_config(
            download_timeout=config.download_timeout,
            success_threshold=config.success_threshold,
            max_retries=config.max_retries,
            cache_download_images=config.cache_download_images,
            cache_image_captions=config.cache_image_captions,
        )

        # ----- 獲取最近一次結果 -----
        if crawl_results is None:
            log_session("Loading Latest Results", style="cyan")
            crawl_results = load_latest_results(
                run_manager.base_folder, "website_crawler"
            )

        # ---- 執行圖片摘要 -----
        log_session("Image Summarization", style="cyan")
        enhanced_results = webpage_image_summarizer.summarize_crawl_results_images(
            crawl_results,
            model=config.model,
            prompt=config.prompt,
            vlm_max_workers=config.vlm_max_workers,
            image_source=config.image_source,
            **config.litellm_kwargs,
        )

        if enhanced_results is None:
            log_session("Image Summarization Failed", style="red")
            return None

        # ---- 儲存結果 -----
        run_manager.save_results_as_json(enhanced_results)
        save_results_as_md(
            enhanced_results, run_manager.results_folder_path, "enhanced_markdown"
        )
        if data_manager is not None:
            data_manager.publish_markdown(
                site_id=config.site_id,
                enhanced_results=enhanced_results,
                results_folder_path=run_manager.results_folder_path,
            )
            data_manager.publish_run_metadata(
                site_id=run_manager.site_id,
                category="webpages",
                module_config_path=run_manager.module_config_toml_path,
                run_config_path=run_manager.run_config_toml_path,
                log_path=run_manager.log_path,
            )

        # ----- 儲存設定 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)
        if run_config is not None:
            save_run_config_as_toml(run_config, run_manager.run_config_toml_path)

        # ----- 輸出完成訊息 -----
        log_session("Image Summarization Completed", style="cyan")
        run_manager.log_run_paths("complete")

    return enhanced_results


def run_rag_build(
    config_name: str = "default",
    force_rebuild: bool = False,
    webpages_data_use_latest_results: bool = False,
    save_vector_store_to_runs: bool = False,
    run_name_use_config_name: bool = False,
    data_manager: DataManager | None = None,
    run_config: RAGBuildRunConfig | None = None,
    **config_overrides,
) -> None:
    """建構 RAG 並落盤結果。完整包含建立 rag 流程。"""
    config = RAGConfig.from_toml(config_name, **config_overrides)
    run_manager, run_title = _create_run_context(
        module="rag_build",
        config_name=config_name,
        config=config,
        run_name_use_config_name=run_name_use_config_name,
    )

    with _run_workflow_context(run_title, config, run_manager.log_path):
        log_session("Run Paths", style="cyan")
        run_manager.log_run_paths("init")

        rag = create_rag(
            config_name=config_name,
            force_rebuild=force_rebuild,
            webpages_data_use_latest_results=webpages_data_use_latest_results,
            save_vector_store_to_runs=save_vector_store_to_runs,
            data_manager=data_manager,
            **config_overrides,
        )

        # ---- 儲存設定 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)
        if run_config is not None:
            save_run_config_as_toml(run_config, run_manager.run_config_toml_path)

        # ----- 輸出完成訊息 -----
        log_session("RAG Build Completed", style="cyan")
        run_manager.log_run_paths("complete")

    rag.close()


def run_rag_query(
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    force_rebuild: bool = False,
    query_times: int = 1,
    run_config: RAGQueryRunConfig | None = None,
    **config_overrides,
) -> None:
    """執行 RAG 查詢工作流程。

    Args:
        config_name: RAGConfig 名稱（對應 configs/rag/{name}.toml）。
        run_name_use_config_name: 是否使用 config_name 作為 run_name。
        force_rebuild: 是否強制重建向量庫。
        query_times: 查詢次數。
        run_config: RunConfig 實例（可選，用於落盤 run config toml）。
        **config_overrides: RAGConfig 覆寫值（含 site_id）。
    """
    # ----- 初始化設定和路徑 -----
    config = RAGConfig.from_toml(config_name, **config_overrides)
    run_manager, run_title = _create_run_context(
        module="rag_query",
        config_name=config_name,
        config=config,
        run_name_use_config_name=run_name_use_config_name,
    )

    with _run_workflow_context(run_title, config, run_manager.log_path):
        log_session("Run Paths", style="cyan")
        run_manager.log_run_paths("init")

        # ----- 建立所有資源 -----
        log_session("Building All Resources", style="cyan")
        rag = create_rag(
            config_name=config_name,
            force_rebuild=force_rebuild,
            **config_overrides,
        )
        builder = RAGBuilder(config)
        builder.build_evaluators(rag)

        # ----- Query -----
        query_results: list[dict] = []
        faithfulness_pass = 0
        relevancy_pass = 0
        for i in range(query_times):
            # ----- 查詢與回應 -----
            log_session(f"Query & Response {i + 1}", style="cyan")
            response = rag.query(config.query, log_sources=True)

            # ----- 回應評估 -----
            # * 可改用 regas 或 deepeval 評估
            log_session("Evaluation", style="cyan")
            faithfulness_result, relevancy_result = rag.evaluate(
                query=config.query, response=response
            )
            if faithfulness_result.passing:
                faithfulness_pass += 1
            if relevancy_result.passing:
                relevancy_pass += 1

            query_results.append(
                response_to_dict(
                    query=config.query,
                    response=response,
                    faithfulness_result=faithfulness_result,
                    relevancy_result=relevancy_result,
                    index=i + 1,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                )
            )

        faithfulness_pass_rate = faithfulness_pass / query_times * 100
        relevancy_pass_rate = relevancy_pass / query_times * 100

        # ----- 輸出評估結果 -----
        log_session("Evaluation Summary", style="green")
        print(f"Query times: {query_times}")
        print(
            f"Faithfulness: {faithfulness_pass_rate:.2f}% ({faithfulness_pass}/{query_times})"
        )
        print(f"Relevancy: {relevancy_pass_rate:.2f}% ({relevancy_pass}/{query_times})")

        # ----- 儲存結果 -----
        query_results_dict = {
            "config": {
                "config_name": config.config_name,
                "run_name": run_manager.run_name,
                "query": config.query,
                "query_llm_name": config.query_llm_name,
                "evaluator_llm_name": config.evaluator_llm_name,
                "vector_store_type": config.vector_store_type,
                "collection_name": config.site_id,
                "query_mode": config.query_mode,
                "similarity_top_k": config.similarity_top_k,
                "hybrid_top_k": config.hybrid_top_k,
                "alpha": config.alpha,
                "cutoff": config.cutoff,
                "query_times": query_times,
            },
            "summary": {
                "query_times": query_times,
                "faithfulness_pass_count": faithfulness_pass,
                "faithfulness_pass_rate": faithfulness_pass_rate,
                "relevancy_pass_count": relevancy_pass,
                "relevancy_pass_rate": relevancy_pass_rate,
            },
            "results": query_results,
        }
        run_manager.save_results_as_json(query_results_dict)
        save_query_results_as_md(query_results_dict, run_manager.results_folder_path)

        # ---- 儲存設定 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)
        if run_config is not None:
            save_run_config_as_toml(run_config, run_manager.run_config_toml_path)

        # ----- 輸出完成訊息 -----
        log_session("RAG Query Completed", style="cyan")
        run_manager.log_run_paths("complete")

    rag.close()


def run_agent(
    query: str,
    config_name: str = "default",
    thread_id: str | None = None,
    stream: bool = False,
    data_manager: DataManager | None = None,
    run_config: AgentRunConfig | None = None,
    **config_overrides,
) -> None:
    """執行 Agent 問答（CLI 的 agent-cli 分支）。

    流程：建立 RunManager → 建立 Tool（內含 RAGRegistry）→ create_agent 建立 agent
    → 問答（stream 決定串流/非串流）→ 顯示回答與來源 → 落盤 runs/
    → 釋放 RAG 資源（Tool.__exit__ → RAGRegistry.close()）。

    Args:
        query: 使用者問題。
        config_name: AgentConfig 名稱（對應 configs/agent/{name}.toml）。
        thread_id: 多輪記憶 session 識別（None 時每次獨立）。
        stream: True 時逐 token 串流顯示回答。
        data_manager: DataManager 實例（可選，用於發布結果到 data/）。
        run_config: AgentRunConfig 實例（可選，用於落盤 run config toml）。
        **config_overrides: AgentConfig 覆寫值（llm_name / system_prompt）。
    """
    config = AgentConfig.from_toml(config_name, **config_overrides)
    run_manager, _ = _create_run_no_site_context(
        module="agent",
        config_name=config_name,
        base_folder="runs",
    )

    with (
        save_logging_file(run_manager.log_path),
    ):
        log_session("Run Paths", style="cyan")
        run_manager.log_run_paths("init")

        tool = Tool(config_name=config_name)
        agent = create_agent(
            config=config,
            tools=tool.tools,
            run_manager=run_manager,
        )

        if stream:
            result = asyncio.run(
                agent.astream_result(
                    query,
                    thread_id,
                    on_token=lambda token: print(token, end="", flush=True),
                )
            )
            print()  # 串流 token 結束後換行
        else:
            result = agent.ask(query, thread_id)

        log_session("Agent Response", style="green")
        print_log(result["response"])
        log_session("Sources", style="cyan")
        for i, url in enumerate(result["sources"], 1):
            print(f"{i}. {url}")

        # 無 thread_id 時自動產生（確保每次執行都有結果檔）
        if thread_id is None:
            thread_id = f"auto-{uuid.uuid4().hex[:8]}"
        agent.save_results([result], thread_id=thread_id)
        log_session("Conversation Saved", style="green")
        print(f"Results json: {run_manager.results_json_path}")

        if run_config is not None:
            save_run_config_as_toml(run_config, run_manager.run_config_toml_path)
        run_manager.log_run_paths("complete")

    tool.close()


def run_app(
    config_name: str = "default",
    run_config: ServerRunConfig | None = None,
    allowed_origins: list[str] | None = None,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    """建立並啟動 Server 模式的 FastAPI app。

    流程：Tool → RunManager(base_folder="chats")
    → create_agent → create_app(agent) → uvicorn.run()

    Args:
        config_name: config 名稱（共用，分別從 configs/rag/ 和 configs/agent/ 載入）。
        run_config: ServerRunConfig 實例（可選，用於落盤 run config toml）。
        allowed_origins: CORS 允許來源（None 時全開放）。
        host: 監聽位址，預設 "127.0.0.1"。
        port: 監聽連接埠，預設 8000。

    Returns:
        None。此函式會阻塞直到伺服器停止。
    """
    run_manager, _ = _create_run_no_site_context(
        module="app",
        config_name=config_name,
        base_folder="chats",
    )

    tool = Tool(config_name=config_name)
    agent = create_agent(
        config=AgentConfig.from_toml(config_name),
        tools=tool.tools,
        run_manager=run_manager,
    )

    app = create_app(agent=agent, allowed_origins=allowed_origins)
    uvicorn.run(app, host=host, port=port)

    if run_config is not None:
        save_run_config_as_toml(run_config, run_manager.run_config_toml_path)

    tool.close()
