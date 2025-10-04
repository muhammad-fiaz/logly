---
title: Error Types & Exceptions - Logly Python Logging
description: Complete reference for all error types and exceptions in Logly Python logging library with detailed descriptions and troubleshooting.
keywords: python, logging, errors, exceptions, error types, troubleshooting, logly
---

# Error Types & Exceptions

Complete reference for all error types and exceptions in Logly.

---

## Overview

Logly provides comprehensive error handling with clear, actionable error messages. All errors include a link to the GitHub issue tracker for bug reporting.

| Error Type | Python Exception | Use Case |
|------------|------------------|----------|
| `InvalidLevel` | `ValueError` | Invalid log level string |
| `InvalidRotation` | `ValueError` | Invalid rotation policy |
| `InvalidSizeLimit` | `ValueError` | Invalid size limit format |
| `InvalidFormat` | `ValueError` | Invalid template format |
| `FileOperation` | `IOError` | File I/O errors |
| `AsyncOperation` | `RuntimeError` | Async writing errors |
| `Configuration` | `ValueError` | General configuration errors |
| `CallbackError` | `RuntimeError` | Python callback errors |

---

## InvalidLevel

Raised when an invalid log level string is provided.

### When It Occurs

```python
from logly import logger

# Invalid level in configure()
logger.configure(level="INVALID")  # ❌ Raises ValueError

# Invalid level in add()
logger.add("console", level="INVALID")  # ❌ Raises ValueError
```

### Error Message

```
Invalid log level: 'INVALID'. Valid levels are: TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL

If you believe this is a bug in Logly, please report it at: https://github.com/muhammad-fiaz/logly
```

### Valid Levels

| Level | Severity | Use Case |
|-------|----------|----------|
| `TRACE` | Lowest | Detailed debugging information |
| `DEBUG` | Low | Diagnostic information |
| `INFO` | Normal | General informational messages |
| `SUCCESS` | Normal | Success confirmation messages |
| `WARNING` | Medium | Warning messages |
| `ERROR` | High | Error messages |
| `CRITICAL` | Highest | Critical failures |

**Case Insensitive**: All levels accept uppercase, lowercase, or mixed case:

```python
logger.configure(level="INFO")    # ✓
logger.configure(level="info")    # ✓
logger.configure(level="InFo")    # ✓
```

### Example: Correct Usage

```python
from logly import logger

# Valid levels
logger.configure(level="DEBUG")     # ✓
logger.configure(level="INFO")      # ✓
logger.configure(level="WARNING")   # ✓

logger.add("console", level="ERROR")     # ✓
logger.add("app.log", level="CRITICAL")  # ✓
```

**Expected Output:**
```
No errors - logger configured successfully
```

---

## InvalidRotation

Raised when an invalid rotation policy string is provided.

### When It Occurs

```python
from logly import logger

# Invalid rotation policy
logger.add("app.log", rotation="invalid")  # ❌ Raises ValueError
logger.add("app.log", rotation="weekly")   # ❌ Raises ValueError
```

### Error Message

```
Invalid rotation policy: 'invalid'. Valid policies are: daily, hourly, minutely, or size-based (e.g., '500 B', '1 KB', '10 MB', '1 GB')

If you believe this is a bug in Logly, please report it at: https://github.com/muhammad-fiaz/logly
```

### Valid Rotation Policies

#### Time-Based Rotation

| Policy | Description | Log Files Created |
|--------|-------------|-------------------|
| `daily` | Rotate daily at midnight | `app.log`, `app.2025-01-15.log` |
| `hourly` | Rotate every hour | `app.log`, `app.2025-01-15-10.log` |
| `minutely` | Rotate every minute | `app.log`, `app.2025-01-15-10-30.log` |

**Case Insensitive**: All policies accept any case:

```python
logger.add("app.log", rotation="daily")    # ✓
logger.add("app.log", rotation="DAILY")    # ✓
logger.add("app.log", rotation="Daily")    # ✓
```

#### Size-Based Rotation

