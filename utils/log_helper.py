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
        self.file_stream.write(ANSI_ESCAPE_PATTERN.sub("", data))
        return len(data)

    def flush(self) -> None:
        self.terminal_stream.flush()
        self.file_stream.flush()

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

    logging.getLogger("app.modules.website_crawler").setLevel(logging_level)
    logging.getLogger("app.modules.webpage_image_summarizer").setLevel(logging_level)
    logging.getLogger("app.modules.rag").setLevel(logging_level)

    if logger is not None:
        logger.setLevel(logging_level)


def setup_logging_file(log_file_path: str) -> None:
    """設定終端機輸出和日誌同時保存到檔案."""
    global _tee_stream, _logging_path

    disable_logging_file()
    _logging_path = log_file_path

    # 建立檔案輸出流
    file_stream = open(log_file_path, "a", encoding="utf-8")

    # 捕捉直接寫入 stdout / stderr 的訊息
    _tee_stream = _TeeStream(_stdout_original, file_stream)
    sys.stdout = _tee_stream
    sys.stderr = _tee_stream


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
    """Context manager for setup/teardown of run-specific file logging."""
    setup_logging_file(log_file_path)
    try:
        yield
    finally:
        disable_logging_file()
        _collapse_adjacent_progress_lines(log_file_path)


def disable_logging_file() -> None:
    """Restore streams and close previous file logging resources."""
    global _tee_stream

    sys.stdout = _stdout_original
    sys.stderr = _stderr_original

    if _tee_stream is not None:
        _tee_stream.file_stream.close()
        _tee_stream = None


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
