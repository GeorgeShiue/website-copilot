"""CLI（website-copilot）測試：參數解析結果以 mock 攔截 pipeline 函式驗證，不實際執行。

- `--run.config` 參數名稱（Python 屬性仍為 config_name）；舊的 `--run.config-name` 被拒。
- `--module.*` 巢狀覆寫參數：只傳遞有指定的欄位，合併後的 config 值正確。
- 型別錯誤由 tyro 擋下；dict 欄位（litellm_kwargs）不在 CLI；exp 子命令已移除。
"""

from unittest.mock import MagicMock, patch

import pytest

from website_copilot.cli import main
from website_copilot.config.pipeline_config import (
    AgentRunConfig,
    PrepareRunConfig,
    RAGQueryRunConfig,
    ServeRunConfig,
    WebsiteCrawlerRunConfig,
)
from website_copilot.config.rag_config import RAGConfig
from website_copilot.config.website_crawler_config import WebsiteCrawlerConfig


@pytest.fixture(autouse=True)
def _no_logging_setup():
    with patch("website_copilot.utils.log_helper.setup_logging"):
        yield


def _run(args: list[str], target: str) -> MagicMock:
    """以 args 執行 CLI，回傳攔截 target（pipeline 函式）的 mock。"""
    with patch(target) as mock:
        main(args)
    return mock


def test_run_config_argument_name() -> None:
    mock = _run(
        ["run", "rag-query", "--run.config", "test", "--run.query-times", "3"],
        "website_copilot.pipelines.exp.run_rag_query",
    )

    mock.assert_called_once_with(
        RAGQueryRunConfig(config_name="test", query_times=3), {}
    )


def test_old_config_name_argument_rejected() -> None:
    with pytest.raises(SystemExit):
        main(["run", "rag-query", "--run.config-name", "test"])


def test_nested_module_overrides() -> None:
    mock = _run(
        [
            "run",
            "rag-query",
            "--run.config",
            "test",
            "--module.retriever.similarity-top-k",
            "20",
            "--module.retriever.query-mode",
            "default",
            "--module.vector-store.hybrid-ranker-params.weights",
            "1.0",
            "0.3",
        ],
        "website_copilot.pipelines.exp.run_rag_query",
    )

    run_config, overrides = mock.call_args.args
    assert overrides == {
        "retriever": {"similarity_top_k": 20, "query_mode": "default"},
        "vector_store": {"hybrid_ranker_params": {"weights": [1.0, 0.3]}},
    }

    # 覆寫值寫入最終 config，未指定的欄位維持設定檔的值
    config = RAGConfig.from_yaml(run_config.config_name, overrides)
    assert config.retriever.similarity_top_k == 20
    assert config.retriever.query_mode == "default"
    assert config.retriever.hybrid_top_k == 10
    params = config.vector_store.hybrid_ranker_params
    assert params is not None and params.weights == [1.0, 0.3]


def test_bool_override() -> None:
    mock = _run(
        [
            "run",
            "website-crawler",
            "--run.config",
            "test",
            "--run.no-save",
            "--module.init.light-mode",
            "False",
            "--module.init.max-pages",
            "5",
        ],
        "website_copilot.pipelines.prepare.run_website_crawler",
    )

    run_config, overrides = mock.call_args.args
    assert run_config == WebsiteCrawlerRunConfig(config_name="test", save=False)
    assert overrides == {"init": {"light_mode": False, "max_pages": 5}}
    config = WebsiteCrawlerConfig.from_yaml("test", overrides)
    assert config.init.light_mode is False
    assert config.init.wait_for_images is True


def test_agent_command() -> None:
    mock = _run(
        ["run", "agent", "--run.query", "你好", "--module.llm-name", "other-llm"],
        "website_copilot.pipelines.exp.run_agent_query",
    )

    mock.assert_called_once_with(
        AgentRunConfig(query="你好"), {"llm_name": "other-llm"}
    )


@pytest.mark.parametrize(
    "args",
    [
        ["run", "rag-query", "--module.retriever.similarity-top-k", "abc"],
        ["run", "rag-query", "--module.retriever.query-mode", "dense"],
        ["run", "image-summarizer", "--module.litellm-kwargs", "{}"],
    ],
    ids=["int", "literal", "dict-field"],
)
def test_invalid_cli_arguments_rejected(args: list[str]) -> None:
    with pytest.raises(SystemExit):
        main(args)


def test_prepare_command() -> None:
    mock = _run(
        ["prepare", "--run.config", "test", "--run.no-publish"],
        "website_copilot.pipelines.prepare.run_prepare",
    )

    mock.assert_called_once_with(PrepareRunConfig(config_name="test", publish=False))


def test_prepare_publishes_by_default() -> None:
    mock = _run(["prepare"], "website_copilot.pipelines.prepare.run_prepare")

    mock.assert_called_once_with(PrepareRunConfig(config_name="default", publish=True))


def test_serve_command() -> None:
    mock = _run(
        ["serve", "--run.config", "test", "--run.port", "9000"],
        "website_copilot.pipelines.serve.serve",
    )

    mock.assert_called_once_with(ServeRunConfig(config_name="test", port=9000))


def test_exp_command_removed() -> None:
    with pytest.raises(SystemExit):
        main(["exp", "rag_dense_vs_hybrid"])
