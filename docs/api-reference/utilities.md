---
title: Utility Methods API - Logly Python Logging
description: Logly utility methods API reference. Learn about helper functions for logger control, finalization, and advanced configuration options.
keywords: python, logging, utilities, api, helper, methods, control, finalization, configuration, logly
---

# Utility Methods

Helper methods for controlling logger behavior and finalization.

---

## Overview

Logly provides utility methods for:

| Method | Purpose |
|--------|---------|
| `enable()` | Enable logging for this logger instance |
| `disable()` | Disable logging for this logger instance |
| `level()` | Register custom log level aliases |
| `reset()` | Reset logger configuration to default settings |
| `complete()` | Finalize logger and flush all buffers |

---

## logger.enable()

Enable logging for this logger instance.

### Signature

```python
logger.enable() -> None
```

### Parameters
- None

### Returns
- `None`

### Description

Enables logging for this logger instance. When enabled, log messages are processed and output to configured sinks. When disabled (via `disable()`), all log messages are silently ignored.

### Examples

=== "Basic Usage"
    ```python
    from logly import logger
    
    # Disable logging
    logger.disable()
    logger.info("This won't be logged")
    
    # Re-enable logging
    logger.enable()
    logger.info("This will be logged")
    ```

=== "Temporary Disable"
    ```python
    # Enable logging
    logger.enable()
    logger.info("Logging is enabled")
    
    # Temporarily disable
    logger.disable()
    logger.warning("This warning is suppressed")
    
    # Re-enable
    logger.enable()
    logger.error("This error will be logged")
    ```

=== "Conditional Logging"
    ```python
    # Conditionally enable/disable based on environment
    if debug_mode:
        logger.enable()
    else:
        logger.disable()
    
    logger.debug("Debug information")
    ```

### Notes

!!! tip "Instance-Level Control"
    `enable()` and `disable()` control logging for the entire logger instance, not individual modules.

!!! info "Default State"
    Logging is **enabled** by default when a logger instance is created.

!!! warning "Performance"
    Disabled logging has minimal performance overhead - messages are ignored before formatting.

---

## logger.disable()

Disable logging for this logger instance.

### Signature

```python
logger.disable() -> None
```

### Parameters
- None

### Returns
- `None`

### Description

Disables logging for this logger instance. When disabled, all log messages are silently ignored without any performance overhead from formatting or serialization.

### Examples

=== "Disable All Logging"
    ```python
    from logly import logger
    
    # Disable logging
    logger.disable()
    logger.info("This won't be logged")
    logger.error("This won't be logged either")
    ```

=== "Silence During Tests"
    ```python
    import pytest
    from logly import logger
    
    @pytest.fixture(autouse=True)
    def silence_logs():
        """Disable logging during tests."""
        logger.disable()
        yield
        logger.enable()
    ```

=== "Production Optimization"
    ```python
    # Disable debug logging in production
    if production:
        logger.disable()
    
    # All logging suppressed
    logger.info("Not logged in production")
    ```

### Notes

!!! tip "When to Use disable()"
    - **Testing**: Silence logs during test execution
    - **Production**: Completely disable logging for specific instances
    - **Performance**: Eliminate logging overhead for high-performance sections

!!! warning "Instance-Wide"
    `disable()` affects **all log levels** on this instance:
    ```python
    logger.disable()
    logger.trace("Hidden")
    logger.info("Hidden")
    logger.error("Hidden")  # Even errors are suppressed
    ```

!!! info "Per-Instance"
    Each logger instance (created via `bind()`) has independent enable/disable state:
    ```python
    request_logger = logger.bind(request_id="123")
    request_logger.disable()
    
    logger.info("Still logged")  # Original logger unaffected
    request_logger.info("Suppressed")  # Bound logger disabled
    ```

---

## logger.level()

Register a custom log level name as an alias to an existing level.

### Signature

