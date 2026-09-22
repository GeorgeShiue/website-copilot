import asyncio
import os
import time
import uuid

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
from app.engines.rag import RAGBuilder
from app.engines.rag.rag_factory import create_rag
from app.engines.webpage_image_summarizer import WebpageImageSummarizer
from app.engines.webpage_markdown_cleaner import WebpageMarkdownCleaner
from app.engines.website_crawler import WebsiteCrawler
from app.server.app import ChatApp
from app.server.server import ChatServer
from app.workflow.data_manager import DataManager
from app.workflow.run_persistence import (
    load_latest_results,
    save_generated_exclude_words,
    save_query_results_as_md,
    save_results_as_md,
)
from app.workflow.workflow_helper import (
    create_run_context,
    create_run_no_site_context,
    run_workflow_context,
)
from utils.config_helper import (
    log_config,
    save_module_config_as_toml,
    save_run_config_as_toml,
)
from utils.log_helper import (
    log_session,
    print_log,
)
from utils.rag_helper import response_to_dict


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
    config = WebsiteCrawlerConfig.from_toml(config_name, **config_overrides)
    run_manager, run_title = create_run_context(
        module="website_crawler",
        config_name=config_name,
        config=config,
        run_name_use_config_name=run_name_use_config_name,
    )

    crawl_results = None
    with run_workflow_context(run_title, run_manager=run_manager):
        # ----- 初始化物件 -----
        log_config(f"{config.__class__.__name__} Loaded from toml", config)
        website_crawler = WebsiteCrawler(
            max_depth=config.max_depth,
            max_pages=config.max_pages,
            content_threshold=config.content_threshold,
            light_mode=config.light_mode,
            wait_for_images=config.wait_for_images,
            cleaner=WebpageMarkdownCleaner(
                model=config.llm_model,
                sample_ratio=config.sample_ratio,
                repeat=config.repeat,
                max_prompt_tokens=config.max_prompt_tokens,
                seed=config.seed,
            ),
        )

        # ---- 執行網站爬蟲 -----
        log_session("Website Crawling", style="cyan")
        crawl_results = website_crawler.crawl_website(
            url=config.url,
            url_patterns=config.url_patterns,
            allowed_domains=config.allowed_domains,
            path_prefix=config.path_prefix,
        )

        if website_crawler.generation_result is not None:
            save_generated_exclude_words(
                website_crawler.generation_result,
                website_crawler.raw_pages,
                run_manager.run_path,
            )

        # ----- 輸出完成訊息 -----
        if crawl_results is None:
            log_session("Website Crawling Failed", style="red")
            return None
        log_session("Website Crawling Completed", style="cyan")

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
    config = WebpageImageSummarizerConfig.from_toml(config_name, **config_overrides)
    run_manager, run_title = create_run_context(
        module="webpage_image_summarizer",
        config_name=config_name,
        config=config,
        run_name_use_config_name=run_name_use_config_name,
    )

    with run_workflow_context(run_title, run_manager=run_manager):
        # ----- 初始化物件 -----
        log_config(f"{config.__class__.__name__} Loaded from toml", config)
        webpage_image_summarizer = WebpageImageSummarizer(
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

        # ----- 輸出完成訊息 -----
        if enhanced_results is None:
            log_session("Image Summarization Failed", style="red")
            return None
        log_session("Image Summarization Completed", style="cyan")

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
    run_manager, run_title = create_run_context(
        module="rag_build",
        config_name=config_name,
        config=config,
        run_name_use_config_name=run_name_use_config_name,
    )

    with run_workflow_context(run_title, run_manager=run_manager):
        # ---- 建置 RAG -----
        log_config(f"{config.__class__.__name__} Loaded from toml", config)
        rag = create_rag(
            config_name=config_name,
            force_rebuild=force_rebuild,
            webpages_data_use_latest_results=webpages_data_use_latest_results,
            save_vector_store_to_runs=save_vector_store_to_runs,
            data_manager=data_manager,
            **config_overrides,
        )
        rag.close()

        # ----- 輸出完成訊息 -----
        log_session("RAG Build Completed", style="cyan")

        # ---- 儲存設定 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)
        if run_config is not None:
            save_run_config_as_toml(run_config, run_manager.run_config_toml_path)

        # ---- 儲存結果 -----
        if data_manager is not None:
            if rag.milvus_uri and os.path.exists(rag.milvus_uri):
                data_manager.publish_vector_store(
                    site_id=config.site_id,
                    source_path=rag.milvus_uri,
                )
            data_manager.publish_run_metadata(
                site_id=config.site_id,
                category="rag",
                module_config_path=run_manager.module_config_toml_path,
                run_config_path=run_manager.run_config_toml_path,
                log_path=run_manager.log_path,
            )


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
    run_manager, run_title = create_run_context(
        module="rag_query",
        config_name=config_name,
        config=config,
        run_name_use_config_name=run_name_use_config_name,
    )

    with run_workflow_context(run_title, run_manager=run_manager):
        # ----- 初始化 RAG 和 評估器 -----
        log_session("Building RAG and Evaluators", style="cyan")
        log_config(f"{config.__class__.__name__} Loaded from toml", config)
        rag = create_rag(
            config_name=config_name,
            force_rebuild=force_rebuild,
            **config_overrides,
        )

        try:
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

            # ----- 輸出完成訊息 -----
            log_session("RAG Query Completed", style="cyan")

            # ----- 輸出評估結果 -----
            log_session("Evaluation Summary", style="green")
            print(f"Query times: {query_times}")
            faithfulness_pass_rate = faithfulness_pass / query_times * 100
            print(
                f"Faithfulness: {faithfulness_pass_rate:.2f}% ({faithfulness_pass}/{query_times})"
            )
            relevancy_pass_rate = relevancy_pass / query_times * 100
            print(
                f"Relevancy: {relevancy_pass_rate:.2f}% ({relevancy_pass}/{query_times})"
            )

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
            save_query_results_as_md(
                query_results_dict, run_manager.results_folder_path
            )

            # ---- 儲存設定 -----
            save_module_config_as_toml(config, run_manager.module_config_toml_path)
            if run_config is not None:
                save_run_config_as_toml(run_config, run_manager.run_config_toml_path)
        except Exception as e:
            log_session("RAG Query Failed", style="red")
            print_log(f"Error: {e}")
            rag.close()
            raise
        finally:
            rag.close()


def run_agent_build(
    config_name: str = "default",
    run_config: AgentRunConfig | None = None,
    **config_overrides,
) -> None:
    """建構 Agent 並落盤結果。完整包含建立 agent 流程。"""
    config = AgentConfig.from_toml(config_name, **config_overrides)
    run_manager, run_title = create_run_no_site_context(
        module="agent_build",
        config_name=config_name,
    )

    with run_workflow_context(run_title, run_manager=run_manager):
        # ---- 初始化 Agent -----
        log_config(f"{config.__class__.__name__} Loaded from toml", config)
        agent = create_agent(config_name, **config_overrides)

        # ----- 輸出完成訊息 -----
        log_session("Agent Build Completed", style="cyan")

        # ---- 儲存設定 -----
        save_module_config_as_toml(config, run_manager.module_config_toml_path)
        if run_config is not None:
            save_run_config_as_toml(run_config, run_manager.run_config_toml_path)

    agent.close()


def run_agent_query(
    query: str,
    config_name: str = "default",
    thread_id: str | None = None,
    stream: bool = False,
    run_config: AgentRunConfig | None = None,
    **config_overrides,
) -> None:
    """執行 Agent 問答工作流程（建立 run context → 建構 agent → 問答 → 落盤 → 關閉）。

    流程：問答 → 顯示回答與來源 → 落盤 runs/ → 寫 run_config.toml → 關閉 agent。
    agent 的建立與 Tool 生命週期皆在本函式內完成（呼叫端不需持有 agent）。

    Args:
        config_name: AgentConfig 名稱（對應 configs/agent/{name}.toml）。
        query: 使用者問題。
        thread_id: session 識別；None 時自動產生 auto-{uuid}。
        stream: 是否逐 token 串流輸出。
        run_config: RunConfig 實例（可選，用於落盤 run config toml）。
        **config_overrides: AgentConfig 覆寫值（llm_name / system_prompt）。
    """

    run_manager, run_title = create_run_no_site_context(
        module="agent",
        config_name=config_name,
        base_folder="runs",
    )

    with run_workflow_context(run_title, run_manager=run_manager):
        # ---- 初始化 Agent -----
        config = AgentConfig.from_toml(config_name, **config_overrides)
        log_config(f"{config.__class__.__name__} Loaded from toml", config)
        agent = create_agent(config_name, **config_overrides)

        try:
            # ---- Agent 問答 -----
            log_session("Agent Query and Response", style="cyan")
            print_log(f"Query: {query}")
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
            print_log(f"Response: {result['response']}")

            log_session("Sources", style="cyan")
            for i, url in enumerate(result["sources"], 1):
                print_log(f"{i}. {url}")

            # ---- 輸出完成訊息 -----
            log_session("Agent Query Completed", style="cyan")

            # ---- 儲存設定 -----
            save_module_config_as_toml(config, run_manager.module_config_toml_path)
            if run_config is not None:
                save_run_config_as_toml(run_config, run_manager.run_config_toml_path)

            # ---- 儲存結果 -----
            if thread_id is None:
                thread_id = f"auto-{uuid.uuid4().hex[:8]}"
            run_manager.save_agent_results_as_json(
                thread_id=thread_id,
                results=[result],
                agent_config=agent.config,
            )
        except Exception as e:
            log_session("Agent Query Failed", style="red")
            print_log(f"Error: {e}")
            agent.close()
            raise
        finally:
            agent.close()


def run_app(
    config_name: str = "default",
    run_config: ServerRunConfig | None = None,
    allowed_origins: list[str] | None = None,
    host: str = "127.0.0.1",
    port: int = 8000,
    **config_overrides,
) -> tuple[uvicorn.Server, ChatApp]:
    """建立 Agent 與 ChatApp（FastAPI app）並回傳 server handle（非阻塞）。

    呼叫端可透過 server.run() 阻塞，或以 asyncio 啟動後透過 server.should_exit=True 關閉。
    agent 資源生命週期由 ChatApp 承接：呼叫端持有回傳的 chat_app 並呼叫 chat_app.close()。

    Args:
        config_name: AgentConfig 名稱（對應 configs/agent/{name}.toml）。
        run_config: ServerRunConfig 實例（可選，用於落盤 run config toml）。
        allowed_origins: CORS 允許來源（None 時全開放）。
        host: 監聽位址，預設 "127.0.0.1"。
        port: 監聽連接埠，預設 8000。
        **config_overrides: AgentConfig 覆寫值（llm_name / system_prompt）。

    Returns:
        (uvicorn.Server, ChatApp)：server 交由呼叫端 run()；chat_app 負責關閉 agent。
    """
    run_manager, run_title = create_run_no_site_context(
        module="agent",
        config_name=config_name,
        base_folder="runs",
    )

    # 標題註明僅為初始化：耗時訊息不應被誤讀成 server 的執行時間
    with run_workflow_context("Server", run_manager=run_manager):
        # --- 初始化 Agent -----
        config = AgentConfig.from_toml(config_name, **config_overrides)
        log_config(f"{config.__class__.__name__} Loaded from toml", config)
        agent = create_agent(config_name, **config_overrides)

        try:
            # --- 初始化 App & Server -----
            chat_app = ChatApp.create(
                agent=agent,
                run_manager=run_manager,
                allowed_origins=allowed_origins,
            )

            # --- 啟動 Server -----
            uvicorn_config = uvicorn.Config(
                chat_app.app, host=host, port=port, log_level="info"
            )
            server = ChatServer(uvicorn_config)

            # ---- 輸出完成訊息 -----
            log_session("Server Initialization Completed", style="cyan")

            # ---- 儲存設定 -----
            if run_config is not None:
                save_run_config_as_toml(run_config, run_manager.run_config_toml_path)
        except Exception as e:
            log_session("Server Initialization Failed", style="red")
            print_log(f"Error: {e}")
            agent.close()
            raise

    return server, chat_app
