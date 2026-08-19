import asyncio
import os
import time

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
from app.workflow.workflow_manager import RunManager
from utils.config_helper import log_config, save_module_config_as_toml
from utils.log_helper import (
    log_run_time,
    log_session,
    print_log,
    save_logging_file,
)
from utils.rag_helper import response_to_dict


def run_website_crawler(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    **config_overrides,
) -> dict[str, dict] | None:
    # ----- 初始化設定和路徑 -----
    website_crawler = WebsiteCrawler()
    config = WebsiteCrawlerConfig.from_toml(config_name, **config_overrides)
    if run_manager is None:
        run_manager = RunManager("website_crawler")
    if run_name_use_config_name:
        run_manager.set_run_path(config_name)
    else:
        run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()

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
            return None

        # ----- 儲存設定和結果 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)
        run_manager.save_results_as_json(crawl_results)
        run_manager.save_results_as_md(crawl_results, "fit_markdown")

        # ----- 輸出完成訊息 -----
        log_session("Website Crawling Completed", style="cyan")

    return crawl_results


def run_webpage_image_summarizer(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    crawl_results: dict[str, dict] | None = None,
    **config_overrides,
) -> dict[str, dict] | None:
    # ----- 初始化設定和路徑 -----
    webpage_image_summarizer = WebpageImageSummarizer()
    config = WebpageImageSummarizerConfig.from_toml(config_name, **config_overrides)
    if run_manager is None:
        run_manager = RunManager("webpage_image_summarizer")
    if run_name_use_config_name:
        run_manager.set_run_path(config_name)
    else:
        run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()

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
            crawl_results = run_manager.load_latest_results_from_json()

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

        # ----- 儲存設定和結果 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)
        run_manager.save_results_as_json(enhanced_results)
        run_manager.save_results_as_md(enhanced_results, "enhanced_markdown")

        # ----- 輸出完成訊息 -----
        log_session("Image Summarization Completed", style="cyan")

    return enhanced_results


def run_rag_build(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    webpages_data_use_latest_results: bool = False,
    save_vector_store_to_runs: bool = False,
    **config_overrides,
) -> None:
    # ----- 初始化設定和路徑 -----
    config = RAGConfig.from_toml(config_name, **config_overrides)
    if run_manager is None:
        run_manager = RunManager("rag_build")
    if run_name_use_config_name:
        run_manager.set_run_path(config_name)
    else:
        run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()
    run_title = f"RAG Build ({config_name})"

    # ----- 解決 webpages 資料路徑（如有需要可覆蓋 config 預設值）-----
    if webpages_data_use_latest_results:
        log_session("Finding Latest Webpages Data", style="cyan")
        webpages_data_folder_path = run_manager.load_latest_summarizer_run_path()
        config.webpages_data_folder_path = webpages_data_folder_path

    # ----- 解決向量庫存放位置（預設位置 vs 本次 run 的 results/）-----
    if save_vector_store_to_runs:
        log_session("Saving Vector Store to Run Results", style="cyan")
        vector_store_folder = os.path.join(
            run_manager.results_folder_path, "vector_store"
        )
        if config.vector_store_type == "qdrant":
            config.qdrant_db_folder_path = os.path.join(
                vector_store_folder, "qdrant_db"
            )
        elif config.vector_store_type == "milvus":
            config.milvus_uri = os.path.join(vector_store_folder, "milvus.db")
        else:
            raise ValueError(
                f"Unsupported vector_store_type: {config.vector_store_type}"
            )

    # ----- 使用 RAGBuilder 一鍵建構 -----
    rag = RAGBuilder(config).build()

    with (
        rag,
        save_logging_file(run_manager.log_path),
        log_run_time(run_title),
    ):
        # ----- 輸出開始訊息 -----
        log_session(run_title, style="purple")
        log_config("RAG Config Loaded from toml", config)

        # ----- Query & Response -----
        log_session("Query & Response", style="cyan")
        rag.query(config.query, log_sources=True)

        # ----- 儲存設定和結果 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)


def run_rag_query(
    run_manager: RunManager | None = None,
    config_name: str = "default",
    run_name_use_config_name: bool = False,
    force_rebuild: bool = False,
    query_times: int = 1,
    **config_overrides,
) -> None:
    # ----- 初始化設定和路徑 -----
    config = RAGConfig.from_toml(config_name, **config_overrides)
    if run_manager is None:
        run_manager = RunManager("rag_query")
    if run_name_use_config_name:
        run_manager.set_run_path(config_name)
    else:
        run_manager.set_run_path(config.run_name)
    run_manager.init_module_run_paths()
    run_title = f"RAG Query ({config_name})"

    rag = RAG(webpages_data_folder_path=config.webpages_data_folder_path)
    builder = RAGBuilder(config)

    with (
        rag,
        save_logging_file(run_manager.log_path),
        log_run_time(run_title),
    ):
        # ----- 建立所有資源 -----
        log_session("Building All Resources", style="cyan")
        rebuild = builder.build_reusable(rag, force_rebuild=force_rebuild)
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

        # ----- 儲存 query 結果 -----
        log_session("Saving Query Results", style="cyan")
        query_results_dict = {
            "config": {
                "config_name": config.config_name,
                "run_name": run_manager.run_name,
                "query": config.query,
                "query_llm_name": config.query_llm_name,
                "evaluator_llm_name": config.evaluator_llm_name,
                "vector_store_type": config.vector_store_type,
                "collection_name": config.collection_name,
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
        run_manager.save_query_results_as_md(query_results_dict)

        # ----- 儲存設定和結果 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)

        if rebuild:
            module_config_folder_path = (
                config.qdrant_db_folder_path
                if config.vector_store_type == "qdrant"
                else config.milvus_uri
            )
            save_module_config_as_toml(
                config,
                os.path.join(module_config_folder_path, "module_config.toml"),
            )

        # ----- 輸出完成訊息 -----


def run_agent(
    query: str,
    config_name: str = "default",
    thread_id: str | None = None,
    stream: bool = False,
    agent_run_manager: RunManager | None = None,
    **config_overrides,
) -> None:
    """執行 Agent 問答（CLI 的 agent-cli 分支，亦可被 server 重用）。

    流程：create_rag_agent 建立 agent → 問答（stream 決定串流/非串流）
    → 顯示回答與來源 → 落盤 chats/ → 釋放 RAG 資源（agent.close()）。

    Args:
        query: 使用者問題。
        config_name: AgentConfig 名稱（對應 configs/agent/{name}.toml）。
        thread_id: 多輪記憶 session 識別（None 時每次獨立）。
        stream: True 時逐 token 串流顯示回答。
        **config_overrides: AgentConfig 覆寫值（如 llm_name / system_prompt）。
        agent_run_manager: 聊天專用 RunManager（base_folder="chats"，None 時自動建立）。
    """
    if agent_run_manager is None:
        # 聊天記錄與實驗分離：預設落盤至 chats/
        agent_run_manager = RunManager("agent", base_folder="chats")

    agent = create_rag_agent(
        config=AgentConfig.from_toml(config_name, **config_overrides),
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
