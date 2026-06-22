---
title: Exceptions
description: Complete reference for logly exception classes
---

# Exceptions

All Logly exceptions inherit from a single base class. Import them from `logly.exceptions`:

```python
from logly.exceptions import (
    LoglyError,
    SinkError,
    FormatterError,
    FilterError,
    ConfigError,
    RotationError,
    CompressionError,
)
```

## Exception Hierarchy

```
LoglyError
├── SinkError
│   ├── RotationError
│   └── CompressionError
├── FormatterError
├── FilterError
└── ConfigError
```

---

## Base Exception

### LoglyError

Base exception for all Logly errors. Catch this to handle any Logly-related error.

```python
from logly.exceptions import LoglyError

try:
    logger.add("nonexistent/dir/file.log")
except LoglyError as e:
    print(f"Logly error: {e}")
```

---

## Sink Errors

### SinkError

Raised when a sink operation fails (write errors, connection failures, etc.).

```python
from logly.exceptions import SinkError

try:
    logger.info("Test message")
except SinkError as e:
    print(f"Sink failed: {e}")
```

**Common causes:**
- File system permission denied
- Network connection timeout
- Disk full
- Invalid sink configuration

---

### RotationError

Raised when log rotation fails. Inherits from `SinkError`.

```python
from logly.exceptions import RotationError

try:
    logger.add("app.log", rotation="invalid_policy")
except RotationError as e:
    print(f"Rotation failed: {e}")
```

**Common causes:**
- Invalid rotation policy string
- File system permission denied during rename
- Rotation function raised an exception

---

### CompressionError

Raised when log compression fails. Inherits from `SinkError`.

```python
from logly.exceptions import CompressionError

try:
    logger.add("app.log", compression="unknown_codec")
except CompressionError as e:
    print(f"Compression failed: {e}")
```

**Common causes:**
- Unknown compression codec
- Missing compression library (e.g., `zstd` not installed)
- File system permission denied

---

## Formatter Errors

### FormatterError

Raised when a log format string is invalid or a formatter function fails.

```python
from logly.exceptions import FormatterError

try:
    logger.add("stdout", format="{invalid_token}")
except FormatterError as e:
    print(f"Format error: {e}")
```

**Common causes:**
- Unknown format token (e.g., `{invalid}`)
- Malformed time format (e.g., `{time:}`)
- Formatter function raised an exception

---

## Filter Errors

### FilterError

Raised when a filter function is invalid or raises an exception.

```python
from logly.exceptions import FilterError

try:
    logger.add("stdout", filter="not_a_function")
except FilterError as e:
    print(f"Filter error: {e}")
```

**Common causes:**
- Filter is not callable
- Filter function raised an exception
- Filter returned non-boolean value

---

## Config Errors

### ConfigError

Raised when logger configuration is invalid.

```python
from logly.exceptions import ConfigError

try:
    logger.configure(handlers="not_a_list")
except ConfigError as e:
    print(f"Config error: {e}")
```

**Common causes:**
- Invalid handler configuration
- Missing required parameters
- Conflicting configuration options

---

## Error Handling Patterns

### Catch All Logly Errors

```python
from logly.exceptions import LoglyError

try:
    logger.add("app.log", rotation="daily")
    logger.info("Application started")
except LoglyError as e:
    print(f"Logging error: {e}")
```

### Catch Specific Errors

```python
from logly.exceptions import RotationError, CompressionError

try:
    logger.add("app.log", rotation="daily", compression="gzip")
except RotationError:
    print("Rotation failed - check rotation policy")
except CompressionError:
    print("Compression failed - check codec availability")
```

### Error Callback

```python
from logly import logger
from logly.exceptions import LoglyError

def log_error(e: LoglyError):
    print(f"Logging system error: {e}")

logger.add("app.log", catch=True)  # Default: catches silently
```

### Reraise After Logging

```python
from logly import logger

with logger.catch(reraise=True):
    critical_operation()
# Exception is logged then re-raised
```
