"""RAG 查詢評估與 Agent 問答 workflow（實驗／除錯用，不屬於 prepare 或 serve 階段）。"""

import asyncio
import time
import uuid
from typing import Any

from website_copilot.config.pipeline_config import AgentRunConfig, RAGQueryRunConfig
from website_copilot.config.rag_config import RAGConfig
from website_copilot.config.site_config import SiteConfig
from website_copilot.ingestion.indexing.index import COLLECTION_NAME
from website_copilot.pipelines.serve import run_agent_build
from website_copilot.retrieval.evaluation import (
    build_evaluators,
    evaluate_response,
    response_to_dict,
)
from website_copilot.retrieval.factory import (
    load_rag,
    published_target,
    vector_store_run_target,
)
from website_copilot.storage.run_context import (
    create_run_context,
    create_run_no_site_context,
    run_workflow_context,
)
from website_copilot.storage.run_persistence import save_query_results_as_md
from website_copilot.utils.config_helper import (
    log_config,
    save_module_config,
    save_run_config,
    save_site_config,
)
from website_copilot.utils.log_helper import log_session, print_log


def run_rag_query(
    run_config: RAGQueryRunConfig,
    overrides: dict[str, Any] | None = None,
) -> None:
    """執行 RAG 查詢工作流程。

    Args:
        run_config: 執行參數（site 對應 configs/sites/{site}.yml；config_name 對應
            configs/rag/{name}.yml；query 未指定時使用站點的 sample_query；vector_store_run
            指定 rag-build 的 run 資料夾時查詢其向量庫；query_times 查詢次數）。
        overrides: RAGConfig 的巢狀覆寫值。

    只查詢既有向量庫、不建庫也不寫入 data/：預設為 data/ 中已 publish 的向量庫
    （data/vector_db/{site_id}.db），指定 vector_store_run 時為該 run 的 results/milvus.db。
    建庫一律走 run_rag_build。

    Raises:
        ValueError: run_config.query 與站點的 sample_query 皆未設定時，或 vector_store_run
            屬於其他站點時。
        FileNotFoundError: 向量庫不存在時。
    """
    # ----- 初始化設定和路徑 -----
    query_times = run_config.query_times
    site = SiteConfig.from_yaml(run_config.site)
    query = run_config.query or site.sample_query
    if not query:
        raise ValueError(
            f"未指定查詢：請以 --run.query 指定，或在 {site.source} 設定 sample_query"
        )
    config = RAGConfig.from_yaml(run_config.config_name, overrides)
    run_manager, run_title = create_run_context(
        module="rag_query",
        config_name=run_config.config_name,
        site_id=site.site_id,
        config=config,
        run_name_use_config_name=run_config.run_name_use_config_name,
    )
    assert run_manager is not None  # save 未在此函式開放，永遠會建立 RunManager

    with run_workflow_context(run_title, run_manager=run_manager):
        # ----- 初始化 RAG 和 評估器 -----
        log_session("Building RAG and Evaluators", style="cyan")
        log_config("SiteConfig Loaded from yaml", site)
        log_config(f"{config.__class__.__name__} Loaded from yaml", config)
        target = (
            vector_store_run_target(site.site_id, run_config.vector_store_run)
            if run_config.vector_store_run
            else published_target(site.site_id)
        )
        rag = load_rag(config, target, build_query_engine=True)

        try:
            evaluators = build_evaluators(config)

            # ----- Query -----
            query_results: list[dict] = []
            faithfulness_pass = 0
            relevancy_pass = 0
            for i in range(query_times):
                # ----- 查詢與回應 -----
                log_session(f"Query & Response {i + 1}", style="cyan")
                response = rag.query(query, log_sources=True)

                # ----- 回應評估 -----
                # * 可改用 regas 或 deepeval 評估
                log_session("Evaluation", style="cyan")
                faithfulness_result, relevancy_result = evaluate_response(
                    evaluators, query=query, response=response
                )
                if faithfulness_result.passing:
                    faithfulness_pass += 1
                if relevancy_result.passing:
                    relevancy_pass += 1

                query_results.append(
                    response_to_dict(
                        query=query,
                        response=response,
                        faithfulness_result=faithfulness_result,
                        relevancy_result=relevancy_result,
                        index=i + 1,
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    )
                )

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

            # ----- 輸出完成訊息 -----
            log_session("RAG Query Completed", style="cyan")

            # ----- 儲存結果 -----
            query_results_dict = {
                "config": {
                    "config_name": config.config_name,
                    "run_name": run_manager.run_name,
                    "query": query,
                    "query_llm_name": config.query_engine.query_llm_name,
                    "evaluator_llm_name": config.query_engine.evaluator_llm_name,
                    "vector_store_type": config.vector_store.vector_store_type,
                    "collection_name": COLLECTION_NAME,
                    "query_mode": config.retriever.query_mode,
                    "similarity_top_k": config.retriever.similarity_top_k,
                    "hybrid_top_k": config.retriever.hybrid_top_k,
                    "alpha": config.retriever.alpha,
                    "cutoff": config.query_engine.cutoff,
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
            save_module_config(config, run_manager.module_config_path)
            save_site_config(site, run_manager.site_config_path)
            save_run_config(run_config, run_manager.run_config_path)
        except Exception as e:
            log_session("RAG Query Failed", style="red")
            print_log(f"Error: {e}")
            raise
        finally:
            rag.close()


def run_agent_query(
    run_config: AgentRunConfig,
    overrides: dict[str, Any] | None = None,
) -> None:
    """執行 Agent 問答工作流程（建構 agent → 建立 run context → 問答 → 落盤 → 關閉）。

    流程：run_agent_build() 建構 agent（module_config.yml 寫在 runs/<ts>/agent_build/）
    → 問答 → 顯示回答與來源 → 落盤 runs/<ts>/agent/ → 寫 run_config.yml → 關閉 agent。
    agent 的 Tool 生命週期在本函式內結束（呼叫端不需持有 agent）。

    Args:
        run_config: 執行參數（config_name 對應 configs/agent/{name}.yml；query 使用者問題；
            thread_id 為 session 識別，None 時自動產生 auto-{uuid}；stream 是否逐 token 串流輸出）。
        overrides: AgentConfig 的巢狀覆寫值（llm_name / system_prompt）。
    """
    query, thread_id = run_config.query, run_config.thread_id

    # ---- 建構 Agent（獨立的 agent_build run context）-----
    agent = run_agent_build(run_config, overrides)

    try:
        run_manager, run_title = create_run_no_site_context(
            module="agent",
            config_name=run_config.config_name,
        )

        with run_workflow_context(run_title, run_manager=run_manager):
            try:
                # ---- Agent 問答 -----
                log_session("Agent Query and Response", style="cyan")
                print_log(f"Query: {query}")
                if run_config.stream:
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

                # ---- 儲存設定（module_config.yml 已由 run_agent_build 寫入）-----
                save_run_config(run_config, run_manager.run_config_path)

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
                raise
    finally:
        agent.close()
