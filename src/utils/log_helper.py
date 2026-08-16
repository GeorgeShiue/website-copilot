import logging
import re
import sys
import time
from contextlib import contextmanager
from logging import Logger
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    ProgressColumn,
    TextColumn,
)
from rich.rule import Rule
from rich.text import Text

# 全域變數用於檔案輸出
_tee_stream: "_TeeStream | None" = None
_logging_path: str | None = None
# 巢狀 save_logging_file 計數器（如 agent 內包 retriever tool）：
# 只有最外層的 with block 結束時才真正還原 stdout/stderr
_tee_depth: int = 0
_stdout_original = sys.stdout
_stderr_original = sys.stderr
ANSI_ESCAPE_PATTERN = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
PROGRESS_LINE_PREFIXES = (
    "Downloading images...",
    "Generating captions...",
)


class _TeeStream:
    """Mirror stdout/stderr writes to both terminal and log file."""

    def __init__(self, terminal_stream, file_stream) -> None:
        self.terminal_stream = terminal_stream
        self.file_stream = file_stream

    def write(self, data: str) -> int:
        self.terminal_stream.write(data)
        # 保留終端彩色輸出，但寫檔時移除 ANSI 控制碼
        try:
            self.file_stream.write(ANSI_ESCAPE_PATTERN.sub("", data))
        except ValueError:
            # 檔案已關閉（如 milvus_lite 在 tee 關閉後才停止輸出）
            pass
        return len(data)

    def flush(self) -> None:
        self.terminal_stream.flush()
        try:
            self.file_stream.flush()
        except ValueError:
            pass

    def isatty(self) -> bool:
        return self.terminal_stream.isatty()


