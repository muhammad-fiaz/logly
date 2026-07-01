"""Azure Monitor / Application Insights integration for Logly.

Provides ``AzureMonitorSink`` that sends log entries to Azure Monitor
via OpenTelemetry.

Requires ``opentelemetry-api``, ``opentelemetry-sdk``, and
``azure-monitor-opentelemetry``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[azure-monitor]

    # Option 2: pip
    pip install "logly[azure-monitor]"

    # Option 3: uv without extras
    uv add opentelemetry-api opentelemetry-sdk azure-monitor-opentelemetry

    # Option 4: pip without extras
    pip install opentelemetry-api opentelemetry-sdk azure-monitor-opentelemetry
"""

from __future__ import annotations

import importlib.util
from typing import Any

_has_otel = importlib.util.find_spec("opentelemetry") is not None
_has_azure_monitor = importlib.util.find_spec("azure.monitor") is not None

_IMPORT_MSG = (
    "opentelemetry-api, opentelemetry-sdk, and azure-monitor-opentelemetry "
    "are required for Logly Azure Monitor integration.\n"
    "Install with one of:\n"
    "  uv add logly[azure-monitor]       # recommended\n"
    "  pip install logly[azure-monitor]\n"
    "  uv add opentelemetry-api opentelemetry-sdk azure-monitor-opentelemetry\n"
    "  pip install opentelemetry-api opentelemetry-sdk azure-monitor-opentelemetry"
)


class AzureMonitorSink:
    """Send log entries to Azure Monitor via OpenTelemetry.

    Usage::

        from logly import logger
        from logly.integrations.azure_monitor import AzureMonitorSink

        logger.add(
            AzureMonitorSink(
                connection_string="InstrumentationKey=...;IngestionEndpoint=...",
            ),
            level="WARNING",
        )

    Args:
        connection_string: Azure Monitor connection string. If ``None``,
            ``instrumentation_key`` must be provided.
        instrumentation_key: Application Insights instrumentation key.
            Ignored if ``connection_string`` is provided.

    Raises:
        ImportError: If required packages are not installed.
    """

    def __init__(
        self,
        *,
        connection_string: str | None = None,
        instrumentation_key: str | None = None,
    ) -> None:
        """Initialize the Azure Monitor sink.

        Args:
            connection_string: Azure Monitor connection string.
            instrumentation_key: Application Insights instrumentation key.

        Raises:
            ImportError: If required packages are not installed.
        """
        if not _has_otel or not _has_azure_monitor:
            raise ImportError(_IMPORT_MSG)

        from azure.monitor.opentelemetry import configure_azure_monitor

        kwargs: dict[str, Any] = {}
        if connection_string:
            kwargs["connection_string"] = connection_string
        elif instrumentation_key:
            kwargs["instrumentation_key"] = instrumentation_key

        configure_azure_monitor(**kwargs)

        from opentelemetry.sdk._logs import LoggerProvider

        self._provider: Any = LoggerProvider()
        self._logger: Any = self._provider.get_logger("logly.azure_monitor")

    def write(self, message: str) -> None:
        """Send one log entry to Azure Monitor.

        Args:
            message: The formatted log message to send.
        """
        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        msg = strip_ansi(message.rstrip("\n"))
        severity = self._detect_severity(msg)

        try:
            from opentelemetry._logs import SeverityNumber

            severity_number = getattr(SeverityNumber, severity, SeverityNumber.INFO)
        except (ImportError, AttributeError):
            severity_number = 9  # INFO

        self._logger.emit(
            severity_number=severity_number,
            body=msg,
            attributes={},
        )

    @staticmethod
    def _detect_severity(message: str) -> str:
        """Detect log severity from message content.

        Maps Logly levels to OTel ``SeverityNumber`` attribute names:

        - ``TRACE``, ``DEBUG`` -> ``TRACE``
        - ``INFO``, ``NOTICE``, ``SUCCESS`` -> ``INFO``
        - ``WARNING`` -> ``WARN``
        - ``ERROR``, ``FAIL`` -> ``ERROR``
        - ``CRITICAL``, ``FATAL`` -> ``FATAL``

        Args:
            message: The log message string.

        Returns:
            OTel ``SeverityNumber`` attribute name.
        """
        upper = message.upper()
        if "FATAL" in upper or "CRITICAL" in upper:
            return "FATAL"
        if "ERROR" in upper or "FAIL" in upper:
            return "ERROR"
        if "WARNING" in upper or "WARN" in upper:
            return "WARN"
        if "NOTICE" in upper:
            return "INFO"
        if "SUCCESS" in upper:
            return "INFO"
        if "DEBUG" in upper or "TRACE" in upper:
            return "TRACE"
        return "INFO"

    def flush(self) -> None:
        """Flush pending log records."""
        try:
            self._provider.force_flush()
        except Exception:
            pass

    def close(self) -> None:
        """Shut down the logger provider."""
        try:
            self._provider.shutdown()
        except Exception:
            pass
