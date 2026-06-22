---
title: Structlog
description: Processor for structlog integration.
---

# Structlog

`logly_processor()` creates a structlog processor chain that routes to Logly. `LoglyRenderer` provides a renderer that outputs through Logly.

## Installation

This integration requires the `structlog` package.

::: code-group

```bash [uv]
uv add logly[structlog]
```

```bash [pip]
pip install "logly[structlog]"
```

```bash [uv (without extras)]
uv add structlog
```

```bash [pip (without extras)]
pip install structlog
```

:::

::: warning Missing Dependency
If `structlog` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'structlog'
```
:::

## Usage

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

## Full Example

```python
import structlog
from logly.integrations.structlog import logly_processor, LoglyRenderer

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.BoundLogger,
)

log = structlog.get_logger()
log.info("user_login", user_id=123, ip="192.168.1.1")
log.warning("rate_limit_exceeded", endpoint="/api/users")
log.error("database_connection_failed", host="db.example.com")
```
