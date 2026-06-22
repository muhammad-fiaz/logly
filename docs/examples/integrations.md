---
title: Integrations
description: Use Logly with FastAPI, Django, Rich, structlog, and stdlib logging.
---

# Integrations

Logly integrates with popular frameworks and libraries.

## FastAPI

```python
from fastapi import FastAPI
from logly.integrations.fastapi import LoglyMiddleware

app = FastAPI()
app.add_middleware(LoglyMiddleware)

@app.get("/")
def root():
    return {"status": "ok"}
```

## Django

```python
# settings.py
LOGGING = {
    "handlers": ["logly"],
    "logly": {
        "class": "logly.integrations.django.LoglyHandler",
        "level": "INFO",
    },
}

MIDDLEWARE = [
    "logly.integrations.django.LoglyMiddleware",
    # ... other middleware
]
```

## Rich Console

```python
from logly import logger
from logly.integrations.rich import LoglyRichSink

sink_id = logger.add(LoglyRichSink(), colorize=True)
logger.info("Rich-formatted output!")
logger.complete()
logger.remove(sink_id)
```

## Stdlib Logging

```python
import logging
from logly.integrations.stdlib import InterceptHandler

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
logging.getLogger("uvicorn").info("Routed through Logly!")
```

::: tip Framework middleware
Framework integrations automatically bind request context (path, method, status code) to each log record.
:::
