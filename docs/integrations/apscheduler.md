---
title: APScheduler
description: Route APScheduler job logs through Logly.
---

# APScheduler

`APSchedulerHandler` is a `logging.Handler` that routes APScheduler log records through Logly. A convenience function `setup_apscheduler_logging()` configures everything in one call.

## Installation

This integration requires the `apscheduler` package.

::: code-group

```bash [uv]
uv add logly[apscheduler]
```

```bash [pip]
pip install "logly[apscheduler]"
```

```bash [uv (without extras)]
uv add apscheduler
```

```bash [pip (without extras)]
pip install apscheduler
```

:::

::: warning Missing Dependency
If `apscheduler` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'apscheduler'
```
:::

## Quick Setup

```python
from logly.integrations.apscheduler import setup_apscheduler_logging

setup_apscheduler_logging()
```

## Manual Setup

```python
import logging
from logly.integrations.apscheduler import APSchedulerHandler

handler = APSchedulerHandler()
logging.getLogger("apscheduler").addHandler(handler)
```

## `setup_apscheduler_logging()`

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level for APScheduler logs |

## Tips

- Use `setup_apscheduler_logging()` for the simplest integration.
- Set `level="WARNING"` to suppress routine scheduler start/stop messages.

## Full Example

```python
from apscheduler.schedulers.background import BackgroundScheduler
from logly import logger
from logly.integrations.apscheduler import setup_apscheduler_logging

setup_apscheduler_logging(level="INFO")

scheduler = BackgroundScheduler()

@scheduler.scheduled_job("interval", hours=1)
def cleanup():
    logger.info("Running cleanup job")

scheduler.start()
```
