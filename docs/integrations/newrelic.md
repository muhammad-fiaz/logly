---
title: New Relic
description: Send log records to New Relic.
---

# New Relic

`NewRelicHandler` sends log records to New Relic via the Log API. Supports license key authentication and structured logging.

## Installation

This integration requires the `newrelic` package.

::: code-group

```bash [uv]
uv add logly[newrelic]
```

```bash [pip]
pip install "logly[newrelic]"
```

```bash [uv (without extras)]
uv add newrelic
```

```bash [pip (without extras)]
pip install newrelic
```

:::

::: warning Missing Dependency
If `newrelic` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'newrelic'
```
:::

## Usage

```python
from logly import logger
from logly.integrations.newrelic import NewRelicHandler

logger.add(
    NewRelicHandler(
        license_key="your-license-key",
        app_name="my-app",
    )
)
```

## Full Example

```python
from logly import logger
from logly.integrations.newrelic import NewRelicHandler

logger.add(
    NewRelicHandler(
        license_key="abc123def456",
        app_name="my-api",
        insert_key="your-insights-insert-key",
        region="US",
    ),
    level="INFO",
)

logger.info("Deployment completed", version="2.1.0")
logger.error("Database timeout", query="SELECT * FROM users")
```
