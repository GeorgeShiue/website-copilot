import asyncio
import os
import time
from pathlib import Path
from typing import Literal

from app.agent.agent import (
    ask_agent,
    astream_agent_result,
    create_rag_agent,
    save_conversation_results,
)
from app.configs.agent_config import AgentConfig
from app.configs.rag_config import (
    RAGConfig,
)
from app.configs.webpage_image_summarizer_config import WebpageImageSummarizerConfig
from app.configs.website_crawler_config import WebsiteCrawlerConfig
from app.engines.rag import RAG, RAGBuilder
from app.engines.webpage_image_summarizer import WebpageImageSummarizer
from app.engines.website_crawler import WebsiteCrawler
from app.workflow.data_manager import DataManager
from app.workflow.run_manager import RunManager
from app.workflow.run_persistence import (
    load_latest_results,
    save_query_results_as_md,
    save_results_as_md,
)
from utils.config_helper import log_config, save_module_config_as_toml
from utils.log_helper import (
    log_run_time,
    log_session,
    print_log,
    save_logging_file,
)
from utils.rag_helper import response_to_dict
from utils.server_helper import (
    DEFAULT_FOLLOW_UP,
    DEFAULT_QUERY,
    shutdown_server,
    spawn_server,
    validate_server,
    wait_ready,
)


def run_website_crawler(
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    data_manager: DataManager | None = None,
    **config_overrides,
) -> tuple[dict[str, dict] | None, RunManager]:
    """執行網站爬蟲工作流程。

    Args:
        config_name: WebsiteCrawlerConfig 名稱（對應 configs/website_crawler/{name}.toml）。
        run_name_use_config_name: 是否使用 config_name 作為 run_name。
        data_manager: DataManager 實例（可選，用於發布結果到 data/）。
        **config_overrides: WebsiteCrawlerConfig 覆寫值（含 site_id）。

    Returns:
        (爬取結果 dict | None, RunManager)。
    """
    # ----- 初始化設定和路徑 -----
    website_crawler = WebsiteCrawler()
    config = WebsiteCrawlerConfig.from_toml(config_name, **config_overrides)
    run_name = config.config_name if run_name_use_config_name else config.run_name
    run_manager = RunManager.for_run(
        module="website_crawler",
        site_id=config.site_id,
        run_name=run_name,
    )

    crawl_results = None
    with (
        save_logging_file(run_manager.log_path),
        log_run_time("Website Crawling"),
    ):
        # ----- 輸出開始訊息 -----
        log_session(f"Website Crawler ({config_name})", style="purple")
        log_config("WebsiteCrawler Config Loaded from toml", config)
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
            return None, run_manager

        # ----- 儲存設定和結果 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)
        run_manager.save_results_as_json(crawl_results)
        save_results_as_md(
            crawl_results, run_manager.results_folder_path, "fit_markdown"
        )

        if data_manager:
            data_manager.publish_crawl_results(
                site_id=config.site_id,
                results=crawl_results,
                results_json_path=run_manager.results_json_path,
                results_folder_path=run_manager.results_folder_path,
            )

        # ----- 輸出完成訊息 -----
        log_session("Website Crawling Completed", style="cyan")

    return crawl_results, run_manager


def run_webpage_image_summarizer(
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    crawl_results: dict[str, dict] | None = None,
    data_manager: DataManager | None = None,
    **config_overrides,
) -> tuple[dict[str, dict] | None, RunManager]:
    """執行網頁圖片摘要工作流程。

    Args:
        config_name: WebpageImageSummarizerConfig 名稱。
        run_name_use_config_name: 是否使用 config_name 作為 run_name。
        crawl_results: 爬取結果 dict（可選，None 時從最新結果載入）。
        data_manager: DataManager 實例（可選，用於發布結果到 data/）。
        **config_overrides: WebpageImageSummarizerConfig 覆寫值（含 site_id）。

    Returns:
        (增強後的爬取結果 dict | None, RunManager)。
    """
    # ----- 初始化設定和路徑 -----
    webpage_image_summarizer = WebpageImageSummarizer()
    config = WebpageImageSummarizerConfig.from_toml(config_name, **config_overrides)
    run_name = config.config_name if run_name_use_config_name else config.run_name
    run_manager = RunManager.for_run(
        module="webpage_image_summarizer",
        site_id=config.site_id,
        run_name=run_name,
    )

    with (
        save_logging_file(run_manager.log_path),
        log_run_time("Image Summarization"),
    ):
        # ----- 輸出開始訊息 -----
        log_session(f"Webpage Image Summarizer ({config_name})", style="purple")
        log_config("WebpageImageSummarizer Config Loaded from toml", config)
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
            return None, run_manager

        # ----- 儲存設定和結果 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)
        run_manager.save_results_as_json(enhanced_results)
        save_results_as_md(
            enhanced_results, run_manager.results_folder_path, "enhanced_markdown"
        )

        if data_manager:
            data_manager.publish_markdown(
                site_id=config.site_id,
                enhanced_results=enhanced_results,
                results_folder_path=run_manager.results_folder_path,
            )

        # ----- 輸出完成訊息 -----
        log_session("Image Summarization Completed", style="cyan")

    return enhanced_results, run_manager


