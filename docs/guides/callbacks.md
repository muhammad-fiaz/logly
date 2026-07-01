---
title: Callbacks & Hooks
description: Use callbacks and hooks for custom log processing in Logly
---

# Callbacks & Hooks

Logly provides several callback mechanisms for customizing log processing. Use these to handle exceptions, filter records dynamically, transform messages, and control output formatting.

## `catch(onerror=...)` - Exception Callback

The `onerror` callback is invoked when `catch()` captures an exception.

### Basic Usage

```python
from logly import logger

def handle_error(exc: BaseException) -> None:
    print(f"Caught: {type(exc).__name__}: {exc}")

with logger.catch(onerror=handle_error):
    raise ValueError("something went wrong")
```

### With Reraise

```python
from logly import logger

def notify_on_error(exc: BaseException) -> None:
    print(f"Notifying admin about: {exc}")

try:
    with logger.catch(onerror=notify_on_error, reraise=True):
        raise RuntimeError("critical failure")
except RuntimeError:
    print("Handled upstream")
```

### As Decorator

```python
from logly import logger

def log_failure(exc: BaseException) -> None:
    logger.error("Function failed: {}", exc)

@logger.catch(onerror=log_failure)
def risky_operation():
    raise ConnectionError("timeout")
```

## `add(filter=...)` - Callable Filter

The filter callable receives the record dict and returns `True` to allow or `False` to reject.

### Signature

```python
def my_filter(record: dict[str, object]) -> bool:
    # Access record fields
    level = record.get("level", "")
    message = record.get("message", "")
    extra = record.get("extra", {})

    # Return True to allow, False to reject
    return True
```

### Filter by Level

```python
from logly import logger

def only_errors(record: dict[str, object]) -> bool:
    return record.get("level") in {"ERROR", "CRITICAL", "FAIL"}

logger.add("errors.log", filter=only_errors)
```

### Filter by Message Content

```python
from logly import logger

def important_messages(record: dict[str, object]) -> bool:
    msg = str(record.get("message", "")).lower()
    return "critical" in msg or "urgent" in msg

logger.add("important.log", filter=important_messages)
```

### Filter by Extra Fields

```python
from logly import logger

def production_only(record: dict[str, object]) -> bool:
    extra = record.get("extra", {})
    return extra.get("env") == "production"

logger.add("prod.log", filter=production_only)
```

### Block All Records

```python
from logly import logger

def block_all(record: dict[str, object]) -> bool:
    return False

logger.add("disabled.log", filter=block_all)
```

## `add(patch=...)` - Patcher Callback

The patcher callable receives the record dict and mutates it in-place before dispatch.

### Signature

```python
def my_patcher(record: dict[str, object]) -> None:
    # Modify record in-place
    record["extra"]["custom_field"] = "value"
```

### Add Extra Fields

```python
from logly import logger

def add_service_name(record: dict[str, object]) -> None:
    record.setdefault("extra", {})["service"] = "my-api"

patched = logger.patch(add_service_name)
patched.info("Request processed")  # extra includes service=my-api
```

### Modify Messages

```python
from logly import logger

def uppercase_message(record: dict[str, object]) -> None:
    record["message"] = str(record.get("message", "")).upper()

patched = logger.patch(uppercase_message)
patched.info("hello")  # Output: HELLO
```

### Multiple Patchers

```python
from logly import logger

def add_env(record: dict[str, object]) -> None:
    record.setdefault("extra", {})["env"] = "prod"

def add_region(record: dict[str, object]) -> None:
    record.setdefault("extra", {})["region"] = "us-east-1"

patched = logger.patch(add_env).patch(add_region)
patched.info("Deployed")  # extra includes env=prod, region=us-east-1
```

### Per-Sink Patcher

```python
from logly import logger

def json_enricher(record: dict[str, object]) -> None:
    record.setdefault("extra", {})["source"] = "logly"

sink_id = logger.add(
    "structured.json",
    format="{message}",
    serialize=True,
    patch=json_enricher,
)
```

## `add(format=...)` - Callable Formatter

The format callable receives the record dict and returns the formatted string.

### Signature

```python
def my_format(record: dict[str, object]) -> str:
    return f"{record['level']}: {record['message']}"
```

### Simple Custom Format

```python
from logly import logger

def minimal_format(record: dict[str, object]) -> str:
    return f"[{record['level']}] {record['message']}"

logger.add("minimal.log", format=minimal_format)
logger.info("Hello")  # Output: [INFO] Hello
```

### Include Extra Fields

```python
from logly import logger

def json_format(record: dict[str, object]) -> str:
    import json
    extra = record.get("extra", {})
    return json.dumps({
        "level": record.get("level"),
        "message": record.get("message"),
        "extra": extra,
    })

logger.add("json.log", format=json_format)
```

### Conditional Formatting

