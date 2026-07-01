---
title: Independent Loggers
description: Create independent loggers with separate sinks and configurations
---

# Independent Loggers

Logly supports creating completely independent `Logger` instances that do not share sinks, context, or configuration with the global `logger`. This is useful when you need separate logging pipelines for different subsystems.

## Creating Independent Loggers

```python
from logly import Logger

# Create a completely independent logger
db_logger = Logger(name="database")

# Each logger has its own sinks
db_logger.add("database.log", level="INFO")
db_logger.info("Database connected")  # Only goes to database.log

# The global logger does not see this
from logly import logger
logger.info("App started")  # Only goes to default stderr
```

## Independent Loggers with Different Configurations

```python
from logly import Logger

# API logger
api_logger = Logger(name="api")
api_logger.add(
    "logs/api.log",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | API | {level:<8} | {message}",
    rotation="daily",
    retention="30 days",
    compression="gzip",
)

# Worker logger
worker_logger = Logger(name="worker")
worker_logger.add(
    "logs/worker.log",
    level="DEBUG",
    format="{time:HH:mm:ss} | Worker | {level:<8} | {message}",
    rotation="100 MB",
    retention="7 days",
)

# Each logger is independent
api_logger.info("Request processed")
worker_logger.debug("Task started")
```

## Independent Loggers with Context Binding

```python
from logly import Logger

auth_logger = Logger(name="auth")

# Bind persistent context
auth_logger = auth_logger.bind(service="auth", region="us-east-1")
auth_logger.info("User authenticated")
# Output includes: service=auth region=us-east-1

# Bind additional context without affecting the base logger
request_logger = auth_logger.bind(request_id="req-123")
request_logger.info("Token validated")
# Output includes: service=auth region=us-east-1 request_id=req-123
```

## Using Multiple Sinks per Logger

```python
from logly import Logger

# Create a logger for the payment subsystem
payment_logger = Logger(name="payments")

# Console for development
payment_logger.add("stderr", level="DEBUG", colorize=True)

# File for audit trail
payment_logger.add(
    "logs/payments-audit.log",
    level="INFO",
    filter={"module": "payments"},
    rotation="daily",
    retention="365 days",
)

# JSON file for analysis
payment_logger.add(
    "logs/payments.json",
    level="INFO",
    serialize=True,
    rotation="100 MB",
    retention="90 days",
    compression="zstd",
)

# All three sinks receive the message
payment_logger.info("Payment processed", amount=99.99, currency="USD")
```

## Cloning Loggers

```python
from logly import logger

# Clone inherits all sinks and configuration
task_logger = logger.bind(task="cleanup")

# The clone is independent - adding a sink does not affect the original
task_logger.add("task.log", level="INFO")
task_logger.info("Task running")  # Goes to stderr + task.log

logger.info("Original logger")  # Only goes to stderr
```

## Comparison with Global Logger

| Feature | Global `logger` | Independent `Logger()` |
|---------|----------------|----------------------|
| Sinks | Shared (module-level) | Per-instance |
| Context (`bind`) | Shared via `_context` | Per-instance |
| Levels | Global registration | Global registration |
| Format templates | Per-sink | Per-sink |
| `opt()` options | Per-view | Per-view |
| Thread safety | Yes | Yes |

::: tip
Custom levels registered via `logger.level()` are global and visible to all Logger instances.
:::

## Use Cases

### Separate Error Tracking

```python
from logly import Logger

error_logger = Logger(name="errors")
error_logger.add(
    "logs/errors.json",
    level="ERROR",
    serialize=True,
    rotation="daily",
    retention="1 year",
)

@error_logger.catch(reraise=True)
def risky_operation():
    ...
```

### Multi-Tenant Logging

```python
from logly import Logger

def get_tenant_logger(tenant_id: str) -> Logger:
    log = Logger(name=f"tenant.{tenant_id}")
    log.add(
        f"logs/tenants/{tenant_id}.log",
        level="INFO",
        rotation="daily",
        retention="90 days",
    )
    return log.bind(tenant_id=tenant_id)

tenant_log = get_tenant_logger("acme-corp")
tenant_log.info("Data imported")
```

### Testing with Captured Logs

```python
from logly import Logger

def test_my_function():
    test_logger = Logger(name="test")
    messages = []
    test_logger.add(lambda m: messages.append(m), level="DEBUG")

    # ... run code that uses test_logger ...
    test_logger.info("Expected message")

    assert len(messages) == 1
    assert "Expected message" in messages[0]
```
