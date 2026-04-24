import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.rule import Rule


def setup_logging(level: int = logging.INFO) -> None:
    """Initialize shared Rich logging configuration for app and tests."""
    logging.basicConfig(
        level=level,
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
