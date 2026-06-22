---
title: Exception Handling
description: Catch, log, and handle exceptions with the catch() API.
---

# Exception Handling

Logly provides `catch()` as both a decorator and context manager.

## Context Manager

```python
from logly import logger

with logger.catch():
    result = 1 / 0
logger.info("Execution continues")
logger.complete()
```

## Decorator

```python
from logly import logger

@logger.catch()
def process():
    raise ValueError("Invalid input")

process()
logger.complete()
```

## Custom Level and Message

```python
from logly import logger

with logger.catch(level="CRITICAL"):
    database.connect()
logger.complete()
```

## Re-raise After Logging

```python
from logly import logger

with logger.catch(reraise=True):
    risky_operation()
logger.complete()
```

::: warning Don't swallow exceptions silently
Use `reraise=True` in production when you want to log the error but still propagate it.
:::

## Exclude Specific Exceptions

```python
from logly import logger

with logger.catch(exclude=ValueError):
    raise TypeError("This will propagate")
logger.complete()
```

::: info
The `onerror` callback lets you run custom logic when an exception is caught.
:::
