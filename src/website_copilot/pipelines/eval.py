"""RAG 查詢評估 workflow（實驗／除錯用，不屬於 prepare 或 serve 階段）。"""

import time

from website_copilot.config.rag_config import RAGConfig
from website_copilot.config.pipeline_config import RAGQueryRunConfig
from website_copilot.ingestion.indexing.index import RAGBuilder
from website_copilot.ingestion.indexing.index import create_rag
from website_copilot.storage.run_persistence import save_query_results_as_md
from website_copilot.storage.run_context import (
    create_run_context,
    run_workflow_context,
)
from website_copilot.utils.config_helper import (
    log_config,
    save_module_config_as_toml,
    save_run_config_as_toml,
)
from website_copilot.utils.log_helper import log_session, print_log
from website_copilot.retrieval.helpers import response_to_dict


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
        rag = create_rag(
            config=config,
            force_rebuild=force_rebuild,
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
