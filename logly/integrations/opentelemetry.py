"""OpenTelemetry integration for Logly.

Provides ``OTelLogSink`` that exports log records to OpenTelemetry collectors.

Requires ``opentelemetry-api`` and ``opentelemetry-sdk``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[opentelemetry]

    # Option 2: pip
    pip install "logly[opentelemetry]"

    # Option 3: uv without extras
    uv add opentelemetry-api opentelemetry-sdk

    # Option 4: pip without extras
    pip install opentelemetry-api opentelemetry-sdk
"""

from __future__ import annotations

from typing import Any

_IMPORT_MSG = (
    "opentelemetry-api and opentelemetry-sdk are required.\n"
    "Install with one of:\n"
    "  uv add logly[opentelemetry]       # recommended\n"
    "  pip install logly[opentelemetry]\n"
    "  uv add opentelemetry-api opentelemetry-sdk\n"
    "  pip install opentelemetry-api opentelemetry-sdk"
)


class OTelLogSink:
    """Send log records to OpenTelemetry log collector.

    Usage::

        from logly import logger
        from logly.integrations.opentelemetry import OTelLogSink

        logger.add(OTelLogSink(service_name="my-service"), level="INFO")

    Args:
        service_name: Service name for the OTel resource.
        endpoint: OTLP endpoint URL (default: ``http://localhost:4318``).
        protocol: Export protocol, ``"http"`` or ``"grpc"``.
    """

    def __init__(
        self,
        service_name: str = "logly",
        endpoint: str = "http://localhost:4318",
        protocol: str = "http",
    ) -> None:
        """Initialize the OpenTelemetry sink.

        Args:
            service_name: Service name for the OTel resource.
            endpoint: OTLP endpoint URL.
            protocol: Export protocol, ``"http"`` or ``"grpc"``.

        Raises:
            ImportError: If OpenTelemetry packages are not installed.
        """
        try:
            from opentelemetry.sdk._logs import LoggerProvider as SDKLoggerProvider
            from opentelemetry.sdk.resources import SERVICE_NAME, Resource
        except ImportError:
            raise ImportError(_IMPORT_MSG) from None

        self._service_name = service_name
        self._endpoint = endpoint
        self._protocol = protocol

        resource = Resource.create({SERVICE_NAME: service_name})
        self._provider: Any = SDKLoggerProvider(resource=resource)
        self._otel_logger: Any = self._provider.get_logger(service_name)

    def write(self, message: str) -> None:
        """Forward one rendered message to the OTel logger."""
        severity = self._resolve_severity()
        self._otel_logger.emit(severity_number=severity, body=message.rstrip("\n"))

    @staticmethod
    def _resolve_severity() -> int:
        try:
            from opentelemetry._logs import SeverityNumber

            return SeverityNumber.INFO.value
        except (ImportError, AttributeError):
            return 9

    def flush(self) -> None:
        """Flush the OTel log provider."""
        self._provider.force_flush()

    def close(self) -> None:
        """Shut down the OTel log provider."""
        self._provider.shutdown()
