"""Celery integration for Logly.

Configures Celery to route all worker task logs through Logly.
"""

from __future__ import annotations

import logging
from typing import Any

from logly.integrations.stdlib import InterceptHandler


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
        level: Minimum log level for Celery logs.
        format: Log format string.
        **kwargs: Additional arguments passed to ``logger.add()``.
    """
    _ = format  # Reserved for future per-handler format customization
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

    Usage::

        @app.task
        def my_task():
            from logly.integrations.celery import patch_task_logger
            patch_task_logger(my_task.get_logger())

    Args:
        task_logger: Celery task logger instance.
        level: Minimum log level (default: ``"INFO"``).
    """
    if hasattr(task_logger, "handlers"):
        task_logger.handlers = [InterceptHandler()]
    if hasattr(task_logger, "setLevel"):
        task_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
