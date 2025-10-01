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

# Configure global settings with console enabled
logger.configure(level="DEBUG", console=True)

# Add file sink - detailed logging to file
logger.add(
    "app.log",
    filter_min_level="DEBUG",  # All levels to file
    rotation="daily",
    retention=7
)

# Add JSON file sink - for log aggregation
logger.add(
    "app.jsonl",
    filter_min_level="WARNING",  # Only warnings and errors
    date_enabled=True
)

# Test logging at different levels
logger.debug("This debug message goes to console and file")
logger.info("This info message goes to console and file")
logger.warning("This warning goes to console, file, and JSON")
logger.error("This error goes to console, file, and JSON")

# Add context that will appear in all logs
logger.bind(user_id=12345, request_id="req-abc")

logger.info("User action performed")
logger.warning("Suspicious activity detected", ip="192.168.1.100")
logger.error("Critical system error", component="database", error_code="CONN_FAIL")
```

## Output Examples

### Console Output (Human Readable)
```
[DEBUG] This debug message goes to console and file | module=__main__ | function=<module>
[INFO] This info message goes to console and file | module=__main__ | function=<module>
[WARN] This warning goes to console, file, and JSON | module=__main__ | function=<module>
[ERROR] This error goes to console, file, and JSON | module=__main__ | function=<module>
[INFO] User action performed | user_id=12345 | request_id=req-abc | module=__main__ | function=<module>
[WARN] Suspicious activity detected | ip=192.168.1.100 | user_id=12345 | request_id=req-abc | module=__main__ | function=<module>
[ERROR] Critical system error | component=database | error_code=CONN_FAIL | user_id=12345 | request_id=req-abc | module=__main__ | function=<module>
```

### File Output (app.log - Text Format)
```
[DEBUG] This debug message goes to console and file | module=__main__ | function=<module>
[INFO] This info message goes to console and file | module=__main__ | function=<module>
[WARN] This warning goes to console, file, and JSON | module=__main__ | function=<module>
[ERROR] This error goes to console, file, and JSON | module=__main__ | function=<module>
[INFO] User action performed | user_id=12345 | request_id=req-abc | module=__main__ | function=<module>
[WARN] Suspicious activity detected | ip=192.168.1.100 | user_id=12345 | request_id=req-abc | module=__main__ | function=<module>
[ERROR] Critical system error | component=database | error_code=CONN_FAIL | user_id=12345 | request_id=req-abc | module=__main__ | function=<module>
```

### JSON Output (app.jsonl - Structured)
```json
{"level": "WARNING", "message": "This warning goes to console, file, and JSON", "module": "__main__", "function": "<module>"}
{"level": "ERROR", "message": "This error goes to console, file, and JSON", "module": "__main__", "function": "<module>"}
{"level": "INFO", "message": "User action performed", "user_id": 12345, "request_id": "req-abc", "module": "__main__", "function": "<module>"}
{"level": "WARNING", "message": "Suspicious activity detected", "ip": "192.168.1.100", "user_id": 12345, "request_id": "req-abc", "module": "__main__", "function": "<module>"}
{"level": "ERROR", "message": "Critical system error", "component": "database", "error_code": "CONN_FAIL", "user_id": 12345, "request_id": "req-abc", "module": "__main__", "function": "<module>"}
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