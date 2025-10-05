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
| `enable_sink()` | Enable a specific sink by handler ID |
| `disable_sink()` | Disable a specific sink by handler ID |
| `is_sink_enabled()` | Check if a specific sink is enabled |
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

## logger.enable_sink()

Enable a specific sink by its handler ID.

### Signature

```python
logger.enable_sink(sink_id: int) -> bool
```

### Parameters
- `sink_id` (`int`): The handler ID of the sink to enable

### Returns
- `bool`: `True` if the sink was found and enabled, `False` if not found

### Description

Enables a specific sink by its handler ID. When a sink is enabled, log messages will be written to it. Sinks are enabled by default when created with `logger.add()`.

Unlike the global `enable()` method which affects all logging, `enable_sink()` provides fine-grained control over individual output destinations.

### Examples

=== "Basic Usage"
    ```python
    from logly import logger
    
    # Add sinks
    console_id = logger.add("console")
    file_id = logger.add("app.log")
    
    # Disable file logging
    logger.disable_sink(file_id)
    logger.info("Only to console")  # Logged to console only
    
    # Re-enable file logging
    logger.enable_sink(file_id)
    logger.info("To both sinks")  # Logged to both console and file
    ```

=== "Conditional Output"
    ```python
    from logly import logger
    
    # Setup sinks
    console_id = logger.add("console")
    debug_file_id = logger.add("debug.log")
    error_file_id = logger.add("error.log", filter_min_level="ERROR")
    
    # Disable debug file in production
    if production:
        logger.disable_sink(debug_file_id)
    
    logger.debug("Debug info")  # To console (and debug file in dev)
    logger.error("Error occurred")  # To all sinks
    ```

=== "Dynamic Control"
    ```python
    from logly import logger
    
    # Feature-specific logging
    feature_sinks = {}
    
    def enable_feature_logging(feature_name):
        """Enable detailed logging for a feature."""
        sink_id = logger.add(f"logs/{feature_name}.log")
        feature_sinks[feature_name] = sink_id
        return sink_id
    
    def disable_feature_logging(feature_name):
        """Disable logging for a feature."""
        if feature_name in feature_sinks:
            sink_id = feature_sinks[feature_name]
            logger.disable_sink(sink_id)
    
    # Use feature logging
    enable_feature_logging("payment")
    # ... lots of payment logs ...
    disable_feature_logging("payment")  # Stop logging payments
    ```

### Notes

!!! tip "Sink-Level Control"
    `enable_sink()` and `disable_sink()` provide granular control over individual sinks without affecting other outputs.

!!! info "Default State"
    Sinks are **enabled** by default when created with `add()`.

!!! warning "Disabled vs Removed"
    - Disabled sinks remain registered but don't write logs
    - Use `remove()` to completely unregister a sink
    - Disabled sinks can be re-enabled; removed sinks cannot

---

## logger.disable_sink()

Disable a specific sink by its handler ID.

### Signature

```python
logger.disable_sink(sink_id: int) -> bool
```

### Parameters
- `sink_id` (`int`): The handler ID of the sink to disable

### Returns
- `bool`: `True` if the sink was found and disabled, `False` if not found

### Description

Disables a specific sink by its handler ID. When a sink is disabled, log messages will not be written to it, but the sink remains registered and can be re-enabled later with `enable_sink()`.

This provides fine-grained control for temporarily suspending output to specific destinations without removing them entirely.

### Examples

=== "Temporary Silence"
    ```python
    from logly import logger
    
    # Setup
    file_id = logger.add("app.log")
    
    # Temporarily stop file logging
    logger.disable_sink(file_id)
    logger.info("Not in file")
    
    # Resume file logging
    logger.enable_sink(file_id)
    logger.info("Back in file")
    ```

=== "Performance Optimization"
    ```python
    from logly import logger
    import time
    
    # Setup sinks
    console_id = logger.add("console")
    verbose_id = logger.add("verbose.log")
    
    # Disable verbose logging for high-performance section
    logger.disable_sink(verbose_id)
    
    start = time.time()
    for i in range(1000000):
        process_item(i)
        # No verbose file writes during hot loop
    
    logger.enable_sink(verbose_id)
    logger.info(f"Processed 1M items in {time.time() - start:.2f}s")
    ```

=== "Environment-Based Control"
    ```python
    from logly import logger
    import os
    
    # Setup sinks
    console_id = logger.add("console")
    debug_id = logger.add("debug.log")
    
    # Disable debug file in production
    if os.getenv("ENV") == "production":
        logger.disable_sink(debug_id)
    
    logger.debug("Debug information")  # Only to console in prod
    logger.info("Application started")  # To both sinks
    ```

### Notes

!!! tip "Use Cases"
    - **Performance**: Disable expensive sinks during hot loops
    - **Environment**: Different outputs for dev vs prod
    - **Features**: Enable/disable per-feature logging dynamically

!!! info "State Preserved"
    Disabled sinks maintain their configuration (filters, format, rotation) and can be re-enabled anytime.

!!! warning "Check Return Value"
    ```python
    success = logger.disable_sink(sink_id)
    if not success:
        print(f"Sink {sink_id} not found")
    ```

---

## logger.is_sink_enabled()

Check if a specific sink is enabled.

### Signature

```python
logger.is_sink_enabled(sink_id: int) -> bool | None
```

### Parameters
- `sink_id` (`int`): The handler ID of the sink to check

### Returns
- `True` if the sink is enabled
- `False` if the sink is disabled
- `None` if the sink does not exist

### Description

Checks whether a specific sink is currently enabled. This is useful for conditional logic, debugging, or monitoring sink status.

### Examples

