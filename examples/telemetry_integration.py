"""Telemetry integration example.

Sends log events to a custom callback for integration with
OpenTelemetry, StatsD, Prometheus, or any custom backend.
No extra dependencies required.
"""

from logly import logger
from logly.integrations.telemetry import TelemetrySink

# Define your telemetry callback
_events: list[dict] = []


def collect_telemetry(event: dict) -> None:
    """Receive telemetry events and store them."""
    _events.append(event)


# Add telemetry sink
logger.add(
    TelemetrySink(
        collect_telemetry,
        service_name="my-api",
        environment="production",
    ),
    level="INFO",
)

logger.info("Request served in {}ms", 120)
logger.warning("Upstream latency spike detected")
logger.error("Connection pool exhausted")

logger.complete()

# Inspect collected events
for _event in _events:
    pass
