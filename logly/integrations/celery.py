"""Celery integration for Logly.

Configures Celery to route all worker task logs through Logly.

Requires ``celery``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[celery]

    # Option 2: pip
    pip install "logly[celery]"

    # Option 3: uv without extras
    uv add celery

    # Option 4: pip without extras
    pip install celery
"""

from __future__ import annotations

import logging
from typing import Any

from logly.integrations.stdlib import InterceptHandler

_IMPORT_MSG = (  # pragma: no cover
    "celery is required for Logly Celery integration.\n"
    "Install with one of:\n"
    "  uv add logly[celery]       # recommended\n"
    "  pip install logly[celery]\n"
    "  uv add celery\n"
    "  pip install celery"
)  # pragma: no cover


def setup_celery_logging(
    level: str = "INFO",
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    **kwargs: Any,
) -> None:
    """Configure Celery logging to use Logly.

    Call this in your Celery app's ``on_after_configure`` signal::

        from celery import Celery
        from logly.integrations.celery import setup_celery_logging

        app = Celery("myapp")
        app.conf.on_after_configure.connect(setup_celery_logging)

    Args:
        level: Minimum log level for Celery logs (default ``"INFO"``).
        format: Log format string (unused, kept for API compatibility).
        **kwargs: Additional arguments passed to ``logger.add()``.

    Raises:
        ImportError: If ``celery`` is not installed.
    """
    _ = (format, kwargs)
    # Attach Logly to Celery's root logger
    celery_logger = logging.getLogger("celery")
    celery_logger.handlers = [InterceptHandler()]
    celery_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    celery_logger.propagate = False

    # Also attach to celery.app, celery.task, celery.worker
    for name in ("celery.app", "celery.task", "celery.worker"):
        child = logging.getLogger(name)
        child.handlers = [InterceptHandler()]
        child.setLevel(getattr(logging, level.upper(), logging.INFO))
        child.propagate = False


def patch_task_logger(task_logger: Any, level: str = "INFO") -> None:
    """Patch a Celery task logger to use Logly.

    Replaces all handlers on the given task logger with a Logly
    ``InterceptHandler`` that forwards messages to Logly.

    Usage::

        @app.task
        def my_task():
            from logly.integrations.celery import patch_task_logger
            patch_task_logger(my_task.get_logger())

    Args:
        task_logger: Celery task logger instance.
        level: Minimum log level (default ``"INFO"``).

    Raises:
        ImportError: If ``celery`` is not installed.
    """
    if hasattr(task_logger, "handlers"):
        task_logger.handlers = [InterceptHandler()]
    if hasattr(task_logger, "setLevel"):
        task_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