| Format | Description | Example |
|--------|-------------|---------|
| `<number> B` | Bytes | `500 B` |
| `<number> KB` | Kilobytes | `1 KB`, `100 KB` |
| `<number> MB` | Megabytes | `10 MB`, `500 MB` |
| `<number> GB` | Gigabytes | `1 GB`, `5 GB` |

**Format Rules**:

- Number must be positive integer
- Space between number and unit is **required**
- Units are case-insensitive

```python
logger.add("app.log", rotation="10 MB")   # ✓
logger.add("app.log", rotation="10 mb")   # ✓
logger.add("app.log", rotation="10MB")    # ❌ Missing space
logger.add("app.log", rotation="10.5 MB") # ❌ Float not allowed
```

### Example: Correct Usage

```python
from logly import logger
logger.configure(level="INFO")

# Time-based rotation
logger.add("daily.log", rotation="daily")       # ✓ Rotate at midnight
logger.add("hourly.log", rotation="hourly")     # ✓ Rotate every hour
logger.add("minute.log", rotation="minutely")   # ✓ Rotate every minute

# Size-based rotation
logger.add("small.log", rotation="1 MB")        # ✓ Rotate at 1 MB
logger.add("medium.log", rotation="10 MB")      # ✓ Rotate at 10 MB
logger.add("large.log", rotation="100 MB")      # ✓ Rotate at 100 MB

# Log some messages
logger.info("Application started")
```

**Expected Output:**
```
2025-01-15 10:30:45 | INFO | Application started
```

**Files Created:**
```
daily.log           # Current log file
hourly.log          # Current log file
minute.log          # Current log file
small.log           # Current log file
```

---

## InvalidSizeLimit

Raised when an invalid size limit format is provided.

### When It Occurs

```python
from logly import logger

# Invalid size limit formats
logger.add("app.log", size_limit="invalid")    # ❌ Raises ValueError
logger.add("app.log", size_limit="10")         # ❌ Raises ValueError (missing unit)
logger.add("app.log", size_limit="10.5 MB")    # ❌ Raises ValueError (float)
```

### Error Message

```
Invalid size limit format: 'invalid'. Expected format: '<number> <unit>' (e.g., '500 B', '1 KB', '10 MB', '1 GB')

If you believe this is a bug in Logly, please report it at: https://github.com/muhammad-fiaz/logly
```

### Valid Size Limit Formats

| Unit | Full Name | Example | Bytes |
|------|-----------|---------|-------|
| `B` | Bytes | `500 B` | 500 |
| `KB` | Kilobytes | `1 KB` | 1,024 |
| `MB` | Megabytes | `10 MB` | 10,485,760 |
| `GB` | Gigabytes | `1 GB` | 1,073,741,824 |

**Format Requirements**:

1. Positive integer number
2. Single space
3. Unit (B, KB, MB, GB)
4. Units are case-insensitive

```python
# Valid formats
logger.add("app.log", size_limit="1 MB")      # ✓
logger.add("app.log", size_limit="1 mb")      # ✓
logger.add("app.log", size_limit="100 KB")    # ✓

# Invalid formats
logger.add("app.log", size_limit="1MB")       # ❌ Missing space
logger.add("app.log", size_limit="1.5 MB")    # ❌ Float not allowed
logger.add("app.log", size_limit="-1 MB")     # ❌ Negative number
logger.add("app.log", size_limit="1 TB")      # ❌ Invalid unit
```

### Example: Correct Usage

```python
from logly import logger
logger.configure(level="INFO")

# Different size limits
logger.add("tiny.log", size_limit="100 KB")     # ✓ Limit to 100 KB
logger.add("small.log", size_limit="1 MB")      # ✓ Limit to 1 MB
logger.add("medium.log", size_limit="50 MB")    # ✓ Limit to 50 MB
logger.add("large.log", size_limit="1 GB")      # ✓ Limit to 1 GB

# Log messages
for i in range(1000):
    logger.info(f"Message {i}")
```