def run_rag_build(
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    webpages_data_use_latest_results: bool = False,
    save_vector_store_to_runs: bool = False,
    data_manager: DataManager | None = None,
    **config_overrides,
) -> RunManager:
    """執行 RAG 建構工作流程。

    Args:
        config_name: RAGConfig 名稱（對應 configs/rag/{name}.toml）。
        run_name_use_config_name: 是否使用 config_name 作為 run_name。
        webpages_data_use_latest_results: 是否使用最新的 webpage 資料。
        save_vector_store_to_runs: 是否將向量庫儲存到 runs/ 目錄。
        data_manager: DataManager 實例（可選，用於發布結果到 data/）。
        **config_overrides: RAGConfig 覆寫值（含 site_id）。

    Returns:
        RunManager。
    """
    # ----- 初始化設定和路徑 -----
    config = RAGConfig.from_toml(config_name, **config_overrides)
    run_name = config.config_name if run_name_use_config_name else config.run_name
    run_manager = RunManager.for_run(
        module="rag_build",
        site_id=config.site_id,
        run_name=run_name,
    )
    run_title = f"RAG Build ({config_name})"

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
        log_session("Saving Vector Store to Run Results", style="cyan")
        vector_store_folder = os.path.join(
            run_manager.results_folder_path, "vector_store"
        )
        config.milvus_uri = os.path.join(vector_store_folder, "milvus.db")

    rag = RAG(webpages_data_folder_path=config.webpages_data_folder_path or "")

    with (
        rag,
        save_logging_file(run_manager.log_path),
        log_run_time(run_title),
    ):
        # ----- 輸出開始訊息 -----
        log_session(run_title, style="purple")
        log_config("RAG Config Loaded from toml", config)

        # ----- 建立 RAG -----
        log_session("Building RAG", style="cyan")
        builder = RAGBuilder(config)
        builder.build(rag)

        # ----- Query & Response -----
        log_session("Query & Response", style="cyan")
        rag.query(config.query, log_sources=True)

        # ----- 儲存設定和結果 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)

        if data_manager:
            if config.milvus_uri and os.path.exists(config.milvus_uri):
                data_manager.publish_vector_store(
                    site_id=config.site_id,
                    source_path=config.milvus_uri,
                )

        # ----- 輸出完成訊息 -----
        log_session("RAG Build Completed", style="cyan")

    return run_manager


def run_rag_query(
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    force_rebuild: bool = False,
    query_times: int = 1,
    **config_overrides,
) -> RunManager:
    """執行 RAG 查詢工作流程。

    Args:
        config_name: RAGConfig 名稱（對應 configs/rag/{name}.toml）。
        run_name_use_config_name: 是否使用 config_name 作為 run_name。
        force_rebuild: 是否強制重建向量庫。
        query_times: 查詢次數。
        **config_overrides: RAGConfig 覆寫值（含 site_id）。

    Returns:
        RunManager。
    """
    # ----- 初始化設定和路徑 -----
    config = RAGConfig.from_toml(config_name, **config_overrides)
    run_name = config.config_name if run_name_use_config_name else config.run_name
    run_manager = RunManager.for_run(
        module="rag_query",
        site_id=config.site_id,
        run_name=run_name,
    )
    run_title = f"RAG Query ({config_name})"

    rag = RAG(webpages_data_folder_path=config.webpages_data_folder_path or "")

    with (
        rag,
        save_logging_file(run_manager.log_path),
        log_run_time(run_title),
    ):
        # ----- 輸出開始訊息 -----
        log_session(run_title, style="purple")
        log_config("RAG Config Loaded from toml", config)

        # ----- 建立所有資源 -----
        log_session("Building All Resources", style="cyan")
        builder = RAGBuilder(config)
        builder.build_reusable(rag, force_rebuild=force_rebuild)
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

        # ----- 儲存設定和結果 -----
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

        save_module_config_as_toml(config, run_manager.module_config_toml_path)

        # ----- 輸出完成訊息 -----
        log_session("RAG Query Completed", style="cyan")

    return run_manager


