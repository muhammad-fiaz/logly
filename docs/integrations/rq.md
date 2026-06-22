---
title: RQ (Redis Queue)
description: Route RQ worker job logs through Logly.
---

# RQ (Redis Queue)

`RQHandler` is a `logging.Handler` that routes RQ (Redis Queue) log records through Logly. A convenience function `setup_rq_logging()` configures both the `rq` and `rq.worker` loggers.

## Installation

This integration requires the `rq` package.

::: code-group

```bash [uv]
uv add logly[rq]
```

```bash [pip]
pip install "logly[rq]"
```

```bash [uv (without extras)]
uv add rq
```

```bash [pip (without extras)]
pip install rq
```

:::

::: warning Missing Dependency
If `rq` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'rq'
```
:::

## Quick Setup

```python
from logly.integrations.rq import setup_rq_logging

setup_rq_logging()
```

## Manual Setup

```python
import logging
from logly.integrations.rq import RQHandler

handler = RQHandler()
logging.getLogger("rq").addHandler(handler)
logging.getLogger("rq.worker").addHandler(handler)
```

## `setup_rq_logging()`

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level for RQ logs |

## Tips

- Use `setup_rq_logging()` for the simplest integration.
- RQ worker processes are forked, so configure logging after the worker starts.

## Full Example

```python
import logging
from logly import logger
from logly.integrations.rq import setup_rq_logging

setup_rq_logging(level="INFO")

logger.add("worker.log", level="DEBUG", rotation="10 MB")
```