```python
from logly import logger

def smart_format(record: dict[str, object]) -> str:
    level = record.get("level", "INFO")
    msg = record.get("message", "")
    if level in {"ERROR", "CRITICAL"}:
        return f"!!! {level}: {msg} !!!"
    return f"{level}: {msg}"

logger.add("smart.log", format=smart_format)
```

## `opt(exception=...)` - Exception Formatting

Attach an exception to a log record for formatted traceback output.

### Capture Current Exception

```python
from logly import logger

try:
    1 / 0
except ZeroDivisionError:
    logger.opt(exception=True).error("Division failed")
    # Includes full traceback in output
```

### Attach Specific Exception

```python
from logly import logger

exc = ValueError("invalid input")
logger.opt(exception=exc).error("Processing failed")
```

### With Backtrace Control

```python
from logly import logger

try:
    risky_operation()
except Exception as e:
    # Full backtrace (default)
    logger.opt(exception=e, backtrace=True).error("Failed")

    # Short traceback
    logger.opt(exception=e, backtrace=False).error("Failed")
```

### With Diagnostics

```python
from logly import logger

try:
    complex_operation()
except Exception as e:
    # Include diagnostic information (variable values, etc.)
    logger.opt(exception=e, diagnose=True).error("Diagnostic failure")
```

## `opt(lazy=...)` - Lazy Evaluation

Defer string formatting and callable evaluation until the message is actually emitted.

### Skip Evaluation When Filtered

```python
from logly import logger

call_count = 0

def expensive_computation() -> str:
    global call_count
    call_count += 1
    return "result: " + str(sum(range(1_000_000)))

messages = []

def capture(msg: str) -> None:
    messages.append(msg)

sink_id = logger.add(capture, level="WARNING")

# This will NOT call expensive_computation because level is filtered
logger.opt(lazy=True).info(expensive_computation)

print(call_count)  # 0 - function was never called
logger.remove(sink_id)
```

### Evaluate When Emitted

```python
from logly import logger

messages = []

def capture(msg: str) -> None:
    messages.append(msg)

def lazy_value() -> str:
    return "computed value"

sink_id = logger.add(capture)
logger.opt(lazy=True).info("Value: {}", lazy_value)
logger.remove(sink_id)

print(messages[0])  # "Value: computed value"
```

### Lazy with Callables in Arguments

```python
from logly import logger

def heavy_db_query() -> str:
    # Simulate expensive query
    return "query_result"

logger.opt(lazy=True).debug("Query result: {}", heavy_db_query)
# heavy_db_query() only evaluated if DEBUG level is active
```

## Combining Callbacks

```python
from logly import logger

def enrich_record(record: dict[str, object]) -> None:
    record.setdefault("extra", {})["source"] = "api"

def only_api_errors(record: dict[str, object]) -> bool:
    level = record.get("level", "")
    extra = record.get("extra", {})
    return level in {"ERROR", "CRITICAL"} and extra.get("source") == "api"

def api_format(record: dict[str, object]) -> str:
    return f"[API] {record.get('level')}: {record.get('message')}"

sink_id = logger.add(
    "api-errors.log",
    filter=only_api_errors,
    patch=enrich_record,
    format=api_format,
)

patched = logger.patch(enrich_record)
patched.error("Request failed")  # Goes to api-errors.log with custom format
```

## Complete Example

```python
from logly import logger

# Custom patcher to add context
def add_request_context(record: dict[str, object]) -> None:
    extra = record.setdefault("extra", {})
    extra.setdefault("service", "web-api")
    extra.setdefault("env", "production")

# Custom filter for production errors
def production_errors(record: dict[str, object]) -> bool:
    level = record.get("level", "")
    extra = record.get("extra", {})
    return level in {"ERROR", "CRITICAL"} and extra.get("env") == "production"

# Custom formatter for structured output
def structured_format(record: dict[str, object]) -> str:
    import json
    return json.dumps({
        "ts": str(record.get("time", "")),
        "level": record.get("level"),
        "msg": record.get("message"),
        "extra": record.get("extra", {}),
    })

# Configure sinks with callbacks
logger.add(
    "app.log",
    level="INFO",
    rotation="daily",
    retention="30 days",
    patch=add_request_context,
)

logger.add(
    "production-errors.json",
    level="DEBUG",
    filter=production_errors,
    format=structured_format,
    serialize=False,
    patch=add_request_context,
)

# Exception handling with onerror
def alert_on_critical(exc: BaseException) -> None:
    logger.critical("Alert: {}", exc)

with logger.catch(onerror=alert_on_critical):
    critical_operation()

# Lazy evaluation for expensive computations
def compute_metrics() -> str:
    return "cpu=45% mem=62%"

logger.opt(lazy=True).debug("Metrics: {}", compute_metrics)

logger.complete()
```
