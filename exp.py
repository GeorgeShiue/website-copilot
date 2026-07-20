from app.workflow.workflow import run_rag_query, run_webpage_image_summarizer
from app.workflow.workflow_manager import RunManager
from utils.log_helper import setup_logging

setup_logging("debug")


# TODO: 支援使用 CLI 控制實驗
def webpage_image_summarizer_model():
    # gemini_flash_lite_models = ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite"]
    # gemini_3_all_tier_models = [
    #     "gemini-3.1-flash-lite",
    #     "gemini-3-flash",
    #     "gemini-3-pro",
    # ]
    models = ["gemini-3.1-flash-lite", "gemini-3-flash"]  # temp
    run_manager = RunManager()

    for model in models:
        run_webpage_image_summarizer(
            run_manager=run_manager,
            config_name=model,
            run_name_use_config_name=True,
        )


def webpage_image_summarizer_prompt():
    # all_prompts = ["prompt-v1", "prompt-v2", "prompt-v3"]
    prompts = ["prompt-v3"]  # temp
    run_manager = RunManager()

    for prompt in prompts:
        run_webpage_image_summarizer(
            run_manager=run_manager,
            config_name=prompt,
            run_name_use_config_name=True,
        )


def rag_dense_model():
    run_manager = RunManager()
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

    for i in range(len(queries)):
        run_manager.set_module_path(f"query_{i + 1}")
        query = queries[i]
        for model in models:
            run_rag_query(
                run_manager=run_manager,
                config_name=model,
                run_name_use_config_name=True,
                query_times=10,
                query=query,
            )


# TODO: 測試 milvus vector store
def rag_hybrid_ranker():
    run_manager = RunManager()
    run_manager.set_module_path("rag_hybrid_ranker")
    hybrid_rankers = [
        "milvus-weight",
        "milvus-RRF",
    ]

    for hybrid_ranker in hybrid_rankers:
        run_rag_query(
            run_manager=run_manager,
            config_name=hybrid_ranker,
        )


def rag_hybrid_ranker_weights():
    run_manager = RunManager()
    run_manager.set_module_path("rag_hybrid_ranker_weights")

    hybrid_ranker_weights = [
        "milvus-weight-1.0_0.3",
        "milvus-weight-1.0_0.5",
        "milvus-weight-0.9_0.3",
    ]

    for hybrid_ranker_weight in hybrid_ranker_weights:
        run_rag_query(
            run_manager=run_manager,
            config_name=hybrid_ranker_weight,
            run_name_use_config_name=True,
        )


def rag_hybrid_top_k():
    run_manager = RunManager()
    run_manager.set_module_path("rag_hybrid_top_k")

    hybrid_top_k_configs = [
        "milvus-topk-10",
        "milvus-topk-20",
        "milvus-topk-30",
    ]

    for hybrid_top_k_config in hybrid_top_k_configs:
        run_rag_query(
            run_manager=run_manager,
            config_name=hybrid_top_k_config,
            run_name_use_config_name=True,
        )


def rag_hybrid_five_question():
    run_manager = RunManager()
    run_manager.set_module_path("rag_hybrid_five_question")
    queries = [
        "milvus-q1-members",
        "milvus-q2-activities",
        "milvus-q3-prepare",
        "milvus-q4-contact",
        "milvus-q5-papers",
    ]

    for query in queries:
        run_rag_query(
            run_manager=run_manager,
            config_name=query,
            run_name_use_config_name=True,
        )


if __name__ == "__main__":
    import asyncio

    asyncio.set_event_loop(asyncio.new_event_loop())

    # webpage_image_summarizer_model()
    # webpage_image_summarizer_prompt()

    # rag_dense_model()

    # rag_hybrid_ranker()
    # rag_hybrid_ranker_weights()
    # rag_hybrid_top_k()
    rag_hybrid_five_question()
