---
title: Formatting
description: Customize log output with format tokens, templates, and color markup.
---

# Formatting

Control exactly how log records appear using format strings and tokens.

## Format Tokens

```python
from logly import logger

sink_id = logger.add(
    "formatted.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}",
)
logger.info("Detailed format")
logger.complete()
logger.remove(sink_id)
```

Common tokens: `{time}`, `{level}`, `{name}`, `{function}`, `{line}`, `{message}`, `{extra}`.

## Callable Formatter

```python
from logly import logger

def custom_fmt(record):
    return f"[{record['time'].timestamp():.3f}] {record['level'].name}: {record['message']}"

sink_id = logger.add("custom.log", format=custom_fmt)
logger.info("Callable formatter active")
logger.complete()
logger.remove(sink_id)
```

## Color Markup

```python
from logly import logger

sink_id = logger.add("stderr", colorize=True)
logger.info("<green>Success</green> message")
logger.warning("<yellow><bold>Important warning</bold></yellow>")
logger.complete()
logger.remove(sink_id)
```

::: tip Color tags
Use `<red>`, `<green>`, `<blue>`, `<yellow>`, `<magenta>`, `<cyan>`, `<bold>`, `<dim>`, `<italic>`.
:::
