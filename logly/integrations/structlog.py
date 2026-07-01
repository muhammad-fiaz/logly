"""structlog integration for Logly.

Provides ``logly_processor`` and ``LoglyRenderer`` to bridge structlog with Logly.

Requires ``structlog``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[structlog]

    # Option 2: pip
    pip install "logly[structlog]"

    # Option 3: uv without extras
    uv add structlog

    # Option 4: pip without extras
    pip install structlog
"""

from __future__ import annotations

from typing import Any

from logly import logger

_IMPORT_MSG = (
    "structlog is required for Logly structlog integration.\n"
    "Install with one of:\n"
    "  uv add logly[structlog]       # recommended\n"
    "  pip install logly[structlog]\n"
    "  uv add structlog\n"
    "  pip install structlog"
)


def _check_structlog() -> None:
    """Verify that structlog is installed.

    Raises:
        ImportError: If ``structlog`` is not installed.
    """
    try:
        import structlog  # noqa: F401
    except ImportError:
        raise ImportError(_IMPORT_MSG) from None


def logly_processor(
    logger_name: str | None = None,
    wrapper_class: Any = None,
    **kwargs: Any,
) -> list[Any]:
    """Create a structlog processor chain that routes to Logly.

    Returns a list of standard structlog processors plus a final processor
    that forwards all events to Logly's logger. The chain includes
    ``merge_contextvars``, ``add_log_level``, and ``TimeStamper``.

    Usage::

        import structlog
        from logly.integrations.structlog import logly_processor

        structlog.configure(
            processors=logly_processor(),
            logger_factory=structlog.PrintLoggerFactory(),
        )
        log = structlog.get_logger()
        log.info("hello", key="value")

    Args:
        logger_name: Optional logger name to bind to Logly context.
        wrapper_class: Optional structlog wrapper class (unused, kept for
            API compatibility).
        **kwargs: Additional keyword arguments (unused).

    Returns:
        List of structlog processors including a Logly sink processor.
    """
    _check_structlog()
    import structlog

    def _logly_sink(
        logger_name: str | None,
        event_method: str,
        event_dict: dict[str, Any],
    ) -> dict[str, Any]:
        level = event_method.upper()
        message = event_dict.pop("event", "")
        extra = {k: str(v) for k, v in event_dict.items() if k != "level"}

        bound = logger.bind(**extra) if extra else logger
        if logger_name:
            bound = bound.bind(logger_name=logger_name)

        bound.log(level, str(message))
        return event_dict

    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        _logly_sink,
    ]

    return processors


class LoglyRenderer:
    """structlog renderer that outputs through Logly.

    A callable class that can be used as a structlog processor to forward
    all log events to Logly's native logger.

    Usage::

        import structlog
        from logly.integrations.structlog import LoglyRenderer

        structlog.configure(
            processors=[structlog.processors.add_log_level, LoglyRenderer()],
            logger_factory=structlog.PrintLoggerFactory(),
            wrapper_class=structlog.BoundLogger,
        )

    Args:
        level: Minimum log level (default ``"INFO"``).
        **kwargs: Additional keyword arguments (unused).
    """

    def __init__(self, level: str = "INFO", **kwargs: Any) -> None:
        """Initialize the structlog renderer.

        Args:
            level: Minimum log level.
            **kwargs: Additional keyword arguments.
        """
        _check_structlog()
        self._level = level
        self._kwargs = kwargs

    def __call__(
        self, logger_name: str | None, method_name: str, event_dict: dict[str, Any]
    ) -> None:
        """Render a structlog event through Logly.

        Args:
            logger_name: Optional logger name.
            method_name: Log method name (e.g. ``"info"``).
            event_dict: Structlog event dictionary.
        """
        level = method_name.upper()
        message = event_dict.pop("event", "")
        extra = {k: str(v) for k, v in event_dict.items() if k != "level"}

        bound = logger.bind(**extra) if extra else logger
        bound.log(level, str(message))
