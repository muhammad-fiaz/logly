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

Binary streams are adapted the same way: `logger.add(open("app.log", "w+b"))`
decodes with `encoding` (default `"utf-8"`) without ever closing your object.
Non-UTF-8 encodings cannot be combined with `rotation`, `retention`,
`compression`, `delay`, or `watch`.

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


def custom_opener(path, flags):
    # An opener receives the path and os.open-style flags and returns a
    # file descriptor.
    return os.open(path, flags, 0o644)


logger.add("app.log", opener=custom_opener)
```

::: info
A custom `opener`, non-default `buffering`, or non-UTF-8 `encoding` opens
the file in Python, so it cannot be combined with `rotation`, `retention`,
`compression`, `delay`, or `watch`, which require the native file sink.
:::

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
