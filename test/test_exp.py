from test.test_dev import test_webpage_image_summarizer
from utils.exp_manager import ExperimentManager

# TODO: 將以下function改為exp...，放到exp.py


def test_webpage_image_summarizer_model():
    exp_manager = ExperimentManager("webpage_image_summarizer")
    models = ["gpt-5-mini", "gpt-4.1-mini", "gpt-4o-mini"]

    for model in models:
        test_webpage_image_summarizer(exp_manager, config_name=model)
