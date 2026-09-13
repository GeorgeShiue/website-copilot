"""共用 workflow helper 函式。

自 workflow.py 拆分而出，提供各 run_* 工作流程共用的初始化與 logging 樣板，
以及 RAG 建構流程。僅依賴 RunManager / DataManager / config / log 工具，
不依賴 workflow.py，避免循環匯入。
"""

from contextlib import ExitStack

from app.configs.rag_config import RAGConfig
from app.configs.webpage_image_summarizer_config import WebpageImageSummarizerConfig
from app.configs.website_crawler_config import WebsiteCrawlerConfig
from app.workflow.run_manager import RunManager
from utils.log_helper import log_run_time, log_session, save_logging_file

# create_run_context 需要 site_id 欄位，但 BaseModuleConfig 未宣告（由使用 site 的
# 子類自行宣告），故以實際呼叫端的模組 config 聯集標註。
SiteModuleConfig = RAGConfig | WebsiteCrawlerConfig | WebpageImageSummarizerConfig


def create_run_context(
    module: str,
    config_name: str,
    config: SiteModuleConfig,
    run_name_use_config_name: bool = False,
) -> tuple[RunManager, str]:
    """共用初始化：建立 RunManager 與 run_title。

    Returns:
        (RunManager, run_title)。
    """
    run_name = config.config_name if run_name_use_config_name else config.run_name
    run_manager = RunManager.for_run(
        module=module,
        site_id=config.site_id,
        run_name=run_name,
    )
    run_title = f"{module.replace('_', ' ').title()} ({config_name})"
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


def run_workflow_context(
    run_title: str,
    run_manager: RunManager,
) -> _WorkflowContext:
    """共用 logging preamble context manager。

    取代 run_* 函式中重複的 logging pattern：
    save_logging_file + log_run_time + log_session + run_paths。
    log_config 已移至各呼叫端，不再由本函式處理。
    """
    stack = ExitStack()
    stack.enter_context(save_logging_file(run_manager.log_path))
    stack.enter_context(log_run_time(run_title))
    log_session(run_title, style="purple")

    log_session("Run Paths", style="cyan")
    run_manager.log_run_paths("init")

    return _WorkflowContext(stack, run_manager)
