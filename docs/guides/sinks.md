---
title: Sinks
description: Configure console, file, callable, and write-style sinks in Logly
---

# Sinks

Sinks are destinations for log messages. Logly supports console streams, file paths, callable functions, and write-style objects.

## Console Sinks

```python
from logly import logger

# Stderr (default)
logger.add("stderr", level="INFO")

# Stdout
logger.add("stdout", level="DEBUG")

# With color
logger.add("stderr", level="INFO", colorize=True)

# With custom format
logger.add(
    "stderr",
    level="INFO",
    format="{time:HH:mm:ss} | {level:<8} | {message}",
    colorize=True,
)
```

## File Sinks

```python
from logly import logger
from pathlib import Path

# Basic file sink
logger.add("app.log")

# With level filter
logger.add("app.log", level="DEBUG")

# With format
logger.add(
    "app.log",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
)

# With Path object
logger.add(Path("logs") / "app.log")

# Overwrite mode (instead of append)
logger.add("app.log", mode="w")

# Custom encoding
logger.add("app.log", encoding="utf-8")

# Delay file opening until first write
logger.add("app.log", delay=True)
```

## Callable Sinks

```python
from logly import logger

# Simple callable
def my_sink(message: str) -> None:
    print(f"LOG: {message}", end="")

logger.add(my_sink, level="INFO")

# With capture
messages: list[str] = []
logger.add(lambda m: messages.append(m), level="DEBUG")

# Send to external service
def send_to_datadog(message: str) -> None:
    # Your Datadog API call here
    pass

logger.add(send_to_datadog, level="ERROR")
```

## Write-Style Sinks

```python
from logly import logger

# Any object with a write() method
class CustomWriter:
    def write(self, message: str) -> None:
        print(f"[CUSTOM] {message}", end="")
    def flush(self) -> None:
        pass

logger.add(CustomWriter(), level="INFO")

# StringIO
from io import StringIO
buffer = StringIO()
logger.add(buffer, level="DEBUG")
```

## Per-Sink Options

Every `add()` call accepts these options:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str \| int` | `"DEBUG"` | Minimum log level |
| `format` | `str \| Callable` | `None` | Format template or callable |
| `filter` | `str \| Callable \| Mapping` | `None` | Filter rule |
| `patch` | `Callable[[dict], None]` | `None` | Per-sink record mutator |
| `serialize` | `bool` | `False` | Output JSON |
| `pretty_json` | `bool \| PrettyJsonConfig \| None` | `None` | Pretty JSON configuration |
| `colorize` | `bool \| None` | `None` | ANSI color override |
| `rotation` | `str \| int \| object` | `None` | Rotation policy |
| `retention` | `int \| str \| object` | `None` | Retention policy |
| `compression` | `str \| object` | `None` | Compression codec |
| `enqueue` | `bool` | `False` | Background worker |
| `encoding` | `str` | `"utf-8"` | File encoding |
| `delay` | `bool` | `False` | Delay file opening |
| `catch` | `bool` | `True` | Catch sink errors |
| `mode` | `str` | `"a"` | File mode (`"a"` or `"w"`) |
| `backtrace` | `bool` | `False` | Enable backtrace on exceptions |
| `diagnose` | `bool` | `False` | Enable diagnostic mode |
| `context` | `str \| multiprocessing.context.BaseContext \| None` | `None` | Multiprocessing context |
| `buffering` | `int` | `-1` | File buffering |
| `loop` | `asyncio.AbstractEventLoop \| None` | `None` | Event loop for async sinks |
| `opener` | `Callable \| None` | `None` | Custom file opener |

## Removing Sinks

```python
from logly import logger

# Add a sink
sink_id = logger.add("app.log", level="INFO")

# Remove specific sink
logger.remove(sink_id)

# Remove all sinks
logger.remove()
```

## Flushing

```python
from logly import logger

logger.add("app.log", enqueue=True)
logger.info("Important message")

# Flush all sinks (drains background queues)
logger.complete()
```

::: warning
Always call `logger.complete()` before your process exits to ensure all queued messages are written.
:::

## Multiple Sinks Example

```python
from logly import logger

# Console output
logger.add("stderr", level="INFO", colorize=True)

# Application logs
logger.add(
    "logs/app.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
    rotation="daily",
    retention="30 days",
    compression="gzip",
)

# Error monitoring
logger.add(
    "logs/errors.log",
    level="ERROR",
    rotation="daily",
    retention="90 days",
    serialize=True,
)

# Audit trail
logger.add(
    "logs/audit.log",
    level="INFO",
    filter={"channel": "audit"},
    rotation="daily",
    retention="365 days",
)

logger.info("This goes to console, app.log, and audit.log (if bound)")
logger.error("This goes to console, app.log, and errors.log")
logger.complete()
```
