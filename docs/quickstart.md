---
title: Quick Start - Logly Python Logging Tutorial
description: Get started with Logly logging library in 5 minutes. Learn basic setup, configuration, and core features for Python applications.
keywords: python, logging, tutorial, quickstart, setup, configuration, logly
---

# Quick Start

Get started with Logly in 5 minutes!

---

## Basic Setup

### 1. Import and Configure

```python
from logly import logger

# Configure logging level and output format
logger.configure(
    level="INFO",      # Minimum log level
    color=True         # Colored output for console
)
```

### 2. Add Output Destinations

```python
# Add console output (automatically added by configure)
# Add file output with daily rotation
logger.add("logs/app.log", rotation="daily", retention=7)
```

### 3. Start Logging

```python
# Log messages at different levels
logger.info("Application started", version="1.0.0")
logger.debug("Debug information", step=1)
logger.warning("Low disk space", available_gb=2.5)
logger.error("Failed to connect", retry_count=3)
logger.critical("System out of memory")

# Always call complete() before exit
logger.complete()
```

**Expected Output:**
```
2025-01-15T10:30:15.123456+00:00 [INFO] Application started | version=1.0.0
2025-01-15T10:30:15.124567+00:00 [WARN] Low disk space | available_gb=2.5
2025-01-15T10:30:15.125678+00:00 [ERROR] Failed to connect | retry_count=3
2025-01-15T10:30:15.126789+00:00 [CRITICAL] System out of memory
```

Note: The DEBUG message doesn't appear because the level is set to INFO.

---

## Complete Example

Here's a complete working example:

```python
from logly import logger

def main():
    # Configure
    logger.configure(level="INFO", color=True)
    
    # Add sinks
    logger.add("console")
    logger.add("logs/app.log", rotation="daily", retention=7)
    
    # Log messages
    logger.info("Application starting", version="1.0.0")
    
    try:
        # Your application logic
        process_data()
        logger.success("Processing complete")
        
    except Exception as e:
        logger.exception("Application error")
        raise
    
    finally:
        # Cleanup
        logger.complete()

def process_data():
    logger.debug("Processing data", records=1000)
    # ... processing logic ...
    logger.info("Data processed successfully")

if __name__ == "__main__":
    main()
```

**Expected Output:**
```
2025-01-15T10:30:45.123456+00:00 [INFO] Application starting | version=1.0.0
2025-01-15T10:30:46.234567+00:00 [INFO] Data processed successfully
```

Note: The DEBUG and SUCCESS messages won't appear because level is set to INFO.

---

## Common Patterns

### Pattern 1: Web Application Logging

```python
from logly import logger
from fastapi import FastAPI, Request

app = FastAPI()

# Configure once at startup
@app.on_event("startup")
async def setup_logging():
    logger.configure(level="INFO", json=True)
    logger.add("console")
    logger.add("logs/api.log", rotation="hourly", retention=24)

# Log requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_logger = logger.bind(
        request_id=request.headers.get("X-Request-ID", "unknown"),
        method=request.method,
        path=request.url.path
    )
    
    request_logger.info("Request received")
    response = await call_next(request)
    request_logger.info("Response sent", status=response.status_code)
    
    return response

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    logger.info("Fetching user", user_id=user_id)
    # ... fetch user logic ...
    return {"user_id": user_id, "name": "Alice"}
```

**Expected Output (console and logs/api.log with pretty JSON):**
```json
{
  "timestamp": "2025-01-15T10:30:15.123456+00:00",
  "level": "INFO",
  "message": "Request received",
  "request_id": "req-123",
  "method": "GET",
  "path": "/api/users/123"
}
{
  "timestamp": "2025-01-15T10:30:15.234567+00:00",
  "level": "INFO",
  "message": "Fetching user",
  "user_id": 123
}
{
  "timestamp": "2025-01-15T10:30:15.345678+00:00",
  "level": "INFO",
  "message": "Response sent",
  "request_id": "req-123",
  "status": 200
}
```

### Pattern 2: Script with Progress Logging

```python
from logly import logger
import time

def process_batch(batch_id, items):
    batch_logger = logger.bind(batch_id=batch_id)
    batch_logger.info("Batch started", items=len(items))
    
    for idx, item in enumerate(items):
        with batch_logger.contextualize(item_id=item.id):
            try:
                # Process item
                process_item(item)
                batch_logger.debug("Item processed", progress=f"{idx+1}/{len(items)}")
            except Exception:
                batch_logger.exception("Item failed")
    
    batch_logger.success("Batch complete", duration=time.time())

def main():
    logger.configure(level="INFO")
    logger.add("console")
    logger.add("logs/batch.log", rotation="daily")
    
    batches = get_batches()
    for batch_id, items in enumerate(batches):
        process_batch(batch_id, items)
    
    logger.complete()

if __name__ == "__main__":
    main()
```

