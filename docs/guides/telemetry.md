---
title: Telemetry
description: Forward logs to telemetry systems and HTTP endpoints
---

# Telemetry

Logly provides sinks for forwarding log messages to external telemetry systems.

## TelemetrySink

Forward rendered messages to any telemetry callback:

```python
from logly import logger
from logly.integrations.telemetry import TelemetrySink

def send_to_collector(event: dict[str, object]) -> None:
    # Send to your telemetry backend
    print(f"Telemetry event: {event}")

logger.add(
    TelemetrySink(emit=send_to_collector, service_name="billing"),
    format="{level}:{message}",
)
logger.info("Invoice created")
```

### TelemetrySink Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `emit` | `Callable` | (required) | Function to receive telemetry events |
| `service_name` | `str` | `"logly"` | Service name for the telemetry event |
| `environment` | `str \| None` | `None` | Optional deployment environment |

## HttpJsonSink

POST log messages to an HTTP JSON endpoint:

```python
from logly import logger
from logly.integrations.telemetry import HttpJsonSink

logger.add(
    HttpJsonSink(endpoint="https://collector.example.com/logs"),
    level="ERROR",
    serialize=True,
)
logger.error("Error occurred")
```

### HttpJsonSink Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `endpoint` | `str` | (required) | URL to POST log events to |
| `headers` | `dict \| None` | `None` | Optional HTTP headers |
| `timeout` | `float` | `5.0` | Request timeout in seconds |

## Custom Telemetry Integration

```python
from logly import logger
from logly.integrations.telemetry import TelemetrySink

# OpenTelemetry-style integration
def otel_exporter(event: dict[str, object]) -> None:
    span = {
        "name": f"logly.{event.get('level', 'unknown')}",
        "attributes": {
            "message": event.get("message", ""),
            "level": event.get("level", ""),
            "service.name": "my-service",
        },
    }
    # Send to OTel collector
    send_to_otel(span)

logger.add(TelemetrySink(otel_exporter, service_name="my-service"))
```

## StatsD Integration

```python
from logly import logger
from logly.integrations.telemetry import TelemetrySink

def statsd_exporter(event: dict[str, object]) -> None:
    level = event.get("level", "").lower()
    # Increment counter for each log level
    statsd.increment(f"logly.{level}.count")

logger.add(TelemetrySink(statsd_exporter))
```

## Prometheus Integration

```python
from logly import logger
from logly.integrations.telemetry import TelemetrySink

log_counter = Counter("logly_logs_total", "Total log messages", ["level"])

def prometheus_exporter(event: dict[str, object]) -> None:
    level = str(event.get("level", "unknown")).lower()
    log_counter.labels(level=level).inc()

logger.add(TelemetrySink(prometheus_exporter))
```
