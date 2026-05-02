from run import run_webpage_image_summarizer
from utils.run_manager import RunManager


def webpage_image_summarizer_model():
    run_manager = RunManager("webpage_image_summarizer")
    # models = ["gpt-5-mini", "gpt-4.1-mini", "gpt-4o-mini"] # openai
    models = ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite"]  # google

    for model in models:
        run_webpage_image_summarizer(run_manager, config_name=model)


def webpage_image_summarizer_prompt():
    run_manager = RunManager("webpage_image_summarizer")
    prompts = ["prompt-v1", "prompt-v2"]
    for prompt in prompts:
        run_webpage_image_summarizer(run_manager, config_name=prompt, run_name=prompt)


if __name__ == "__main__":
    # webpage_image_summarizer_model()
    webpage_image_summarizer_prompt()
