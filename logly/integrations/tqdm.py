"""tqdm integration for Logly.

Provides ``TqdmSink`` that redirects log output through tqdm progress bars,
preventing log messages from interfering with active progress bars.

Requires ``tqdm``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[tqdm]

    # Option 2: pip
    pip install "logly[tqdm]"

    # Option 3: uv without extras
    uv add tqdm

    # Option 4: pip without extras
    pip install tqdm
"""

from __future__ import annotations

import importlib.util
from typing import Any

_IMPORT_MSG = (
    "tqdm is required for Logly tqdm integration.\n"
    "Install with one of:\n"
    "  uv add logly[tqdm]       # recommended\n"
    "  pip install logly[tqdm]\n"
    "  uv add tqdm\n"
    "  pip install tqdm"
)


class TqdmSink:
    """Send log output through tqdm progress bars.

    Wraps ``tqdm.write()`` so log messages don't interfere with
    active progress bars. Works exactly like Loguru's tqdm integration.

    Usage::

        from logly import logger
        from logly.integrations.tqdm import TqdmSink
        from tqdm import tqdm
        import time

        logger.remove()
        logger.add(TqdmSink(), colorize=True)

        for i in tqdm(range(100)):
            if i % 20 == 0:
                logger.info("Processing item {}", i)
            time.sleep(0.05)

    Args:
        tqdm_instance: Optional ``tqdm`` class or instance. If ``None``,
            uses ``tqdm.tqdm`` automatically.

    Raises:
        ImportError: If ``tqdm`` is not installed.
    """

    def __init__(self, tqdm_instance: Any = None) -> None:
        """Initialize the tqdm sink.

        Args:
            tqdm_instance: Optional ``tqdm`` class or instance.

        Raises:
            ImportError: If ``tqdm`` is not installed.
        """
        if importlib.util.find_spec("tqdm") is None:
            raise ImportError(_IMPORT_MSG)

        if tqdm_instance is not None:
            self._tqdm = tqdm_instance
        else:
            import tqdm as _tqdm  # noqa: PLC0415

            self._tqdm = _tqdm

    def write(self, message: str) -> None:
        """Write a log message through tqdm.

        Uses ``tqdm.write()`` to safely output log messages without
        breaking progress bar display.

        Args:
            message: The formatted log message to send.
        """
        self._tqdm.write(message.rstrip("\n"))

    def flush(self) -> None:
        """Flush tqdm output (no-op, tqdm handles this internally)."""

    def close(self) -> None:
        """No-op for tqdm sink."""
