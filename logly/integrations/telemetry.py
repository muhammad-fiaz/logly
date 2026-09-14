"""Telemetry integration - send log events to external collectors.

Provides ``TelemetrySink`` for custom telemetry backends and ``HttpJsonSink``
for HTTP JSON endpoints (back-compat alias over :class:`http.HttpHandler`).

No extra dependencies required - uses only the Python standard library.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from logly.integrations.http import HttpHandler

__all__ = ["HttpJsonSink", "TelemetrySink"]


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


class HttpJsonSink(HttpHandler):
    """Send rendered log events to an HTTP JSON collector.

    Back-compat subclass of :class:`logly.integrations.http.HttpHandler`.
    Accepts the legacy ``endpoint`` positional arg as an alias for ``url``.

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
        endpoint: str = "http://localhost:8080/logs",
        url: str | None = None,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: float = 5.0,
    ) -> None:
        """Create an HTTP JSON telemetry sink.

        Args:
            endpoint: URL to POST log events to (legacy alias for ``url``).
            url: URL to POST log events to (preferred).
            headers: Optional HTTP headers (e.g. authorization tokens).
            timeout: Request timeout in seconds.
        """
        resolved = url if url is not None else endpoint
        super().__init__(url=resolved, method="POST", headers=headers, timeout=timeout)
        self.endpoint = resolved
