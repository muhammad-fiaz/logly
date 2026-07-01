---
title: Datadog
description: Send log records to Datadog Logs.
---

# Datadog

`DatadogHandler` sends log records to Datadog via the HTTP Logs API. No extra dependencies required.

## Installation

No extra dependencies are needed (stdlib only).

::: code-group

```bash [uv]
uv add logly
```

```bash [pip]
pip install logly
```

:::

## Usage

```python
from logly import logger
from logly.integrations.datadog import DatadogHandler

logger.add(
    DatadogHandler(
        api_key="your-datadog-api-key",
        service="my-app",
    )
)
```

## Full Example

```python
from logly import logger
from logly.integrations.datadog import DatadogHandler

logger.add(
    DatadogHandler(
        api_key="abc123def456",
        service="my-api",
        source="python",
        tags=["env:production", "team:backend"],
        hostname="web-01",
    ),
    level="INFO",
)

logger.info("User signed up", user_id="u-123")
logger.warning("High memory usage", usage_pct=92)
```
