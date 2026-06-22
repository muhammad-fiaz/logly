---
title: Custom Log Levels
description: Register custom log levels with priorities and colors.
---

# Custom Log Levels

Define your own log levels beyond the built-in 11.

## Register a Custom Level

```python
from logly import logger

logger.level("AUDIT", no=25, color="<magenta>")
logger.level("METRIC", no=15, color="<cyan>")

logger.log("AUDIT", "User action recorded")
logger.log("METRIC", "Request latency: 42ms")
logger.complete()
```

## Override Existing Colors

```python
from logly import logger

logger.level("DEBUG", color="<blue><bold>")
logger.level("WARNING", color="<red><bold>")

logger.debug("Blue and bold")
logger.warning("Red and bold")
logger.complete()
```

## Use Custom Levels with Filters

```python
from logly import logger

logger.level("SECURITY", no=45, color="<red><bold>")

sink_id = logger.add(
    "security.log",
    level="SECURITY",  # only SECURITY and above
    rotation="daily",
)

logger.log("SECURITY", "Unauthorized access attempt")
logger.complete()
logger.remove(sink_id)
```

::: info
Level priority (`no`) determines filtering: lower values are more verbose. Set custom levels between existing ones (e.g., 15 between DEBUG=10 and INFO=20).
:::
