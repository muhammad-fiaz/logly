---
title: API Reference - Logly Python Logging Library
description: Complete API reference for Logly Python logging library. Detailed documentation of all methods, configuration options, and features.
keywords: python, logging, api, reference, documentation, methods, configuration, logly
---

# API Reference

Complete reference documentation for all Logly methods and features.

---

## Quick Navigation

<div class="grid cards" markdown>

-   **Configuration**

    ---

    Configure logger settings and add sinks

    [Configuration Methods](configuration.md)

-   **Logging**

    ---

    Log messages at different levels

    [Logging Methods](logging.md)

-   **Context**

    ---

    Manage logging context with bind and contextualize

    [Context Management](context.md)

-   **Callbacks**

    ---

    React to log events with async callbacks

    [Callback Methods](callbacks.md)

-   **Exceptions**

    ---

    Handle exceptions with automatic logging

    [Exception Handling](exceptions.md)

-   **Utilities**

    ---

    Additional utility methods

    [Utility Methods](utilities.md)

</div>

---

## Overview

The Logly API is organized into logical categories:

### Configuration Methods
Methods for setting up the logger and managing output destinations.

- `configure()` - Set global logger configuration
- `add()` - Add logging sinks (console, files)
- `remove()` - Remove logging sinks

### Logging Methods
Methods for emitting log messages at different severity levels.

- `trace()`, `debug()`, `info()`, `success()`
- `warning()`, `error()`, `critical()`
- `log()` - Log with custom level

### Context Methods
Methods for managing contextual information in logs.

- `bind()` - Create logger with persistent context
- `contextualize()` - Temporary context within a block

### Callback Methods
Methods for registering event handlers that execute asynchronously.

- `add_callback()` - Register async callback
- `remove_callback()` - Unregister callback

### Exception Methods
Methods for automatic exception logging.

- `catch()` - Decorator/context manager for exceptions
- `exception()` - Log current exception with traceback

### Utility Methods
Additional helper methods.

- `enable()` / `disable()` - Toggle logging
- `level()` - Register custom levels
- `complete()` - Flush pending logs

---

## Logger Instance

```python
from logly import logger
```

The global `logger` instance is a `_LoggerProxy` that wraps the Rust `PyLogger` backend, providing:

- Context binding
- Python-side convenience methods
- Full type hints and IDE support

---

## Type Hints

Logly includes complete type stubs for IDE autocompletion and type checking:

```python
from logly import logger
from typing import Callable, Dict, Any

# Type hints work automatically
logger.info("message", key="value")  # ✅ Type checked

# Callback type hint
callback: Callable[[Dict[str, Any]], None] = lambda rec: print(rec)
callback_id: int = logger.add_callback(callback)
```

---

## Common Patterns

### Pattern: Request Logging

```python
request_logger = logger.bind(
    request_id=request.headers.get("X-Request-ID"),
    method=request.method,
    path=request.url.path
)

request_logger.info("Request received")
# ... process request ...
request_logger.info("Response sent", status_code=200)
```

### Pattern: Batch Processing

```python
batch_logger = logger.bind(job_id="job-123", batch_id=batch.id)

with batch_logger.contextualize(step="validation"):
    batch_logger.debug("Validating batch")

with batch_logger.contextualize(step="processing"):
    batch_logger.info("Processing records", count=len(batch))
```

### Pattern: Error Monitoring

```python
def alert_critical(record):
    if record.get("level") == "CRITICAL":
        send_alert(record)

logger.add_callback(alert_critical)

# All critical logs trigger alerts
logger.critical("System failure", component="database")
```

---

## Next Steps

Explore detailed documentation for each category:

- [Configuration Methods →](configuration.md)
- [Logging Methods →](logging.md)
- [Context Management →](context.md)
- [Callback Methods →](callbacks.md)
- [Exception Handling →](exceptions.md)
- [Utility Methods →](utilities.md)
