---
title: Exception Callbacks & Error Handling
description: Advanced exception catching with callbacks and custom error handling in Logly
---

# Exception Callbacks & Error Handling

Logly provides powerful exception handling through `catch()`, `exception()`, and `opt(exception=True)`. This guide covers all exception handling patterns with callbacks, filtering, and custom error handling.

## `catch()` as Context Manager

The most common pattern for catching and logging exceptions:

### Basic Usage

```python
from logly import logger

# Suppress exception and log it
with logger.catch():
    risky_operation()
# Exception is logged at ERROR level and suppressed
```

### Custom Log Level

```python
from logly import logger

# Log caught exceptions at WARNING instead of ERROR
with logger.catch(level="WARNING"):
    optional_operation()

# Log critical exceptions
with logger.catch(level="CRITICAL"):
    database.connect()
```

### Catch Specific Exception Types

```python
from logly import logger

# Only catch ValueError
with logger.catch(ValueError):
    parse_data()

# Catch multiple exception types
with logger.catch((ValueError, TypeError)):
    process_input()

# Catch connection errors
with logger.catch(ConnectionError):
    api_call()
```

### Re-raise After Logging

```python
from logly import logger

# Log the exception and re-raise it
try:
    with logger.catch(reraise=True):
        risky_operation()
except Exception as e:
    print(f"Caught outside: {e}")
    # Exception was logged at ERROR level before re-raising
```

### Exclude Specific Exceptions

```python
from logly import logger

# Skip KeyboardInterrupt (let it propagate)
with logger.catch(exclude=KeyboardInterrupt):
    long_running_task()

# Skip multiple exception types
with logger.catch(exclude=(KeyboardInterrupt, SystemExit)):
    interactive_operation()
```

### Return Default Value

```python
from logly import logger

# Return None on exception (default)
result = logger.catch(default=None)(risky_function)()

# Return a fallback value
result = logger.catch(default=[])(fetch_data)()

# Return empty dict
result = logger.catch(default={})(load_config)()
```

### On-Error Callback

```python
from logly import logger

def alert_on_error(exc):
    """Send alert when exception occurs."""
    send_slack_alert(f"Error: {exc}")
    update_metrics("error_count")

with logger.catch(onerror=alert_on_error):
    critical_operation()
```

### Combined Options

```python
from logly import logger

# All options together
def handle_db_error(exc):
    reconnect_to_database()

with logger.catch(
    exception=ConnectionError,
    level="CRITICAL",
    reraise=True,
    onerror=handle_db_error,
    exclude=TimeoutError,
):
    database.query("SELECT * FROM users")
```

## `catch()` as Decorator

Apply exception catching to entire functions:

### Basic Decorator

```python
from logly import logger

@logger.catch()
def risky_function():
    raise ValueError("Something went wrong")

risky_function()
# Exception logged at ERROR level, function returns None
```

### Custom Level Decorator

```python
from logly import logger

@logger.catch(level="ERROR")
def run_job():
    raise RuntimeError("Job error")

run_job()
```

### Catch Specific Exception

```python
from logly import logger

@logger.catch(ValueError)
def parse_data():
    raise ValueError("Bad data")

parse_data()
```

### Decorator with Re-raise

```python
from logly import logger

@logger.catch(reraise=True)
def critical_function():
    raise TypeError("Critical error")

try:
    critical_function()
except TypeError:
    print("Caught outside")
```

### Decorator with On-Error Callback

```python
from logly import logger

def cleanup(exc):
    """Clean up resources on exception."""
    remove_temp_files()
    close_connections()

@logger.catch(onerror=cleanup)
def task():
    raise RuntimeError("Failed")

task()
```

### Decorator with Default Return

```python
from logly import logger

@logger.catch(default=0)
def divide(a, b):
    return a / b

result = divide(10, 0)
print(result)  # 0 (exception logged, default returned)
```

### Decorator with Exclusions

```python
from logly import logger

@logger.catch(exclude=KeyboardInterrupt)
def long_task():
    for i in range(1000):
        process(i)

long_task()
# KeyboardInterrupt propagates, other exceptions logged
```

