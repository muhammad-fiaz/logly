---
title: Stdlib Logging
description: Bridge Python's logging module to Logly.
---

# Stdlib Logging

`InterceptHandler` routes Python `logging` records through Logly, replacing standard logging handlers. Maps all 5 standard levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).

## Installation

No additional dependencies required. This integration uses Python's standard library.

## Usage

```python
import logging
from logly.integrations.stdlib import InterceptHandler

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
```

## Specific Logger

```python
import logging
from logly.integrations.stdlib import InterceptHandler

uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.handlers = [InterceptHandler()]
```

## Full Example

```python
import logging
from logly import logger
from logly.integrations.stdlib import InterceptHandler

# Configure root logger
logging.basicConfig(
    handlers=[InterceptHandler()],
    level=logging.INFO,
)

# Route specific loggers
for name in ("uvicorn", "werkzeug", "sqlalchemy"):
    log = logging.getLogger(name)
    log.handlers = [InterceptHandler()]
    log.propagate = False

# Use stdlib logging normally
logging.info("Application started")
logging.warning("Something seems off")
logging.error("Something went wrong")
```
