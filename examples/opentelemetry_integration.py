"""OpenTelemetry integration example - export logs to OTel collector.

Demonstrates OTelLogSink sending log records to an OpenTelemetry
collector with service name attribution.

Requires: pip install opentelemetry-api opentelemetry-sdk
"""

from logly import logger
from logly.integrations.opentelemetry import OTelLogSink

logger.add(
    OTelLogSink(
        service_name="my-service",
        endpoint="http://localhost:4318",
        protocol="http",  # or "grpc"
    ),
    level="INFO",
)

logger.info("Service started")
logger.warning("High latency detected")
logger.error("Request timeout")

logger.complete()
