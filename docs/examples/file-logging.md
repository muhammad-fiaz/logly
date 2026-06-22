---
title: File Logging
description: Write log output to files with encoding and mode options.
---

# File Logging

Add file sinks to persist logs to disk alongside or instead of console output.

## Simple File Sink

```python
from logly import logger

sink_id = logger.add("app.log")
logger.info("This goes to both console and app.log")
logger.complete()
logger.remove(sink_id)
```

## File with Options

```python
from logly import logger

sink_id = logger.add(
    "app.log",
    level="DEBUG",
    format="{time} | {level} | {message}",
    encoding="utf-8",
    mode="w",  # overwrite on startup
)
logger.debug("Debug to file")
logger.info("Info to file")
logger.complete()
logger.remove(sink_id)
```

::: tip File modes
- `w` — overwrite on startup (default)
- `a` — append to existing file
:::

## Custom Opener

```python
from logly import logger

def my_opener(path, mode):
    import os
    fd = os.open(path, os.O_WRONLY | os.O_CREAT, 0o644)
    return os.fdopen(fd, mode)

sink_id = logger.add("secure.log", opener=my_opener)
logger.info("Written with custom opener")
logger.complete()
logger.remove(sink_id)
```

::: info
The `opener` parameter lets you control file creation flags, permissions, or use alternate I/O.
:::
