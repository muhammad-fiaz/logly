---
title: Logging Handlers
description: Use Python stdlib logging.Handler as a Logly sink
---

# Logging Handlers

Logly can use any Python `logging.Handler` instance as a sink. This enables integration with any library or service that provides a stdlib logging handler.

## Basic Usage

```python
import logging
from logly import logger

# Use any logging.Handler as a sink
handler = logging.StreamHandler()
logger.add(handler, level="INFO")
logger.info("This goes through the handler")
```

## Supported Handlers

Any `logging.Handler` subclass works:

```python
import logging
from logly import logger

# RotatingFileHandler
from logging.handlers import RotatingFileHandler
logger.add(RotatingFileHandler("app.log", maxBytes=10_000_000, backupCount=5))

# SysLogHandler
from logging.handlers import SysLogHandler
logger.add(SysLogHandler(address="/dev/log"))

# SocketHandler
from logging.handlers import SocketHandler
logger.add(SocketHandler("localhost", 9020))

# SMTPHandler
from logging.handlers import SMTPHandler
logger.add(SMTPHandler("smtp.example.com", "from@example.com", "to@example.com", "Log Alert"))

# HTTPHandler
from logging.handlers import HTTPHandler
logger.add(HTTPHandler("logs.example.com", "/ingest", method="POST"))

# QueueHandler
from logging.handlers import QueueHandler
import queue
logger.add(QueueHandler(queue.Queue()))
```

## How It Works

When you pass a `logging.Handler` to `logger.add()`:

1. Logly wraps the handler as a callable sink
2. Each log message is converted to a `logging.LogRecord`
3. The handler's `emit()` method is called with the record
4. Exception info is automatically forwarded when available

## Level Mapping

Logly automatically maps message text to detect the log level for the handler:

| Logly Level | Python Level |
|-------------|-------------|
| TRACE, DEBUG | `logging.DEBUG` |
| INFO, NOTICE, SUCCESS | `logging.INFO` |
| WARNING | `logging.WARNING` |
| ERROR, FAIL | `logging.ERROR` |
| CRITICAL, FATAL | `logging.CRITICAL` |

## Example: Custom Handler

```python
import logging
from logly import logger

class AlertHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        if record.levelno >= logging.ERROR:
            send_alert(msg)

logger.add(AlertHandler(), level="ERROR")
logger.error("This triggers an alert")
```

## Example: Multiple Handler Sinks

```python
import logging
from logly import logger

# Route different levels to different handlers
logger.add(logging.StreamHandler(), level="INFO")
logger.add(logging.FileHandler("errors.log"), level="ERROR")
logger.add(logging.FileHandler("all.log"), level="DEBUG")
```

## Parameters

```python
logger.add(
    handler,          # logging.Handler instance
    level="INFO",     # Minimum level for Logly filtering
    format=None,      # Logly format (not used for handler)
    **kwargs,         # Other add() parameters
)
```

::: info
When using a `logging.Handler`, the `format` parameter controls Logly's internal formatting before the message reaches the handler. The handler's own formatter (set via `handler.setFormatter()`) handles final output formatting.
:::
