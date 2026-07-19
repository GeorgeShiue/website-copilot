from app.workflow.workflow import run_webpage_image_summarizer, run_rag_query
from utils.log_helper import setup_logging
from app.workflow.workflow_manager import RunManager

setup_logging("debug")


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


# TODO: 測試 gemini 3.1 pro
def rag_model():
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
        "gemini-3.1-pro",  # 待測試
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


if __name__ == "__main__":
    import asyncio

    asyncio.set_event_loop(asyncio.new_event_loop())

    # webpage_image_summarizer_model()
    # webpage_image_summarizer_prompt()
    # rag_model()
    rag_hybrid_ranker()