```python
logger.level(name: str, mapped_to: str) -> None
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Custom level name/alias to create |
| `mapped_to` | `str` | Existing level to map to ("TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL") |

### Returns
- `None`

### Description

Creates custom level names that map to built-in severity levels. This allows domain-specific terminology while leveraging Logly's existing level infrastructure.

### Examples

=== "Basic Alias"
    ```python
    from logly import logger
    
    # Create custom level alias
    logger.level("NOTICE", "INFO")
    
    # Use custom level
    logger.log("NOTICE", "Important notice", category="security")
    ```

=== "Business-Specific Levels"
    ```python
    # Map business terms to technical levels
    logger.level("AUDIT", "INFO")
    logger.level("SECURITY", "WARNING")
    logger.level("FATAL", "CRITICAL")
    
    logger.log("AUDIT", "User login", user="alice", ip="192.168.1.1")
    logger.log("SECURITY", "Suspicious activity detected", threat_level=7)
    logger.log("FATAL", "System shutdown required")
    ```

=== "Application-Specific Terminology"
    ```python
    # E-commerce application
    logger.level("ORDER", "INFO")
    logger.level("PAYMENT", "WARNING")
    logger.level("FRAUD", "ERROR")
    
    logger.log("ORDER", "Order placed", order_id="ORD-12345", amount=99.99)
    logger.log("PAYMENT", "Payment retry", attempt=2)
    logger.log("FRAUD", "Fraudulent transaction blocked", card="****1234")
    ```

=== "Multiple Aliases"
    ```python
    # Create multiple aliases for same level
    logger.level("NOTICE", "INFO")
    logger.level("NOTE", "INFO")
    logger.level("FYI", "INFO")
    
    logger.log("NOTICE", "Server maintenance scheduled")
    logger.log("NOTE", "Configuration updated")
    logger.log("FYI", "Cache cleared")
    ```

### Notes

!!! tip "When to Use level()"
    - **Domain-Specific Terms**: Use business/domain terminology in logs
    - **API Compatibility**: Match level names from other logging libraries
    - **Readability**: Make logs more intuitive for your team
    - **Legacy Support**: Maintain compatibility with existing log level names

!!! info "Alias Behavior"
    - Aliases inherit the severity of the mapped level
    - Filtering and configuration use the mapped level
    - Multiple aliases can map to the same level
    - Aliases are instance-specific (via `bind()`)

!!! warning "No Custom Severity"
    Unlike some logging libraries, `level()` only creates **aliases**:
    ```python
    logger.level("NOTICE", "INFO")  # Maps to INFO (severity 20)
    
    logger.configure(level="WARNING")  # Minimum WARNING (severity 30)
    logger.log("NOTICE", "Test")  # NOT logged (INFO < WARNING)
    ```

---

## logger.reset()

Reset logger configuration to default settings.

### Signature

```python
logger.reset() -> None
```

### Parameters
- None

### Returns
- `None`

### Description

Resets all logger settings to their default values, clearing any per-level controls and custom configurations. This is useful for:

- **Testing**: Reset state between test cases
- **Configuration Reload**: Clear old settings before applying new configuration
- **Debugging**: Return to known default state

### Examples

=== "Basic Usage"
    ```python
    from logly import logger
    
    # Configure logger with custom settings
    logger.configure(
        level="DEBUG",
        color=True,
        show_time=True,
        show_module=True
    )
    logger.info("Custom configuration")
    
    # Reset to defaults
    logger.reset()
    logger.info("Back to default configuration")
    ```

=== "Testing Cleanup"
    ```python
    import pytest
    from logly import logger
    
    @pytest.fixture(autouse=True)
    def reset_logger():
        """Reset logger before each test."""
        yield
        logger.reset()  # Clean up after test
    
    def test_custom_config():
        logger.configure(level="TRACE", color=False)
        logger.trace("Test message")
        # Automatically reset after test
    ```

=== "Configuration Reload"
    ```python
    def load_config(config_file: str):
        # Reset existing configuration
        logger.reset()
        
        # Load new configuration
        config = read_config(config_file)
        logger.configure(**config)
        logger.info("Configuration reloaded", file=config_file)
    ```

=== "Clear Per-Level Controls"
    ```python
    # Configure with per-level controls
    logger.configure(
        console_levels={"DEBUG": False, "TRACE": False},
        time_levels={"ERROR": True, "CRITICAL": True},
        color_levels={"INFO": False}
    )
    
    # Reset clears all per-level controls
    logger.reset()
    logger.info("All controls reset to defaults")
    ```

### Default Values

After calling `reset()`, the logger returns to these defaults:

```python
{
    "level": "INFO",
    "color": True,
    "json": False,
    "pretty_json": False,
    "console": True,
    "show_time": False,
    "show_module": False,
    "show_function": False,
    "show_filename": False,
    "show_lineno": False,
    "console_levels": None,
    "time_levels": None,
    "color_levels": None,
    "storage_levels": None,
    "color_callback": None
}
```

### Notes

!!! tip "When to Use reset()"
    - **Testing**: Call between tests to ensure clean state
    - **Config Reload**: Clear old settings before loading new configuration
    - **Debugging**: Return to known default state
    - **State Management**: Reset after temporary configuration changes

!!! info "What Gets Reset"
    `reset()` clears:
    - ✅ Log level (back to INFO)
    - ✅ Per-level controls (console_levels, time_levels, color_levels, storage_levels)
    - ✅ Color callback functions
    - ✅ Display flags (show_time, show_module, etc.)
    - ✅ JSON formatting settings

!!! warning "What Doesn't Get Reset"
    `reset()` does **NOT** affect:
    - ❌ Registered sinks (use `remove()` to clear sinks)
    - ❌ Registered callbacks (use `remove_callback()`)
    - ❌ Log files already created

---

## logger.complete()

Finalize the logger, flush all buffers, and close file handles.

### Signature

```python
logger.complete() -> None
```

### Parameters
- None

### Returns
- `None`

### Examples

=== "Basic Cleanup"
    ```python
    from logly import logger
    
    # Application code
    logger.info("Application started")
    logger.info("Processing data")
    logger.info("Application complete")
    
    # Cleanup at exit
    logger.complete()
    ```

=== "Context Manager"
    ```python
    def main():
        try:
            logger.configure(level="INFO")
            logger.add("logs/app.log")
            
            # Application logic
            logger.info("Running application")
            process_data()
            
        finally:
            # Always cleanup
            logger.complete()
    
    if __name__ == "__main__":
        main()
    ```

=== "Multiple Sinks"
    ```python
    # Configure multiple sinks
    logger.add("console")
    logger.add("logs/app.log")
    logger.add("logs/error.log", level="ERROR")
    
    # Application code
    logger.info("Processing...")
    logger.error("Error occurred")
    
    # Flush all sinks
    logger.complete()
    ```

=== "Async Application"
    ```python
    import asyncio
    
    async def main():
        logger.configure(level="INFO")
        logger.add("logs/async.log", async_write=True)
        
        # Async operations
        await async_task()
        
        # Wait for async writes to complete
        logger.complete()
    
    asyncio.run(main())
    ```

### Notes

!!! tip "When to Use complete()"
    - **Application Exit**: Always call at program exit
    - **Testing**: Call between tests to reset state
    - **Context Managers**: Use in `finally` blocks
    - **Async Applications**: Ensure all async writes complete

!!! warning "Required for File Sinks"
    **Always** call `complete()` when using file sinks to ensure:
    - ✅ All buffers are flushed
    - ✅ File handles are closed
    - ✅ No data loss on exit
    ```python
    logger.add("logs/app.log")
    # ... application code ...
    logger.complete()  # REQUIRED
    ```

!!! info "Async Writes"
    For async file sinks, `complete()` waits for pending writes:
    ```python
    logger.add("logs/app.log", async_write=True)
    logger.info("Message 1")
    logger.info("Message 2")
    logger.complete()  # Waits for both messages to be written
    ```

!!! warning "Post-complete Behavior"
    After calling `complete()`, subsequent log calls may fail or be ignored:
    ```python
    logger.complete()
    logger.info("This may not log")  # ⚠️ Logger finalized
    ```

---

## Complete Example

```python
from logly import logger
import sys

