---
title: Sentry
description: Error event capture for Sentry monitoring.
---

# Sentry

`SentrySink` captures error-level logs as Sentry events. Only WARNING and above are forwarded by default.

## Installation

This integration requires the `sentry-sdk` package.

::: code-group

```bash [uv]
uv add logly[sentry]
```

```bash [pip]
pip install "logly[sentry]"
```

```bash [uv (without extras)]
uv add sentry-sdk
```

```bash [pip (without extras)]
pip install sentry-sdk
```

:::

::: warning Missing Dependency
If `sentry_sdk` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'sentry_sdk'
```
:::

## Usage

```python
from logly import logger
from logly.integrations.sentry import SentrySink

logger.add(SentrySink(dsn="https://...@sentry.io/..."), level="WARNING")
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `dsn` | `None` | Sentry DSN |
| `environment` | `None` | Sentry environment tag |
| `release` | `None` | Sentry release tag |
| `level` | `"WARNING"` | Minimum level to forward |

## Full Example

```python
from logly import logger
from logly.integrations.sentry import SentrySink

logger.add(
    SentrySink(
        dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
        environment="production",
        release="1.0.0",
        level="WARNING",
    ),
    level="INFO",
)

logger.info("User logged in")  # Not sent to Sentry
logger.warning("Rate limit hit")  # Sent to Sentry
logger.error("Payment failed")  # Sent to Sentry
```
