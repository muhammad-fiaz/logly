"""Rich console integration.

Provides ``LoglyRichSink`` for beautiful console output using Rich,
and ``RichHandler`` for seamless integration with Python's stdlib logging.

Requires ``rich``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[rich]

    # Option 2: pip
    pip install "logly[rich]"

    # Option 3: uv without extras
    uv add rich

    # Option 4: pip without extras
    pip install rich
"""

from __future__ import annotations

import sys
from typing import Any

_IMPORT_MSG = (
    "rich is required for LoglyRichSink.\n"
    "Install with one of:\n"
    "  uv add logly[rich]       # recommended\n"
    "  pip install logly[rich]\n"
    "  uv add rich\n"
    "  pip install rich"
)


class LoglyRichSink:
    """Write-style sink using Rich for formatted console output.

    Usage::

        from logly import logger
        from logly.integrations.rich import LoglyRichSink

        # Method 1: Using the Rich sink class
        logger.add(LoglyRichSink(), colorize=True)
        logger.info("Rich-formatted output!")

        # Method 2: Using Rich's Console.print directly
        from rich.console import Console

        console = Console()
        logger.add(console.print, colorize=True, format="{message}")
        logger.info("Hello World")
        logger.success("Operation completed")
        logger.warning("Disk almost full")
        logger.error("Something failed")
    """

    def __init__(self, file: Any = None, **kwargs: Any) -> None:
        """Initialize the Rich sink.

        Args:
            file: Output file object (default: ``sys.stderr``).
            **kwargs: Additional arguments passed to ``rich.console.Console``.

        Raises:
            ImportError: If ``rich`` is not installed.
        """
        try:
            from rich.console import Console
            from rich.text import Text
        except ImportError:
            raise ImportError(_IMPORT_MSG) from None

        self._console: Any = Console(file=file or sys.stderr, **kwargs)
        self._text_class: Any = Text

    def write(self, message: str) -> None:
        """Write-style sink interface."""
        msg = message.rstrip("\n")
        if msg:
            try:
                self._console.print(
                    self._text_class(msg, no_wrap=True),
                    highlight=False,
                    end="",
                )
            except Exception:
                self._console.print(msg, end="", highlight=False)

    def flush(self) -> None:
        """Flush the Rich console."""
        self._console.file.flush()


RichSink = LoglyRichSink


class RichHandler:
    """stdlib ``logging.Handler`` that routes logs through Rich.

    Usage::

        import logging
        from logly.integrations.rich import RichHandler

        logging.basicConfig(handlers=[RichHandler()], level=logging.INFO)
        logging.getLogger("uvicorn").info("Routed through Rich!")
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the Rich handler.

        Args:
            *args: Positional arguments passed to ``rich.logging.RichHandler``.
            **kwargs: Keyword arguments passed to ``rich.logging.RichHandler``.

        Raises:
            ImportError: If ``rich`` is not installed.
        """
        try:
            from rich.logging import RichHandler as _RichHandler
        except ImportError:
            raise ImportError(_IMPORT_MSG) from None

        self._handler: Any = _RichHandler(*args, **kwargs)

    def emit(self, record: Any) -> None:
        """Emit a log record through Rich."""
        self._handler.emit(record)

    def flush(self) -> None:
        """Flush the Rich handler."""
        if hasattr(self._handler, "flush"):
            self._handler.flush()