## `catch(exclude=...)` to Skip Specific Exceptions

Filter which exceptions are caught:

```python
from logly import logger

# Skip KeyboardInterrupt
with logger.catch(exclude=KeyboardInterrupt):
    interactive_task()

# Skip SystemExit
with logger.catch(exclude=SystemExit):
    managed_process()

# Skip multiple exception types
with logger.catch(exclude=(KeyboardInterrupt, SystemExit, GeneratorExit)):
    background_worker()
```

### Practical Example

```python
from logly import logger

def process_file(filepath):
    """Process file, catching errors but letting interrupts pass."""
    with logger.catch(exclude=KeyboardInterrupt, level="ERROR"):
        with open(filepath, "r") as f:
            data = f.read()
        result = parse(data)
        save(result)
        return result
```

## `catch(onerror=...)` Callback

Execute custom logic when an exception is caught:

### Basic Callback

```python
from logly import logger

def on_error(exc):
    print(f"Caught: {exc}")

with logger.catch(onerror=on_error):
    risky_operation()
```

### Send Alerts

```python
from logly import logger

def alert_team(exc):
    """Send Slack alert on error."""
    import requests
    requests.post(
        "https://hooks.slack.com/services/xxx",
        json={"text": f"Error in production: {exc}"},
    )

with logger.catch(onerror=alert_team):
    production_task()
```

### Update Metrics

```python
from logly import logger

error_count = 0

def track_error(exc):
    global error_count
    error_count += 1
    metrics.gauge("error_rate", error_count)

with logger.catch(onerror=track_error):
    for _ in range(100):
        process_item()
```

### Cleanup Resources

```python
from logly import logger

def cleanup(exc):
    """Clean up on error."""
    remove_temp_files()
    close_database_connections()
    release_locks()

with logger.catch(onerror=cleanup):
    complex_operation()
```

### Callback with Context

```python
from logly import logger

def handle_error(exc, context):
    """Handle error with context."""
    logger.bind(**context).error("Operation failed: {}", exc)
    send_alert(context["service"], exc)

with logger.catch(
    onerror=lambda exc: handle_error(exc, {"service": "api", "endpoint": "/users"})
):
    api_request()
```

## `catch(default=...)` Return Value

Provide a fallback return value when an exception occurs:

```python
from logly import logger

# Return None (default behavior)
result = logger.catch()(risky_function)()

# Return empty list
result = logger.catch(default=[])(fetch_items)()

# Return empty dict
result = logger.catch(default={})(load_config)()

# Return zero
result = logger.catch(default=0)(divide_numbers)(10, 0)

# Return False
result = logger.catch(default=False)(validate_input)()
```

### Practical Example

```python
from logly import logger

def get_user(user_id):
    """Fetch user, returning None on error."""
    return logger.catch(default=None)(
        lambda: db.query("SELECT * FROM users WHERE id = ?", user_id)
    )()

user = get_user(123)
if user is None:
    logger.warning("User not found or database error")
```

## `catch(reraise=True)` Re-raise After Logging

Log the exception and re-raise it for upstream handling:

```python
from logly import logger

try:
    with logger.catch(reraise=True):
        risky_operation()
except Exception as e:
    print(f"Caught outside: {e}")
    # Exception was logged at ERROR level before re-raising
```

### Decorator with Re-raise

```python
from logly import logger

@logger.catch(reraise=True)
def critical_operation():
    raise ValueError("Critical failure")

try:
    critical_operation()
except ValueError as e:
    print(f"Handled: {e}")
    # Exception was logged before reaching here
```

### Combined with Callback

```python
from logly import logger

def on_critical_error(exc):
    """Log critical error details."""
    logger.critical("Critical failure: {}", exc)

try:
    with logger.catch(reraise=True, onerror=on_critical_error):
        critical_operation()
except Exception:
    handle_critical_failure()
```

## `catch(level=...)` Custom Severity

