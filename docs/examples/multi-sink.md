---
title: Multi-Sink Setup - Logly Examples
description: Multi-sink logging example showing how to configure Logly to log to multiple destinations simultaneously with different formats.
keywords: python, logging, example, multi-sink, multiple, destinations, console, file, json, logly
---

# Multi-Sink Setup

This example demonstrates how to configure Logly to send logs to multiple destinations simultaneously, with console and file logging.

## Code Example

```python
from logly import logger

# Configure global settings
logger.configure(level="DEBUG")

# Sink 1: Console - only INFO and above
logger.add("console", filter_min_level="INFO")

# Sink 2: Text file - all logs with rotation
logger.add(
    "app.log",
    filter_min_level="DEBUG",
    rotation="daily",
    retention=7
)

# Sink 3: JSON file - only warnings and errors
logger.add(
    "errors.json",
    filter_min_level="WARNING",
    pretty_json=True
)

# Test logging at different levels
logger.debug("Debug message - only in app.log")
logger.info("Info message - console and app.log")
logger.warning("Warning - all three sinks")
logger.error("Error - all three sinks", error_code="E500")

logger.complete()
```

## Expected Output

### Console Output (INFO and above)
```
2025-01-15T14:32:10.123456+00:00 [INFO] Info message - console and app.log
2025-01-15T14:32:10.124567+00:00 [WARN] Warning - all three sinks
2025-01-15T14:32:10.125678+00:00 [ERROR] Error - all three sinks | error_code=E500
```

### File `app.log` (All DEBUG and above)
```
2025-01-15T14:32:10.122345+00:00 [DEBUG] Debug message - only in app.log
2025-01-15T14:32:10.123456+00:00 [INFO] Info message - console and app.log
2025-01-15T14:32:10.124567+00:00 [WARN] Warning - all three sinks
2025-01-15T14:32:10.125678+00:00 [ERROR] Error - all three sinks | error_code=E500
```

### File `errors.json` (WARNING and above, pretty JSON)
```json
{
  "timestamp": "2025-01-15T14:32:10.124567+00:00",
  "level": "WARNING",
  "message": "Warning - all three sinks"
}
{
  "timestamp": "2025-01-15T14:32:10.125678+00:00",
  "level": "ERROR",
  "message": "Error - all three sinks",
  "error_code": "E500"
}
```

### What Happens

1. **Each sink has independent filtering**:
   - Console: Shows INFO, WARN, ERROR (no DEBUG)
   - app.log: Shows everything (DEBUG and above)
   - errors.json: Only WARNING and ERROR

2. **Same log event goes to multiple destinations**:
   - The WARNING and ERROR messages appear in all three sinks
   - The INFO message appears in console and app.log (not errors.json)
   - The DEBUG message only appears in app.log

3. **Different formats per sink**:
   - Console and app.log use default text format
   - errors.json uses pretty-printed JSON format

4. **File rotation on app.log**:
   - Rotates daily (creates new file at midnight)
   - Keeps last 7 days of logs
   - Old logs are automatically deleted

## Advanced Multi-Sink Patterns

### Environment-Based Configuration

```python
import os
from logly import logger

def configure_logging():
    # Always log to console
    logger.configure(level="DEBUG")
    logger.add("console", filter_min_level="INFO")

    # Add file logging in production
    if os.getenv("ENVIRONMENT") == "production":
        logger.add("/var/log/app.log", filter_min_level="WARNING", rotation="100 MB", retention=30)

    # Add JSON logging for log aggregation
    if os.getenv("LOG_AGGREGATION_URL"):
        logger.add(callback=send_to_log_aggregator, filter_min_level="ERROR")

def send_to_log_aggregator(record):
    """Send log record to external log aggregation service"""
    # Implementation for sending to ELK, Splunk, etc.
    pass
```

### Service-Specific Sinks

```python
from logly import logger

# Configure different sinks for different services
logger.configure(level="DEBUG")

# General application logs
logger.add("app.log", filter_min_level="INFO")

# Security events only
logger.add("security.log", filter_min_level="WARNING")

# Performance metrics
logger.add("performance.log", filter_min_level="INFO")

# Audit trail
logger.add("audit.log")

# Usage
logger.info("User login", tags=["security"], user="john", ip="192.168.1.1")
logger.info("Query executed", category="performance", duration_ms=150)
logger.info("File accessed", audit=True, user="john", action="read", resource="/etc/passwd")
```

## Sink Types and Options

### File Sink Options
```python
logger.configure(level="INFO")
logger.add(
    "logs/app.log",
    filter_min_level="INFO",
    rotation="10 MB",      # Size-based rotation
    retention=7,           # Number of files to keep
    async_write=True       # Async writing
)
```

### Console Sink Options
```python
logger.configure(level="INFO")
logger.add("console", filter_min_level="INFO")
```

### Callback Sink Options
```python
logger.configure(level="ERROR")
logger.add(
    callback=my_callback_function,
    filter_min_level="ERROR"
)
```

## Key Features Demonstrated

- **Multiple destinations**: Log to console, files, and external systems
- **Different formats**: Human-readable, structured JSON, detailed traces
- **Level filtering**: Different log levels per sink
- **Rotation and retention**: Automatic log file management
- **Context sharing**: Same context appears in all sinks