---
title: Troubleshooting
description: Common issues and solutions for Logly
---

# Troubleshooting

## Common Issues

### No output appears

**Symptoms:** Logger calls produce no visible output.

**Cause:** No sinks configured or all sinks filtered out.

**Solution:**

```python
from logly import logger

# Check if sinks are configured
print(f"Number of sinks: {len(logger._sink_configs)}")

# Add a stderr sink if none exist
logger.add(sys.stderr, level="DEBUG")
```

### Messages appear twice

**Symptoms:** Each log message prints to stderr twice.

**Cause:** Multiple handlers attached to the same stream.

**Solution:**

```python
import sys
from logly import logger

# Remove all existing handlers
logger.remove()

# Add only one stderr handler
logger.add(sys.stderr, level="INFO")
```

### "Queue is full" warning

**Symptoms:** Warning about queue being full when using `enqueue=True`.

**Cause:** Application producing logs faster than the worker thread can consume them.

**Solutions:**

```python
from logly import logger

# 1. Remove enqueue for synchronous logging
logger.add("app.log")  # No enqueue

# 2. Use a higher log level to reduce volume
logger.add("app.log", enqueue=True, level="WARNING")
```

### Rotation not working

**Symptoms:** Files not rotating at expected intervals.

**Cause:** Rotation checks happen only when a new message is logged.

**Solution:**

```python
from logly import logger

# Ensure rotation check happens
logger.add(
    "app.log",
    rotation="100 MB",  # or "daily", "weekly"
    retention="30 days",
)

# Force rotation check by logging a message
logger.info("Rotation check triggered")
```

### Memory usage growing

**Symptoms:** Application memory increases over time.

**Cause:** Large log files accumulating without retention policy.

**Solution:**

```python
from logly import logger

# Add retention policy
logger.add(
    "app.log",
    rotation="daily",
    retention="30 days",  # Keep only last 30 days
    compression="gzip",   # Compress old files
)
```

### Exceptions not captured

**Symptoms:** `logger.exception()` doesn't show traceback.

**Cause:** Called outside an active exception context.

**Solution:**

```python
from logly import logger

try:
    1 / 0
except ZeroDivisionError:
    # Must be called inside except block
    logger.exception("Division by zero")
    # Or use catch() decorator
```

### Extra fields not showing

**Symptoms:** `{extra[key]}` in format shows empty or raises error.

**Cause:** Extra fields not bound correctly.

**Solution:**

```python
from logly import logger

# Correct: bind before logging
bound_logger = logger.bind(user_id="12345")
bound_logger.info("User logged in")

# Wrong: binding after logging
logger.info("User logged in")  # No extra fields here
logger.bind(user_id="12345")   # This creates a new logger instance
```

## Performance Issues

### Slow logging in hot path

**Solutions:**

```python
from logly import logger

# 1. Use lazy evaluation
logger.opt(lazy=True).debug("Expensive: {}", lambda: expensive_computation())

# 2. Use level check before logging
if logger._core.engine.is_enabled("DEBUG"):
    logger.debug("Only computed if enabled")

# 3. Use enqueue for I/O-bound sinks
logger.add("app.log", enqueue=True)
```

### High CPU usage

**Solutions:**

```python
from logly import logger

# 1. Reduce log level in production
logger.add("app.log", level="WARNING")

# 2. Use simpler format
logger.add("app.log", format="{message}")

# 3. Disable diagnose in production
logger.add("app.log", diagnose=False)
```

## Integration Issues

### FastAPI middleware not logging requests

**Solution:**

```python
from fastapi import FastAPI
from logly.integrations.fastapi import LoglyMiddleware

app = FastAPI()
app.add_middleware(LoglyMiddleware)

# Verify middleware is added
print(app.user_middleware)
```

### Django integration not working

**Solution:**

```python
# settings.py
LOGGING = {
    "version": 1,
    "handlers": {
        "logly": {
            "class": "logly.integrations.django.LoglyHandler",
        },
    },
    "root": {
        "handlers": ["logly"],
        "level": "DEBUG",
    },
}
```

### Structlog compatibility

**Solution:**

```python
import structlog
from logly.integrations.structlog import logly_processor

structlog.configure(
    processors=[logly_processor()],
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.BoundLogger,
)
```

## Debugging

### Enable debug output

```python
from logly import logger

# Add debug sink
logger.add(sys.stderr, level="DEBUG", format="{time} | {level} | {name} | {message}")

# Log with extra context
logger.bind(component="auth").debug("Processing login request")
```

### Inspect logger state

```python
from logly import logger

# Check configured sinks
print(f"Sinks: {len(logger._sink_configs)}")

# Check bound context
print(f"Context: {logger._context}")

# Check level
print(f"Level: {logger._level}")
```