def main():
    try:
        # Configure logger
        logger.configure(
            level="DEBUG",
            color=True,
            show_time=True,
            show_module=True,
            show_filename=True,
            show_lineno=True
        )
        logger.add("console")
        logger.add("logs/app.log", rotation="daily")
        
        # Register custom level aliases
        logger.level("AUDIT", "INFO")
        logger.level("SECURITY", "WARNING")
        logger.level("FATAL", "CRITICAL")
        
        # Application logic
        logger.info("Application started", version="1.0.0")
        
        # Use custom levels
        logger.log("AUDIT", "User login", user="alice", ip="192.168.1.1")
        
        # Process data
        process_data()
        
        logger.log("SECURITY", "Access granted", resource="/admin")
        logger.success("Application complete")
        
    except Exception:
        logger.exception("Application failed")
        sys.exit(1)
    
    finally:
        # Always cleanup
        logger.complete()

def process_data():
    logger.debug("Starting data processing")
    # ... processing logic ...
    logger.debug("Data processing complete")

if __name__ == "__main__":
    main()
```

**Output:**
```
2025-01-15 10:30:45 | INFO | __main__ | main | app.py:20 | Application started version=1.0.0
2025-01-15 10:30:45 | INFO | __main__ | main | app.py:23 | User login user=alice ip=192.168.1.1
2025-01-15 10:30:45 | DEBUG | __main__ | process_data | app.py:35 | Starting data processing
2025-01-15 10:30:45 | DEBUG | __main__ | process_data | app.py:37 | Data processing complete
2025-01-15 10:30:45 | WARNING | __main__ | main | app.py:28 | Access granted resource=/admin
2025-01-15 10:30:45 | SUCCESS | __main__ | main | app.py:29 | ✅ Application complete
```

---

## Best Practices

### ✅ DO

```python
# 1. Always call complete() at exit
try:
    run_application()
