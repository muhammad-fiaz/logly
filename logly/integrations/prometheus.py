"""Prometheus integration for Logly.

Provides ``PrometheusLogSink`` that exposes log metrics via Prometheus client.

Requires ``prometheus-client``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[prometheus]

    # Option 2: pip
    pip install "logly[prometheus]"

    # Option 3: uv without extras
    uv add prometheus-client

    # Option 4: pip without extras
    pip install prometheus-client
"""

from __future__ import annotations

from typing import Any

_IMPORT_MSG = (
    "prometheus-client is required for Logly Prometheus integration.\n"
    "Install with one of:\n"
    "  uv add logly[prometheus]       # recommended\n"
    "  pip install logly[prometheus]\n"
    "  uv add prometheus-client\n"
    "  pip install prometheus-client"
)


class PrometheusLogSink:
    """Emit log metrics to Prometheus.

    Counts log messages by level and tracks message lengths.

    Usage::

        from logly import logger
        from logly.integrations.prometheus import PrometheusLogSink

        logger.add(PrometheusLogSink(), level="INFO")

    After adding this sink, expose metrics via::

        from prometheus_client import start_http_server
        start_http_server(8000)
    """

    def __init__(self, namespace: str = "logly", **kwargs: Any) -> None:
        """Initialize the Prometheus sink.

        Args:
            namespace: Prometheus metric namespace prefix.
            **kwargs: Additional arguments passed to Prometheus metric constructors.

        Raises:
            ImportError: If ``prometheus-client`` is not installed.
        """
        try:
            from prometheus_client import (
                Counter,
                Gauge,
                Histogram,
            )
        except ImportError:
            raise ImportError(_IMPORT_MSG) from None

        self._namespace = namespace

        self._log_total = Counter(
            f"{namespace}_log_total",
            "Total number of log messages",
            ["level"],
            **kwargs,
        )
        self._log_size = Histogram(
            f"{namespace}_log_message_size_bytes",
            "Log message size in bytes",
            buckets=(10, 50, 100, 500, 1000, 5000),
            **kwargs,
        )
        self._log_level = Gauge(
            f"{namespace}_current_log_level",
            "Numeric level of the last log message",
        )

        self._level_numeric: dict[str, int] = {
            "TRACE": 5,
            "DEBUG": 10,
            "INFO": 20,
            "NOTICE": 25,
            "SUCCESS": 30,
            "WARNING": 40,
            "ERROR": 50,
            "FAIL": 55,
            "CRITICAL": 60,
            "FATAL": 70,
            "AUDIT": 35,
        }

    def write(self, message: str) -> None:
        """Process one log entry for Prometheus metrics."""
        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        msg = strip_ansi(message.rstrip("\n"))
        upper = msg.upper()
        for name in (
            "FATAL",
            "CRITICAL",
            "ERROR",
            "FAIL",
            "WARNING",
            "SUCCESS",
            "NOTICE",
            "DEBUG",
            "TRACE",
            "AUDIT",
            "INFO",
        ):
            if name in upper:
                level = name
                break

        self._log_total.labels(level=level).inc()
        self._log_size.observe(float(len(msg)))
        self._log_level.set(self._level_numeric.get(level, 0))

    def flush(self) -> None:
        """No-op for Prometheus sink."""

    def close(self) -> None:
        """No-op for Prometheus sink."""