def run_agent(
    query: str,
    config_name: str = "default",
    thread_id: str | None = None,
    stream: bool = False,
    agent_run_manager: RunManager | None = None,
    **config_overrides,
) -> RunManager:
    """執行 Agent 問答（CLI 的 agent-cli 分支，亦可被 server 重用）。

    流程：create_rag_agent 建立 agent → 問答（stream 決定串流/非串流）
    → 顯示回答與來源 → 落盤 chats/ → 釋放 RAG 資源（agent.close()）。

    Args:
        query: 使用者問題。
        config_name: AgentConfig 名稱（對應 configs/agent/{name}.toml）。
        thread_id: 多輪記憶 session 識別（None 時每次獨立）。
        stream: True 時逐 token 串流顯示回答。
        **config_overrides: AgentConfig 覆寫值（llm_name / system_prompt）。
        agent_run_manager: 聊天專用 RunManager（base_folder="chats"，None 時自動建立）。
    """
    agent_config = AgentConfig.from_toml(config_name, **config_overrides)

    agent = create_rag_agent(
        config=agent_config,
        run_manager=agent_run_manager,
    )
    try:
        # 問答過程也寫入 log 檔（append 至 agent 建立時開啟的同一個 terminal.log）
        with save_logging_file(agent.run_manager.log_path):
            if stream:
                result = asyncio.run(
                    astream_agent_result(
                        agent,
                        query,
                        thread_id,
                        on_token=lambda token: print(token, end="", flush=True),
                    )
                )
                print()  # 串流 token 結束後換行
            else:
                result = ask_agent(agent, query, thread_id)
            log_session("Agent Response", style="green")
            print_log(result["response"])
            log_session("Sources", style="cyan")
            for i, url in enumerate(result["sources"], 1):
                print(f"{i}. {url}")
            save_conversation_results(agent, [result])
            log_session("Conversation Saved", style="green")
            print(f"Results json: {agent.run_manager.results_json_path}")
    finally:
        agent.close()

    return agent.run_manager


def run_server(
    host: str = "127.0.0.1",
    port: int = 8001,
    config_name: str = "default",
    mode: Literal["validate", "block"] = "validate",
    *,
    output: Literal["inherit", "devnull"] | Path = "devnull",
    allowed_origins: list[str] | None = None,
    startup_timeout: int = 600,
    query: str = DEFAULT_QUERY,
    follow_up: str = DEFAULT_FOLLOW_UP,
) -> None:
    """Server 生命週期統一入口。

    mode="validate" → 啟動 → health check → SSE 驗證 → 落盤 → 關閉
    mode="block"    → 啟動 → health check → 等待 Ctrl+C → 關閉

    Args:
        host: server 監聽位址。
        port: server 監聽 port。
        config_name: AgentConfig 名稱（對應 configs/agent/{name}.toml）。
        mode: "validate"（測試）或 "block"（互動/正式）。
        output: subprocess stdout/stderr 去向。
        allowed_origins: CORS 允許來源。
        startup_timeout: 等待 server 就緒的最長秒數。
        query: validate 模式單輪測試問題。
        follow_up: validate 模式多輪測試問題。
    """
    base_url = f"http://{host}:{port}"

    # allowed_origins: subprocess calls app.run_server() without this param;
    # it defaults to ["*"] (full CORS). Override via app-level config if needed.
    log_session(f"Starting Server ({mode})", style="purple")
    proc = spawn_server(
        host,
        port,
        config_name,
        output=output,
    )
    try:
        wait_ready(base_url, timeout=startup_timeout)
        if mode == "validate":
            validate_server(base_url, query, follow_up)
        else:  # block
            log_session("Server Ready", style="green")
            print_log(f"Server ready at {base_url} , use Ctrl+C to stop.")
            proc.wait()

    except TimeoutError as exc:
        print_log(f"[bold red]FAIL: {exc}[/bold red]")
        raise
    except KeyboardInterrupt:
        log_session("Server Shutting Down", style="yellow")
        print_log("收到終止訊號，關閉 server...")
    finally:
        shutdown_server(proc)
        log_session("Server Stopped", style="red")
