---
title: Lazy Evaluation
description: Defer expensive operations and message formatting until needed.
---

# Lazy Evaluation

Use `opt(lazy=True)` to defer message evaluation until the log is actually emitted.

## Lazy Message Arguments

```python
from logly import logger

def get_user_data():
    print("Expensive query executed")
    return {"name": "alice", "role": "admin"}

logger.opt(lazy=True).debug("User data: {}", get_user_data)
# "Expensive query executed" only prints if DEBUG is enabled
logger.complete()
```

## Lazy with Lambda

```python
from logly import logger

items = list(range(1000))
logger.opt(lazy=True).debug("Processing {} items", lambda: len(items))
logger.complete()
```

## Exception Capture

```python
from logly import logger

try:
    risky_operation()
except Exception:
    logger.opt(exception=True).error("Operation failed")
logger.complete()
```

::: info Performance benefit
Lazy evaluation avoids the cost of string formatting or function calls when the log level is filtered out.
:::

::: tip Combine with `exception=True`
`logger.opt(exception=True)` captures the current exception and appends the traceback automatically.
:::
