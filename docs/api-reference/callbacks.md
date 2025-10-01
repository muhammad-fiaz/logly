---
title: Callbacks API - Logly Python Logging
description: Logly callbacks API reference. Learn how to register asynchronous callback functions for real-time log processing and monitoring.
keywords: python, logging, callbacks, api, asynchronous, handlers, real-time, processing, logly
---

# Callbacks

Methods for managing asynchronous log event handlers.

---

## Overview

Logly supports **async callbacks** that are invoked for each log event. Callbacks enable:

- ✅ **Custom Backends**: Send logs to external services (Slack, PagerDuty, Sentry)
- ✅ **Metrics**: Track log counts, error rates
- ✅ **Alerting**: Trigger alerts on ERROR/CRITICAL logs
- ✅ **Filtering**: Custom filtering logic
- ✅ **Aggregation**: Collect logs for batch processing

**Callback Execution:**
- Callbacks are **async** (run in background)
- Callbacks **do not block** log operations
- Callbacks receive **log record dictionary**
- Callbacks can be **added** or **removed** dynamically

---

## logger.add_callback()

Register an async callback function to be invoked for each log event.

### Signature

```python
logger.add_callback(callback: Callable[[dict], Coroutine], name: str | None = None) -> str
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `callback` | `Callable[[dict], Coroutine]` | *required* | Async function that receives log record |
| `name` | `str \| None` | `None` | Optional callback name (auto-generated if omitted) |

### Returns
- `str`: Callback ID (use with `remove_callback()`)

### Log Record Structure

The callback receives a dictionary with this structure:

```python
{
    "timestamp": "2025-01-15T10:30:45.123Z",  # ISO 8601 timestamp
    "level": "INFO",                           # Log level name
    "message": "User logged in",               # Formatted message
    "fields": {                                # Additional context
        "user_id": "alice",
        "request_id": "abc-123"
    },
    "file": "app.py",                          # Source file
    "line": 42,                                # Source line
    "function": "handle_login",                # Source function
    "module": "myapp.auth",                    # Source module
    "process": 12345,                          # Process ID
    "thread": 67890                            # Thread ID
}
```

### Examples

=== "Slack Notifications"
    ```python
    from logly import logger
    import aiohttp
    
    async def slack_callback(record: dict):
        """Send ERROR/CRITICAL logs to Slack"""
        if record["level"] in ["ERROR", "CRITICAL"]:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
                    json={
                        "text": f"🚨 {record['level']}: {record['message']}",
                        "attachments": [{
                            "color": "danger",
                            "fields": [
                                {"title": k, "value": str(v), "short": True}
                                for k, v in record.get("fields", {}).items()
                            ]
                        }]
                    }
                )
    
    # Register callback
    callback_id = logger.add_callback(slack_callback, name="slack_alerts")
    
    # This will trigger Slack notification
    logger.error("Payment failed", order_id=1234, amount=99.99)
    ```

=== "Metrics Collection"
    ```python
    from logly import logger
    from collections import Counter
    
    log_counts = Counter()
    
    async def metrics_callback(record: dict):
        """Count logs by level"""
        log_counts[record["level"]] += 1
        
        # Every 100 logs, print summary
        if sum(log_counts.values()) % 100 == 0:
            print(f"Log counts: {dict(log_counts)}")
    
    logger.add_callback(metrics_callback, name="metrics")
    
    # Log some events
    for i in range(150):
        logger.info(f"Event {i}")
    # Prints: Log counts: {'INFO': 100}
    # Prints: Log counts: {'INFO': 150}
    ```

=== "Error Alerting"
    ```python
    from logly import logger
    import asyncio
    
    error_count = 0
    error_threshold = 10
    
    async def alert_callback(record: dict):
        """Alert if too many errors"""
        global error_count
        
        if record["level"] in ["ERROR", "CRITICAL"]:
            error_count += 1
            
            if error_count >= error_threshold:
                await send_alert(f"High error rate: {error_count} errors")
                error_count = 0  # Reset counter
    
    async def send_alert(message: str):
        print(f"🚨 ALERT: {message}")
        # Send to PagerDuty, email, etc.
    
    logger.add_callback(alert_callback, name="error_alerting")
    
    # Trigger alerts
    for i in range(12):
        logger.error(f"Error {i}")
    # Prints: 🚨 ALERT: High error rate: 10 errors
    ```

=== "Custom Filtering"
    ```python
    from logly import logger
    
    async def filter_callback(record: dict):
        """Log only errors from specific module"""
        if (record["level"] == "ERROR" and 
            record.get("module", "").startswith("myapp.critical")):
            
            # Re-log to separate file
            with open("critical_errors.log", "a") as f:
                f.write(f"{record['timestamp']} | {record['message']}\n")
    
    logger.add_callback(filter_callback, name="critical_filter")
    ```

=== "Batch Processing"
    ```python
    from logly import logger
    import asyncio
    
    log_buffer = []
    
    async def batch_callback(record: dict):
        """Collect logs and process in batches"""
        log_buffer.append(record)
        
        # Process every 50 logs
        if len(log_buffer) >= 50:
            await process_batch(log_buffer.copy())
            log_buffer.clear()
    
    async def process_batch(records: list):
        print(f"Processing batch of {len(records)} logs")
        # Send to database, analytics service, etc.
    
    logger.add_callback(batch_callback, name="batch_processor")
    ```

### Notes

!!! tip "When to Use Callbacks"
    - **External Services**: Send logs to Slack, PagerDuty, Sentry
    - **Metrics**: Track log volume, error rates
    - **Alerting**: Trigger alerts on specific conditions
    - **Custom Storage**: Write to databases, cloud storage
    - **Real-time Processing**: Stream logs to analytics

!!! warning "Async Required"
    Callbacks **must** be async functions:
    ```python
    # ❌ WRONG: Sync function
    def sync_callback(record: dict):
        print(record)
    
    # ✅ CORRECT: Async function
    async def async_callback(record: dict):
        print(record)
    
    logger.add_callback(async_callback)
    ```

!!! info "Non-Blocking"
    Callbacks run in the background and **do not block** logging:
    ```python
    async def slow_callback(record: dict):
        await asyncio.sleep(5)  # 5 second delay
    
    logger.add_callback(slow_callback)
    
    # This returns immediately (does not wait 5 seconds)
    logger.info("Fast log")
    ```

!!! warning "Exception Handling"
    Exceptions in callbacks are caught and logged:
    ```python
    async def broken_callback(record: dict):
        raise ValueError("Oops!")
    
    logger.add_callback(broken_callback)
    logger.info("Test")  # Logs normally, callback error is caught
    ```

---

## logger.remove_callback()

Unregister a callback function.

### Signature

```python
logger.remove_callback(callback_id: str) -> None
```

### Parameters
- `callback_id` (str): Callback ID returned by `add_callback()`

### Returns
- `None`

### Examples

=== "Remove by ID"
    ```python
    from logly import logger
    
    async def my_callback(record: dict):
        print(f"Log: {record['message']}")
    
    # Add callback
    callback_id = logger.add_callback(my_callback, name="printer")
    
    # Log some events
    logger.info("Event 1")  # Callback invoked
    logger.info("Event 2")  # Callback invoked
    
    # Remove callback
    logger.remove_callback(callback_id)
    
    # Log more events
    logger.info("Event 3")  # Callback NOT invoked
    ```

=== "Named Callbacks"
    ```python
    # Add with explicit name
    callback_id = logger.add_callback(my_callback, name="my_callback")
    
    # Remove using stored ID
    logger.remove_callback(callback_id)
    ```

=== "Multiple Callbacks"
    ```python
    # Add multiple callbacks
    id1 = logger.add_callback(callback1, name="slack")
    id2 = logger.add_callback(callback2, name="metrics")
    id3 = logger.add_callback(callback3, name="alerting")
    
    # Remove specific callback
    logger.remove_callback(id2)  # Remove metrics callback
    
    # Other callbacks still active
    logger.info("Test")  # Triggers slack and alerting callbacks
    ```

### Notes

!!! tip "When to Remove Callbacks"
    - **Cleanup**: Remove callbacks at shutdown
    - **Testing**: Remove callbacks between tests
    - **Dynamic**: Remove callbacks based on configuration changes

!!! warning "Invalid ID"
    Removing a non-existent callback ID is a **no-op** (does not raise error):
    ```python
    logger.remove_callback("non_existent_id")  # Safe, no error
    ```

---

## Complete Example

```python
from logly import logger
import aiohttp
import asyncio

