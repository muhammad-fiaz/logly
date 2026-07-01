"""Sentry integration for Logly.

Provides ``SentrySink`` that captures error events to Sentry.

Requires ``sentry-sdk``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[sentry]

    # Option 2: pip
    pip install "logly[sentry]"

    # Option 3: uv without extras
    uv add sentry-sdk

    # Option 4: pip without extras
    pip install sentry-sdk
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    pass

_IMPORT_MSG = (
    "sentry-sdk is required for Logly Sentry integration.\n"
    "Install with one of:\n"
    "  uv add logly[sentry]       # recommended\n"
    "  pip install logly[sentry]\n"
    "  uv add sentry-sdk\n"
    "  pip install sentry-sdk"
)

_LoglyLevel = Literal[
    "TRACE",
    "DEBUG",
    "INFO",
    "NOTICE",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "FAIL",
    "CRITICAL",
    "FATAL",
    "AUDIT",
]
_SentryLevel = Literal["debug", "info", "warning", "error", "fatal"]

_SENTRY_LEVEL_MAP: dict[str, _SentryLevel] = {
    "TRACE": "debug",
    "DEBUG": "debug",
    "INFO": "info",
    "NOTICE": "info",
    "SUCCESS": "info",
    "WARNING": "warning",
    "ERROR": "error",
    "FAIL": "error",
    "CRITICAL": "fatal",
    "FATAL": "fatal",
    "AUDIT": "info",
}


class SentrySink:
    """Forward error-level logs to Sentry.

    Only messages at WARNING level and above are sent as Sentry events.

    Usage::

        from logly import logger
        from logly.integrations.sentry import SentrySink

        logger.add(SentrySink(dsn="https://...@sentry.io/..."), level="WARNING")

    Args:
        dsn: Sentry DSN. If ``None``, uses ``sentry_sdk.init()`` defaults.
        environment: Sentry environment tag.
        release: Sentry release tag.
        level: Minimum Logly level to forward (default: ``"WARNING"``).
    """

    def __init__(
        self,
        dsn: str | None = None,
        *,
        environment: str | None = None,
        release: str | None = None,
        level: _LoglyLevel = "WARNING",
    ) -> None:
        """Initialize the Sentry sink.

        Args:
            dsn: Sentry DSN. If ``None``, uses ``sentry_sdk.init()`` defaults.
            environment: Sentry environment tag.
            release: Sentry release tag.
            level: Minimum Logly level to forward.

        Raises:
            ImportError: If ``sentry-sdk`` is not installed.
        """
        try:
            import sentry_sdk
        except ImportError:
            raise ImportError(_IMPORT_MSG) from None

        self._level = level.upper()
        init_kwargs: dict[str, Any] = {}
        if dsn:
            init_kwargs["dsn"] = dsn
        if environment:
            init_kwargs["environment"] = environment
        if release:
            init_kwargs["release"] = release

        sentry_sdk.init(**init_kwargs)

    def write(self, message: str) -> None:
        """Capture one log message as a Sentry event."""
        try:
            import sentry_sdk  # noqa: PLC0415
        except ImportError:
            return

        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        msg = strip_ansi(message.rstrip("\n"))
        detected_level: _SentryLevel = "info"
        upper = msg.upper()
        for logly_name, sentry_name in _SENTRY_LEVEL_MAP.items():
            if logly_name in upper:
                detected_level = sentry_name
                break

        level_order: dict[str, int] = {"debug": 0, "info": 1, "warning": 2, "error": 3, "fatal": 4}
        threshold = level_order.get(_SENTRY_LEVEL_MAP.get(self._level, "warning"), 2)
        if level_order.get(detected_level, 1) < threshold:
            return

        with sentry_sdk.new_scope() as scope:
            scope.set_level(detected_level)
            sentry_sdk.capture_message(msg, level=detected_level)

    def flush(self) -> None:
        """Flush Sentry transport."""
        try:
            import sentry_sdk

            sentry_sdk.flush()
        except ImportError:
            pass

    def close(self) -> None:
        """Close Sentry client."""
        self.flush()
