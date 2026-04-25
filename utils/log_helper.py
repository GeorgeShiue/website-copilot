import logging

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


def setup_logging(level: str = "info") -> None:
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

    if level.lower() == "debug":
        logging.getLogger("app.website_crawler").setLevel(logging.DEBUG)
        logging.getLogger("app.webpage_image_summarizer").setLevel(logging.DEBUG)


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
