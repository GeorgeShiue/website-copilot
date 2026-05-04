from run import run_webpage_image_summarizer


def webpage_image_summarizer_model():
    google_flash_lite_models = ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite"]
    # google_all_tier_models = [
    #     "gemini-3.1-flash-lite",
    #     "gemini-3-flash",
    #     "gemini-3-pro",
    # ]

    run_webpage_image_summarizer(
        config_names=google_flash_lite_models,
    )


def webpage_image_summarizer_prompt():
    prompts = ["prompt-v1", "prompt-v2"]
    run_webpage_image_summarizer(
        config_names=prompts,
        run_name_use_config_name=True,
    )


if __name__ == "__main__":
    # webpage_image_summarizer_model()
    webpage_image_summarizer_prompt()