**Output:**
```
[2024-01-15 10:30:15] INFO: Batch started batch_id=0 items=100
[2024-01-15 10:30:15] DEBUG: Item processed batch_id=0 item_id=1 progress=1/100
[2024-01-15 10:30:15] DEBUG: Item processed batch_id=0 item_id=2 progress=2/100
...
[2024-01-15 10:30:16] SUCCESS: Batch complete batch_id=0 duration=1705312216.123
```

### Pattern 3: Monitoring with Callbacks

```python
from logly import logger

def alert_on_errors(record):
    """Send alerts for critical errors"""
    if record.get("level") == "CRITICAL":
        send_slack_alert(f"🚨 Critical: {record['message']}")

def collect_metrics(record):
    """Collect metrics from logs"""
    if record.get("level") == "ERROR":
        increment_error_counter()

def main():
    logger.configure(level="INFO")
    logger.add("console")
    
    # Register callbacks
    logger.add_callback(alert_on_errors)
    logger.add_callback(collect_metrics)
    
    # Application logic
    logger.info("Application started")
    
    try:
        risky_operation()
    except Exception:
        logger.exception("Operation failed")  # Triggers callbacks
    
    logger.complete()

if __name__ == "__main__":
    main()
```

**Output:**
```
[2024-01-15 10:30:15] INFO: Application started
[2024-01-15 10:30:15] ERROR: Operation failed
[2024-01-15 10:30:15] CRITICAL: System error occurred
Slack alert sent: 🚨 Critical: System error occurred
Error counter incremented
```

---

## Log Levels

Logly supports 7 log levels (from lowest to highest):

| Level | Method | Use Case | Example |
|-------|--------|----------|---------|
| **TRACE** | `logger.trace()` | Detailed debugging | Function entry/exit |
| **DEBUG** | `logger.debug()` | Development debugging | Variable values |
| **INFO** | `logger.info()` | General information | Application state |
| **SUCCESS** | `logger.success()` | Success messages | Operation completed |
| **WARNING** | `logger.warning()` | Warning messages | Deprecated API usage |
| **ERROR** | `logger.error()` | Error messages | Failed operations |
| **CRITICAL** | `logger.critical()` | Critical errors | System failures |

```python
# Examples
logger.trace("Function called", args={"x": 1, "y": 2})
logger.debug("Variable value", x=42)
logger.info("User logged in", user="alice")
logger.success("Payment processed", amount=99.99)
logger.warning("API rate limit approaching", remaining=10)
logger.error("Database connection failed", retry_count=3)
logger.critical("System out of memory", available_mb=10)
```

**Output:**
```
[2024-01-15 10:30:15] TRACE: Function called args={"x": 1, "y": 2}
[2024-01-15 10:30:15] DEBUG: Variable value x=42
[2024-01-15 10:30:15] INFO: User logged in user=alice
[2024-01-15 10:30:15] SUCCESS: Payment processed amount=99.99
[2024-01-15 10:30:15] WARNING: API rate limit approaching remaining=10
[2024-01-15 10:30:15] ERROR: Database connection failed retry_count=3
[2024-01-15 10:30:15] CRITICAL: System out of memory available_mb=10
```

---

## Output Formats

### Text Format (Default)

```python
logger.configure(json=False, color=True)
logger.info("User logged in", user="alice", ip="192.168.1.1")
```

**Output:**
```
2025-01-15 10:30:45 | INFO     | User logged in user=alice ip=192.168.1.1
```

### JSON Format

```python
logger.configure(json=True, pretty_json=False)
logger.info("User logged in", user="alice", ip="192.168.1.1")
```

**Output:**
```json
{"timestamp":"2025-01-15T10:30:45.123Z","level":"INFO","message":"User logged in","fields":{"user":"alice","ip":"192.168.1.1"}}
```

### Pretty JSON (Development)

```python
logger.configure(json=True, pretty_json=True)
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

## File Rotation

### Time-Based Rotation

```python
# Daily rotation (new file every day at midnight)
logger.add("logs/app.log", rotation="daily", retention=7)

# Hourly rotation
logger.add("logs/app.log", rotation="hourly", retention=24)

# Minutely rotation (for testing)
logger.add("logs/app.log", rotation="minutely", retention=60)
```

**Output:**
```
File sink added: logs/app.log (daily rotation, 7 day retention)
File sink added: logs/app.log (hourly rotation, 24 hour retention)
File sink added: logs/app.log (minutely rotation, 60 minute retention)
```

### Size-Based Rotation

```python
# Rotate when file reaches 10MB
logger.add("logs/app.log", size_limit="10MB", retention=5)

# Combine time and size rotation
logger.add("logs/app.log", rotation="daily", size_limit="500MB", retention=7)
```

**Output:**
```
File sink added: logs/app.log (size limit 10MB, 5 file retention)
File sink added: logs/app.log (daily rotation, size limit 500MB, 7 day retention)
```

### Retention Policy

```python
# Keep last 7 rotated files (older files auto-deleted)
logger.add("logs/app.log", rotation="daily", retention=7)

