"""PropagateHandler - bridges Logly messages back to stdlib logging.

Use this when you want Logly's logger to forward messages to Python's
standard ``logging`` module, for example to feed into existing monitoring
or log aggregation tools that hook into stdlib logging.

Install with::

    # Option 1: uv (recommended)
    uv add logly

    # Option 2: pip
    pip install logly
"""

from __future__ import annotations

import logging


class PropagateHandler(logging.Handler):
    """A ``logging.Handler`` that routes Logly records into stdlib logging.

    This handler acts as a bridge from Logly to Python's standard logging
    system. It implements the ``write()`` interface expected by Logly's
    sink API, so it can be added via ``logger.add()``.

    Usage::

        from logly import logger
        from logly.integrations.propagate import PropagateHandler

        logger.add(PropagateHandler(), format="{message}")

    Any message logged through Logly will be emitted via the root logger
    (or the logger specified by ``name``).

    Args:
        name: Name of the stdlib logger to emit to (default ``"logly"``).
        level: Logging level threshold (default ``NOTSET``).
    """

    def __init__(self, name: str = "logly", level: int = logging.NOTSET) -> None:
        """Initialize the propagate handler.

        Args:
            name: Name of the stdlib logger to emit to.
            level: Logging level threshold.
        """
        super().__init__(level=level)
        self._logger = logging.getLogger(name)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a stdlib log record (no-op, this is a destination, not a source).

        Args:
            record: The log record (unused).
        """

    def write(self, message: str) -> None:
        """Write a formatted Logly message to stdlib logging.

        The log level is inferred from the message content (e.g., messages
        containing "ERROR" are emitted at ERROR level).

        Args:
            message: The formatted log line from Logly.
        """
        # Determine stdlib level from Logly level prefix
        level = logging.INFO
        upper = message.upper()
        if "TRACE" in upper or "DEBUG" in upper:
            level = logging.DEBUG
        elif "NOTICE" in upper:
            level = logging.INFO
        elif "SUCCESS" in upper:
            level = logging.INFO
        elif "WARNING" in upper or "WARN" in upper:
            level = logging.WARNING
        elif "ERROR" in upper or "FAIL" in upper:
            level = logging.ERROR
        elif "CRITICAL" in upper or "FATAL" in upper:
            level = logging.CRITICAL

        self._logger.log(level, message.rstrip())

    def flush(self) -> None:
        """Flush is a no-op for stdlib logging."""
