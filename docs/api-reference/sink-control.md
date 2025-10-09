---
title: Sink Control API - Logly Python Logging
description: Logly sink control API reference. Learn how to enable/disable individual sinks and manage global logging state for fine-grained control.
keywords: python, logging, sink control, api, enable, disable, global, state, logly
---

# API Reference: Sink Control

Control individual sinks (enable/disable) and manage global logging state.

## Overview

Logly provides two levels of logging control:

1. **Global Control**: The `console` parameter in `configure()` acts as a master kill-switch
2. **Per-Sink Control**: Individual sinks can be enabled/disabled independently

Both controls work together: logging only occurs when BOTH global AND sink-level are enabled.

---

## Global Logging Control

### `configure(console=True|False)`

The `console` parameter controls **ALL** logging globally, not just console output.

```python
from logly import logger

# Enable ALL logging (default)
logger.configure(console=True)
logger.info("This appears")

# Disable ALL logging (kill-switch)
logger.configure(console=False)
logger.info("This doesn't appear anywhere")
logger.error("This also doesn't appear")

# Re-enable
logger.configure(console=True)
logger.info("Back to normal")
```

**Performance:** When `console=False`, log calls return immediately with zero overhead.

---

## Per-Sink Control

### `enable_sink(sink_id: int) -> bool`

Enable a specific sink by its handler ID.

**Parameters:**
- `sink_id` (int): The handler ID returned by `add()`

**Returns:**
- `bool`: `True` if sink was found and enabled, `False` if not found

**Example:**

```python
from logly import logger

# Create a file sink
sink_id = logger.add("app.log")

# Disable it temporarily
logger.disable_sink(sink_id)
logger.info("Not written to app.log")

# Re-enable it
logger.enable_sink(sink_id)
logger.info("Written to app.log")
```

**Notes:**
- Sinks are enabled by default when created
- Enabling an already-enabled sink is a no-op (idempotent)
- Returns `False` if sink ID doesn't exist

---

### `disable_sink(sink_id: int) -> bool`

Disable a specific sink by its handler ID.

**Parameters:**
- `sink_id` (int): The handler ID returned by `add()`

**Returns:**
- `bool`: `True` if sink was found and disabled, `False` if not found

**Example:**

```python
from logly import logger

# Create multiple sinks
console_sink = logger.add("console")
file_sink = logger.add("app.log")
error_sink = logger.add("errors.log", filter_min_level="ERROR")

# Disable console during sensitive operation
logger.disable_sink(console_sink)
logger.info("Only goes to files, not console")

# Re-enable console
logger.enable_sink(console_sink)
logger.info("Goes to console and files")
```

**Notes:**
- Disabled sinks remain registered and can be re-enabled
- Disabling an already-disabled sink is a no-op (idempotent)
- Sink configuration (rotation, filters, etc.) is preserved

---

### `is_sink_enabled(sink_id: int) -> bool | None`

Check if a specific sink is currently enabled.

**Parameters:**
- `sink_id` (int): The handler ID returned by `add()`

**Returns:**
- `bool`: `True` if enabled, `False` if disabled
- `None`: If sink ID doesn't exist

**Example:**

```python
from logly import logger

sink_id = logger.add("app.log")

# Check initial state
if logger.is_sink_enabled(sink_id):
    print("Sink is enabled")

# Disable and check again
logger.disable_sink(sink_id)
status = logger.is_sink_enabled(sink_id)
print(f"Sink enabled: {status}")  # False

# Check non-existent sink
status = logger.is_sink_enabled(99999)
print(f"Invalid sink: {status}")  # None
```

---

## Combined Control Examples

### Example 1: Temporary Global Disable

```python
from logly import logger

logger.add("app.log")
logger.add("debug.log")

# Disable ALL logging temporarily
logger.configure(console=False)

# Process sensitive data (no logs)
process_passwords()
process_credit_cards()

# Re-enable logging
logger.configure(console=True)
logger.info("Logging resumed")
```

### Example 2: Selective Sink Control