def setup_logging(level: str = "info", logger: Logger | None = None) -> None:
    """Initialize shared Rich logging configuration for app and tests."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            RichHandler(
                show_time=False,
                show_path=False,
                rich_tracebacks=True,
            )
        ],
        force=True,
    )
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)  # * 減少 debug log

    logging_level = logging.INFO
    if level.lower() == "debug":
        logging_level = logging.DEBUG

    logging.getLogger("app.engines.website_crawler").setLevel(logging_level)
    logging.getLogger("app.engines.webpage_image_summarizer").setLevel(logging_level)
    logging.getLogger("app.engines.rag").setLevel(logging_level)

    if logger is not None:
        logger.setLevel(logging_level)


def setup_logging_file(log_file_path: str) -> None:
    """設定終端機輸出和日誌同時保存到檔案."""
    global _tee_stream, _logging_path, _tee_depth

    if _tee_depth > 0:
        # 巢狀呼叫（如 agent 內的 tool 建立）：沿用外層 tee，避免關閉外層記錄
        _tee_depth += 1
        return

    disable_logging_file()
    _logging_path = log_file_path

    # 建立檔案輸出流
    file_stream = open(log_file_path, "a", encoding="utf-8")

    # 捕捉直接寫入 stdout / stderr 的訊息
    _tee_stream = _TeeStream(_stdout_original, file_stream)
    sys.stdout = _tee_stream
    sys.stderr = _tee_stream
    _tee_depth = 1


def _is_target_progress_line(line: str) -> bool:
    """Whether the line is one of the progress outputs to be collapsed."""
    stripped = line.lstrip()
    return stripped.startswith(PROGRESS_LINE_PREFIXES)


def _collapse_adjacent_progress_lines(log_file_path: str) -> None:
    """Keep only the last line for each adjacent progress-line block."""
    log_path = Path(log_file_path)
    if not log_path.exists():
        return

    original_lines = log_path.read_text(encoding="utf-8").splitlines(keepends=True)
    collapsed_lines: list[str] = []

    idx = 0
    while idx < len(original_lines):
        current_line = original_lines[idx]
        if not _is_target_progress_line(current_line):
            collapsed_lines.append(current_line)
            idx += 1
            continue

        block_last_line = current_line
        idx += 1
        while idx < len(original_lines) and _is_target_progress_line(
            original_lines[idx]
        ):
            block_last_line = original_lines[idx]
            idx += 1

        collapsed_lines.append(block_last_line)

    if collapsed_lines != original_lines:
        log_path.write_text("".join(collapsed_lines), encoding="utf-8")


@contextmanager
def save_logging_file(log_file_path: str):
    """Context manager for setup/teardown of run-specific file logging.

    支援巢狀呼叫（如 agent 內包 retriever tool 建立）：內層 with block
    結束時沿用外層 tee，只有最外層結束才還原 stdout/stderr。
    """
    setup_logging_file(log_file_path)
    try:
        yield
    finally:
        disable_logging_file()
        _collapse_adjacent_progress_lines(log_file_path)


def disable_logging_file() -> None:
    """Restore streams and close previous file logging resources."""
    global _tee_stream, _tee_depth

    if _tee_depth == 0:
        return

    _tee_depth -= 1
    if _tee_depth > 0:
        # 內層結束：保留外層 tee
        return

    sys.stdout = _stdout_original
    sys.stderr = _stderr_original

    # 根治：將仍引用 tee 的 logging handler（如 milvus_lite 啟動時
    # 捕捉 sys.stdout 的 StreamHandler）替換為原始 stdout，
    # 避免 tee 關閉後 logger 寫入已關閉的檔案
    _detach_handlers_from_tee()

    if _tee_stream is not None:
        _tee_stream.file_stream.close()
        _tee_stream = None


def _detach_handlers_from_tee() -> None:
    """將所有 logger 中 stream 仍指向 tee 的 handler 替換為原始 stdout（內部使用）。"""
    if _tee_stream is None:
        return

    def _detach(handler: logging.Handler) -> None:
        if isinstance(handler, logging.StreamHandler):
            stream = getattr(handler, "stream", None)
            if stream is _tee_stream:
                handler.stream = _stdout_original

    for handler in logging.getLogger().handlers:
        _detach(handler)
    for logger in logging.Logger.manager.loggerDict.values():
        if isinstance(logger, logging.Logger):
            for handler in logger.handlers:
                _detach(handler)


@contextmanager
def log_run_time(title: str = ""):
    """Context manager that logs elapsed run time in finally block."""
    start_time = time.perf_counter()
    try:
        yield
    finally:
        elapsed_seconds = time.perf_counter() - start_time
        message = f"Completed in {elapsed_seconds:.3f} seconds"
        if title:
            message = f"{title} {message}"
        logging.getLogger(__name__).info(message)


def _get_logging_console() -> Console:
    """Get the Rich console used by current logging handlers (internal use)."""
    root_logger = logging.getLogger()

    for handler in root_logger.handlers:
        if isinstance(handler, RichHandler):
            return handler.console

    return Console()


def print_log(content: object) -> None:
    """Get logging console and print content directly."""
    console = _get_logging_console()
    console.print(content)


def log_session(title: str, style: str) -> None:
    """Log a visually distinct section header for a module session using Rich styling."""
    print_log(Rule(f"[bold {style}]{title}[/bold {style}]", style=style))


def log_source_title(page_title, score, page_type):
    parts = [
        f"[bold green]Page: {page_title}[/bold green]",
        f"[bold yellow]Score: {score:0.3f}[/bold yellow]",
        f"[bold cyan]Type: {page_type}[/bold cyan]",
    ]
    print_log(Rule("  [dim white]|[/dim white]  ".join(parts), style="blue"))


class FlexibleTimeElapsedColumn(ProgressColumn):
    def render(self, task) -> Text:
        default_time_text = "-:--:--"
        elapsed = task.finished_time if task.finished else task.elapsed
        if elapsed is None:
            return Text(default_time_text, style="progress.elapsed")

        # * 自訂：顯示格式為 MM:SS.mmm
        minutes, seconds = divmod(elapsed, 60)
        hours, minutes = divmod(int(minutes), 60)

        time_text = default_time_text
        if hours > 0:
            time_text = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
        elif minutes > 0:
            time_text = f"{minutes:02d}:{seconds:06.3f}"
        elif seconds >= 10:
            time_text = f"{seconds:06.3f}s"
        else:
            time_text = f"{seconds:05.3f}s"

        return Text(time_text, style="progress.elapsed")


class TaskCountProgress(Progress):
    """Shared progress template: description + bar + completed/total + elapsed."""

    def __init__(self, **kwargs) -> None:
        super().__init__(
            TextColumn("[yellow]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            FlexibleTimeElapsedColumn(),
            **kwargs,
        )