**Expected Output:**
```
2025-01-15 10:30:45 | INFO | Message 0
2025-01-15 10:30:45 | INFO | Message 1
...
```

**Behavior**: When log file reaches size limit, oldest entries are removed.

---

## FileOperation

Raised when file I/O operations fail.

### When It Occurs

```python
from logly import logger

# Invalid file path
logger.add("/invalid/path/app.log")  # ❌ May raise IOError

# Permission denied
logger.add("/root/app.log")  # ❌ May raise IOError (Linux)

# Disk full
logger.add("app.log")  # ❌ May raise IOError (if disk full)
```

### Error Message

```
Failed to open log file '/invalid/path/app.log': No such file or directory

If you believe this is a bug in Logly, please report it at: https://github.com/muhammad-fiaz/logly
```

### Common Causes

| Cause | Solution |
|-------|----------|
| Directory doesn't exist | Create parent directories or use relative path |
| Permission denied | Check file/directory permissions |
| Disk full | Free up disk space |
| File locked | Close other applications using the file |
| Invalid filename | Use valid filename characters |

### Example: Correct Usage

```python
from logly import PyLogger
import os
logger.configure(level="INFO")

# Ensure directory exists
os.makedirs("logs", exist_ok=True)

# Use valid paths
logger.add("logs/app.log")              # ✓ Relative path
logger.add("./output/debug.log")        # ✓ Relative with ./
logger.add("C:/logs/app.log")           # ✓ Absolute path (Windows)
logger.add("/var/log/myapp/app.log")    # ✓ Absolute path (Linux)

logger.info("Logging to file")
```

**Expected Output** (in `logs/app.log`):
```
2025-01-15 10:30:45 | INFO | Logging to file
```

---

## AsyncOperation

Raised when asynchronous operations fail.

### When It Occurs

```python
from logly import logger
logger.configure(level="INFO")
logger.add("app.log", async_write=True)

# Async writer thread fails
logger.info("Message")  # ❌ May raise RuntimeError if async thread crashes
```

### Error Message

```
Async write operation failed: <error details>

If you believe this is a bug in Logly, please report it at: https://github.com/muhammad-fiaz/logly
```

### Common Causes

| Cause | Solution |
|-------|----------|
| Buffer overflow | Increase `max_buffered_lines` |
| Thread panic | Check system resources |
| File write failure | Verify disk space and permissions |

### Example: Correct Usage

```python
from logly import logger
logger.configure(level="INFO")

# Configure async writing with proper limits
logger.add(
    "app.log",
    async_write=True,
    buffer_size=8192,           # ✓ 8 KB buffer
    flush_interval=1000,        # ✓ Flush every second
    max_buffered_lines=1000     # ✓ Max 1000 lines buffered
)

# Log messages
for i in range(100):
    logger.info(f"Message {i}")
```

**Expected Output** (in `app.log`):
```
2025-01-15 10:30:45 | INFO | Message 0
2025-01-15 10:30:45 | INFO | Message 1
...
```

---

## Configuration

Raised for general configuration errors.

### When It Occurs

```python
from logly import logger

# Invalid configuration combination
logger.configure(invalid_param="value")  # ❌ May raise ValueError
```

### Error Message

```
Configuration error: <error details>

If you believe this is a bug in Logly, please report it at: https://github.com/muhammad-fiaz/logly
```

### Example: Correct Usage

```python
from logly import logger

# Valid configuration
logger.configure(
    level="INFO",           # ✓ Valid level
    colorize=True,          # ✓ Enable colors
    backtrace=True,         # ✓ Enable backtrace
    diagnose=False          # ✓ Disable diagnose
)

logger.add("console")
logger.info("Configuration successful")
```

**Expected Output:**
```
2025-01-15 10:30:45 | INFO | Configuration successful
```

---

## CallbackError

Raised when Python callback functions fail.

### When It Occurs

```python
from logly import PyLogger

def bad_callback(record):
    raise ValueError("Callback error")  # ❌ Callback raises exception
logger.add("console", callback=bad_callback)

logger.info("Test")  # ❌ May raise RuntimeError
```