# Configure
logger.configure(level="INFO", json=True)
logger.add("console")
logger.add("logs/app.log")

# Callback 1: Slack notifications for errors
async def slack_callback(record: dict):
    if record["level"] in ["ERROR", "CRITICAL"]:
        async with aiohttp.ClientSession() as session:
            await session.post(
                "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
                json={"text": f"🚨 {record['level']}: {record['message']}"}
            )

# Callback 2: Metrics collection
log_counts = {"INFO": 0, "ERROR": 0}

async def metrics_callback(record: dict):
    level = record["level"]
    if level in log_counts:
        log_counts[level] += 1

# Callback 3: Custom alerting
error_threshold = 5

async def alert_callback(record: dict):
    if record["level"] == "ERROR":
        if log_counts["ERROR"] >= error_threshold:
            print(f"🚨 ALERT: {error_threshold} errors detected!")

# Register callbacks
slack_id = logger.add_callback(slack_callback, name="slack")
metrics_id = logger.add_callback(metrics_callback, name="metrics")
alert_id = logger.add_callback(alert_callback, name="alerting")

# Application code
async def main():
    logger.info("Application started")
    
    # Simulate errors
    for i in range(10):
        logger.error(f"Error {i}", error_code=i)
        await asyncio.sleep(0.1)
    
    # Print metrics
    print(f"Final counts: {log_counts}")
    
    # Cleanup
    logger.remove_callback(slack_id)
    logger.remove_callback(metrics_id)
    logger.remove_callback(alert_id)
    logger.complete()

