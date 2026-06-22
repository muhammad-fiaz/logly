---
title: Getting Started
description: Install and start using Logly in minutes
---

# Getting Started

Logly is a high-performance logging library for Python powered by a Rust engine built with PyO3. It provides a clean API with 10 built-in log levels, flexible sinks, file rotation, compression, and first-class framework integrations.

## Installation

::: code-group

```bash [pip]
pip install logly
```

```bash [uv]
uv add logly
```

```bash [Poetry]
poetry add logly
```

```bash [From Source]
git clone https://github.com/muhammad-fiaz/logly.git
cd logly
uv sync
uv run maturin develop
```

:::

### System Requirements

- Python 3.10 or later
- Rust toolchain (for building from source)
- Supported platforms: Linux, macOS, Windows

### Verifying Installation

```python
import logly
print(logly.__version__)
```

## Basic Usage

### Start Logging

```python
from logly import logger

logger.info("Application started")
logger.debug("Debug info")
logger.warning("Something looks off")
logger.error("An error occurred")
logger.success("Operation completed!")
```

### Use Different Levels

Logly has 10 built-in levels organized by severity:

| Level | Numeric | Description |
|-------|---------|-------------|
| `TRACE` | 5 | Finer-grained than DEBUG |
| `DEBUG` | 10 | Diagnostic information |
| `INFO` | 20 | General information |
| `NOTICE` | 25 | Normal but significant |
| `SUCCESS` | 30 | Successful operations |
| `WARNING` | 40 | Unexpected behavior |
| `ERROR` | 50 | Serious problems |
| `FAIL` | 55 | Operation failures |
| `CRITICAL` | 60 | Critical system errors |
| `FATAL` | 70 | Unrecoverable errors |

```python
from logly import logger

logger.trace("Trace message")
logger.debug("Debug message")
logger.info("Info message")
logger.notice("Notice message")
logger.success("Success message")
logger.warning("Warning message")
logger.error("Error message")
logger.fail("Fail message")
logger.critical("Critical message")
logger.fatal("Fatal message")
```

### Set the Minimum Level

```python
from logly import logger

# Only show WARNING and above
logger.add("stdout", level="WARNING")
```

## Log to Files

### Add a File Sink

```python
from logly import logger

# Basic file logging
logger.add("app.log")

# With rotation and retention
logger.add(
    "app.log",
    level="INFO",
    rotation="daily",
    retention="30 days",
    compression="gzip",
)

logger.info("This goes to the file")
```

### Multiple Sinks

```python
from logly import logger

logger.add("app.log", level="DEBUG", rotation="daily")
logger.add("errors.log", level="ERROR", retention="90 days")
logger.add("stdout", level="INFO", colorize=True)

logger.info("All three sinks receive this")
```

## Bind Context

Attach persistent metadata to a logger:

```python
from logly import logger

user_logger = logger.bind(user_id="12345", request_id="abc-789")
user_logger.info("User logged in")
# Output includes: user_id=12345 request_id=abc-789
```

## Catch Exceptions

Automatically log exceptions without crashing:

```python
from logly import logger

with logger.catch():
    risky_operation()

# Or with options
with logger.catch(reraise=True):
    dangerous_call()

# Exclude specific exceptions
with logger.catch(exclude=ValueError):
    optional_operation()
```

## Framework Integrations

### FastAPI

```python
from fastapi import FastAPI
from logly.integrations.fastapi import LoglyMiddleware

app = FastAPI()
app.add_middleware(LoglyMiddleware)
```

### Django

```python
# settings.py
LOGGING = {
    "handlers": {
        "logly": {
            "()": "logly.integrations.django.LoglyHandler",
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["logly"],
        "level": "INFO",
    },
}
```

### Flask

```python
from flask import Flask
from logly.integrations.flask import LoglyHandler

app = Flask(__name__)
LoglyHandler().init_app(app)
```

## Async Logging

Logly handles async through queue-based workers, not asyncio. Enable with `enqueue=True`:

```python
from logly import logger

logger.add("app.log", enqueue=True)

# All log calls remain synchronous
# A background worker processes the queue
```

## Next Steps

- [Sinks](/guides/sinks) - Learn about all sink types
- [Console & Output Control](/guides/console-output) - Enable/disable console and file output
- [Source Location & Timestamps](/guides/source-location-timestamps) - Customize file info and timestamps
- [Formatting](/guides/formatting) - Customize output format
- [Filtering](/guides/filtering) - Control which messages pass through
- [Context Binding](/guides/context-binding) - Attach metadata to logs
- [Rotation & Retention](/guides/rotation-retention-compression) - Manage log files
- [Custom Levels](/guides/custom-levels) - Register your own log levels
- [Concurrency](/guides/concurrency) - Thread-safe background logging
- [Integrations](/integrations/) - Connect to FastAPI, Django, Flask, and more

## Troubleshooting

If you encounter issues, check the [Troubleshooting Guide](/guides/troubleshooting) or [FAQ](/guides/faq).
