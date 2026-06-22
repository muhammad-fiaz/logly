---
title: Multiple Sinks
description: Route log records to multiple outputs with different levels and formats.
---

# Multiple Sinks

Add several sinks to write the same logs to different destinations.

## Console + File

```python
from logly import logger

# Console at INFO
logger.add("stderr", level="INFO")

# File at DEBUG with rotation
logger.add("app.log", level="DEBUG", rotation="daily")

logger.info("Goes to both console and file")
logger.debug("Only to file")
logger.complete()
```

## Error-Only File

```python
from logly import logger

logger.add("stderr", level="INFO")
logger.add("errors.log", level="ERROR")
logger.add("audit.json", serialize=True, level="WARNING")

logger.info("Console only")
logger.warning("Console + audit.json")
logger.error("Console + errors.log + audit.json")
logger.complete()
```

## Per-Sink Formatting

```python
from logly import logger

# Concise console format
logger.add("stderr", format="{level:<8} | {message}")

# Verbose file format
logger.add(
    "verbose.log",
    format="{time} | {level} | {name}:{function}:{line} - {message}",
)

logger.info("Two formats for the same record")
logger.complete()
```

::: tip Remove sinks dynamically
Store the sink ID returned by `logger.add()` and call `logger.remove(sink_id)` when no longer needed.
:::
