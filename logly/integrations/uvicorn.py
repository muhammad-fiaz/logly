"""Uvicorn integration for Logly.

Routes Uvicorn access and error logs through Logly.

Requires ``uvicorn``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[uvicorn]

    # Option 2: pip
    pip install "logly[uvicorn]"

    # Option 3: uv without extras
    uv add uvicorn

    # Option 4: pip without extras
    pip install uvicorn
"""

from __future__ import annotations

import logging
from typing import Any

from logly.integrations.stdlib import InterceptHandler
from logly.logger import logger

_IMPORT_MSG = (
    "uvicorn is required for Logly Uvicorn integration.\n"
    "Install with one of:\n"
    "  uv add logly[uvicorn]       # recommended\n"
    "  pip install logly[uvicorn]\n"
    "  uv add uvicorn\n"
    "  pip install uvicorn"
)


def setup_uvicorn_logging(
    level: str = "INFO",
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    **kwargs: Any,
) -> None:
    """Configure Uvicorn logging to use Logly.

    Use this with uvicorn's ``--log-config`` option or in code::

        import uvicorn
        from logly.integrations.uvicorn import setup_uvicorn_logging

        setup_uvicorn_logging()
        uvicorn.run("app:app")

    Or pass as log_config::

        import uvicorn
        from logly.integrations.uvicorn import get_log_config

        uvicorn.run("app:app", log_config=get_log_config())

    Args:
        level: Minimum log level (default ``"INFO"``).
        format: Log format string.
        **kwargs: Additional arguments passed to ``logger.add()``.

    Raises:
        ImportError: If ``uvicorn`` is not installed.
    """
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        log = logging.getLogger(name)
        log.handlers = [InterceptHandler()]
        log.setLevel(getattr(logging, level.upper(), logging.INFO))
        log.propagate = False

    # Configure logly with the format
    logger.add(
        "stderr",
        level=level,
        format=format,
        **kwargs,
    )


def get_log_config(level: str = "INFO") -> dict[str, Any]:
    """Return a uvicorn-compatible log config dict using Logly.

    Usage::

        import uvicorn
        from logly.integrations.uvicorn import get_log_config

        uvicorn.run("app:app", log_config=get_log_config())

    Args:
        level: Minimum log level (default ``"INFO"``).

    Returns:
        A dict suitable for ``uvicorn.run(log_config=...)``.

    Raises:
        ImportError: If ``uvicorn`` is not installed.
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "logly": {
                "()": "logly.integrations.uvicorn._UvicornFormatter",
            },
        },
        "handlers": {
            "logly": {
                "class": "logly.integrations.uvicorn._UvicornHandler",
                "level": level,
                "formatter": "logly",
            },
        },
        "root": {
            "level": level,
            "handlers": ["logly"],
        },
        "loggers": {
            "uvicorn": {"level": level, "handlers": ["logly"], "propagate": False},
            "uvicorn.error": {"level": level, "handlers": ["logly"], "propagate": False},
            "uvicorn.access": {"level": level, "handlers": ["logly"], "propagate": False},
        },
    }


class _UvicornFormatter(logging.Formatter):
    """Formatter that passes messages through to Logly.

    This formatter simply returns the raw message, allowing Logly
    to handle all formatting.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record by returning its message.

        Args:
            record: The Python logging record.

        Returns:
            The log message string.
        """
        return record.getMessage()


class _UvicornHandler(logging.Handler):
    """Handler that routes Uvicorn logs through Logly."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record through Logly.

        Args:
            record: The Python logging record to emit.
        """
        try:
            msg = self.format(record)
            level = record.levelname
            logger.opt(depth=1).log(level, msg)
        except Exception:
            self.handleError(record)
