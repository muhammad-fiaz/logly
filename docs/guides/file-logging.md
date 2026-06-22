---
title: File Logging
description: Configuring file sinks with encoding, modes, and custom openers
---

# File Logging

## Basic File Sink

```python
from logly import logger

# Simple file sink
logger.add("app.log", level="INFO")
logger.info("This goes to app.log")
```

::: tip
By default, Logly creates the file if it doesn't exist and appends to it.
:::

## Custom Encoding

```python
logger.add("app.log", encoding="utf-8")
logger.add("legacy.log", encoding="latin-1")
```

## File Modes

```python
# Append mode (default)
logger.add("app.log", mode="a")

# Write mode (truncate on open)
logger.add("app.log", mode="w")
```

## Custom Opener

Use the `opener` parameter to customize how files are opened (e.g., for custom permissions):

```python
import os

def custom_opener(path, mode):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT, 0o644)
    return os.fdopen(fd, mode)

logger.add("app.log", opener=custom_opener)
```

## Delay Opening

```python
# Don't open the file until the first message is logged
logger.add("app.log", delay=True)
```

## Combining with Rotation

```python
logger.add(
    "app.log",
    level="INFO",
    rotation="100 MB",
    retention="30 days",
    compression="gzip",
    encoding="utf-8",
    mode="a",
)
```

## Using root_dir

Set a default root directory so all file paths are relative to it:

```python
logger.root_dir("/var/log/myapp")
logger.add("app.log")  # Creates /var/log/myapp/app.log
logger.add("errors.log", level="ERROR")  # Creates /var/log/myapp/errors.log
```

::: info
`root_dir()` creates the directory if it doesn't exist.
:::
