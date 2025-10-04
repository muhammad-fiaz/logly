---
title: Error Handling Guide - Logly Python Logging
description: Comprehensive error handling guide for Logly Python logging library with user-friendly error messages and troubleshooting.
keywords: python, logging, error handling, guide, troubleshooting, messages, logly
---

# Error Handling

Logly provides comprehensive error handling with user-friendly error messages that help you quickly identify and fix configuration issues.

## Overview

All runtime errors from Logly include:

- A clear description of the problem
- Valid options or expected format (where applicable)
- A link to the [GitHub issue tracker](https://github.com/muhammad-fiaz/logly) for reporting bugs

## Error Types

### InvalidLevel

Raised when an invalid log level is provided.

**Valid levels:** `TRACE`, `DEBUG`, `INFO`, `SUCCESS`, `WARNING`, `ERROR`, `CRITICAL`

**Example:**

```python
from logly import logger

try:
    logger.configure(level="INVALID_LEVEL")
except ValueError as e:
    print(e)
```

**Output:**

```
Invalid log level: 'INVALID_LEVEL'. Valid levels are: TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL

If you believe this is a bug in Logly, please report it at: https://github.com/muhammad-fiaz/logly
```

### InvalidRotation

Raised when an invalid rotation policy is provided.

**Valid policies:** `daily`, `hourly`, `minutely`, or size-based (e.g., `"10MB"`)

**Example:**

```python
try:
    logger.add("app.log", rotation="invalid_rotation")
except ValueError as e:
    print(e)
```

**Output:**

```
Invalid rotation policy: 'invalid_rotation'. Valid policies are: daily, hourly, minutely, or size-based (e.g., '10MB')

If you believe this is a bug in Logly, please report it at: https://github.com/muhammad-fiaz/logly
```

### InvalidSizeLimit

Raised when an invalid size limit format is provided.

**Valid formats:** `500B`, `5KB`, `10MB`, `1GB`

**Example:**

```python
try:
    logger.add("app.log", size_limit="invalid_size")
except ValueError as e:
    print(e)
```

**Output:**

```
Invalid size limit: 'invalid_size'. Expected format: '500B', '5KB', '10MB', '1GB'

If you believe this is a bug in Logly, please report it at: https://github.com/muhammad-fiaz/logly
```

## Parameter Validation

Logly validates all configuration parameters at the time of configuration to fail fast and provide clear error messages.

### Log Level Validation

Log levels are case-insensitive and validated against the list of supported levels:

```python
logger.configure(level="info")   # ✓ Valid (case-insensitive)
logger.configure(level="INFO")   # ✓ Valid
logger.configure(level="Debug")  # ✓ Valid
logger.configure(level="INVALID") # ✗ Raises ValueError
```

### Rotation Policy Validation

Rotation policies are case-insensitive and support both time-based and size-based rotation:

```python
# Time-based rotation
logger.add("app.log", rotation="daily")    # ✓ Valid
logger.add("app.log", rotation="HOURLY")   # ✓ Valid
logger.add("app.log", rotation="minutely") # ✓ Valid

# Size-based rotation
logger.add("app.log", rotation="10MB")     # ✓ Valid
logger.add("app.log", rotation="1GB")      # ✓ Valid

# Invalid
logger.add("app.log", rotation="weekly")   # ✗ Raises ValueError
```

### Size Limit Validation

Size limits must include a number followed by a unit (B, KB, MB, or GB):

```python
logger.add("app.log", size_limit="500B")    # ✓ Valid (bytes)
logger.add("app.log", size_limit="1KB")     # ✓ Valid (kilobytes)
logger.add("app.log", size_limit="10MB")    # ✓ Valid (megabytes)
logger.add("app.log", size_limit="1GB")     # ✓ Valid (gigabytes)
logger.add("app.log", size_limit=" 5 MB ")  # ✓ Valid (spaces trimmed)

logger.add("app.log", size_limit="500")     # ✗ Raises ValueError (missing unit)
logger.add("app.log", size_limit="10TB")    # ✗ Raises ValueError (TB not supported)
```

## Best Practices

### 1. Validate Early

Configure your logger at application startup to catch configuration errors early:

```python
from logly import logger

def setup_logging():
    """Configure logging at application startup."""
    try:
        logger.configure(
            level="INFO",
            color=True,
            console=True
        )
        logger.add(
            "logs/app.log",
            rotation="daily",
            retention=7
        )
    except ValueError as e:
        print(f"Logging configuration error: {e}")
        raise
    
    return logger

# At application startup
logger = setup_logging()
```

### 2. Handle Errors Gracefully

Provide fallback configuration if user-provided configuration fails:

```python
import os

def configure_logging_with_fallback():
    """Configure logging with fallback to defaults."""
    # Try to use environment variable or config file
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    try:
        logger.configure(level=log_level)
    except ValueError:
        # Fall back to INFO level if invalid level provided
        print(f"Warning: Invalid log level '{log_level}', using INFO")
        logger.configure(level="INFO")
    
    return logger
```

### 3. Report Bugs

If you encounter an error that you believe is a bug in Logly:

1. Check if the error message indicates invalid configuration
2. Verify your configuration against the valid options shown in the error
3. If the error seems incorrect, report it at [github.com/muhammad-fiaz/logly/issues](https://github.com/muhammad-fiaz/logly/issues)

## Exception Hierarchy

Logly uses Python's standard exception types:

- **ValueError**: Configuration and validation errors (invalid levels, rotation policies, size limits)
- **IOError**: File operation errors (failed to open, write, or rotate files)
- **RuntimeError**: Async operation and callback execution errors

## See Also

- [Configuration Guide](../guides/configuration.md) - Detailed configuration options
- [API Reference - Exceptions](../api-reference/exceptions.md) - Complete exception documentation
