from run import run_rag, run_webpage_image_summarizer
from utils.log_helper import setup_logging

setup_logging("debug")


def webpage_image_summarizer_model():
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
    # all_prompts = ["prompt-v1", "prompt-v2", "prompt-v3"]
    prompts = ["prompt-v3"]  # temp

    for prompt in prompts:
        run_webpage_image_summarizer(
            config_name=prompt,
            run_name_use_config_name=True,
        )


# TODO: 使用多 config 進行詳細測試
def rag_query_engine():
    cutoffs = ["cutoff-0.5", "cutoff-0.3"]

    for cutoff in cutoffs:
        run_rag(
            config_name=cutoff,
            run_name_use_config_name=True,
        )


if __name__ == "__main__":
    # webpage_image_summarizer_model()
    # webpage_image_summarizer_prompt()
    rag_query_engine()
