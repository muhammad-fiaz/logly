---
title: Loki
description: Grafana Loki push for log aggregation.
---

# Loki

`LokiSink` pushes log entries to Grafana Loki via HTTP. No extra dependencies — uses `urllib.request` from the standard library.

## Installation

No additional dependencies required. This integration uses Python's standard library.

## Usage

```python
from logly import logger
from logly.integrations.loki import LokiSink

logger.add(
    LokiSink(
        "http://localhost:3100/loki/api/v1/push",
        labels={"app": "myapp", "env": "production"},
    ),
    level="INFO",
)
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `endpoint` | `http://localhost:3100/loki/api/v1/push` | Loki push API URL |
| `labels` | `{"app": "logly"}` | Default labels for every stream |
| `timeout` | `5.0` | HTTP request timeout in seconds |
| `username` | `None` | Optional basic auth username |
| `password` | `None` | Optional basic auth password |

## Full Example

```python
from logly import logger
from logly.integrations.loki import LokiSink

logger.add(
    LokiSink(
        endpoint="http://loki:3100/loki/api/v1/push",
        labels={"app": "myapi", "env": "production", "region": "us-east-1"},
        timeout=10.0,
        username="admin",
        password="secret",
    ),
    level="INFO",
)

logger.info("User signed in", user_id=123)
logger.error("Payment failed", order_id="abc-123")
```
