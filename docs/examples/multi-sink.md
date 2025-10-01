---
title: Multi-Sink Setup - Logly Examples
description: Multi-sink logging example showing how to configure Logly to log to multiple destinations simultaneously with different formats.
keywords: python, logging, example, multi-sink, multiple, destinations, console, file, json, logly
---

# Multi-Sink Setup

This example demonstrates how to configure Logly to send logs to multiple destinations simultaneously, each with different formats and levels.

## Code Example

```python
from logly import logger
import json

# Configure global settings
logger.configure(level="DEBUG")  # Global minimum level

# Add console sink - human readable
logger.add(
    "console",
    level="INFO",  # Only INFO and above to console
    format="{time} | {level:8} | {message}",
    colorize=True
)

# Add file sink - detailed logging
logger.add(
    "app.log",
    level="DEBUG",  # All levels to file
    format="{time} | {level} | {file}:{line} | {message}",
    rotation="10 MB",
    retention=7
)

# Add JSON sink - for log aggregation
logger.add(
    "app.jsonl",
    level="WARNING",  # Only warnings and errors
    json=True,
    rotation="1 day"
)

# Add error-only sink
logger.add(
    "errors.log",
    level="ERROR",  # Only errors
    format="{time} [{level}] {message}\n{exception}",
    rotation="1 week"
)

# Test logging at different levels
logger.debug("This debug message goes only to file")
logger.info("This info message goes to console and file")
logger.warning("This warning goes to all sinks")
logger.error("This error goes to all sinks with full traceback")

# Add context that will appear in all sinks
logger.bind(user_id=12345, request_id="req-abc")

logger.info("User action performed")
logger.warning("Suspicious activity detected", ip="192.168.1.100")
logger.error("Critical system error", component="database", error_code="CONN_FAIL")
```

## Output Examples

### Console Output (Human Readable)
```
2025-01-15 10:30:45 | INFO     | Application started
2025-01-15 10:30:45 | WARNING  | Suspicious activity detected
2025-01-15 10:30:45 | ERROR    | Critical system error
```

### File Output (app.log - Detailed)
```
2025-01-15 10:30:45 | DEBUG | main.py:45 | This debug message goes only to file
2025-01-15 10:30:45 | INFO | main.py:46 | This info message goes to console and file
2025-01-15 10:30:45 | WARNING | main.py:47 | This warning goes to all sinks
2025-01-15 10:30:45 | ERROR | main.py:48 | This error goes to all sinks with full traceback
```

### JSON Output (app.jsonl - Structured)
```json
{"timestamp": "2025-01-15T10:30:45Z", "level": "WARNING", "message": "Suspicious activity detected", "module": "main", "function": "test_logging", "line": 47, "user_id": 12345, "request_id": "req-abc", "ip": "192.168.1.100"}
{"timestamp": "2025-01-15T10:30:45Z", "level": "ERROR", "message": "Critical system error", "module": "main", "function": "test_logging", "line": 48, "user_id": 12345, "request_id": "req-abc", "component": "database", "error_code": "CONN_FAIL"}
```

### Error Output (errors.log - Critical Only)
```
2025-01-15 10:30:45 [ERROR] Critical system error
component=database error_code=CONN_FAIL user_id=12345 request_id=req-abc
Traceback (most recent call last):
  File "main.py", line 48, in test_logging
    CriticalError: System failure
```

## Advanced Multi-Sink Patterns

### Environment-Based Configuration

```python
import os
from logly import logger

def configure_logging():
    # Always log to console
    logger.configure(level="DEBUG")
    logger.add("console", level="INFO", format="{level} | {message}")

    # Add file logging in production
    if os.getenv("ENVIRONMENT") == "production":
        logger.add("/var/log/app.log", level="WARNING", rotation="100 MB", retention=30)

    # Add JSON logging for log aggregation
    if os.getenv("LOG_AGGREGATION_URL"):
        logger.add(callback=send_to_log_aggregator, level="ERROR")

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
logger.add("app.log", level="INFO")

# Security events only
logger.add("security.log", level="WARNING")  # Note: filtering would need custom implementation

# Performance metrics
logger.add("performance.log", level="INFO")  # Note: filtering would need custom implementation

# Audit trail
logger.add("audit.log", format="AUDIT | {time} | {user} | {action} | {resource}")  # Note: filtering would need custom implementation

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
    level="INFO",
    format="{time} | {level} | {message}",
    rotation="10 MB",      # Size-based rotation
    retention=7,           # Number of files to keep
    encoding="utf-8",      # File encoding
    async_=True,           # Async writing
    buffer_size=8192       # Buffer size for async
)
```

### Console Sink Options
```python
logger.configure(level="INFO")
logger.add(
    "console",
    level="INFO",
    format="{time} | {level} | {message}",
    colorize=True,        # Enable/disable colors
    stderr=False          # Use stderr instead of stdout
)
```

### Callback Sink Options
```python
logger.configure(level="ERROR")
logger.add(
    callback=my_callback_function,
    level="ERROR",
    async_=True            # Async callback execution
)
```

## Key Features Demonstrated

- **Multiple destinations**: Log to console, files, and external systems
- **Different formats**: Human-readable, structured JSON, detailed traces
- **Level filtering**: Different log levels per sink
- **Rotation and retention**: Automatic log file management
- **Context sharing**: Same context appears in all sinks