```python
from logly import logger

# Set up multiple sinks
console = logger.add("console")
debug_log = logger.add("debug.log")
production_log = logger.add("production.log", filter_min_level="INFO")

# Development mode: all sinks enabled
logger.debug("Development message")  # Goes to console and debug.log

# Production mode: disable debug log
logger.disable_sink(debug_log)
logger.disable_sink(console)
logger.debug("Not logged anywhere")
logger.info("Only in production.log")
```

### Example 3: Conditional Logging

```python
from logly import logger
import os

# Set up logging
file_sink = logger.add("app.log")

# Disable file logging in tests
if os.getenv("TESTING"):
    logger.disable_sink(file_sink)

# Or disable ALL logging in tests
if os.getenv("TESTING"):
    logger.configure(console=False)
```

### Example 4: Performance-Critical Sections

```python
from logly import logger
import time

logger.add("app.log")

# Disable logging during performance-critical loop
logger.configure(console=False)

start = time.time()
for i in range(1000000):
    expensive_operation(i)
    # logger.debug() calls here have zero overhead
elapsed = time.time() - start

# Re-enable and log results
logger.configure(console=True)
logger.info(f"Operation completed in {elapsed:.2f}s")
```

---

## Control Flow

```
Log Call (e.g., logger.info("message"))
    ↓
Check Global Enabled (console parameter)
    ↓ NO → Return immediately (zero overhead)
    ↓ YES
    ↓
Check Sink Enabled (per-sink flag)
    ↓ NO → Skip this sink
    ↓ YES
    ↓
Check Level Filters
    ↓
Check Module/Function Filters
    ↓
Write to Sink
```

**Key Points:**
- Global disable provides early exit (fastest)
- Per-sink disable skips individual sinks
- Both controls are independent and complementary

---

## Best Practices

### 1. Use Global Control for Complete Shutdown

```python
# Disable ALL logging in production errors
logger.configure(console=False)
```

### 2. Use Per-Sink Control for Selective Output

```python
# Disable console in background workers
console_id = logger.add("console")
if is_background_worker:
    logger.disable_sink(console_id)
```

### 3. Store Sink IDs for Later Control

```python
class App:
    def __init__(self):
        self.console_sink = logger.add("console")
        self.file_sink = logger.add("app.log")
    
    def quiet_mode(self):
        logger.disable_sink(self.console_sink)
    
    def verbose_mode(self):
        logger.enable_sink(self.console_sink)
```

### 4. Check State Before Toggling

```python
# Toggle sink state
if logger.is_sink_enabled(sink_id):
    logger.disable_sink(sink_id)
else:
    logger.enable_sink(sink_id)
```

### 5. Use Context Managers for Temporary Changes

```python
from contextlib import contextmanager

@contextmanager
def silence_logging():
    """Temporarily disable all logging."""
    logger.configure(console=False)
    try:
        yield
    finally:
        logger.configure(console=True)

# Usage
with silence_logging():
    sensitive_operation()
```

---

## Comparison with Other Loggers

### Loguru

```python
# Loguru: Remove sink to disable
from loguru import logger
handler_id = logger.add("file.log")
logger.remove(handler_id)  # Can't re-enable easily

# Logly: Disable/enable without removing
from logly import logger
sink_id = logger.add("file.log")
logger.disable_sink(sink_id)  # Temporarily disable
logger.enable_sink(sink_id)   # Re-enable later
```

### Standard Logging

```python
# Standard: Disable by setting level
import logging
logging.disable(logging.CRITICAL)  # Disables everything

# Logly: More granular control
logger.configure(console=False)  # Global disable
logger.disable_sink(specific_sink)  # Sink-specific disable
```

---

## API Summary

| Method | Purpose | Returns |
|--------|---------|---------|
| `configure(console=bool)` | Global enable/disable ALL logging | None |
| `enable_sink(sink_id)` | Enable specific sink | True/False |
| `disable_sink(sink_id)` | Disable specific sink | True/False |
| `is_sink_enabled(sink_id)` | Check sink status | True/False/None |

---

## Related Documentation

- [Configuration Guide](configuration.md) - All configure() parameters
- [Sink Management](sink-management.md) - Managing multiple outputs
- [Configuration Guide](../guides/configuration.md#performance-tuning) - Performance optimization strategies
- [API Reference](index.md) - Complete API documentation

---

*Last updated: October 2025*
