"""Gunicorn integration for Logly.

Provides ``LoglyWorker`` for Gunicorn sync/async worker processes.

Requires ``gunicorn``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[gunicorn]

    # Option 2: pip
    pip install "logly[gunicorn]"

    # Option 3: uv without extras
    uv add gunicorn

    # Option 4: pip without extras
    pip install gunicorn
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from logly import logger

_IMPORT_MSG = (  # pragma: no cover
    "gunicorn is required for LoglyWorker.\n"
    "Install with one of:\n"
    "  uv add logly[gunicorn]       # recommended\n"
    "  pip install logly[gunicorn]\n"
    "  uv add gunicorn\n"
    "  pip install gunicorn"
)  # pragma: no cover


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


class _GunicornHandler(logging.Handler):
    """Route gunicorn logs through Logly."""

    def emit(self, record: logging.LogRecord | None) -> None:
        if record is None:
            return
        try:
            level = _resolve_level(record)
        except Exception:
            level = record.levelname.upper()

        exc: BaseException | None = None
        if record.exc_info and record.exc_info[1] is not None:
            exc = record.exc_info[1]

        logger.opt(exception=exc).log(level, record.getMessage())

    def handleError(self, record: logging.LogRecord | None) -> None:  # noqa: N802
        if sys.stderr is not None:
            try:
                print("Logly GunicornHandler error:", file=sys.stderr)  # noqa: T201
            except Exception:
                pass


def setup_gunicorn_logging(
    level: str = "INFO",
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    **kwargs: Any,
) -> None:
    """Configure Gunicorn logging to use Logly.

    Call this in your Gunicorn config file::

        # gunicorn.conf.py
        from logly.integrations.gunicorn import setup_gunicorn_logging
        setup_gunicorn_logging()

    Args:
        level: Minimum log level for Gunicorn logs.
        format: Log format string.
        **kwargs: Additional arguments passed to ``logger.add()``.
    """
    _ = format
    for name in ("gunicorn", "gunicorn.error", "gunicorn.access"):
        log = logging.getLogger(name)
        log.handlers = [_GunicornHandler()]
        log.setLevel(getattr(logging, level.upper(), logging.INFO))
        log.propagate = False

    logger.add("stderr", level=level, **kwargs)


class LoglyWorker:
    """Gunicorn worker class that routes logs through Logly.

    Usage::

        # gunicorn.conf.py
        worker_class = "logly.integrations.gunicorn.LoglyWorker"
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the Logly Gunicorn worker.

        Args:
            *args: Positional arguments passed to ``SyncWorker``.
            **kwargs: Keyword arguments passed to ``SyncWorker``.

        Raises:
            ImportError: If ``gunicorn`` is not installed.
        """
        try:
            from gunicorn.workers.sync import SyncWorker  # pragma: no cover
        except ImportError:
            raise ImportError(_IMPORT_MSG) from None  # pragma: no cover

        setup_gunicorn_logging()
        self._worker = SyncWorker(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        """Proxy attribute access to the underlying SyncWorker.

        Args:
            name: Attribute name to access.

        Returns:
            The attribute value from the SyncWorker.
        """
        return getattr(self._worker, name)
