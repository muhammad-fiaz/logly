---
title: File Logging
description: Write log output to files with all format, encoding, and mode options.
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
- `a` - append to existing file (default)
- `w` - overwrite on startup
:::

## Plain Text File (.txt)

```python
from logly import logger

sink_id = logger.add(
    "output.txt",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
)
logger.info("Plain text log file")
logger.complete()
logger.remove(sink_id)
```

## Log File (.log)

```python
from logly import logger

sink_id = logger.add(
    "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}",
)
logger.info("Standard log format")
logger.complete()
logger.remove(sink_id)
```

## JSON File

```python
from logly import logger

sink_id = logger.add(
    "structured.log",
    serialize=True,
)
logger.info("JSON log file")
logger.complete()
logger.remove(sink_id)
```

## Pretty JSON File

```python
from logly import logger

sink_id = logger.add(
    "pretty.log",
    serialize=True,
    pretty_json=True,
)
logger.info("Pretty JSON log file")
logger.complete()
logger.remove(sink_id)
```

## Pretty JSON with Custom Options

```python
from logly import logger, PrettyJsonConfig

config = PrettyJsonConfig(
    indent=2,
    sort_keys=True,
    ensure_ascii=False,
    separators=(",", ": "),
)

sink_id = logger.add(
    "custom-pretty.log",
    serialize=True,
    pretty_json=config,
)
logger.info("Custom pretty JSON log file")
logger.complete()
logger.remove(sink_id)
```

## Multiple File Sinks

```python
from logly import logger

# Console output
logger.add("stderr", colorize=True)

# Plain text file
logger.add("app.txt", format="{time} | {level} | {message}")

# JSON file
logger.add("structured.json", serialize=True)

# Pretty JSON file
logger.add("pretty.json", serialize=True, pretty_json=True)

logger.info("Goes to all four destinations")
logger.complete()
```

## File with Encoding

```python
from logly import logger

sink_id = logger.add(
    "unicode.log",
    encoding="utf-8",
    format="{time} | {level} | {message}",
)
logger.info("Unicode: こんにちは世界")
logger.complete()
logger.remove(sink_id)
```

## Delayed File Opening

```python
from logly import logger

sink_id = logger.add(
    "delayed.log",
    delay=True,  # don't open until first write
)
logger.info("File opened on first write")
logger.complete()
logger.remove(sink_id)
```

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

## Root Directory

Set a root directory for all relative file paths:

```python
from logly import logger

logger.root_dir("/var/log/myapp")

# Files are created under /var/log/myapp/
logger.add("app.log")  # /var/log/myapp/app.log
logger.add("errors.log")  # /var/log/myapp/errors.log

logger.info("Files created under root directory")
logger.complete()
```
