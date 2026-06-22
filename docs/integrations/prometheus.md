---
title: Prometheus
description: Metrics export for log monitoring.
---

# Prometheus

`PrometheusLogSink` exposes log metrics via Prometheus client. Counts messages by level and tracks message sizes.

## Installation

This integration requires the `prometheus-client` package.

::: code-group

```bash [uv]
uv add logly[prometheus]
```

```bash [pip]
pip install "logly[prometheus]"
```

```bash [uv (without extras)]
uv add prometheus-client
```

```bash [pip (without extras)]
pip install prometheus-client
```

:::

::: warning Missing Dependency
If `prometheus_client` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'prometheus_client'
```
:::

## Usage

```python
from logly import logger
from logly.integrations.prometheus import PrometheusLogSink
from prometheus_client import start_http_server

logger.add(PrometheusLogSink(), level="INFO")
start_http_server(8000)
```

## Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `logly_log_total` | Counter | Total log messages by level |
| `logly_log_message_size_bytes` | Histogram | Message size distribution |
| `logly_current_log_level` | Gauge | Numeric level of last message |

## Full Example

```python
from logly import logger
from logly.integrations.prometheus import PrometheusLogSink
from prometheus_client import start_http_server

logger.add(PrometheusLogSink(namespace="myapp"), level="INFO")

# Start Prometheus metrics endpoint
start_http_server(8000)

logger.info("Application started")
logger.warning("High memory usage")
logger.error("Request failed")
```
