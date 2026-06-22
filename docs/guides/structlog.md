---
title: structlog Integration
description: Integrating Logly with structlog
---

# structlog Integration

## Basic Setup

```python
import structlog
from logly.integrations.structlog import logly_processor

structlog.configure(
    processors=logly_processor(),
    logger_factory=structlog.PrintLoggerFactory(),
)

log = structlog.get_logger()
log.info("hello", key="value")
```

## Custom Renderer

```python
from logly.integrations.structlog import LoglyRenderer
from logly import logger

renderer = LoglyRenderer(level="DEBUG")
renderer(None, "info", {"event": "test message", "key": "value"})
```

## Integration with Logly Sinks

```python
import structlog
from logly import logger

# Configure Logly sinks
logger.add("app.log", level="INFO", serialize=True)

# Use structlog processors that route to Logly
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)
```

::: tip
The `LoglyRenderer` class can be used as a standalone structlog processor that routes all output through Logly's sink system.
:::
