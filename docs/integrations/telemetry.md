---
title: Telemetry
description: Generic telemetry sink for custom backends.
---

# Telemetry

`TelemetrySink` sends log events to any external collector via a custom `emit` callable. `HttpJsonSink` is a convenience class for HTTP JSON endpoints.

## Installation

No additional dependencies required. This integration uses Python's standard library.

## Quick Setup

```python
from logly import logger
from logly.integrations.telemetry import HttpJsonSink

logger.add(HttpJsonSink(endpoint="http://localhost:8080/logs"), level="INFO")
```

## Manual Setup

```python
from logly import logger
from logly.integrations.telemetry import TelemetrySink

def my_collector(event):
    print(f"Telemetry event: {event}")

logger.add(TelemetrySink(emit=my_collector, service_name="my-service"), level="INFO")
```

## Parameters

### `TelemetrySink`

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `emit` | `Callable` | (required) | Callable that forwards telemetry events |
| `service_name` | `str` | `"logly"` | Service name attached to every event |
| `environment` | `str \| None` | `None` | Optional deployment environment |

### `HttpJsonSink`

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `endpoint` | `str` | (required) | URL to POST log events to |
| `headers` | `dict \| None` | `None` | Optional HTTP headers |
| `timeout` | `float` | `5.0` | Request timeout in seconds |

## Tips

- Use `HttpJsonSink` for HTTP-based log ingestion APIs.
- Use `TelemetrySink` with a custom callable for non-HTTP backends.
- Add authentication headers for secured endpoints.

## Full Example

```python
from logly import logger
from logly.integrations.telemetry import HttpJsonSink

logger.add(
    HttpJsonSink(
        endpoint="http://localhost:8080/telemetry",
        headers={"Authorization": "Bearer token123"},
        timeout=10.0,
    ),
    level="INFO",
)

logger.info("Telemetry event", event_type="api_call", latency_ms=42)
```
