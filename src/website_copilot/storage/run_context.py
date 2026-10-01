"""共用 workflow helper 函式。

提供 pipelines.prepare／pipelines.serve／pipelines.exp 各 run_* 工作流程共用的
初始化與 logging 樣板。僅依賴 RunManager / config / log 工具，不依賴各流程模組，
避免循環匯入；也不 import 任何引擎，serve 階段可安全使用。
"""

import os
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager

from website_copilot.config.base_config import BaseModuleConfig
from website_copilot.storage.run_manager import RunManager
from website_copilot.utils.log_helper import (
    log_run_time,
    log_session,
    save_logging_file,
)


def create_run_context(
    module: str,
    config_name: str,
    site_id: str,
    config: BaseModuleConfig,
    run_name_use_config_name: bool = False,
    save: bool = True,
) -> tuple[RunManager | None, str]:
    """共用初始化：建立 runs/<ts>/<module>/<site_id>/<run_name>/ 的 RunManager 與 run_title。

    save=False 時完全不建立 RunManager（也就不會在 runs/ 底下建立任何目錄）。

    Returns:
        (RunManager | None, run_title)。
    """
    run_title = f"{module.replace('_', ' ').title()} ({site_id}, {config_name})"
    if not save:
        return None, run_title

    run_name = config.config_name if run_name_use_config_name else config.run_name
    run_manager = RunManager.for_run(
        module=module,
        site_id=site_id,
        run_name=run_name,
    )
    return run_manager, run_title


def create_run_no_site_context(
    module: str,
    config_name: str,
    run_name: str | None = None,
    base_folder: str = "runs",
) -> tuple[RunManager, str]:
    """建立不需要 site_id 的 RunManager 與 run title。"""
    run_title = f"{module.replace('_', ' ').title()} ({config_name})"
    run_manager = RunManager.for_run_no_site(
        module=module,
        run_name=run_name or config_name,
        base_folder=base_folder,
    )
    return run_manager, run_title


class _WorkflowContext:
    """Wraps ExitStack + optional run_manager lifecycle."""

    def __init__(self, stack: ExitStack, run_manager: RunManager | None) -> None:
        self._stack = stack
        self._run_manager = run_manager

    def __enter__(self) -> "_WorkflowContext":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if self._run_manager is not None and exc_type is None:
                self._run_manager.log_run_paths("complete")
        finally:
            self._stack.__exit__(exc_type, exc_val, exc_tb)


@contextmanager
def publish_log_file(run_manager: RunManager | None, publish: bool) -> Iterator[str]:
    """回傳發布時要複製的 terminal.log 路徑；publish-only 模式用暫存檔，離開時刪除。

    - run_manager 存在（save=True）：回傳 run 的 terminal.log，不建立暫存檔。
    - run_manager 為 None 且 publish=True：在系統暫存資料夾建立 terminal.log 路徑，
      離開 with 時整個暫存資料夾刪除（log 內容已隨發布複製到 data/）。
    - 兩者皆否（不存 runs/ 也不發布）：回傳空字串，表示不記錄 log 檔。

    呼叫端須在 run_workflow_context 結束之後才複製（log 已關檔並壓縮進度列）。
    """
    if run_manager is not None:
        yield run_manager.log_path
        return
    if not publish:
        yield ""
        return
    folder = tempfile.mkdtemp(prefix="terminal_log_")
    try:
        yield os.path.join(folder, "terminal.log")
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def run_workflow_context(
    run_title: str,
    run_manager: RunManager | None,
    log_path: str = "",
) -> _WorkflowContext:
    """共用 logging preamble context manager。

    取代 run_* 函式中重複的 logging pattern：
    save_logging_file + log_run_time + log_session + run_paths。
    log_config 已移至各呼叫端，不再由本函式處理。
    run_manager 為 None（save=False）時跳過 runs/ 相關操作；此時若指定 log_path
    （publish-only 的暫存 log，見 publish_log_file）仍會把輸出寫進該檔案。
    """
    stack = ExitStack()
    effective_log_path = run_manager.log_path if run_manager is not None else log_path
    if effective_log_path:
        stack.enter_context(save_logging_file(effective_log_path))
    stack.enter_context(log_run_time(run_title))
    log_session(run_title, style="purple")

    if run_manager is not None:
        log_session("Run Paths", style="cyan")
        run_manager.log_run_paths("init")

    return _WorkflowContext(stack, run_manager)
