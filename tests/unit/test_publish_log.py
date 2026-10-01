"""publish-only 模式的 terminal.log：暫存 log 的建立／清除，以及發布時內容完整。"""

import os

from website_copilot.storage.data_manager import DataManager
from website_copilot.storage.run_context import (
    publish_log_file,
    run_workflow_context,
)
from website_copilot.storage.run_manager import RunManager


def test_publish_log_file_uses_temp_and_cleans_up() -> None:
    with publish_log_file(None, True) as log_path:
        assert os.path.basename(log_path) == "terminal.log"
        folder = os.path.dirname(log_path)
        assert os.path.isdir(folder)
    assert not os.path.exists(folder)


def test_publish_log_file_without_publish_or_run_manager_is_empty() -> None:
    with publish_log_file(None, False) as log_path:
        assert log_path == ""


def test_publish_log_file_prefers_run_manager_log(tmp_path) -> None:
    run_manager = RunManager.for_run(
        module="m", site_id="s", run_name="r", base_folder=str(tmp_path)
    )
    with publish_log_file(run_manager, True) as log_path:
        assert log_path == run_manager.log_path


def test_published_log_is_complete_after_workflow_context(tmp_path) -> None:
    data_manager = DataManager(base_folder=str(tmp_path / "data"))
    with publish_log_file(None, True) as log_path:
        with run_workflow_context("Demo Run", run_manager=None, log_path=log_path):
            print("hello from workflow")
        # context 結束後才複製：log 已關檔，內容完整
        dest = tmp_path / "data" / "aug_webpages" / "site"
        dest.mkdir(parents=True)
        data_manager._copy_single_file(log_path, str(dest), "terminal.log")

    text = (dest / "terminal.log").read_text(encoding="utf-8")
    assert "Demo Run" in text and "hello from workflow" in text