# Unlimited retention (set to None)
logger.add("logs/app.log", rotation="daily", retention=None)
```

**Output:**
```
File sink added: logs/app.log (daily rotation, 7 day retention)
File sink added: logs/app.log (daily rotation, unlimited retention)
```

---

## Context Management

### Bind (Persistent Context)

```python
# Create logger with persistent context
request_logger = logger.bind(request_id="r-123", user="alice")

# All logs include context
request_logger.info("Request started")
# Output: ... request_id=r-123 user=alice

request_logger.error("Request failed")
# Output: ... request_id=r-123 user=alice
```

**Output:**
```
[2024-01-15 10:30:15] INFO: Request started request_id=r-123 user=alice
[2024-01-15 10:30:15] ERROR: Request failed request_id=r-123 user=alice
```

### Contextualize (Temporary Context)

```python
request_logger = logger.bind(request_id="r-123")

with request_logger.contextualize(step="validation"):
    request_logger.debug("Validating input")
    # Output: ... request_id=r-123 step=validation

request_logger.info("Validation complete")
# Output: ... request_id=r-123 (no step field)
```

**Output:**
```
[2024-01-15 10:30:15] DEBUG: Validating input request_id=r-123 step=validation
[2024-01-15 10:30:15] INFO: Validation complete request_id=r-123
```

---

## Exception Handling

### Automatic Exception Logging

```python
# As decorator (swallow exception)
@logger.catch(reraise=False)
def may_fail():
    return 1 / 0  # Exception logged, not raised

# As decorator (re-raise)
@logger.catch(reraise=True)
def critical_operation():
    risky_code()  # Exception logged and re-raised

# As context manager
with logger.catch(reraise=True):
    dangerous_operation()

# Manual exception logging
try:
    risky_operation()
except Exception:
    logger.exception("Operation failed", operation="data_sync")
```

**Output:**
```
[2024-01-15 10:30:15] ERROR: Exception in may_fail: division by zero
[2024-01-15 10:30:15] CRITICAL: Exception in critical_operation: risky_code failed
[2024-01-15 10:30:15] ERROR: Exception in context: dangerous_operation failed
[2024-01-15 10:30:15] ERROR: Operation failed operation=data_sync
Traceback (most recent call last):
  File "example.py", line 25, in risky_operation
    ZeroDivisionError: division by zero
```

---

## Best Practices

### ✅ DO

```python
# 1. Always call complete() before exit
logger.complete()

# 2. Use appropriate log levels
logger.error("Connection failed", retry=3)  # Error condition
logger.info("User logged in", user="alice")  # Normal info

# 3. Include context
request_logger = logger.bind(request_id=req_id)
request_logger.info("Processing")

# 4. Configure once at startup
logger.configure(level="INFO", json=True)
logger.add("console")
logger.add("logs/app.log", rotation="daily")
```

**Output:**
```
Logger completed successfully
[2024-01-15 10:30:15] ERROR: Connection failed retry=3
[2024-01-15 10:30:15] INFO: User logged in user=alice
[2024-01-15 10:30:15] INFO: Processing request_id=123
Logger configured successfully
Console sink added
File sink added: logs/app.log (daily rotation)
```

### ❌ DON'T

```python
# 1. Don't log sensitive data
logger.info("Login attempt", password=password)  # ❌ Security risk

# 2. Don't log in tight loops without filtering
for i in range(1000000):
    logger.debug(f"Iteration {i}")  # ❌ Performance hit

# 3. Don't forget cleanup
# ... logging ...
# (missing logger.complete())  # ❌ Buffered logs may be lost

# 4. Don't use string concatenation
logger.info("User " + user + " logged in")  # ❌ Use structured logging instead

# 5. Don't configure multiple times
logger.configure(level="INFO")
logger.configure(level="DEBUG")  # ❌ Configure once
```

**Output (What NOT to do):**
```
[2024-01-15 10:30:15] INFO: Login attempt password=secret123  # ❌ Sensitive data exposed
[2024-01-15 10:30:15] DEBUG: Iteration 0
[2024-01-15 10:30:15] DEBUG: Iteration 1
... (999,998 more lines)  # ❌ Performance impact
# Logs may be lost on exit  # ❌ No cleanup
[2024-01-15 10:30:15] INFO: User alice logged in  # ❌ Less efficient
Logger configured successfully
Logger reconfigured successfully  # ❌ Multiple configurations
```

---

## Next Steps

<div class="grid cards" markdown>

-   **API Reference**

    ---

    Complete documentation of all methods

    [API Reference](api-reference/index.md)

-   **Callbacks**

    ---

    Async callbacks for log events

    [Callbacks Docs](api-reference/callbacks.md)

-   **Utilities**

    ---

    Enable/disable, custom levels, cleanup

    [Utilities Docs](api-reference/utilities.md)

</div>
