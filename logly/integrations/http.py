"""HTTP integration for Logly.

Provides ``HttpHandler`` that sends log entries to HTTP endpoints.

No extra dependencies required - uses ``urllib.request`` from the
Python standard library.
"""

from __future__ import annotations

import json
import urllib.request
from collections.abc import Mapping
from typing import Literal


class HttpHandler:
    """Send log entries to an HTTP endpoint.

    Usage::

        from logly import logger
        from logly.integrations.http import HttpHandler

        handler = HttpHandler(
            "https://api.example.com/logs",
            method="POST",
            headers={"Authorization": "Bearer token"},
        )
        logger.add(handler, level="WARNING")

    Args:
        url: HTTP endpoint URL.
        method: HTTP method (GET, POST, PUT, PATCH).
        headers: Additional HTTP headers.
        timeout: HTTP request timeout in seconds.
        format: Request body format (``"json"`` or ``"text"``).
    """

    def __init__(
        self,
        url: str = "http://localhost:8080/logs",
        *,
        method: Literal["GET", "POST", "PUT", "PATCH"] = "POST",
        headers: Mapping[str, str] | None = None,
        timeout: float = 5.0,
        format: Literal["json", "text"] = "json",
    ) -> None:
        self.url = url
        self.method = method
        self.headers = dict(headers or {})
        self.timeout = timeout
        self.format = format

    def write(self, message: str) -> None:
        """Send one log message via HTTP.

        Args:
            message: The formatted log message to send.
        """
        body: str | bytes
        headers: dict[str, str]

        if self.format == "json":
            body = json.dumps({"message": message.rstrip("\n")}).encode("utf-8")
            headers = {"Content-Type": "application/json", **self.headers}
        else:
            body = message.rstrip("\n").encode("utf-8")
            headers = {"Content-Type": "text/plain", **self.headers}

        request = urllib.request.Request(
            self.url,
            data=body,
            headers=headers,
            method=self.method,
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response.read()
        except Exception:
            pass

    def flush(self) -> None:
        """No-op for HTTP handler."""

    def close(self) -> None:
        """No-op for HTTP handler."""
