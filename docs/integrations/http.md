---
title: HTTP
description: Send log entries to HTTP endpoints.
---

# HTTP

`HttpHandler` sends log entries to any HTTP endpoint. Uses the Python standard library (`urllib.request`) — no extra dependencies required.

## Installation

No additional dependencies required. This integration uses Python's standard library.

## Usage

```python
from logly import logger
from logly.integrations.http import HttpHandler

handler = HttpHandler(
    "https://api.example.com/logs",
    method="POST",
    headers={"Authorization": "Bearer token"},
)
logger.add(handler, level="WARNING")
```

## Constructor Args

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `url` | `str` | `http://localhost:8080/logs` | HTTP endpoint URL |
| `method` | `"GET" \| "POST" \| "PUT" \| "PATCH"` | `"POST"` | HTTP method |
| `headers` | `Mapping[str, str] \| None` | `None` | Additional HTTP headers |
| `timeout` | `float` | `5.0` | HTTP request timeout in seconds |
| `format` | `"json" \| "text"` | `"json"` | Request body format |

## Tips

- Use `"json"` format for structured log aggregation services (Datadog, Splunk, etc.).
- Use `"text"` format for simple log endpoints that expect plain text.
- Include authentication headers for secured endpoints.

## Full Example

```python
from logly import logger
from logly.integrations.http import HttpHandler

handler = HttpHandler(
    url="https://httpbin.org/post",
    method="POST",
    headers={
        "Authorization": "Bearer my-api-token",
        "X-Service": "myapp",
    },
    timeout=10.0,
    format="json",
)
logger.add(handler, level="WARNING")

logger.warning("Request latency high", latency_ms=1200)
logger.error("External API timeout", api="payment-gateway")
```
