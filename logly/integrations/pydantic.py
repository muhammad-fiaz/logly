"""Pydantic integration for Logly.

Provides ``PydanticLogHandler`` and ``LoglyFormatter`` for Pydantic-based
applications that use Python's ``logging`` module.

No extra dependencies required - uses only the Python standard library.
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logly.logger import Logger

from logly import logger


def _resolve_level(record: logging.LogRecord) -> str:
    """Resolve a Python logging record to a Logly level name.

    Args:
        record: The Python logging record.

    Returns:
        Logly level name string.
    """
    stdlib_map: dict[int, str] = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
    }
    return stdlib_map.get(record.levelno, record.levelname.upper())


class PydanticLogHandler(logging.Handler):
    """Route Python logging records through Logly for Pydantic apps.

    A logging handler that forwards all log records to Logly's intercept
    handler, suitable for use in Pydantic models and services.

    Usage::

        import logging
        from logly.integrations.pydantic import PydanticLogHandler

        handler = PydanticLogHandler()
        handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(handler)

    Or attach to a specific logger::

        logger = logging.getLogger("pydantic")
        logger.addHandler(PydanticLogHandler())
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record through Logly.

        Args:
            record: The Python logging record to emit.
        """
        try:
            level = _resolve_level(record)
        except Exception:
            level = record.levelname.upper()

        exc: BaseException | None = None
        if record.exc_info and record.exc_info[1] is not None:
            exc = record.exc_info[1]

        logger.opt(exception=exc).log(level, record.getMessage())

    def handleError(self, record: logging.LogRecord) -> None:  # noqa: N802
        """Prevent logging errors from causing recursive failures.

        Args:
            record: The log record that caused the error (unused).
        """
        if sys.stderr is not None:
            try:
                print("Logly PydanticLogHandler error:", file=sys.stderr)  # noqa: T201
            except Exception:
                pass


class LoglyFormatter:
    """A Pydantic-compatible log formatter backed by Logly.

    Formats Python logging records into strings using Logly's logger.

    Usage::

        import logging
        from logly.integrations.pydantic import LoglyFormatter

        handler = logging.StreamHandler()
        handler.setFormatter(LoglyFormatter())
        logging.getLogger().addHandler(handler)

    Args:
        logly_logger: Optional Logly logger instance. Uses the global
            ``logly.logger`` if not provided.
    """

    def __init__(self, logly_logger: Logger | None = None) -> None:
        """Initialize the formatter.

        Args:
            logly_logger: Optional Logly logger instance. Uses the global
                ``logly.logger`` if not provided.
        """
        self._logger: Logger = logly_logger or logger

    def format(self, record: logging.LogRecord) -> str:
        """Format a logging record into a string.

        Args:
            record: The Python logging record to format.

        Returns:
            The formatted log message string.
        """
        try:
            level = _resolve_level(record)
        except Exception:
            level = record.levelname.upper()

        exc: BaseException | None = None
        if record.exc_info and record.exc_info[1] is not None:
            exc = record.exc_info[1]

        self._logger.opt(exception=exc).log(level, record.getMessage())
        return record.getMessage()
