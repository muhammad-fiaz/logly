---
title: Stdlib Logging Integration
description: Route Python logging module through Logly
---

# Stdlib Logging Integration

Route Python's `logging` module through Logly using `InterceptHandler`.

## Basic Setup

```python
import logging
from logly.integrations.stdlib import InterceptHandler

# Route all stdlib logging through Logly
logging.basicConfig(
    handlers=[InterceptHandler()],
    level=logging.INFO,
    format="",
)

# Now stdlib loggers go through Logly
logging.getLogger("uvicorn").info("Request processed")
logging.getLogger("django").warning("Deprecated feature used")
```

## With FastAPI/Uvicorn

```python
import logging
from fastapi import FastAPI
from logly.integrations.stdlib import InterceptHandler

app = FastAPI()

# Route uvicorn logging through Logly
logging.basicConfig(
    handlers=[InterceptHandler()],
    level=logging.INFO,
    format="",
)
logging.getLogger("uvicorn").handlers = [InterceptHandler()]
logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
```

## With Django

```python
# settings.py
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "logly": {
            "class": "logly.integrations.stdlib.InterceptHandler",
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["logly"],
        "level": "INFO",
    },
}
```

## Level Mapping

`InterceptHandler` automatically maps Python log levels to Logly levels:

| Python Level | Logly Level |
|--------------|-------------|
| `logging.DEBUG` | `DEBUG` |
| `logging.INFO` | `INFO` |
| `logging.WARNING` | `WARNING` |
| `logging.ERROR` | `ERROR` |
| `logging.CRITICAL` | `CRITICAL` |

## Custom Level Mapping

```python
import logging
from logly.integrations.stdlib import InterceptHandler
from logly import logger

# Register a custom level
logger.level("AUDIT", no=25)

# Add custom mapping
class CustomInterceptHandler(InterceptHandler):
    _LEVEL_MAP = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
        25: "AUDIT",  # Custom level
    }
```

## Third-Party Library Integration

```python
import logging
from logly.integrations.stdlib import InterceptHandler

# Route third-party loggers
for name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]:
    logging.getLogger(name).handlers = [InterceptHandler()]
    logging.getLogger(name).setLevel(logging.INFO)
```
