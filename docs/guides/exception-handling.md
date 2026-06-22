---
title: Exception Handling
description: Catch exceptions with context managers, decorators, and opt()
---

# Exception Handling

Logly provides multiple ways to catch and log exceptions.

## catch() as Context Manager

```python
from logly import logger

# Suppress exception and log it
with logger.catch():
    risky_operation()

# Re-raise after logging
try:
    with logger.catch(reraise=True):
        risky_operation()
except Exception:
    print("Caught outside")

# Custom level
with logger.catch(level="CRITICAL"):
    database.connect()

# Catch specific exception type
with logger.catch(ConnectionError):
    database.connect()

# Exclude specific exceptions
with logger.catch(exclude=KeyboardInterrupt):
    long_running_task()
```

## catch() as Decorator

```python
from logly import logger

# Catch all exceptions
@logger.catch()
def risky_function():
    raise ValueError("Something went wrong")

risky_function()

# Custom level
@logger.catch(level="ERROR")
def run_job():
    raise RuntimeError("Job error")

run_job()

# Catch specific exception type
@logger.catch(ValueError)
def parse_data():
    raise ValueError("Bad data")

# With re-raise
@logger.catch(reraise=True)
def critical_function():
    raise TypeError("Critical error")

try:
    critical_function()
except TypeError:
    print("Caught outside")

# With onerror callback
@logger.catch(onerror=lambda exc: cleanup())
def task():
    raise RuntimeError("Failed")
```

## opt(exception=...)

```python
from logly import logger

# Attach current exception
try:
    risky_operation()
except Exception:
    logger.opt(exception=True).error("Operation failed")

# Attach specific exception
exc = ValueError("bad value")
logger.opt(exception=exc).error("Value error occurred")

# Exception with lazy evaluation
logger.opt(exception=True).lazy().error("Error: {}", lambda: expensive_computation())
```

## exception() Method

```python
from logly import logger

# Convenience method - logs at ERROR with exception info
try:
    risky_operation()
except Exception:
    logger.exception("Something failed")
    # Equivalent to: logger.opt(exception=True).error("Something failed")
```

## Exception in Formatted Messages

```python
from logly import logger

# Exception text in message
try:
    risky_operation()
except Exception as e:
    logger.error("Failed: {}", str(e))

# Exception in extra fields
try:
    risky_operation()
except Exception as e:
    logger.bind(error_type=type(e).__name__).error("Failed: {}", e)
```

## Exception with Context

```python
from logly import logger

# Combined with bind
api_logger = logger.bind(service="api", endpoint="/users")

with logger.catch(level="ERROR"):
    response = api_client.get("/users")

# Combined with contextualize
with logger.contextualize(request_id="req-123"):
    try:
        risky_operation()
    except Exception:
        logger.exception("Request failed")
```

## Complete Exception Handling Examples

```python
from logly import logger

# Example 1: Database operations
with logger.catch(level="CRITICAL"):
    db.connect()

# Example 2: HTTP requests
@logger.catch(level="ERROR")
def make_request(url: str):
    return httpx.get(url)

# Example 3: Background task
@logger.catch(level="ERROR")
def background_task():
    process_data()

# Example 4: File operations
with logger.catch():
    with open("data.txt", "w") as f:
        f.write("content")

# Example 5: Nested exception handling
@logger.catch(level="ERROR")
def outer():
    with logger.catch(level="WARNING"):
        inner()
```
