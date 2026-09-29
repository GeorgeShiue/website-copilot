"""`website-copilot` CLI 與入口流程測試。

涵蓋：
- 子命令解析與分派（prepare / serve / run <module> / exp），執行邏輯以 mock 替代
- run 子命令的 module override 轉換（weights → hybrid_ranker_params）與 save／publish 拆出，
  且 run_config 保留 save／publish（run_config.toml 完整記錄）
- exp 名稱清單與 pipelines.exp.EXPERIMENTS 一致
- serve：執行 server.run() 並吞下 KeyboardInterrupt；run_prepare：階段串接與提前結束
- CLI 與 serve 路徑不載入爬蟲模組
"""

from __future__ import annotations

import subprocess
import sys
from typing import get_args
from unittest.mock import MagicMock, patch

import pytest

from website_copilot.cli import main
from website_copilot.cli.exp import ExperimentName

LOG_SETUP = "website_copilot.utils.log_helper.setup_logging"


# ===========================================================================
# 子命令分派
# ===========================================================================


def test_prepare_dispatches_run_prepare() -> None:
    with (
        patch(LOG_SETUP),
        patch("website_copilot.pipelines.prepare.run_prepare") as mock_prepare,
    ):
        main(["prepare", "--run.config-name", "test"])
    mock_prepare.assert_called_once_with(config_name="test")


def test_serve_dispatches_serve() -> None:
    with (
        patch(LOG_SETUP),
        patch("website_copilot.pipelines.serve.serve") as mock_serve,
    ):
        main(["serve", "--run.port", "9000"])
    run_config = mock_serve.call_args.args[0]
    assert run_config.port == 9000
    assert run_config.config_name == "default"


def test_run_rag_build_converts_overrides() -> None:
    with (
        patch(LOG_SETUP),
        patch("website_copilot.pipelines.prepare.run_rag_build") as mock_build,
    ):
        main(
            [
                "run",
                "rag-build",
                "--run.config-name",
                "test",
                "--run.publish",
                "--module.weights",
                "1.0",
                "0.5",
                "--module.similarity-top-k",
                "5",
            ]
        )
    kwargs = mock_build.call_args.kwargs
    assert kwargs["config_name"] == "test"
    assert kwargs["save"] is True
    assert kwargs["publish"] is True
    assert kwargs["hybrid_ranker_params"] == {"weights": [1.0, 0.5]}
    assert kwargs["similarity_top_k"] == 5
    assert "weights" not in kwargs
    assert kwargs["run_config"].config_name == "test"


def test_run_config_keeps_save_and_publish(tmp_path) -> None:
    """save／publish 只從 kwargs 拆出，run_config 本身保留，run_config.toml 完整記錄。"""
    import tomllib

    from website_copilot.utils.config_helper import save_run_config_as_toml

    with (
        patch(LOG_SETUP),
        patch("website_copilot.pipelines.prepare.run_rag_build") as mock_build,
    ):
        main(["run", "rag-build", "--run.config-name", "test", "--run.publish"])
    run_config = mock_build.call_args.kwargs["run_config"]
    assert run_config.save is True
    assert run_config.publish is True

    toml_path = tmp_path / "run_config.toml"
    save_run_config_as_toml(run_config, str(toml_path))
    with toml_path.open("rb") as f:
        saved = tomllib.load(f)
    assert saved["save"] is True
    assert saved["publish"] is True
    assert saved["config_name"] == "test"


def test_run_rag_query_dispatches_without_save_publish() -> None:
    with (
        patch(LOG_SETUP),
        patch("website_copilot.pipelines.exp.run_rag_query") as mock_query,
    ):
        main(["run", "rag-query", "--run.query-times", "3"])
    kwargs = mock_query.call_args.kwargs
    assert kwargs["query_times"] == 3
    assert "save" not in kwargs
    assert "publish" not in kwargs


def test_run_agent_dispatches_run_agent_query() -> None:
    with (
        patch(LOG_SETUP),
        patch("website_copilot.pipelines.exp.run_agent_query") as mock_agent,
    ):
        main(["run", "agent", "--run.query", "hi", "--module.llm-name", "gpt-x"])
    kwargs = mock_agent.call_args.kwargs
    assert kwargs["query"] == "hi"
    assert kwargs["llm_name"] == "gpt-x"
    assert kwargs["stream"] is False


@pytest.mark.parametrize(
    ("subcommand", "target"),
    [
        ("website-crawler", "website_copilot.pipelines.prepare.run_website_crawler"),
        (
            "image-summarizer",
            "website_copilot.pipelines.prepare.run_image_summarizer",
        ),
    ],
)
def test_run_prepare_modules_dispatch(subcommand: str, target: str) -> None:
    with patch(LOG_SETUP), patch(target) as mock_run:
        main(["run", subcommand, "--run.config-name", "test"])
    assert mock_run.call_args.kwargs["config_name"] == "test"


def test_exp_dispatches_by_name() -> None:
    with (
        patch(LOG_SETUP),
        patch("website_copilot.pipelines.exp.run_experiment") as mock_exp,
    ):
        main(["exp", "rag_hybrid_top_k"])
    mock_exp.assert_called_once_with("rag_hybrid_top_k")


def test_exp_names_match_experiments() -> None:
    from website_copilot.pipelines.exp import EXPERIMENTS

    assert set(get_args(ExperimentName)) == set(EXPERIMENTS)


def test_run_experiment_rejects_unknown_name() -> None:
    from website_copilot.pipelines.exp import run_experiment

    with pytest.raises(ValueError, match="Unknown experiment"):
        run_experiment("nope")


# ===========================================================================
# 入口流程
# ===========================================================================


def test_serve_runs_server_and_swallows_interrupt() -> None:
    from website_copilot.config.pipeline_config import ServeRunConfig
    from website_copilot.pipelines.serve import serve

    server = MagicMock()
    server.run.side_effect = KeyboardInterrupt
    with (
        patch("website_copilot.pipelines.serve.run_agent_build"),
        patch(
            "website_copilot.pipelines.serve.run_server_build", return_value=server
        ) as mock_run_server_build,
    ):
        serve(ServeRunConfig(port=9000))
    assert mock_run_server_build.call_args.kwargs["port"] == 9000
    server.run.assert_called_once()


def test_run_prepare_chains_stages_with_publish() -> None:
    from website_copilot.pipelines import prepare

    with (
        patch.object(prepare, "run_website_crawler", return_value={"p": {}}) as crawl,
        patch.object(prepare, "run_image_summarizer", return_value={"p": {}}) as image,
        patch.object(prepare, "run_rag_build") as rag,
    ):
        prepare.run_prepare("test")
    crawl.assert_called_once_with(config_name="test", save=False, publish=True)
    image.assert_called_once_with(
        config_name="test", crawl_results={"p": {}}, save=False, publish=True
    )
    rag.assert_called_once_with(config_name="test", save=False, publish=True)


def test_run_prepare_stops_when_crawler_returns_none() -> None:
    from website_copilot.pipelines import prepare

    with (
        patch.object(prepare, "run_website_crawler", return_value=None),
        patch.object(prepare, "run_image_summarizer") as image,
        patch.object(prepare, "run_rag_build") as rag,
    ):
        prepare.run_prepare("test")
    image.assert_not_called()
    rag.assert_not_called()


def test_cli_and_serve_path_do_not_load_crawler() -> None:
    code = (
        "import sys, website_copilot.cli, website_copilot.cli.serve, "
        "website_copilot.pipelines.serve; "
        "print([m for m in sys.modules if 'crawl4ai' in m or 'ingestion.crawling' in m])"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    assert result.stdout.strip() == "[]"
