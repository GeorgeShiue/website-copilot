"""utils/log_helper.py：save_logging_file 的巢狀（可重入）tee 行為。"""

import sys
from pathlib import Path

from website_copilot.utils import log_helper
from website_copilot.utils.log_helper import save_logging_file


def test_nested_save_logging_file_keeps_outer_tee(tmp_path: Path) -> None:
    outer = tmp_path / "outer.log"
    inner = tmp_path / "inner.log"

    with save_logging_file(str(outer)):
        tee = sys.stdout
        assert isinstance(tee, log_helper._TeeStream)
        print("outer-before")

        with save_logging_file(str(inner)):
            # 巢狀呼叫沿用外層 tee，不另開檔案
            assert sys.stdout is tee
            print("inner")

        # 內層結束後外層 tee 仍有效
        assert sys.stdout is tee
        assert not tee.file_stream.closed
        print("outer-after")

    assert "outer-before" in outer.read_text(encoding="utf-8")
    assert "inner" in outer.read_text(encoding="utf-8")
    assert "outer-after" in outer.read_text(encoding="utf-8")
    assert not inner.exists()


def test_outermost_exit_restores_streams_and_closes_file(tmp_path: Path) -> None:
    log_path = tmp_path / "run.log"

    with save_logging_file(str(log_path)):
        tee = log_helper._tee_stream
        assert tee is not None
        assert log_helper._tee_depth == 1

    assert sys.stdout is log_helper._stdout_original
    assert sys.stderr is log_helper._stderr_original
    assert log_helper._tee_depth == 0
    assert tee.file_stream.closed


def test_save_logging_file_restores_streams_on_exception(tmp_path: Path) -> None:
    log_path = tmp_path / "run.log"

    try:
        with save_logging_file(str(log_path)):
            raise RuntimeError("boom")
    except RuntimeError:
        pass

    assert sys.stdout is log_helper._stdout_original
    assert log_helper._tee_depth == 0
