---
title: Configuration Guide - Logly
description: Advanced configuration guide for Logly Python logging library. Learn about sinks, formats, levels, and optimization.
keywords: python, logging, guide, configuration, advanced, sinks, formats, optimization, logly
---

# Configuration Guide

This guide covers advanced configuration options for Logly, including sink configuration, custom formats, performance tuning, and environment-specific setups.

## Configuration Structure

Logly configuration consists of:

```python
logger.configure(
    level="INFO",        # Global minimum log level
    format="{time} | {level} | {message}",  # Default format
    sinks=[             # List of output destinations
        {
            "type": "console",
            # ... sink-specific options
        }
    ]
)
```

## Sink Types

### Console Sink

Outputs to stdout/stderr with optional colors.

```python
{
    "type": "console",
    "level": "INFO",           # Minimum level for this sink
    "format": "{time} | {level} | {message}",
    "colorize": True,          # Enable colored output
    "stderr": False            # Use stderr instead of stdout
}
```

### File Sink

Writes to files with rotation and retention.

```python
{
    "type": "file",
    "path": "logs/app.log",    # File path
    "level": "DEBUG",
    "format": "{time} | {level} | {message}",
    "rotation": "10 MB",       # Rotate when file reaches size
    "retention": "7 days",     # Keep files for duration
    "encoding": "utf-8",       # File encoding
    "async": True,            # Async writing
    "buffer_size": 8192       # Buffer size for async
}
```

### Callback Sink

Send logs to custom functions.

```python
def my_callback(record):
    """Custom log handler"""
    # record contains: level, message, time, etc.
    send_to_external_service(record)

{
    "type": "callback",
    "level": "ERROR",
    "callback": my_callback,
    "async": True
}
```

## Format Strings

Logly supports custom format strings with placeholders that get replaced with actual log data. Placeholders are enclosed in curly braces `{}` and are case-insensitive.

### Built-in Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{time}` | ISO 8601 timestamp | `2025-01-15T10:30:45Z` |
| `{level}` | Log level | `INFO`, `ERROR` |
| `{message}` | Log message | `User logged in` |
| `{extra}` | All extra fields as `key=value` pairs | `user=alice \| session=123` |

### Extra Field Placeholders

Any key-value pair passed to the log call becomes available as a placeholder:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{module}` | Python module (if provided) | `main`, `utils.auth` |
| `{function}` | Function name (if provided) | `login`, `process_data` |
| `{filename}` | Source filename (if provided) | `app.py`, `utils/auth.py` |
| `{lineno}` | Line number (if provided) | `42`, `157` |
| `{user_id}` | Custom field | `12345` |
| `{request_id}` | Custom field | `req-abc-123` |

### Custom Formatting

```python
# Simple format
format="{time} [{level}] {message}"

# Include specific extra fields
format="{time} [{level}] {message} | user={user_id}"

# Use {extra} for all remaining fields
format="{time} [{level}] {message} | {extra}"

# Include caller information
format="{time} [{level}] {filename}:{lineno} - {message}"

# JSON format
import json
format=json.dumps({
    "timestamp": "{time}",
    "level": "{level}",
    "message": "{message}",
    "extra": "{extra}"
})
```

### Placeholder Behavior

- **Case-insensitive**: `{TIME}`, `{time}`, and `{Time}` all work
- **Extra fields**: Any data passed to `logger.info("msg", key="value")` becomes a placeholder
- **Automatic appending**: Extra fields not used in placeholders are appended at the end (unless `{extra}` is used)
- **Missing placeholders**: Unmatched placeholders remain as-is in the output

## Level Configuration

### Global vs Sink Levels

```python
logger.configure(
    level="WARNING",    # Global minimum - DEBUG/INFO filtered out
    sinks=[
        {
            "type": "console",
            "level": "INFO"    # Override for this sink
        },
        {
            "type": "file",
            "level": "DEBUG"   # Different level for file
        }
    ]
)
```

### Custom Levels

```python
from logly import logger

# Add custom level
logger.add_level("TRACE", 5)  # Below DEBUG

# Use custom level
logger.trace("Very detailed information")
```

## Rotation and Retention

### Size-Based Rotation

```python
{
    "type": "file",
    "path": "app.log",
    "rotation": "10 MB",      # Rotate at 10MB
    # Files: app.log, app.2025-01-15.log, app.2025-01-14.log, ...
}
```

### Time-Based Rotation

```python
{
    "type": "file",
    "path": "app.log",
    "rotation": "1 day",      # Rotate daily
    # Files: app.log, app.2025-01-15.log, app.2025-01-14.log, ...
}
```

### Combined Rotation

```python
{
    "type": "file",
    "path": "app.log",
    "rotation": "1 day",      # OR
    "rotation": "10 MB",      # Whichever comes first
}
```

### Retention Policies

```python
# Keep by count
"retention": "5"             # Keep 5 files

