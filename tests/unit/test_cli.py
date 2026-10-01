"""CLI（website-copilot）測試：參數解析結果以 mock 攔截 pipeline 函式驗證，不實際執行。

- `--run.config` 參數名稱（Python 屬性仍為 config_name）；舊的 `--run.config-name` 被拒。
- `--module.*` 巢狀覆寫參數：只傳遞有指定的欄位，合併後的 config 值正確。
- 型別錯誤由 tyro 擋下；dict 欄位（litellm_kwargs）不在 CLI；exp 子命令已移除。
- `--help` 顯示 config class 的預設值，不顯示 None 選項；站點為必填的位置參數。
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
        [
            "run",
            "rag-query",
            "nculab",
            "--run.config",
            "test",
            "--run.query-times",
            "3",
        ],
        "website_copilot.pipelines.exp.run_rag_query",
    )

    mock.assert_called_once_with(
        RAGQueryRunConfig(site="nculab", config_name="test", query_times=3), {}
    )


def test_old_config_name_argument_rejected() -> None:
    with pytest.raises(SystemExit):
        main(["run", "rag-query", "nculab", "--run.config-name", "test"])


def test_nested_module_overrides() -> None:
    mock = _run(
        [
            "run",
            "rag-query",
            "nculab",
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
            "ncucsie",
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
    assert run_config == WebsiteCrawlerRunConfig(
        site="ncucsie", config_name="test", save=False
    )
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
        ["run", "rag-query", "nculab", "--module.retriever.similarity-top-k", "abc"],
        ["run", "rag-query", "nculab", "--module.retriever.query-mode", "dense"],
        ["run", "image-summarizer", "nculab", "--module.litellm-kwargs", "{}"],
        # 站點資訊不再是模組參數（Phase C 過渡期的參數已消失）
        ["run", "rag-query", "nculab", "--module.site-id", "x"],
        ["run", "rag-query", "nculab", "--module.query-engine.query", "q"],
        # 站點為必填的位置參數
        ["run", "rag-query", "--run.config", "test"],
        ["prepare", "--run.config", "test"],
    ],
    ids=[
        "int",
        "literal",
        "dict-field",
        "no-module-site-id",
        "no-module-query",
        "missing-site",
        "prepare-missing-site",
    ],
)
def test_invalid_cli_arguments_rejected(args: list[str]) -> None:
    with pytest.raises(SystemExit):
        main(args)


def test_prepare_command() -> None:
    mock = _run(
        ["prepare", "ncucsie", "--run.config", "test", "--run.no-publish"],
        "website_copilot.pipelines.prepare.run_prepare",
    )

    mock.assert_called_once_with(
        PrepareRunConfig(site="ncucsie", config_name="test", publish=False)
    )


def test_prepare_publishes_by_default() -> None:
    mock = _run(["prepare", "nculab"], "website_copilot.pipelines.prepare.run_prepare")

    mock.assert_called_once_with(
        PrepareRunConfig(site="nculab", config_name="default", publish=True)
    )


def test_rag_query_query_argument() -> None:
    mock = _run(
        ["run", "rag-query", "ncucsie", "--run.query", "介紹資工系課程"],
        "website_copilot.pipelines.exp.run_rag_query",
    )

    run_config, _ = mock.call_args.args
    assert run_config.site == "ncucsie"
    assert run_config.query == "介紹資工系課程"


def test_serve_command() -> None:
    mock = _run(
        ["serve", "--run.config", "test", "--run.port", "9000"],
        "website_copilot.pipelines.serve.serve",
    )

    mock.assert_called_once_with(ServeRunConfig(config_name="test", port=9000))


def test_exp_command_removed() -> None:
    with pytest.raises(SystemExit):
        main(["exp", "rag_dense_vs_hybrid"])


def test_help_shows_class_defaults(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("COLUMNS", "200")  # 避免 rich 換行切斷字串
    with pytest.raises(SystemExit):
        main(["run", "rag-query", "--help"])
    out = capsys.readouterr().out

    assert "--module.retriever.similarity-top-k INT" in out
    assert "dense 檢索回傳的節點數 (default: 10)" in out
    assert "--module.retriever.query-mode {hybrid,default}" in out
    # 可選 section 的預設值取自上層的預設實例
    assert "WeightedRanker 的 [dense, sparse] 權重 (default: [1.0, 0.5])" in out
    assert "SITE  站點名稱，對應 configs/sites/{site}.yml (required)" in out
    # 站點欄位已移出模組 config，模組參數全部都有預設值
    assert "--module.query-engine.query " not in out
    assert "(必填，來自設定檔)" not in out
    assert "--module.retriever.similarity-top-k {None" not in out
