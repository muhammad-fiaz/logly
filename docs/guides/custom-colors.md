---
title: Custom Colors
description: Guide to customizing log level colors in Logly with ANSI escape codes.
---

# Custom Colors

Logly supports custom colors for all log levels using ANSI escape codes. No extra dependencies required - colors work natively in any terminal that supports ANSI.

## Built-in Level Colors

Each built-in level has a default color:

| Level | Color |
|-------|-------|
| TRACE | Cyan (dim) |
| DEBUG | Blue |
| INFO | Green |
| NOTICE | Cyan |
| SUCCESS | Green |
| AUDIT | Magenta |
| WARNING | Yellow |
| ERROR | Red |
| FAIL | Red |
| CRITICAL | Bold Red |
| FATAL | Bold Red |

## Custom Colors with `level()`

Override the default color for any level:

```python
from logly import logger

# Override built-in level color
logger.level("DEBUG", color="<blue><bold>")
logger.level("WARNING", color="<yellow><bold>")

# Register new level with custom color
logger.level("SECURITY", no=45, color="<red><bold>")
logger.level("PERF", no=10, color="<cyan><bold>")

# Use new levels
logger.log("SECURITY", "Unauthorized access attempt")
logger.log("PERF", "Request took 200ms")
```

## ANSI Escape Codes

Logly uses standard ANSI escape codes. The `color` parameter accepts ANSI markup:

| Markup | Meaning |
|--------|---------|
| `<red>` | Red text |
| `<green>` | Green text |
| `<blue>` | Blue text |
| `<yellow>` | Yellow text |
| `<cyan>` | Cyan text |
| `<magenta>` | Magenta text |
| `<bold>` | Bold text |
| `<dim>` | Dim text |
| `<underline>` | Underlined text |
| `<white>` | White text |

Combine them:

```python
logger.level("CRITICAL", color="<red><bold><underline>")
```

## Rich-Enhanced Colors

If you have [Rich](https://rich.readthedocs.io/) installed, Logly uses Rich's color engine for richer rendering. Without Rich, standard ANSI codes are used - no functionality is lost.

```bash
# Install Rich for enhanced colors
uv add rich
# or
pip install rich
```

With Rich installed:

```python
from logly.integrations.rich import LoglyRichSink

logger.add(LoglyRichSink(), level="DEBUG", colorize=True)
```

::: info
Custom colors work with or without Rich. Rich enhances the visual quality but is not required.
:::

## Example: Full Color Configuration

```python
from logly import logger

# Configure custom colors for all levels
logger.level("TRACE", no=5, color="<dim><cyan>")
logger.level("DEBUG", no=10, color="<blue>")
logger.level("INFO", no=20, color="<green>")
logger.level("NOTICE", no=25, color="<cyan><bold>")
logger.level("SUCCESS", no=30, color="<green><bold>")
logger.level("AUDIT", no=35, color="<magenta>")
logger.level("WARNING", no=40, color="<yellow>")
logger.level("ERROR", no=50, color="<red>")
logger.level("FAIL", no=55, color="<red><bold>")
logger.level("CRITICAL", no=60, color="<red><bold><underline>")
logger.level("FATAL", no=70, color="<red><bold><blink>")

logger.add("colored.log", level="TRACE", colorize=True)

logger.trace("Trace message")
logger.debug("Debug message")
logger.info("Info message")
logger.notice("Notice message")
logger.success("Success message")
logger.log("AUDIT", "Audit message")
logger.warning("Warning message")
logger.error("Error message")
logger.fail("Fail message")
logger.critical("Critical message")
```

## Format Tokens with Colors

Use `{level}` in your format to show the colored level name:

```python
logger.add("app.log", level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}", colorize=True)
```
