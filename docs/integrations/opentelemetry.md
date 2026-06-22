---
title: OpenTelemetry
description: OTel log collector export for distributed tracing.
---

# OpenTelemetry

`OTelLogSink` exports log records to OpenTelemetry collectors via OTLP (HTTP or gRPC).

## Installation

This integration requires the `opentelemetry-api` and `opentelemetry-sdk` packages.

::: code-group

```bash [uv]
uv add logly[opentelemetry]
```

```bash [pip]
pip install "logly[opentelemetry]"
```

```bash [uv (without extras)]
uv add opentelemetry-api opentelemetry-sdk
```

```bash [pip (without extras)]
pip install opentelemetry-api opentelemetry-sdk
```

:::

::: warning Missing Dependency
If `opentelemetry-api` or `opentelemetry-sdk` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'opentelemetry'
```
:::

## Usage

```python
from logly import logger
from logly.integrations.opentelemetry import OTelLogSink

logger.add(OTelLogSink(service_name="my-service"), level="INFO")
```

## Full Example

```python
from logly import logger
from logly.integrations.opentelemetry import OTelLogSink

logger.add(
    OTelLogSink(
        service_name="my-api",
        endpoint="http://localhost:4318",
        protocol="http",
    ),
    level="INFO",
)

logger.info("Request processed", user_id=123)
logger.error("Database connection failed")
```