# Keep by time
"retention": "7 days"        # Keep for 7 days
"retention": "1 month"       # Keep for 1 month

# Keep by size
"retention": "1 GB"          # Keep until total size > 1GB
```

## Performance Tuning

### Async Logging

```python
# Enable async for high-throughput logging
{
    "type": "file",
    "path": "app.log",
    "async": True,
    "buffer_size": 65536,        # Larger buffer
    "flush_interval": 5000,      # Flush every 5 seconds
    "max_buffered_lines": 5000   # Max lines to buffer
}
```

### Benchmark Results

```
Sync logging:  ~2.5s for 50,000 logs
Async logging: ~0.8s for 50,000 logs (3x faster)
```

### Memory Considerations

- **Buffer size**: 8KB default, increase for high throughput
- **Max buffered lines**: 1000 default, adjust based on burst patterns
- **Flush interval**: 1s default, decrease for real-time needs

## Environment-Specific Configuration

### Development

```python
def configure_development():
    logger.configure(
        level="DEBUG",
        format="{time} | {level:8} | {file}:{line} | {message}",
        sinks=[
            {
                "type": "console",
                "colorize": True
            }
        ]
    )
```

### Production

```python
def configure_production():
    logger.configure(
        level="WARNING",
        sinks=[
            {
                "type": "console",
                "level": "INFO",
                "format": "{time} | {level} | {message}"
            },
            {
                "type": "file",
                "path": "/var/log/app.log",
                "level": "WARNING",
                "rotation": "100 MB",
                "retention": "30 days",
                "async": True
            },
            {
                "type": "file",
                "path": "/var/log/errors.log",
                "level": "ERROR",
                "format": "{time} | {level} | {message}\n{exception}"
            }
        ]
    )
```

### Testing

```python
def configure_testing():
    logger.configure(
        level="CRITICAL",  # Suppress most logs during tests
        sinks=[
            {
                "type": "callback",
                "callback": capture_logs_for_assertion
            }
        ]
    )

def capture_logs_for_assertion(record):
    """Capture logs for test assertions"""
    test_logs.append(record)
```

## Advanced Features

### Custom Filters

```python
def error_filter(record):
    """Only log errors from specific modules"""
    return record.level >= logging.ERROR and record.module == "auth"

{
    "type": "file",
    "path": "auth_errors.log",
    "filter": error_filter
}
```

### Dynamic Configuration

```python
import os

# Load from environment
log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE", "app.log")

logger.configure(
    level=log_level,
    sinks=[
        {"type": "console"},
        {"type": "file", "path": log_file}
    ]
)
```

### Configuration Validation

```python
def validate_config(config):
    """Validate logging configuration"""
    required_keys = ["level", "sinks"]
    if not all(key in config for key in required_keys):
        raise ValueError("Missing required configuration keys")

    for sink in config["sinks"]:
        if "type" not in sink:
            raise ValueError("Sink missing 'type' field")

# Use before configuring
validate_config(my_config)
logger.configure(**my_config)
```

## Troubleshooting

### Common Issues

**Logs not appearing?**
- Check sink levels vs global level
- Verify file permissions for file sinks
- Ensure callback functions don't raise exceptions

**Performance issues?**
- Enable async logging for high throughput
- Use appropriate buffer sizes
- Consider log level filtering

**Large log files?**
- Configure rotation and retention
- Use appropriate log levels
- Consider separate sinks for different log types

### Debug Configuration

```python
# Enable debug logging for Logly itself
import logging
logging.getLogger("logly").setLevel(logging.DEBUG)

logger.configure(
    level="DEBUG",
    sinks=[{"type": "console"}]
)
```

## Best Practices

### 1. Use Appropriate Levels
```python
logger.debug("Detailed internal state")    # Development
logger.info("User actions, important events")  # Production
logger.warning("Potential issues")         # Always visible
logger.error("Errors that need attention") # Critical
```

### 2. Structure Your Logs
```python
# Good: Structured data
logger.info("User login", user_id=123, ip="192.168.1.1")

# Bad: Unstructured string
logger.info(f"User 123 logged in from 192.168.1.1")
```

### 3. Use Context Effectively
```python
# Set context at request/user boundaries
logger.bind(request_id="req-123", user_id=456)

# Use temporary context for operations
with logger.contextualize(operation="payment"):
    logger.info("Processing payment")
```

### 4. Configure for Your Environment
```python
# Development: Verbose, colored console
# Production: Structured, rotated files
# Testing: Minimal, captured output
```

This guide covers the most important configuration options. For specific use cases, check the [Examples](../examples/basic-console.md) section or [API Reference](../api-reference/index.md).