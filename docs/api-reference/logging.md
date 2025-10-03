---
title: Logging Methods API - Logly Python Logging
description: Logly logging methods API reference. Complete guide to all logging functions, severity levels, and message formatting options.
keywords: python, logging, methods, api, severity, levels, messages, formatting, logly
---

# Logging Methods

Methods for emitting log messages at different severity levels.

---

## Overview

Logly supports 7 log levels (from lowest to highest):

| Level | Method | Color | Use Case |
|-------|--------|-------|----------|
| **TRACE** | `logger.trace()` | Gray | Detailed debugging, function entry/exit |
| **DEBUG** | `logger.debug()` | Cyan | Development debugging, variable inspection |
| **INFO** | `logger.info()` | White | General information, application state |
| **SUCCESS** | `logger.success()` | Green | Successful operations |
| **WARNING** | `logger.warning()` | Yellow | Warning messages, deprecations |
| **ERROR** | `logger.error()` | Red | Error conditions, failed operations |
| **CRITICAL** | `logger.critical()` | Bold Red | Critical errors, system failures |

All logging methods support:
- ✅ Structured fields (kwargs become JSON fields)
- ✅ Context from `.bind()` and `.contextualize()`
- ✅ Async callbacks

---

## Common Signature

All logging methods share this signature:

```python
logger.METHOD(message: str, **kwargs) -> None
```

**Parameters:**
- `message` (str): Log message
- `**kwargs`: Additional context fields (become JSON fields or key=value suffix)

**Returns:** `None`

---

## logger.trace()

Log at TRACE level (most verbose). Use for detailed debugging.

### Example

```python
logger.trace("Function called", function="process_data", args={"x": 1, "y": 2})
```

### Use Cases
- Function entry/exit logging
- Detailed execution flow
- Variable values at each step

---

## logger.debug()

Log at DEBUG level. Use for development debugging.

### Example

```python
logger.debug("Variable inspection", x=42, y="hello")
```

### Use Cases
- Variable inspection
- Intermediate calculation results
- Development diagnostics

---

## logger.info()

Log at INFO level. Use for general information.

### Example

```python
logger.info("Application started", version="1.0.0")
```

### Use Cases
- Application lifecycle events
- User actions
- Business logic milestones

---

## logger.success()

Log at SUCCESS level (mapped to INFO with green color). Use for successful operations.

### Example

```python
logger.success("Payment processed", order_id=1234, amount=99.99)
```

### Use Cases
- Successful transactions
- Completed operations
- Positive outcomes

---

## logger.warning()

Log at WARNING level. Use for warning messages.

### Example

```python
logger.warning("Disk space low", available_gb=2.5, threshold=5.0)
logger.warning("API rate limit approaching", remaining=10, limit=100)
```

### Use Cases
- Resource constraints
- Deprecated API usage
- Non-critical issues

---

## logger.error()

Log at ERROR level. Use for error conditions.

### Example

```python
logger.error("Database connection failed", retry_count=3, error="timeout")
```

### Use Cases
- Failed operations
- Exceptions (non-critical)
- Recoverable errors

---

## logger.critical()

Log at CRITICAL level (most severe). Use for critical system failures.

### Example

```python
logger.critical("System out of memory", available_mb=10, required_mb=500)
```

### Use Cases
- System failures
- Unrecoverable errors
- Service outages

---

## logger.log()

Log at a custom or runtime-determined level.

### Signature

```python
logger.log(level: str, message: str, **kwargs) -> None
```

### Parameters
- `level` (str): Log level name (e.g., `"INFO"`, `"ERROR"`)
- `message` (str): Log message
- `**kwargs`: Additional context fields

### Example

```python
# Runtime level determination
log_level = "DEBUG" if dev_mode else "INFO"
logger.log(log_level, "Processing data", records=1000)

# Custom level aliases (mapped to existing levels)
logger.level("NOTICE", "INFO")
logger.level("AUDIT", "INFO")
logger.log("NOTICE", "Important notice")
logger.log("AUDIT", "User action logged", user="alice")
```

---

## Structured Logging

### Text Mode (default)

```python
logger.configure(json=False)
logger.info("User logged in", user="alice", ip="192.168.1.1")
```

**Output:**
```
2025-01-15 10:30:45 | INFO | User logged in user=alice ip=192.168.1.1
```

### JSON Mode

```python
logger.configure(json=True)
logger.info("User logged in", user="alice", ip="192.168.1.1")
```

**Output:**
```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "INFO",
  "message": "User logged in",
  "fields": {
    "user": "alice",
    "ip": "192.168.1.1"
  }
}
```

---

## Complete Example

```python
from logly import logger

# Configure
logger.configure(level="DEBUG", color=True)
logger.add("console")
logger.add("logs/app.log", rotation="daily")

# All log levels
logger.trace("Trace message", detail="very verbose")
logger.debug("Debug message", x=42)
logger.info("Info message", user="alice")
logger.success("Success message", task="complete")
logger.warning("Warning message", threshold=90)
logger.error("Error message", retry_count=3)
logger.critical("Critical message", status="failed")

# Runtime level
level = "ERROR" if error_condition else "INFO"
logger.log(level, "Conditional logging")

# Cleanup
logger.complete()
```

---

## Best Practices

### ✅ DO

```python
# 1. Use appropriate levels
logger.info("User logged in")  # General info
logger.error("Connection failed")  # Error condition

# 2. Include context
logger.error("Failed to process", item_id=123, retry_count=3)

# 3. Use structured fields
logger.info("Payment processed", order_id=1234, amount=99.99, currency="USD")
```

### ❌ DON'T

```python
# 1. Don't log sensitive data
logger.info("Login", password=password)  # ❌ Security risk

# 2. Don't use string concatenation
logger.info("User " + user + " logged in")  # ❌ Use structured logging

# 3. Don't log in tight loops
for i in range(1000000):
    logger.debug(f"Iteration {i}")  # ❌ Performance hit

# 4. Don't mix severity
logger.info("Critical error occurred")  # ❌ Use logger.critical()
```

---

## Performance

### Best Performance

```python
# 1. Set appropriate level in production
logger.configure(level="INFO")  # Skip DEBUG and TRACE

# 2. Use async writing
logger.add("logs/app.log", async_write=True)

# 3. Avoid logging in hot paths
if should_log:  # Check before logging
    logger.debug("Hot path", value=x)
```
