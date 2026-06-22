---
title: Production Configuration
description: Production-ready logging setup with rotation, retention, and compression.
---

# Production Configuration

A robust logging setup suitable for production deployments.

## Full Production Setup

```python
import os
from logly import logger

LOG_DIR = os.environ.get("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Application logs - daily rotation, 30-day retention, gzip
logger.add(
    f"{LOG_DIR}/app.log",
    level="INFO",
    rotation="daily",
    retention="30 days",
    compression="gzip",
    serialize=True,
    enqueue=True,
    format="{time} | {level} | {name}:{function}:{line} - {message}",
)

# Error logs - separate file, 90-day retention
logger.add(
    f"{LOG_DIR}/errors.log",
    level="ERROR",
    rotation="daily",
    retention="90 days",
    compression="gzip",
    enqueue=True,
)

# Debug logs - size-based, 3 copies
logger.add(
    f"{LOG_DIR}/debug.log",
    level="DEBUG",
    rotation="50 MB",
    retention=3,
    enqueue=True,
)

logger.info("Production logging configured")
logger.complete()
```

## Using `root_dir`

```python
from logly import logger

logger.add(
    "app.log",
    level="INFO",
    rotation="daily",
    retention=14,
    root_dir="logs/",  # all rotated files go here
)
logger.info("Root dir for rotated files")
logger.complete()
```

## Disable Autoinit

```python
import os
os.environ["LOGLY_AUTOINIT"] = "0"

from logly import logger

# Logger is silent until you add a sink
logger.add("app.log")
logger.info("Now active")
logger.complete()
```

::: warning Always use `enqueue=True` in production
Enqueue mode prevents blocking your application threads on I/O. It's essential for high-throughput services.
:::

::: tip Combine rotation + retention + compression
This trio keeps disk usage bounded while preserving logs for auditing.
:::
