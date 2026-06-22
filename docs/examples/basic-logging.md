---
title: Basic Logging
description: Log messages at all 10 built-in log levels with simple examples.
---

# Basic Logging

Logly provides 10 built-in log levels, from the most verbose TRACE to the most severe FATAL.

## Log at Every Level

```python
from logly import logger

logger.trace("Variables: x=1, y=2")
logger.debug("Loading configuration...")
logger.info("Application started")
logger.notice("Config reloaded")
logger.success("Deployment complete!")
logger.warning("Memory usage at 85%")
logger.error("Connection refused")
logger.fail("Request timeout")
logger.critical("Database unreachable!")
logger.fatal("Process terminated!")
logger.complete()  # flush pending writes
```

::: tip Use `logger.complete()`
Always call `logger.complete()` before exiting to flush any buffered output.
:::

## Format Strings

```python
from logly import logger

user = "alice"
logger.info("User {} logged in", user)
logger.debug("Processing {} items in {}ms", 42, 120)
logger.error("Failed to connect to {}:{}/{}", "db.local", 5432, "mydb")
```

## Custom Format

```python
from logly import logger

sink_id = logger.add(
    "app.log",
    format="{time:HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}",
)
logger.info("Custom formatted message")
logger.complete()
logger.remove(sink_id)
```

::: info
`{time}` supports tokens like `YYYY`, `MM`, `DD`, `HH`, `mm`, `ss`.
:::
