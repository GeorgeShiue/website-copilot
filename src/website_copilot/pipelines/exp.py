"""RAG 查詢評估、Agent 問答 workflow 與批次實驗（實驗／除錯用，不屬於 prepare 或 serve 階段）。"""

import asyncio
import time
import uuid
from collections.abc import Callable

from website_copilot.config.pipeline_config import AgentRunConfig, RAGQueryRunConfig
from website_copilot.config.rag_config import RAGConfig
from website_copilot.pipelines.serve import run_agent_build
from website_copilot.retrieval.evaluation import (
    build_evaluators,
    evaluate_response,
    response_to_dict,
)
from website_copilot.retrieval.factory import build_rag
from website_copilot.storage.run_context import (
    create_run_context,
    create_run_no_site_context,
    run_workflow_context,
)
from website_copilot.storage.run_persistence import save_query_results_as_md
from website_copilot.utils.config_helper import (
    log_config,
    save_module_config_as_toml,
    save_run_config_as_toml,
)
from website_copilot.utils.log_helper import log_session, print_log


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
    assert run_manager is not None  # save 未在此函式開放，永遠會建立 RunManager

    with run_workflow_context(run_title, run_manager=run_manager):
        # ----- 初始化 RAG 和 評估器 -----
        log_session("Building RAG and Evaluators", style="cyan")
        log_config(f"{config.__class__.__name__} Loaded from toml", config)
        rag = build_rag(
            config=config,
            force_rebuild=force_rebuild,
        )

        try:
            evaluators = build_evaluators(config)

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
                faithfulness_result, relevancy_result = evaluate_response(
                    evaluators, query=config.query, response=response
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


def run_agent_query(
    query: str,
    config_name: str = "default",
    thread_id: str | None = None,
    stream: bool = False,
    run_config: AgentRunConfig | None = None,
    **config_overrides,
) -> None:
    """執行 Agent 問答工作流程（建構 agent → 建立 run context → 問答 → 落盤 → 關閉）。

    流程：run_agent_build() 建構 agent（module_config.toml 寫在 runs/<ts>/agent_build/）
    → 問答 → 顯示回答與來源 → 落盤 runs/<ts>/agent/ → 寫 run_config.toml → 關閉 agent。
    agent 的 Tool 生命週期在本函式內結束（呼叫端不需持有 agent）。

    Args:
        config_name: AgentConfig 名稱（對應 configs/agent/{name}.toml）。
        query: 使用者問題。
        thread_id: session 識別；None 時自動產生 auto-{uuid}。
        stream: 是否逐 token 串流輸出。
        run_config: RunConfig 實例（可選，用於落盤 run config toml）。
        **config_overrides: AgentConfig 覆寫值（llm_name / system_prompt）。
    """

    # ---- 建構 Agent（獨立的 agent_build run context）-----
    agent = run_agent_build(config_name, **config_overrides)

    try:
        run_manager, run_title = create_run_no_site_context(
            module="agent",
            config_name=config_name,
            base_folder="runs",
        )

        with run_workflow_context(run_title, run_manager=run_manager):
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

                # ---- 儲存設定（module_config.toml 已由 run_agent_build 寫入）-----
                if run_config is not None:
                    save_run_config_as_toml(
                        run_config, run_manager.run_config_toml_path
                    )

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


# ════════════════════════════════════════════════════════════════════
#  批次實驗（各實驗以 config_name 對應 configs/{module}/{name}.toml）
# ════════════════════════════════════════════════════════════════════


def webpage_image_summarizer_model():
    from website_copilot.pipelines.prepare import run_webpage_image_summarizer

    # gemini_flash_lite_models = ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite"]
    # gemini_3_all_tier_models = [
    #     "gemini-3.1-flash-lite",
    #     "gemini-3-flash",
    #     "gemini-3-pro",
    # ]
    models = ["gemini-3.1-flash-lite", "gemini-3-flash"]  # temp

    for model in models:
        run_webpage_image_summarizer(
            config_name=model,
            run_name_use_config_name=True,
        )


def webpage_image_summarizer_prompt():
    from website_copilot.pipelines.prepare import run_webpage_image_summarizer

    # all_prompts = ["prompt-v1", "prompt-v2", "prompt-v3"]
    prompts = ["prompt-v3"]  # temp

    for prompt in prompts:
        run_webpage_image_summarizer(
            config_name=prompt,
            run_name_use_config_name=True,
        )


def rag_dense_model():
    queries = [
        "實驗室近三年發表過哪些論文？",
        "實驗室的成員有哪些人？",
        "實驗室開發過哪些與 AI 相關的應用？",
    ]
    models = [
        # "gemini-3.1-flash-lite",
        # "gemini-3-flash",
        # "gemini-3.5-flash",
        # "gemini-2.5-pro",
        "gemini-3.1-pro",
    ]

    for query in queries:
        for model in models:
            run_rag_query(
                config_name=model,
                run_name_use_config_name=True,
                query_times=10,
                query=query,
            )


def rag_hybrid_ranker():
    hybrid_rankers = [
        "milvus-weight",
        "milvus-RRF",
    ]

    for hybrid_ranker in hybrid_rankers:
        run_rag_query(
            config_name=hybrid_ranker,
        )


def rag_hybrid_ranker_weights():
    hybrid_ranker_weights = [
        "milvus-weight-1.0_0.3",
        "milvus-weight-1.0_0.5",
        "milvus-weight-0.9_0.3",
    ]

    for hybrid_ranker_weight in hybrid_ranker_weights:
        run_rag_query(
            config_name=hybrid_ranker_weight,
            run_name_use_config_name=True,
        )


def rag_hybrid_top_k():
    hybrid_top_k_configs = [
        "milvus-topk-10",
        "milvus-topk-20",
        "milvus-topk-30",
    ]

    for hybrid_top_k_config in hybrid_top_k_configs:
        run_rag_query(
            config_name=hybrid_top_k_config,
            run_name_use_config_name=True,
        )


def rag_hybrid_five_question():
    queries = [
        "milvus-q1-members",
        "milvus-q2-activities",
        "milvus-q3-prepare",
        "milvus-q4-contact",
        "milvus-q5-papers",
    ]

    for query in queries:
        run_rag_query(
            config_name=query,
            run_name_use_config_name=True,
        )


def rag_dense_vs_hybrid():
    query_modes = ["dense", "hybrid"]
    queries = [
        "實驗室的成員有哪些人？",
        "實驗室在2024年有哪些活動？",
        "加入實驗室需要準備哪些資料？",
        "如何聯絡研究室指導教授？",
        "實驗室近三年發表過哪些論文？",
    ]

    for i, query in enumerate(queries):
        for query_mode in query_modes:
            # 每個 question+strategy 使用獨立 DB 路徑，避免 pymilvus ConnectionManager
            # 以 URI 為 key 快取連線導致下一輪 reconnect 到已關閉的舊 server
            unique_uri = f"data/rag/exps/milvus_{query_mode}_q{i + 1}.db"
            run_rag_query(
                config_name=query_mode,
                run_name_use_config_name=True,
                query=query,
                milvus_uri=unique_uri,
            )
            # MilvusLite gRPC 關閉後 transport 需時間回收，確保新 server 啟動前舊 ping 已消散
            time.sleep(1)


EXPERIMENTS: dict[str, Callable[[], None]] = {
    "webpage_image_summarizer_model": webpage_image_summarizer_model,
    "webpage_image_summarizer_prompt": webpage_image_summarizer_prompt,
    "rag_dense_model": rag_dense_model,
    "rag_hybrid_ranker": rag_hybrid_ranker,
    "rag_hybrid_ranker_weights": rag_hybrid_ranker_weights,
    "rag_hybrid_top_k": rag_hybrid_top_k,
    "rag_hybrid_five_question": rag_hybrid_five_question,
    "rag_dense_vs_hybrid": rag_dense_vs_hybrid,
}


def run_experiment(name: str) -> None:
    """依名稱執行 EXPERIMENTS 中的批次實驗。"""
    if name not in EXPERIMENTS:
        raise ValueError(
            f"Unknown experiment '{name}'. Available: {', '.join(EXPERIMENTS)}"
        )
    EXPERIMENTS[name]()
