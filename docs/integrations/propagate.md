---
title: Propagate
description: Propagate Logly records back to Python's standard logging module.
---

# Propagate

`PropagateHandler` bridges Logly messages back to Python's `logging` module.

## Installation

No additional dependencies required. This integration uses Python's standard library.

## Quick Setup

```python
from logly import logger
from logly.integrations.propagate import PropagateHandler

logger.add(PropagateHandler(), level="INFO")
```

## Manual Setup

```python
import logging
from logly import logger
from logly.integrations.propagate import PropagateHandler

handler = PropagateHandler(name="myapp", level=logging.INFO)
logger.add(handler, level="INFO")
```

## Parameters

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `str` | `"logly"` | Name of the stdlib logger to emit through |
| `level` | `int` | `logging.NOTSET` | Minimum log level |

## Tips

- Use this when you need Logly output to appear in stdlib log handlers.
- Combine with `logging.basicConfig()` for default console output.
- Useful for forwarding logs to third-party logging services.

## Full Example

```python
import logging
from logly import logger
from logly.integrations.propagate import PropagateHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logger.add(PropagateHandler(name="myapp"), level="INFO")
logger.add("app.log", level="DEBUG", rotation="10 MB")

logger.info("This appears in both Logly file and stdlib console output")
```
