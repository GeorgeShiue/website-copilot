"""log_helper 執行摘要累加器、噪音 logger 過濾，與 config 字串截斷的單元測試。"""

import logging

import pytest

from utils import log_helper
from utils.config_helper import CONFIG_VALUE_MAX_CHARS, truncate_config_value
from utils.log_helper import (
    log_main_workflow_run_summary,
    log_run_time,
    record_cost,
    record_elapsed,
    reset_run_summary,
    setup_logging,
)


@pytest.fixture(autouse=True)
def _clean_summary():
    reset_run_summary()
    yield
    reset_run_summary()


# ── truncate_config_value ────────────────────────────────────────────


def test_truncate_keeps_short_string():
    assert truncate_config_value("nculab") == "nculab"


def test_truncate_escapes_newline_before_measuring():
    assert truncate_config_value("a\nb") == "a\\nb"


def test_truncate_cuts_long_string_with_ellipsis():
    long_value = "x" * (CONFIG_VALUE_MAX_CHARS + 10)
    result = truncate_config_value(long_value)
    assert result == "x" * CONFIG_VALUE_MAX_CHARS + "…"


def test_truncate_boundary_is_not_truncated():
    exact = "y" * CONFIG_VALUE_MAX_CHARS
    assert truncate_config_value(exact) == exact


def test_truncate_custom_limit():
    assert truncate_config_value("abcdef", max_chars=3) == "abc…"


# ── 累加器 ───────────────────────────────────────────────────────────


def test_record_elapsed_accumulates_same_stage():
    record_elapsed("stage", 1.5)
    record_elapsed("stage", 2.0)
    assert log_helper._stage_elapsed == {"stage": 3.5}


def test_record_cost_without_stage_goes_to_unattributed():
    record_cost(0.5)
    assert log_helper._stage_costs == {"unattributed": 0.5}


def test_log_run_time_records_elapsed_and_attributes_cost_to_innermost_stage():
    with log_run_time("outer"):
        record_cost(0.1)
        with log_run_time("inner"):
            record_cost(0.2)
        record_cost(0.3)

    assert set(log_helper._stage_elapsed) == {"outer", "inner"}
    assert log_helper._stage_costs["inner"] == pytest.approx(0.2)
    assert log_helper._stage_costs["outer"] == pytest.approx(0.4)
    assert log_helper._stage_stack == []


def test_log_run_time_record_false_skips_summary_and_stage_stack():
    with log_run_time("outer"):
        with log_run_time("detail", record=False):
            record_cost(0.2)

    assert "detail" not in log_helper._stage_elapsed
    # record=False 的步驟不算階段，花費歸屬外層
    assert log_helper._stage_costs == {"outer": pytest.approx(0.2)}


def test_log_run_time_pops_stage_when_body_raises():
    with pytest.raises(RuntimeError):
        with log_run_time("boom"):
            raise RuntimeError("fail")

    assert log_helper._stage_stack == []
    assert "boom" in log_helper._stage_elapsed


def test_log_run_time_without_title_is_not_recorded():
    with log_run_time():
        pass

    assert log_helper._stage_elapsed == {}


def test_reset_run_summary_clears_everything():
    with log_run_time("stage"):
        record_cost(1.0)
    reset_run_summary()

    assert log_helper._stage_elapsed == {}
    assert log_helper._stage_costs == {}
    assert log_helper._stage_stack == []


def test_log_run_summary_prints_stage_rows_and_total_cost(capsys):
    record_elapsed("Crawler", 12.34)
    with log_run_time("Summarizer"):
        record_cost(0.0893)
    log_main_workflow_run_summary()

    out = capsys.readouterr().out
    assert "Crawler" in out
    assert "12.3s" in out
    assert "Summarizer" in out
    assert "$0.0893" in out
    assert "Total cost" in out


def test_log_run_summary_prints_nothing_when_empty(capsys):
    log_main_workflow_run_summary()
    assert capsys.readouterr().out == ""


# ── 噪音 logger 過濾 ─────────────────────────────────────────────────


def test_setup_logging_silences_known_noisy_loggers():
    setup_logging("info")

    for name, level in log_helper.NOISY_LOGGER_LEVELS.items():
        assert logging.getLogger(name).level == level

    reader_logger = logging.getLogger("llama_index.core.readers.file.base")
    assert not reader_logger.isEnabledFor(logging.WARNING)
    assert not logging.getLogger("grpc._server").isEnabledFor(logging.ERROR)