# Run
asyncio.run(main())
```

**Output:**
```
2025-01-15 10:30:45 | INFO | Application started
2025-01-15 10:30:45 | ERROR | Error 0 error_code=0
...
2025-01-15 10:30:46 | ERROR | Error 4 error_code=4
🚨 ALERT: 5 errors detected!
...
Final counts: {'INFO': 1, 'ERROR': 10}
```

---

## Best Practices

### ✅ DO

```python
# 1. Use async callbacks
async def good_callback(record: dict):
    await process_async(record)

logger.add_callback(good_callback)

# 2. Handle exceptions in callbacks
async def safe_callback(record: dict):
    try:
        await risky_operation(record)
    except Exception as e:
        print(f"Callback error: {e}")

# 3. Store callback IDs for cleanup
callback_id = logger.add_callback(my_callback)
# Later...
logger.remove_callback(callback_id)

# 4. Use named callbacks for clarity
logger.add_callback(slack_callback, name="slack_alerts")
logger.add_callback(metrics_callback, name="metrics_collector")
```

### ❌ DON'T

```python
# 1. Don't use sync functions
def sync_callback(record: dict):  # ❌ Not async
    print(record)

logger.add_callback(sync_callback)  # ❌ Won't work

# 2. Don't perform blocking I/O
async def blocking_callback(record: dict):
    with open("file.log", "a") as f:  # ❌ Blocking I/O
        f.write(str(record))

# Use async I/o instead:
async def async_callback(record: dict):
    async with aiofiles.open("file.log", "a") as f:  # ✅ Async I/O
        await f.write(str(record))

# 3. Don't forget to remove callbacks
logger.add_callback(temp_callback)
# ... use logger ...
# ❌ Callback still active (memory leak)

# ✅ Always cleanup:
callback_id = logger.add_callback(temp_callback)
# ... use logger ...
logger.remove_callback(callback_id)

# 4. Don't log inside callbacks (infinite loop)
async def bad_callback(record: dict):
    logger.info("Processing log")  # ❌ Triggers callback again!
```

---

## Performance

### Callback Overhead

- **Minimal**: Callbacks run in background
- **Non-Blocking**: Logging continues immediately
- **Concurrent**: Multiple callbacks run in parallel

### Best Performance

```python
# 1. Use batch processing
log_buffer = []

async def batch_callback(record: dict):
    log_buffer.append(record)
    if len(log_buffer) >= 100:
        await process_batch(log_buffer.copy())
        log_buffer.clear()

# 2. Filter early
async def filtered_callback(record: dict):
    if record["level"] != "ERROR":
        return  # Skip non-errors
    await process_error(record)

# 3. Use connection pooling
session = aiohttp.ClientSession()  # Reuse session

async def http_callback(record: dict):
    await session.post(url, json=record)
```
