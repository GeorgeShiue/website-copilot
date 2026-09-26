"""Shared test helpers for dev tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unittest.mock import MagicMock


def mock_exit_delegates_to_real(
    mock_exit: MagicMock,
    mock_registry_instance: MagicMock,
) -> None:
    """Configure mock __exit__ to delegate to real implementation (calls close(), returns False)."""

    def _handler(exc_type, exc_val, exc_tb):
        if exc_type is not None:
            import logging

            logging.getLogger(__name__).error(
                "Exception in context: %s",
                exc_val,
                exc_info=(exc_type, exc_val, exc_tb),
            )
        mock_registry_instance.close()
        return False

    mock_exit.side_effect = _handler
