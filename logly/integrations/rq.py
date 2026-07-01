"""RQ (Redis Queue) integration for Logly.

Provides ``RQHandler`` that routes RQ worker job logs through Logly.

Requires ``rq``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[rq]

    # Option 2: pip
    pip install "logly[rq]"

    # Option 3: uv without extras
    uv add rq

    # Option 4: pip without extras
    pip install rq
"""

from __future__ import annotations

import logging
import sys

from logly import logger

_IMPORT_MSG = (  # pragma: no cover
    "rq is required for Logly RQ integration.\n"
    "Install with one of:\n"
    "  uv add logly[rq]       # recommended\n"
    "  pip install logly[rq]\n"
    "  uv add rq\n"
    "  pip install rq"
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


class RQHandler(logging.Handler):
    """Route RQ logging records through Logly.

    Usage::

        import logging
        from logly.integrations.rq import RQHandler

        handler = RQHandler()
        logging.getLogger("rq").addHandler(handler)
        logging.getLogger("rq.worker").addHandler(handler)

    No extra dependencies required beyond RQ itself.
    """

    def emit(self, record: logging.LogRecord | None) -> None:
        """Emit a log record.

        Args:
            record: The log record to emit. If ``None``, this is a no-op.
        """
        if record is None:
            return
        try:
            level = _resolve_level(record)
        except Exception:
            level = record.levelname.upper()

        exc: BaseException | None = None
        if record.exc_info and record.exc_info[1] is not None:
            exc = record.exc_info[1]

        try:
            logger.opt(exception=exc).log(level, record.getMessage())
        except Exception:
            pass

    def handleError(self, record: logging.LogRecord | None) -> None:
        """Prevent logging errors from causing recursive failures."""
        if sys.stderr is not None:
            try:
                sys.stderr.write("Logly RQHandler error:\n")
            except Exception:
                pass


def setup_rq_logging(level: str = "INFO") -> None:
    """Configure RQ to use Logly for logging.

    Usage::

        from logly.integrations.rq import setup_rq_logging
        setup_rq_logging()

    Args:
        level: Minimum log level for RQ logs.
    """
    rq_logger = logging.getLogger("rq")
    rq_logger.handlers = [RQHandler()]
    rq_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    rq_logger.propagate = False

    rq_worker_logger = logging.getLogger("rq.worker")
    rq_worker_logger.handlers = [RQHandler()]
    rq_worker_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    rq_worker_logger.propagate = False
