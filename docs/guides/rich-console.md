---
title: Rich Console
description: Rich-formatted console output integration
---

# Rich Console

Logly integrates with [Rich](https://github.com/Textualize/rich) for beautiful, formatted console output.

## Basic Setup

```python
from logly import logger
from logly.integrations.rich import LoglyRichSink

sink_id = logger.add(LoglyRichSink(), colorize=True)
logger.info("Rich-formatted output!")
logger.success("Operation completed!")
logger.error("Something went wrong")
logger.complete()
logger.remove(sink_id)
```

## Installation

```bash
pip install rich
```

## Rich Sink Options

```python
from logly import logger
from logly.integrations.rich import LoglyRichSink

# Default: writes to stderr
logger.add(LoglyRichSink(), colorize=True)

# Custom file output
import sys
sink = LoglyRichSink(file=sys.stdout)
logger.add(sink, level="DEBUG")
```

## With Logly Formatting

```python
from logly import logger
from logly.integrations.rich import LoglyRichSink

# Rich sink with custom format
logger.add(
    LoglyRichSink(),
    format="{time:HH:mm:ss} | {level:<8} | {message}",
    colorize=True,
)

logger.info("Formatted with Logly, rendered with Rich")
```

## With Context Binding

```python
from logly import logger
from logly.integrations.rich import LoglyRichSink

logger.add(LoglyRichSink(), colorize=True, level="DEBUG")

# Bind context
app_logger = logger.bind(service="api", version="1.0")
app_logger.info("Request processed")
# Output includes context fields with Rich formatting
```

## Example Output

Rich-formatted output includes styled level names and colored timestamps:

```
14:30:45 | INFO     | Application started
14:30:45 | SUCCESS  | Operation completed!
14:30:45 | WARNING  | Disk space running low
14:30:45 | ERROR    | Failed to connect to database
```

## Production Setup

```python
from logly import logger
from logly.integrations.rich import LoglyRichSink

# Development: Rich console
if __debug__:
    logger.add(
        LoglyRichSink(),
        level="DEBUG",
        format="{time:HH:mm:ss} | {level:<8} | {message}",
        colorize=True,
    )

# Production: File logging
logger.add(
    "logs/app.log",
    level="INFO",
    rotation="daily",
    retention="30 days",
    compression="gzip",
)

logger.info("Application started")
logger.complete()
```
