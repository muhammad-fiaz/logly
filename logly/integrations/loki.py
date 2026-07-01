"""Loki integration for Logly.

Provides ``LokiSink`` that pushes log entries to Grafana Loki via HTTP.

No extra dependencies required - uses ``urllib.request`` from the Python
standard library.

Install with::

    # Option 1: uv (recommended)
    uv add logly

    # Option 2: pip
    pip install logly
"""

from __future__ import annotations

import json
import time
import urllib.request
from typing import Any


class LokiSink:
    """Send log entries to Grafana Loki.

    Pushes log entries as JSON payloads to the Loki push API endpoint.

    Usage::

        from logly import logger
        from logly.integrations.loki import LokiSink

        logger.add(
            LokiSink(
                "http://localhost:3100/loki/api/v1/push",
                labels={"app": "myapp", "env": "production"},
            ),
            level="INFO",
        )

    Args:
        endpoint: Loki push API URL.
        labels: Default labels attached to every stream.
        timeout: HTTP request timeout in seconds.
        username: Optional basic auth username.
        password: Optional basic auth password.
    """

    def __init__(
        self,
        endpoint: str = "http://localhost:3100/loki/api/v1/push",
        *,
        labels: dict[str, str] | None = None,
        timeout: float = 5.0,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Initialize the Loki sink.

        Args:
            endpoint: Loki push API URL.
            labels: Default labels attached to every stream.
            timeout: HTTP request timeout in seconds.
            username: Optional basic auth username.
            password: Optional basic auth password.
        """
        self.endpoint = endpoint
        self.labels = labels or {"app": "logly"}
        self.timeout = timeout
        self._auth: str | None = None
        if username and password:
            import base64

            self._auth = base64.b64encode(f"{username}:{password}".encode()).decode()

    def write(self, message: str) -> None:
        """Push one log entry to Loki."""
        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        ts = str(int(time.time() * 1_000_000_000))
        stream: dict[str, Any] = {"stream": self.labels}
        stream["values"] = [[ts, strip_ansi(message.rstrip("\n"))]]
        payload = json.dumps({"streams": [stream]}).encode("utf-8")

        headers: dict[str, str] = {
            "Content-Type": "application/json",
        }
        if self._auth:
            headers["Authorization"] = f"Basic {self._auth}"

        request = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            response.read()

    def flush(self) -> None:
        """No-op for Loki sink."""

    def close(self) -> None:
        """No-op for Loki sink."""
