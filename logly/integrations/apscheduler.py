"""APScheduler integration for Logly.

Provides ``APSchedulerHandler`` that routes APScheduler job logs through Logly.

Requires ``apscheduler``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[apscheduler]

    # Option 2: pip
    pip install "logly[apscheduler]"

    # Option 3: uv without extras
    uv add apscheduler

    # Option 4: pip without extras
    pip install apscheduler
"""

from __future__ import annotations

import logging
import sys

from logly import logger

_IMPORT_MSG = (
    "apscheduler is required for Logly APScheduler integration.\n"
    "Install with one of:\n"
    "  uv add logly[apscheduler]       # recommended\n"
    "  pip install logly[apscheduler]\n"
    "  uv add apscheduler\n"
    "  pip install apscheduler"
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


class APSchedulerHandler(logging.Handler):
    """Route APScheduler logging records through Logly.

    Usage::

        import logging
        from logly.integrations.apscheduler import APSchedulerHandler

        handler = APSchedulerHandler()
        logging.getLogger("apscheduler").addHandler(handler)

    Or configure it on the scheduler directly::

        from apscheduler.schedulers.background import BackgroundScheduler
        from logly.integrations.apscheduler import APSchedulerHandler

        scheduler = BackgroundScheduler()
        scheduler.add_listener(APSchedulerHandler())

    No extra dependencies required beyond APScheduler itself.
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
                sys.stderr.write("Logly APSchedulerHandler error:\n")
            except Exception:
                pass


def setup_apscheduler_logging(level: str = "INFO") -> None:
    """Configure APScheduler to use Logly for logging.

    Usage::

        from logly.integrations.apscheduler import setup_apscheduler_logging
        setup_apscheduler_logging()

    Args:
        level: Minimum log level for APScheduler logs.
    """
    import logging

    ap_logger = logging.getLogger("apscheduler")
    ap_logger.handlers = [APSchedulerHandler()]
    ap_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    ap_logger.propagate = False
