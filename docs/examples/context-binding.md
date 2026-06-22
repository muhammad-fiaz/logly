---
title: Context Binding
description: Attach persistent key-value pairs to log records.
---

# Context Binding

Bind metadata to loggers so every record carries contextual information.

## `bind()` - Persistent Context

```python
from logly import logger

bound = logger.bind(user_id="12345", request_id="abc-789")
bound.info("User logged in")
# Output includes: user_id=12345 request_id=abc-789
logger.complete()
```

## `contextualize()` - Scoped Context

```python
from logly import logger

with logger.contextualize(session_id="xyz-000", env="prod"):
    logger.info("Inside session")
    logger.info("Still in session")
# Context restored after block
logger.complete()
```

## `patch()` - Record Modification

```python
from logly import logger

def add_version(record):
    record["extra"]["version"] = "2.1.0"
    record["extra"]["deploy"] = "eu-west-1"

logger.add("app.log", patch=add_version)
logger.info("Patched record")
logger.complete()
```

## Scoped Child Logger

```python
from logly import logger

child = logger.bind(component="auth")
child.info("Authentication started")

child2 = child.bind(action="login")
child2.info("Login attempt")
# Both component=auth and action=login appear
logger.complete()
```

::: tip Use context for tracing
Bind `request_id` or `trace_id` at the start of a request to correlate all logs within it.
:::
