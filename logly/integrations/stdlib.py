"""Stdlib logging integration - route Python logging through Logly.

Provides ``InterceptHandler`` to bridge Python's ``logging`` module with Logly.

No extra dependencies required - uses only the Python standard library.
"""

from __future__ import annotations

import logging
import sys

from logly import logger


def _resolve_level(record: logging.LogRecord) -> str:
    """Resolve a Python logging record to a Logly level name.

    Maps Python's 5 standard levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    to their Logly equivalents. For custom Python levels, passes the
    levelname directly so Logly can resolve it if a matching custom
    level is registered.
    """
    stdlib_map: dict[int, str] = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
    }
    return stdlib_map.get(record.levelno, record.levelname.upper())


class InterceptHandler(logging.Handler):
    """Route Python ``logging`` records through Logly.

    This handler replaces standard logging handlers and forwards all
    log records to Logly for processing and output.

    Usage::

        import logging
        from logly.integrations.stdlib import InterceptHandler

        logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)

    Use with specific loggers::

        import logging
        from logly.integrations.stdlib import InterceptHandler

        uvicorn_logger = logging.getLogger("uvicorn")
        uvicorn_logger.handlers = [InterceptHandler()]

    Or configure via dict::

        LOGGING = {
            "version": 1,
            "handlers": {
                "logly": {
                    "class": "logly.integrations.stdlib.InterceptHandler",
                    "level": "INFO",
                },
            },
            "root": {"handlers": ["logly"], "level": "INFO"},
        }
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

        logger.opt(exception=exc).log(
            level,
            record.getMessage(),
        )

    def handleError(self, record: logging.LogRecord) -> None:  # noqa: N802
        """Prevent logging errors from causing recursive failures.

        Args:
            record: The log record that caused the error (unused).
        """
        if sys.stderr is not None:
            try:
                print("Logly InterceptHandler error:", file=sys.stderr)  # noqa: T201
            except Exception:
                pass