=== "Basic Check"
    ```python
    from logly import logger
    
    file_id = logger.add("app.log")
    
    # Check initial state
    enabled = logger.is_sink_enabled(file_id)
    print(f"Sink enabled: {enabled}")  # True
    
    # Disable and check
    logger.disable_sink(file_id)
    enabled = logger.is_sink_enabled(file_id)
    print(f"Sink enabled: {enabled}")  # False
    ```

=== "Conditional Logic"
    ```python
    from logly import logger
    
    debug_id = logger.add("debug.log")
    
    def toggle_debug_logging():
        """Toggle debug file logging."""
        if logger.is_sink_enabled(debug_id):
            logger.disable_sink(debug_id)
            logger.info("Debug logging disabled")
        else:
            logger.enable_sink(debug_id)
            logger.info("Debug logging enabled")
    ```

=== "Sink Status Report"
    ```python
    from logly import logger
    
    # Add multiple sinks
    console_id = logger.add("console")
    app_log_id = logger.add("app.log")
    error_log_id = logger.add("error.log", filter_min_level="ERROR")
    
    # Report status
    for sink_id in logger.list_sinks():
        info = logger.sink_info(sink_id)
        enabled = logger.is_sink_enabled(sink_id)
        
        print(f"Sink {sink_id}:")
        print(f"  Type: {info.get('type', 'unknown')}")
        print(f"  Path: {info.get('path', 'N/A')}")
        print(f"  Enabled: {enabled}")
    ```

### Notes

!!! tip "Use in Assertions"
    ```python
    # Verify sink state in tests
    assert logger.is_sink_enabled(sink_id) == True
    logger.disable_sink(sink_id)
    assert logger.is_sink_enabled(sink_id) == False
    ```

!!! info "None Return"
    Returns `None` if the sink ID doesn't exist. Check before using:
    ```python
    enabled = logger.is_sink_enabled(sink_id)
    if enabled is None:
        print(f"Sink {sink_id} not found")
    elif enabled:
        print("Sink is active")
    else:
        print("Sink is disabled")
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

# 6. Use sink-specific control for granular output management
console_id = logger.add("console")
debug_file_id = logger.add("debug.log")

# Disable debug file in production
if production:
    logger.disable_sink(debug_file_id)

# 7. Check sink status before operations
if logger.is_sink_enabled(debug_file_id):
    logger.debug("Detailed debug information")
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

# 6. DON'T remove sinks just to temporarily disable them
# ❌ Bad: Removing sink loses configuration
logger.remove_sink(file_id)
# ... later
logger.add("app.log")  # Must reconfigure everything

# ✅ Good: Disable/enable preserves configuration
logger.disable_sink(file_id)
# ... later
logger.enable_sink(file_id)  # Same configuration restored

# 7. DON'T confuse global vs. sink-specific disable
logger.disable()  # ❌ Stops ALL logging (all sinks)
logger.disable_sink(file_id)  # ✅ Only stops this specific sink
```

---

## Global vs. Per-Sink Control

Understanding when to use global enable/disable vs. per-sink controls:

=== "Global Control"
    ```python
    # Use logger.disable()/enable() when:
    # • Testing: Silence all log output
    # • Performance: Temporarily disable all logging
    # • Application state: Pause all logging during critical sections
    
    logger.add("console")
    logger.add("app.log")
    logger.add("error.log")
    
    # Disable ALL sinks at once
    logger.disable()
    logger.info("Not logged anywhere")  # No output to any sink
    
    # Re-enable ALL sinks
    logger.enable()
    logger.info("Logged everywhere")  # Console + both files
    ```

=== "Per-Sink Control"
    ```python
    # Use enable_sink()/disable_sink() when:
    # • Conditional output: Only certain sinks based on conditions
    # • Dynamic routing: Change where logs go at runtime
    # • Performance tuning: Disable expensive sinks temporarily
    
    console_id = logger.add("console")
    app_log_id = logger.add("app.log")
    debug_log_id = logger.add("debug.log")
    
    # Disable only debug file in production
    if production:
        logger.disable_sink(debug_log_id)
    
    logger.info("User login")  # → Console + app.log only
    
    # Re-enable debug file for troubleshooting
    if user_requests_debug:
        logger.enable_sink(debug_log_id)
    
    logger.debug("Detailed info")  # → All 3 sinks now
    ```

=== "Combined Usage"
    ```python
    # Combine both for maximum flexibility
    
    console_id = logger.add("console")
    file_id = logger.add("app.log")
    
    # Scenario 1: Testing mode - silence everything
    if testing:
        logger.disable()  # Global disable (fastest)
    
    # Scenario 2: Debug mode - extra file output
    if debug_mode:
        debug_id = logger.add("debug.log")
    
    # Scenario 3: Performance mode - file logging only
    if performance_mode:
        logger.disable_sink(console_id)  # Disable console
        # File logging still active
    
    # Global disable overrides per-sink settings
    logger.disable()
    logger.enable_sink(file_id)  # Has no effect until global enable()
    logger.info("Not logged")  # Still disabled globally
    
    logger.enable()
    logger.info("Logged to file")  # Now works (file is enabled)
    ```

**Key Differences:**

| Feature | Global (`disable()`/`enable()`) | Per-Sink (`disable_sink()`/`enable_sink()`) |
|---------|--------------------------------|---------------------------------------------|
| **Scope** | All sinks | Single sink by ID |
| **Use Case** | Testing, app-wide pause | Conditional routing, dynamic control |
| **Performance** | Fastest (early exit in Python) | Checks each sink in Rust backend |
| **Configuration** | All settings preserved | Individual sink settings preserved |
| **Priority** | Overrides all per-sink settings | Ignored if globally disabled |
| **Bound Loggers** | Affects bound instances | Only affects parent logger sinks |

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
