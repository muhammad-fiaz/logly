"""New Relic integration for Logly.

Provides ``NewRelicSink`` that sends log records to New Relic
via the ``newrelic.agent`` API.

Requires ``newrelic``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[newrelic]

    # Option 2: pip
    pip install "logly[newrelic]"

    # Option 3: uv without extras
    uv add newrelic

    # Option 4: pip without extras
    pip install newrelic
"""

from __future__ import annotations

import importlib.util
from typing import Any

_IMPORT_MSG = (
    "newrelic is required for Logly New Relic integration.\n"
    "Install with one of:\n"
    "  uv add logly[newrelic]       # recommended\n"
    "  pip install logly[newrelic]\n"
    "  uv add newrelic\n"
    "  pip install newrelic"
)


class NewRelicSink:
    """Send log entries to New Relic via the agent API.

    Usage::

        from logly import logger
        from logly.integrations.newrelic import NewRelicSink

        logger.add(
            NewRelicSink(
                license_key="your-license-key",
                app_name="My Application",
            ),
            level="WARNING",
        )

    Args:
        license_key: New Relic license key. If ``None``, relies on
            ``NEW_RELIC_LICENSE_KEY`` environment variable.
        app_name: Application name in New Relic. If ``None``, relies on
            ``NEW_RELIC_APP_NAME`` environment variable.

    Raises:
        ImportError: If ``newrelic`` is not installed.
    """

    def __init__(
        self,
        *,
        license_key: str | None = None,
        app_name: str | None = None,
    ) -> None:
        """Initialize the New Relic sink.

        Args:
            license_key: New Relic license key.
            app_name: Application name in New Relic.

        Raises:
            ImportError: If ``newrelic`` is not installed.
        """
        if importlib.util.find_spec("newrelic") is None:
            raise ImportError(_IMPORT_MSG)

        import newrelic.agent

        settings: dict[str, Any] = {}
        if license_key:
            settings["license_key"] = license_key
        if app_name:
            settings["app_name"] = app_name

        if settings:
            newrelic.agent.initialize(**settings)

        self._application = newrelic.agent.application()

    def write(self, message: str) -> None:
        """Send one log entry to New Relic.

        Args:
            message: The formatted log message to send.
        """
        import newrelic.agent  # noqa: PLC0415

        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        msg = strip_ansi(message.rstrip("\n"))
        severity = self._detect_severity(msg)

        with newrelic.agent.GroupTrace(speedscope=True, group="Logly"):
            newrelic.agent.log(
                msg,
                level=severity,
                attributes={},
            )

    @staticmethod
    def _detect_severity(message: str) -> str:
        """Detect log severity from message content.

        Args:
            message: The log message string.

        Returns:
            New Relic severity string.
        """
        upper = message.upper()
        if "FATAL" in upper or "CRITICAL" in upper:
            return "critical"
        if "ERROR" in upper or "FAIL" in upper:
            return "error"
        if "WARNING" in upper or "WARN" in upper:
            return "warning"
        if "NOTICE" in upper:
            return "info"
        if "SUCCESS" in upper:
            return "info"
        if "DEBUG" in upper or "TRACE" in upper:
            return "debug"
        return "info"

    def flush(self) -> None:
        """No-op for New Relic sink."""

    def close(self) -> None:
        """No-op for New Relic sink."""
