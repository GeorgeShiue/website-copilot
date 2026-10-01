"""pipelines/exp.py 測試：run_agent_query。

涵蓋：
- agent.ask() 以正確參數呼叫、落盤委派 run_manager.save_agent_results_as_json()、auto thread_id
- stream=True：astream_result（coroutine）串流結果同樣經 save_agent_results_as_json() 落盤
- finally 於成功與失敗路徑呼叫 agent.close()（失敗路徑只呼叫一次）

所有外部依賴以 mock 替代，不觸發真實 LLM / RAG 資源。
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from agent_stubs import (
    FailingAgentStub,
    FailingStreamAgentStub,
    FakeAgentStub,
    setup_mock_run_manager,
)

from website_copilot.config.pipeline_config import AgentRunConfig


@pytest.fixture(autouse=True)
def mock_save_run_config(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """run_config 為必填、一律落盤；以 mock 取代，避免寫出 mock RunManager 的假路徑。"""
    mock = MagicMock()
    monkeypatch.setattr("website_copilot.pipelines.exp.save_run_config", mock)
    return mock


# ===========================================================================
# run_agent_query：run context 所有者（agent 經 run_agent_build 建構）
# ===========================================================================


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_calls_agent_ask(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
):
    """run_agent_query：agent.ask() 以正確 query 和 thread_id 呼叫。"""
    from website_copilot.pipelines.exp import run_agent_query

    fake_agent = FakeAgentStub()
    mock_run_agent_build.return_value = fake_agent
    setup_mock_run_manager(mock_rm_cls)

    run_agent_query(
        AgentRunConfig(config_name="test", query="你好", thread_id="session-1")
    )

    assert len(fake_agent.asked) == 1
    assert fake_agent.asked[0]["query"] == "你好"
    assert fake_agent.asked[0]["thread_id"] == "session-1"


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_delegates_save_to_run_manager(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
):
    """run_agent_query：落盤委派 run_manager.save_agent_results_as_json()。"""
    from website_copilot.pipelines.exp import run_agent_query

    fake_agent = FakeAgentStub()
    mock_run_agent_build.return_value = fake_agent
    mock_rm = setup_mock_run_manager(mock_rm_cls)

    run_agent_query(
        AgentRunConfig(config_name="test", query="hello", thread_id="session-1")
    )

    mock_rm.save_agent_results_as_json.assert_called_once()
    save_kwargs = mock_rm.save_agent_results_as_json.call_args.kwargs
    assert save_kwargs["thread_id"] == "session-1"
    assert save_kwargs["agent_config"] is fake_agent.config
    assert save_kwargs["results"][0]["response"] == "fake answer"


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_passes_run_config_and_overrides(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
    mock_save_run_config,
):
    """run_agent_query：run_config 與 overrides 原樣交給 run_agent_build，run_config 落盤到 agent run。"""
    from website_copilot.pipelines.exp import run_agent_query

    mock_run_agent_build.return_value = FakeAgentStub()
    mock_rm = setup_mock_run_manager(mock_rm_cls)
    run_config = AgentRunConfig(config_name="test", query="hello")
    overrides = {"llm_name": "other-llm"}

    run_agent_query(run_config, overrides)

    mock_run_agent_build.assert_called_once_with(run_config, overrides)
    mock_save_run_config.assert_called_once_with(run_config, mock_rm.run_config_path)


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_auto_generates_thread_id(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
):
    """thread_id 為 None 時自動產生 auto-{uuid} 並用於落盤。"""
    from website_copilot.pipelines.exp import run_agent_query

    mock_run_agent_build.return_value = FakeAgentStub()
    mock_rm = setup_mock_run_manager(mock_rm_cls)

    run_agent_query(AgentRunConfig(config_name="test", query="hello"))

    thread_id = mock_rm.save_agent_results_as_json.call_args.kwargs["thread_id"]
    assert thread_id is not None
    assert thread_id.startswith("auto-")


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_closes_agent_on_success(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
):
    """run_agent_query 在成功時以 finally 呼叫 agent.close()。"""
    from website_copilot.pipelines.exp import run_agent_query

    fake_agent = FakeAgentStub()
    mock_run_agent_build.return_value = fake_agent
    setup_mock_run_manager(mock_rm_cls)

    run_agent_query(AgentRunConfig(config_name="test", query="hello"))

    assert fake_agent.close_called


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_closes_agent_on_error(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
):
    """run_agent_query 在 ask() 拋出例外時仍呼叫 agent.close()，且只呼叫一次。"""
    from website_copilot.pipelines.exp import run_agent_query

    fake_agent = FailingAgentStub()
    mock_run_agent_build.return_value = fake_agent
    setup_mock_run_manager(mock_rm_cls)

    with pytest.raises(RuntimeError):
        run_agent_query(AgentRunConfig(config_name="test", query="hello"))

    assert fake_agent.close_count == 1


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_closes_agent_on_stream_error(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
):
    """run_agent_query 在 stream 模式例外時仍呼叫 agent.close()，且只呼叫一次。"""
    from website_copilot.pipelines.exp import run_agent_query

    fake_agent = FailingStreamAgentStub()
    mock_run_agent_build.return_value = fake_agent
    setup_mock_run_manager(mock_rm_cls)

    with pytest.raises(RuntimeError):
        run_agent_query(AgentRunConfig(config_name="test", query="hello", stream=True))

    assert fake_agent.close_count == 1


@patch("website_copilot.pipelines.exp.run_agent_build")
@patch("website_copilot.storage.run_context.RunManager")
@patch("website_copilot.storage.run_context.save_logging_file")
@patch("website_copilot.pipelines.exp.log_session")
def test_run_agent_query_stream_persists_streamed_result(
    mock_log_session,
    _mock_save_logging,
    mock_rm_cls,
    mock_run_agent_build,
):
    """stream=True 的 happy path：astream_result 的串流結果經 save_agent_results_as_json 落盤。"""
    from website_copilot.pipelines.exp import run_agent_query

    fake_agent = FakeAgentStub()
    mock_run_agent_build.return_value = fake_agent
    mock_rm = setup_mock_run_manager(mock_rm_cls)

    run_agent_query(
        AgentRunConfig(
            config_name="test", query="hello", thread_id="session-1", stream=True
        )
    )

    mock_rm.save_agent_results_as_json.assert_called_once()
    save_kwargs = mock_rm.save_agent_results_as_json.call_args.kwargs
    assert save_kwargs["thread_id"] == "session-1"
    assert save_kwargs["agent_config"] is fake_agent.config
    assert save_kwargs["results"][0]["response"] == "streamed answer"
    assert fake_agent.close_called
