"""Seq structured log server integration for Logly.

Provides ``SeqSink`` that sends structured log records to a Seq
server via the HTTP API.

No extra dependencies required - uses ``urllib.request`` from the
Python standard library.

Install with::

    # Option 1: uv (recommended)
    uv add logly[seq]

    # Option 2: pip
    pip install "logly[seq]"

    # Option 3: uv without extras
    uv add seq

    # Option 4: pip without extras
    pip install seq
"""

from __future__ import annotations

import datetime
import json
import urllib.request
from typing import Any

_IMPORT_MSG = (  # pragma: no cover
    "No extra dependencies required for Logly Seq integration.\n"
    "Uses only Python standard library modules (urllib, json).\n"
    "Install with one of:\n"
    "  uv add logly       # recommended\n"
    "  pip install logly"
)  # pragma: no cover

_SEVERITY_MAP: dict[str, str] = {
    "TRACE": "Debug",
    "DEBUG": "Debug",
    "INFO": "Information",
    "NOTICE": "Information",
    "SUCCESS": "Information",
    "WARNING": "Warning",
    "ERROR": "Error",
    "FAIL": "Error",
    "CRITICAL": "Fatal",
    "FATAL": "Fatal",
    "AUDIT": "Information",
}


class SeqSink:
    """Send log entries to a Seq server via the HTTP API.

    Posts each log message as a JSON payload to the Seq raw ingest
    endpoint (``/api/events/raw``).

    Usage::

        from logly import logger
        from logly.integrations.seq import SeqSink

        logger.add(
            SeqSink(
                server_url="http://localhost:5341",
                api_key="your-seq-api-key",
            ),
            level="WARNING",
        )

    Args:
        server_url: Base URL of the Seq server.
        api_key: Optional API key for authenticated ingestion.
        event_template: Optional default event template dictionary.
            Keys from this dict are merged into every event.
        timeout: HTTP request timeout in seconds.

    Raises:
        ValueError: If ``server_url`` is empty.
    """

    def __init__(
        self,
        server_url: str = "",
        *,
        api_key: str | None = None,
        event_template: dict[str, Any] | None = None,
        timeout: float = 5.0,
    ) -> None:
        """Initialize the Seq sink.

        Args:
            server_url: Base URL of the Seq server.
            api_key: Optional API key for authenticated ingestion.
            event_template: Optional default event template dictionary.
            timeout: HTTP request timeout in seconds.

        Raises:
            ValueError: If ``server_url`` is empty.
        """
        if not server_url:
            raise ValueError("A Seq server URL is required for the Seq handler.")
        self._server_url = server_url.rstrip("/")
        self._api_key = api_key
        self._event_template = event_template or {}
        self._timeout = timeout

    def write(self, message: str) -> None:
        """Send one log entry to Seq.

        Args:
            message: The formatted log message to send.
        """
        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        msg = strip_ansi(message.rstrip("\n"))
        severity = self._detect_severity(msg)
        timestamp = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()

        event: dict[str, Any] = {
            "EventType": severity,
            "MessageTemplate": msg,
            "@t": timestamp,
            "@l": severity,
        }

        event.update(self._event_template)

        self._send_event(event)

    @staticmethod
    def _detect_severity(message: str) -> str:
        """Detect log severity from message content.

        Args:
            message: The log message string.

        Returns:
            Seq severity string.
        """
        upper = message.upper()
        for logly_name, seq_name in _SEVERITY_MAP.items():
            if logly_name in upper:
                return seq_name
        return "Information"

    def _send_event(self, event: dict[str, Any]) -> None:
        """Send a single event to the Seq raw ingest endpoint.

        Args:
            event: Event payload dictionary.
        """
        url = f"{self._server_url}/api/events/raw"
        payload = json.dumps(event).encode("utf-8")

        headers: dict[str, str] = {
            "Content-Type": "application/json",
        }
        if self._api_key:
            headers["X-Seq-ApiKey"] = self._api_key

        request = urllib.request.Request(
            url,
            data=payload,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self._timeout
            ) as response:  # pragma: no cover
                response.read()
        except Exception:
            pass

    def flush(self) -> None:
        """No-op for Seq sink."""

    def close(self) -> None:
        """No-op for Seq sink."""
