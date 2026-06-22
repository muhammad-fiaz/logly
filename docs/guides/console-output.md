---
title: Console & Output Control
description: Enable, disable, and configure console and file output in Logly
---

# Console & Output Control

Logly gives you full control over where logs go. You can enable console output, disable it, route logs to files only, or combine multiple destinations.

## Disabling Console Output

By default, Logly outputs to `stderr`. To disable console output and log to files only:

```python
import sys
from logly import logger

# Remove the default stderr handler
logger.remove()

# Add file sinks only
logger.add("app.log", level="DEBUG")
logger.add("errors.log", level="ERROR")

logger.info("This goes to files only, not the console")
```

### Disable Console Globally at Import

Set the `LOGLY_AUTOINIT` environment variable to `false` before importing:

```python
import os
os.environ["LOGLY_AUTOINIT"] = "false"

from logly import logger

# No sinks are registered yet
logger.add("app.log", level="INFO")
logger.info("File only")
```

Or in your shell:

```bash
export LOGLY_AUTOINIT=false
python app.py
```

## Enabling Console Output

Add a console sink at any time:

```python
from logly import logger

# Remove defaults first
logger.remove()

# Add stderr
logger.add("stderr", level="INFO", colorize=True)

# Or add stdout
logger.add("stdout", level="DEBUG", colorize=True)

logger.info("Visible on console")
```

## Stdout vs Stderr

| Sink | Stream | Typical Use |
|------|--------|-------------|
| `"stderr"` or `sys.stderr` | Standard error | Default, error messages |
| `"stdout"` or `sys.stdout` | Standard output | Application output |

```python
import sys
from logly import logger

logger.remove()

# Info and above to stdout
logger.add("stdout", level="INFO", colorize=True)

# Errors to stderr
logger.add("stderr", level="ERROR", colorize=True)
```

## Colorize Control

The `colorize` parameter controls ANSI color output:

```python
from logly import logger

logger.remove()

# Force colors on (for pipes, redirect)
logger.add("stderr", colorize=True)

# Force colors off (for files)
logger.add("app.log", colorize=False)

# Auto-detect (default for console sinks)
logger.add("stderr", colorize=None)
```

| `colorize` | Behavior |
|------------|----------|
| `None` | Auto-detect via `.isatty()` |
| `True` | Always render ANSI colors |
| `False` | Strip all color tags |

## File-Only Logging

```python
from logly import logger

# Remove all existing sinks
logger.remove()

# Application log
logger.add(
    "logs/app.log",
    level="DEBUG",
    rotation="daily",
    retention="30 days",
    compression="gzip",
)

# Error log
logger.add(
    "logs/errors.log",
    level="ERROR",
    rotation="daily",
    retention="90 days",
)

logger.info("This goes to files only")
logger.error("This goes to both files")
```

## Multiple Destinations

```python
from logly import logger

logger.remove()

# Console with colors
logger.add("stderr", level="INFO", colorize=True)

# File without colors
logger.add(
    "app.log",
    level="DEBUG",
    rotation="daily",
    retention="30 days",
)

# JSON to another file
logger.add(
    "app.json",
    level="INFO",
    serialize=True,
    rotation="daily",
)

logger.info("Goes to console, app.log, and app.json")
```

## Disable/Enable Logger Names

Disable all log emission for a specific logger name:

```python
from logly import logger

# Disable logging for "myapp" name
logger.disable("myapp")

# These are silently dropped
myapp = logger.bind(name="myapp")
myapp.info("This is never logged")  # Silently dropped

# Re-enable later
logger.enable("myapp")
myapp.info("This is logged again")
```

## configure() for Bulk Control

```python
from logly import logger

# Replace all sinks and enable/disable names
logger.configure(
    handlers=[
        {"sink": "stderr", "level": "INFO", "colorize": True},
        {"sink": "app.log", "level": "DEBUG", "rotation": "daily"},
    ],
    activation=[
        ("myapp", True),     # Enable myapp
        ("debug", False),    # Disable debug
    ],
)
```

## Environment Variable Control

| Variable | Effect |
|----------|--------|
| `LOGLY_AUTOINIT=false` | Disable default stderr sink at import |
| `LOGLY_LEVEL=WARNING` | Override minimum level |
| `LOGLY_COLORIZE=NO` | Disable colors globally |
| `LOGLY_SERIALIZE=YES` | Enable JSON output globally |