### Error Message

```
Callback execution failed: ValueError: Callback error

If you believe this is a bug in Logly, please report it at: https://github.com/muhammad-fiaz/logly
```

### Example: Correct Usage

```python
from logly import PyLogger

# Safe callback with error handling
def safe_callback(record):
    try:
        # Process record
        print(f"Callback: {record['message']}")
    except Exception as e:
        # Handle errors gracefully
        print(f"Callback error: {e}")
logger.configure(level="INFO")
logger.add("console", callback=safe_callback)

logger.info("Test message")
```

**Expected Output:**
```
Callback: Test message
2025-01-15 10:30:45 | INFO | Test message
```

---

## Error Handling Best Practices

### 1. Validate Early

```python
# Validate parameters before creating logger
valid_levels = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]

level = "INVALID"
if level.upper() not in valid_levels:
    print(f"Invalid level: {level}")
    level = "INFO"  # Use default
logger.configure(level=level)  # ✓ No error
```

### 2. Use Try-Except

```python
from logly import PyLogger

try:
    logger.configure(level="INFO")
    logger.add("app.log", rotation="daily")
    logger.info("Initialization successful")
except ValueError as e:
    print(f"Configuration error: {e}")
except IOError as e:
    print(f"File error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

**Expected Output** (on success):
```
2025-01-15 10:30:45 | INFO | Initialization successful
```

**Expected Output** (on error):
```
Configuration error: Invalid log level: 'INVALID'. Valid levels are: ...
```

### 3. Handle File Errors

```python
import os
from logly import PyLogger

# Ensure log directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logger.configure(level="INFO")

try:
    logger.add(f"{log_dir}/app.log")
    logger.info("File logging enabled")
except IOError as e:
    print(f"Cannot create log file: {e}")
    # Fallback to console only
    logger.add("console")
    logger.info("Using console logging only")
```

### 4. Validate User Input

```python
from logly import PyLogger

def create_logger(level: str, rotation: str):
    """Create logger with validated parameters."""
    # Validate level
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
    if level.upper() not in valid_levels:
        raise ValueError(f"Invalid level: {level}")
    
    # Validate rotation
    valid_rotations = ["daily", "hourly", "minutely"]
    if rotation.lower() not in valid_rotations and not rotation.endswith(("B", "KB", "MB", "GB")):
        raise ValueError(f"Invalid rotation: {rotation}")
    
    # Create logger
    logger.configure(level=level)
    logger.add("app.log", rotation=rotation)
    
    return logger

# Usage
try:
    logger = create_logger(level="INFO", rotation="daily")
    logger.info("Logger created successfully")
except ValueError as e:
    print(f"Validation error: {e}")
```

**Expected Output** (on success):
```
2025-01-15 10:30:45 | INFO | Logger created successfully
```

---

## Reporting Bugs

If you encounter an error that you believe is a bug in Logly:

1. **Check the error message** for validation issues
2. **Verify your configuration** against this reference
3. **Review the examples** in this documentation
4. **Report the issue** at: https://github.com/muhammad-fiaz/logly/issues

**Include in your bug report:**

- Error message (full text)
- Code snippet that reproduces the error
- Python version and OS
- Logly version (`import logly; print(logly.__version__)`)

---

## Summary

| Error Type | Exception | Validation Function | Common Fix |
|------------|-----------|-------------------|------------|
| InvalidLevel | ValueError | `validate_level()` | Use valid level string |
| InvalidRotation | ValueError | `validate_rotation()` | Use valid rotation policy |
| InvalidSizeLimit | ValueError | `validate_size_limit()` | Use correct size format |
| FileOperation | IOError | N/A | Check file permissions |
| AsyncOperation | RuntimeError | N/A | Check buffer configuration |
| Configuration | ValueError | N/A | Verify parameters |
| CallbackError | RuntimeError | N/A | Fix callback function |

For detailed examples and best practices, refer to the [Getting Started Guide](../guides/getting-started.md) and [API Reference](../api-reference/context.md).