Control the log level for caught exceptions:

```python
from logly import logger

# Log at WARNING
with logger.catch(level="WARNING"):
    optional_operation()

# Log at INFO
with logger.catch(level="INFO"):
    non_critical_operation()

# Log at CRITICAL
with logger.catch(level="CRITICAL"):
    system_operation()

# Log at DEBUG
with logger.catch(level="DEBUG"):
    internal_operation()
```

### Level in Decorator

```python
from logly import logger

@logger.catch(level="WARNING")
def optional_task():
    raise ValueError("Non-critical error")

@logger.catch(level="CRITICAL")
def critical_task():
    raise RuntimeError("System failure")
```

## `opt(exception=True)` Automatic Exception Formatting

Attach the current exception to a log message:

### Basic Usage

```python
from logly import logger

try:
    risky_operation()
except Exception:
    logger.opt(exception=True).error("Operation failed")
    # Exception traceback is automatically appended
```

### Attach Specific Exception

```python
from logly import logger

exc = ValueError("bad value")
logger.opt(exception=exc).error("Value error occurred")
```

### Exception with Lazy Evaluation

```python
from logly import logger

try:
    risky_operation()
except Exception:
    logger.opt(exception=True).lazy().error(
        "Error: {}", lambda: expensive_computation()
    )
```

### Exception in Context

```python
from logly import logger

try:
    risky_operation()
except Exception:
    logger.opt(exception=True).bind(
        request_id="abc-123",
        user_id="456",
    ).error("Request failed")
```

## `exception()` Method

Convenience method that combines `opt(exception=True).error()`:

```python
from logly import logger

try:
    risky_operation()
except Exception:
    logger.exception("Something failed")
    # Equivalent to: logger.opt(exception=True).error("Something failed")
```

### With Context

```python
from logly import logger

try:
    risky_operation()
except Exception:
    logger.bind(request_id="abc-123").exception("Request failed")
```

### In a Loop

```python
from logly import logger

items = [1, 2, 3, None, 5]

for item in items:
    try:
        process(item)
    except Exception:
        logger.exception("Failed to process item: {}", item)
```

## `format_exception_text()` Standalone Function

Format exception information without logging:

```python
from logly import logger
from logly import format_exception_text

try:
    risky_operation()
except Exception:
    # Get formatted exception text
    exc_text = format_exception_text()
    print(f"Formatted: {exc_text}")

    # Use in custom handling
    logger.error("Custom format: {}", exc_text)
```

### With Specific Exception

```python
from logly import format_exception_text

exc = ValueError("bad value")
formatted = format_exception_text(exc)
print(formatted)
```

### Custom Formatting

```python
from logly import format_exception_text

try:
    risky_operation()
except Exception as exc:
    # Get just the exception type and message
    text = format_exception_text()
    short_text = str(exc)
    print(f"Error: {short_text}")
    print(f"Full: {text}")
```

## Backtrace vs Diagnose Modes

### Backtrace Mode

Includes a backtrace in exception output for more context:

```python
from logly import logger

logger.remove()
logger.add(
    "app.log",
    backtrace=True,
    format="{time} | {level} | {message}",
)

with logger.catch():
    risky_operation()
# Exception output includes backtrace with function call history
```

### Diagnose Mode

Includes variable values in exception output:

```python
from logly import logger

logger.remove()
logger.add(
    "app.log",
    diagnose=True,
    format="{time} | {level} | {message}",
)

def process(data, threshold):
    result = compute(data)
    if result > threshold:
        raise ValueError(f"Result {result} exceeds threshold {threshold}")

with logger.catch():
    process([1, 2, 3], 10)
# Exception output includes variable values: data=[1, 2, 3], threshold=10
```

### Both Modes

```python
from logly import logger

logger.remove()
logger.add(
    "app.log",
    backtrace=True,
    diagnose=True,
    format="{time} | {level} | {message}",
)

with logger.catch():
    risky_operation()
# Full backtrace + variable values in exception output
```

### Per-Call Override

