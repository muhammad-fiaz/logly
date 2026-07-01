"""Datadog integration for Logly.

Provides ``DatadogSink`` that sends log records to Datadog
via the Logs API (HTTP).

No extra dependencies required - uses ``urllib.request`` from the
Python standard library.

Install with::

    # Option 1: uv (recommended)
    uv add logly

    # Option 2: pip
    pip install logly
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any

_IMPORT_MSG = (
    "datadog is required for Logly Datadog integration.\n"
    "Install with one of:\n"
    "  uv add logly[datadog]       # recommended\n"
    "  pip install logly[datadog]\n"
    "  uv add datadog\n"
    "  pip install datadog"
)


class DatadogSink:
    """Send log entries to Datadog via the Logs API.

    Posts each log message as a JSON payload to the Datadog Logs API
    endpoint (``https://http-intake.logs.datadoghq.com/api/v2/logs``).

    Usage::

        from logly import logger
        from logly.integrations.datadog import DatadogSink

        logger.add(
            DatadogSink(
                api_key="your-datadog-api-key",
                service="my-service",
                tags=["env:production"],
            ),
            level="WARNING",
        )

    Args:
        api_key: Datadog API key.
        host: Hostname to attach to log entries.
        source: Source attribute (default: ``"python"``).
        service: Service name to attach to log entries.
        tags: List of tags to attach to log entries.
        site: Datadog site (default: ``"datadoghq.com"``).
        timeout: HTTP request timeout in seconds.

    Raises:
        ValueError: If ``api_key`` is empty or ``None``.
    """

    _DEFAULT_URL = "https://http-intake.logs.datadoghq.com/api/v2/logs"

    def __init__(
        self,
        api_key: str = "",
        *,
        host: str | None = None,
        source: str | None = None,
        service: str | None = None,
        tags: list[str] | None = None,
        site: str = "datadoghq.com",
        timeout: float = 5.0,
    ) -> None:
        """Initialize the Datadog sink.

        Args:
            api_key: Datadog API key.
            host: Hostname to attach to log entries.
            source: Source attribute (default: ``"python"``).
            service: Service name to attach to log entries.
            tags: List of tags to attach to log entries.
            site: Datadog site domain.
            timeout: HTTP request timeout in seconds.

        Raises:
            ValueError: If ``api_key`` is empty or ``None``.
        """
        if not api_key:
            raise ValueError("A Datadog API key is required for the Datadog handler.")
        self._api_key = api_key
        self._host = host
        self._source = source or "python"
        self._service = service
        self._tags = tags
        self._site = site
        self._timeout = timeout
        self._url = f"https://http-intake.logs.{site}/api/v2/logs"

    def write(self, message: str) -> None:
        """Send one log entry to Datadog.

        Args:
            message: The formatted log message to send.
        """
        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        msg = strip_ansi(message.rstrip("\n"))
        severity = self._detect_severity(msg)

        log_data: dict[str, Any] = {
            "message": msg,
            "status": severity,
            "ddsource": self._source,
        }
        if self._host:
            log_data["host"] = self._host
        if self._service:
            log_data["service"] = self._service
        if self._tags:
            log_data["ddtags"] = ",".join(self._tags)

        self._send_log(log_data)

    def _detect_severity(self, message: str) -> str:
        """Detect log severity from message content.

        Args:
            message: The log message string.

        Returns:
            Datadog status string.
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

    def _send_log(self, log_data: dict[str, Any]) -> None:
        """Send a log entry to the Datadog Logs API.

        Args:
            log_data: Log payload dictionary.
        """
        payload = json.dumps(log_data).encode("utf-8")
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "DD-API-KEY": self._api_key,
        }

        request = urllib.request.Request(
            self._url,
            data=payload,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                response.read()
        except Exception:
            pass

    def flush(self) -> None:
        """No-op for Datadog sink."""

    def close(self) -> None:
        """No-op for Datadog sink."""