finally:
    logger.complete()

# 2. Use level() for domain-specific terminology
logger.level("AUDIT", "INFO")
logger.level("SECURITY", "ERROR")
logger.log("AUDIT", "Business event")

# 3. Use disable() for testing
@pytest.fixture
def quiet_logs():
    logger.disable()
    yield
    logger.enable()

# 4. Use reset() between test cases
import pytest

@pytest.fixture(autouse=True)
def reset_logger():
    yield
    logger.reset()

# 5. Create bound loggers with independent enable/disable
request_logger = logger.bind(request_id="123")
request_logger.disable()  # Only affects bound instance
```

### ❌ DON'T

```python
# 1. Don't forget to call complete()
logger.add("logs/app.log")
# ... application code ...
# ❌ Missing logger.complete() - data loss!

# 2. Don't expect custom severity levels
logger.level("NOTICE", "INFO")  # Alias to INFO, not new severity
logger.configure(level="WARNING")
logger.log("NOTICE", "Test")  # ❌ Won't log (INFO < WARNING)

# 3. Don't call complete() multiple times
logger.complete()
logger.complete()  # ❌ May cause errors

# 4. Don't use level() for severity control
# ❌ Wrong - level() only creates aliases
logger.level("CUSTOM", "DEBUG")

# ✅ Right - use configure() for severity
logger.configure(level="DEBUG")

# 5. Don't disable and expect bound instances to work
logger.disable()
req_logger = logger.bind(request_id="123")
req_logger.info("Test")  # ❌ Still suppressed (parent disabled)
```

---

## Performance Tips

### Minimize Enable/Disable Calls

```python
# ❌ Don't toggle repeatedly
for item in items:
    logger.disable()
    process(item)
    logger.enable()

# ✅ Disable once
logger.disable()
for item in items:
    process(item)
logger.enable()
```

### Use Per-Level Controls Instead

```python
# Instead of disabling everything, use per-level controls
logger.configure(
    console_levels={"DEBUG": False, "TRACE": False},  # Hide verbose levels
    storage_levels={"DEBUG": True, "TRACE": True}     # But save to files
)

# More flexible than enable/disable
logger.debug("Saved to file, not console")
```

### Instance-Specific Logging

```python
# Create specialized loggers with independent control
audit_logger = logger.bind(category="audit")
debug_logger = logger.bind(category="debug")

# Disable only debug logger in production
if production:
    debug_logger.disable()

audit_logger.info("Always logged")
debug_logger.info("Only in development")
```

### Async File Writes

```python
# Async writes for high-throughput
logger.add("logs/app.log", async_write=True, buffer_size=16384)

# ... log thousands of messages ...

# Ensure all writes complete
logger.complete()
```

---

## Implementation Details

### Python vs Rust Layer

Logly uses a hybrid architecture:

| Method | Implementation | Notes |
|--------|----------------|-------|
| `enable()` | Python | Sets instance flag `_enabled = True` |
| `disable()` | Python | Sets instance flag `_enabled = False` |
| `level()` | Python | Stores alias in `_levels` dictionary |
| `reset()` | Rust | Resets Rust backend configuration |
| `complete()` | Rust | Flushes Rust backend buffers |
| `add()` | Rust | Managed by Rust backend |
| `configure()` | Rust | Rust backend configuration |

### Performance Characteristics

```python
# enable/disable: O(1) flag check (Python-level)
logger.disable()  # Instant
logger.info("Suppressed")  # Checked before Rust call

# level(): O(1) dict lookup (Python-level)
logger.level("AUDIT", "INFO")  # Instant
logger.log("AUDIT", "Message")  # Dict lookup then Rust call

# reset(): Rust backend reset
logger.reset()  # Resets Rust configuration state

# complete(): Rust buffer flush
logger.complete()  # Waits for all async writes
```