```python
from logly import logger

logger.remove()
logger.add("app.log")

# Override backtrace for this call only
logger.opt(backtrace=True).error("This has backtrace")

# Override diagnose for this call only
logger.opt(diagnose=True).error("This has diagnose")
```

## Complete Examples

### Production Error Handler

```python
from logly import logger

logger.remove()

# Console for immediate feedback
logger.add(
    "stderr",
    level="ERROR",
    format="<red>{time:HH:mm:ss}</red> | <level>{level:<8}</level> | <level>{message}</level>",
    colorize=True,
)

# File with full details
logger.add(
    "errors.log",
    level="ERROR",
    backtrace=True,
    diagnose=True,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {file}:{line} | {message}",
    rotation="daily",
    retention="365 days",
    enqueue=True,
)

def process_order(order):
    """Process an order with error handling."""
    try:
        validate_order(order)
        charge_payment(order)
        ship_order(order)
        logger.success("Order {} processed", order["id"])
    except ValueError as e:
        logger.warning("Invalid order {}: {}", order["id"], e)
    except PaymentError as e:
        logger.error("Payment failed for order {}: {}", order["id"], e)
    except Exception as e:
        logger.exception("Unexpected error processing order {}", order["id"])
```

### Decorator-Based Error Handling

```python
from logly import logger

def handle_errors(level="ERROR", reraise=False, onerror=None):
    """Decorator factory for error handling."""
    def decorator(func):
        @logger.catch(level=level, reraise=reraise, onerror=onerror)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@handle_errors(level="CRITICAL", reraise=True)
def critical_operation():
    raise RuntimeError("System failure")

@handle_errors(level="WARNING")
def optional_operation():
    raise ValueError("Non-critical")
```

### Exception with Context Binding

```python
from logly import logger

def api_endpoint(request):
    """Handle API request with error context."""
    with logger.contextualize(
        request_id=request["id"],
        endpoint=request["path"],
        method=request["method"],
    ):
        try:
            result = process_request(request)
            logger.info("Request completed")
            return result
        except Exception:
            logger.exception("Request failed")
            return {"error": "Internal server error"}
```

### Retry with Exception Logging

```python
from logly import logger
import time

def retry_with_logging(func, max_retries=3, delay=1):
    """Retry function with exception logging."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            logger.warning(
                "Attempt {}/{} failed: {}",
                attempt + 1,
                max_retries,
                e,
            )
            if attempt < max_retries - 1:
                time.sleep(delay)
    logger.error("All {} attempts failed", max_retries)
    raise RuntimeError(f"Failed after {max_retries} attempts")

# Usage
result = retry_with_logging(lambda: api_call(), max_retries=3)
```

### Exception Metrics

```python
from logly import logger
from collections import defaultdict

error_counts = defaultdict(int)

def track_errors(exc):
    """Track error types for metrics."""
    error_type = type(exc).__name__
    error_counts[error_type] += 1
    logger.bind(error_type=error_type).error("Error: {}", exc)

def critical_task():
    """Task with error tracking."""
    with logger.catch(onerror=track_errors):
        risky_operation()

# Run task
for _ in range(100):
    critical_task()

# Report metrics
for error_type, count in error_counts.items():
    logger.info("Error type {}: {} occurrences", error_type, count)
```

### Graceful Shutdown Handler

```python
from logly import logger
import signal
import sys

def shutdown_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.warning("Received signal {}, shutting down", signum)
    logger.complete()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

logger.add("app.log", enqueue=True)

try:
    while True:
        process_request()
except Exception:
    logger.exception("Fatal error")
finally:
    logger.complete()
```

### Exception Context Manager with State

```python
from logly import logger
from contextlib import contextmanager

@contextmanager
def error_context(operation, **context):
    """Context manager with error handling and context."""
    try:
        yield
        logger.success("{} completed", operation)
    except Exception as e:
        logger.bind(error=str(e), **context).exception(
            "{} failed", operation
        )
        raise

# Usage
with error_context("database migration", table="users"):
    migrate_table("users")
```
