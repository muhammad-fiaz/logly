"""Telemetry integration - send log events to external collectors.

Provides ``TelemetrySink`` for custom telemetry backends and ``HttpJsonSink``
for HTTP JSON endpoints.

No extra dependencies required - uses only the Python standard library.
"""

from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable, Mapping
from typing import Any


class TelemetrySink:
    """Convert rendered Logly output into telemetry events.

    This sink forwards each log message to a user-provided callable,
    suitable for integration with OpenTelemetry, StatsD, Prometheus,
    or any custom telemetry backend.

    Attributes:
        emit: Callable receiving an event mapping.
        service_name: Service name attached to every event.

    Usage::

        from logly import logger
        from logly.integrations.telemetry import TelemetrySink

        def send_to_collector(event: dict) -> None:
            # Forward to your telemetry backend
            print(f"Telemetry event: {event}")

        logger.add(
            TelemetrySink(send_to_collector, service_name="my-service"),
            level="INFO",
        )
    """

    def __init__(
        self,
        emit: Callable[[Mapping[str, Any]], None],
        *,
        service_name: str = "logly",
        environment: str | None = None,
    ) -> None:
        """Create a telemetry sink.

        Args:
            emit: Callable that forwards telemetry events. It receives a mapping
                with keys ``"body"``, ``"service.name"``, and optionally
                ``"environment"``.
            service_name: Service name attached to every event.
            environment: Optional deployment environment (e.g. ``"production"``,
                ``"staging"``).
        """
        self.emit = emit
        self.service_name = service_name
        self.environment = environment

    def write(self, message: str) -> None:
        """Forward one rendered message as a telemetry event."""
        event = {
            "body": message.rstrip("\n"),
            "environment": self.environment,
            "service.name": self.service_name,
        }
        self.emit(event)


class HttpJsonSink:
    """Send rendered log events to an HTTP JSON collector.

    Posts each log message as a JSON payload to the configured endpoint.

    Usage::

        from logly import logger
        from logly.integrations.telemetry import HttpJsonSink

        logger.add(
            HttpJsonSink(
                "https://collector.example.com/logs",
                headers={"Authorization": "Bearer token"},
            ),
            level="WARNING",
        )

    No extra dependencies required - uses ``urllib.request`` from the
    Python standard library.
    """

    def __init__(
        self,
        endpoint: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: float = 5.0,
    ) -> None:
        """Create an HTTP JSON telemetry sink.

        Args:
            endpoint: URL to POST log events to.
            headers: Optional HTTP headers (e.g. authorization tokens).
            timeout: Request timeout in seconds.
        """
        self.endpoint = endpoint
        self.headers = dict(headers or {})
        self.timeout = timeout

    def write(self, message: str) -> None:
        """Post one rendered message to the configured endpoint."""
        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        payload = json.dumps({"message": strip_ansi(message.rstrip("\n"))}).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers={"content-type": "application/json", **self.headers},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            response.read()
