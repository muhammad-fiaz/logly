"""SQLAlchemy integration for Logly.

Routes SQLAlchemy engine and query logs through Logly.

Requires ``sqlalchemy``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[sqlalchemy]

    # Option 2: pip
    pip install "logly[sqlalchemy]"

    # Option 3: uv without extras
    uv add sqlalchemy

    # Option 4: pip without extras
    pip install sqlalchemy
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from logly import logger

_IMPORT_MSG = (
    "sqlalchemy is required for Logly SQLAlchemy integration.\n"
    "Install with one of:\n"
    "  uv add logly[sqlalchemy]       # recommended\n"
    "  pip install logly[sqlalchemy]\n"
    "  uv add sqlalchemy\n"
    "  pip install sqlalchemy"
)


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


class _SQLAlchemyHandler(logging.Handler):
    """Route SQLAlchemy logs through Logly."""

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
                print("Logly SQLAlchemy handler error:", file=sys.stderr)  # noqa: T201
            except Exception:
                pass


def setup_sqlalchemy_logging(
    level: str = "WARNING",
    echo: bool = False,
    **kwargs: Any,
) -> None:
    """Configure SQLAlchemy logging to use Logly.

    Usage::

        from logly.integrations.sqlalchemy import setup_sqlalchemy_logging
        setup_sqlalchemy_logging(level="INFO", echo=True)

    Args:
        level: Minimum log level for SQLAlchemy logs.
        echo: If True, enable SQL echo on engine creation.
        **kwargs: Additional arguments passed to ``logger.add()``.
    """
    _ = echo
    for name in ("sqlalchemy", "sqlalchemy.engine", "sqlalchemy.dialects"):
        log = logging.getLogger(name)
        log.handlers = [_SQLAlchemyHandler()]
        log.setLevel(getattr(logging, level.upper(), logging.WARNING))
        log.propagate = False

    logger.add("stderr", level=level, **kwargs)


def patch_engine(engine: Any, level: str = "INFO") -> None:
    """Patch a SQLAlchemy engine to log queries through Logly.

    Usage::

        from sqlalchemy import create_engine
        from logly.integrations.sqlalchemy import patch_engine

        engine = create_engine("sqlite:///db.sqlite3")
        patch_engine(engine, level="DEBUG")

    Args:
        engine: SQLAlchemy engine instance.
        level: Log level for SQL queries.
    """
    try:
        import logging as _logging

        engine_logger = _logging.getLogger("sqlalchemy.engine")
        engine_logger.setLevel(getattr(_logging, level.upper(), _logging.INFO))
        engine_logger.handlers = [_SQLAlchemyHandler()]
        engine_logger.propagate = False
        engine.echo = True
    except Exception:
        pass
