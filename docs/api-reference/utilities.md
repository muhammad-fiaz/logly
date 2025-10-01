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
| `enable()` | Enable logging for specific modules/packages |
| `disable()` | Disable logging for specific modules/packages |
| `level()` | Register custom log levels |
| `complete()` | Finalize logger and flush all buffers |

---

## logger.enable()

Enable logging for specific modules or packages.

### Signature

```python
logger.enable(name: str) -> None
```

### Parameters
- `name` (str): Module or package name (supports wildcards)

### Returns
- `None`

### Examples

=== "Enable Module"
    ```python
    from logly import logger
    
    # Disable all by default
    logger.disable("")
    
    # Enable only myapp.api module
    logger.enable("myapp.api")
    
    # Logs from myapp.api will be shown
    # Logs from other modules will be hidden
    ```

=== "Enable Package"
    ```python
    # Enable entire package
    logger.enable("myapp")
    
    # All modules under myapp.* will log
    # myapp.api, myapp.auth, myapp.db, etc.
    ```

=== "Wildcard Patterns"
    ```python
    # Enable multiple modules with wildcard
    logger.enable("myapp.api.*")
    
    # Matches:
    # myapp.api.users
    # myapp.api.orders
    # myapp.api.payments
    ```

=== "Multiple Calls"
    ```python
    # Enable multiple modules
    logger.enable("myapp.api")
    logger.enable("myapp.auth")
    logger.enable("thirdparty.important")
    
    # Only these modules will log
    ```

### Notes

!!! tip "When to Use enable()"
    - **Selective Logging**: Focus on specific modules during debugging
    - **Third-Party Libraries**: Enable logging from specific dependencies
    - **Development**: Enable verbose logging only for modules under development
    - **Testing**: Enable logs only for tested components

!!! info "Wildcard Support"
    Patterns support `*` wildcard:
    - `"myapp"` - Exact module match
    - `"myapp.*"` - All sub-modules
    - `"myapp.api.*"` - All modules under myapp.api

!!! warning "Default Behavior"
    By default, **all modules are enabled**. Use `disable("")` first to disable all, then selectively `enable()`:
    ```python
    logger.disable("")           # Disable all
    logger.enable("myapp.api")   # Enable only myapp.api
    ```

---

## logger.disable()

Disable logging for specific modules or packages.

### Signature

```python
logger.disable(name: str) -> None
```

### Parameters
- `name` (str): Module or package name (supports wildcards). Use `""` to disable all.

### Returns
- `None`

### Examples

=== "Disable Module"
    ```python
    from logly import logger
    
    # Disable specific module
    logger.disable("thirdparty.noisy")
    
    # Logs from thirdparty.noisy will be hidden
    # All other modules will continue logging
    ```

=== "Disable Package"
    ```python
    # Disable entire package
    logger.disable("thirdparty")
    
    # All modules under thirdparty.* will NOT log
    ```

=== "Disable All"
    ```python
    # Disable all logging
    logger.disable("")
    
    # No logs will be output (useful for selective enable)
    logger.enable("myapp.critical")  # Only myapp.critical logs
    ```

=== "Wildcard Patterns"
    ```python
    # Disable multiple modules with wildcard
    logger.disable("thirdparty.*")
    
    # Disables:
    # thirdparty.lib1
    # thirdparty.lib2
    # thirdparty.lib3
    ```

=== "Silence Noisy Libraries"
    ```python
    # Common pattern: disable noisy third-party logs
    logger.disable("urllib3")
    logger.disable("asyncio")
    logger.disable("aiohttp")
    
    # Your application logs normally
    logger.info("Application started")
    ```

### Notes

!!! tip "When to Use disable()"
    - **Noisy Libraries**: Silence verbose third-party libraries
    - **Production**: Disable debug modules in production
    - **Performance**: Reduce log volume by disabling low-priority modules
    - **Testing**: Disable logs from tested components

!!! warning "Empty String"
    `disable("")` disables **all logging**:
    ```python
    logger.disable("")  # Disables EVERYTHING
    logger.info("Test")  # Will NOT log
    ```

!!! info "Priority"
    When both `enable()` and `disable()` are used, **disable** takes priority:
    ```python
    logger.enable("myapp")
    logger.disable("myapp.noisy")
    
    # myapp.api logs ✅
    # myapp.auth logs ✅
    # myapp.noisy logs ❌ (disabled)
    ```

---

## logger.level()

Register a custom log level or remap an existing level.

### Signature

```python
logger.level(name: str, no: int | None = None, color: str | None = None, icon: str | None = None) -> None
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | *required* | Level name (uppercase) |
| `no` | `int \| None` | `None` | Numeric severity (1-50) |
| `color` | `str \| None` | `None` | ANSI color code or name |
| `icon` | `str \| None` | `None` | Icon/emoji for level |

### Returns
- `None`

### Examples

=== "Custom Level"
    ```python
    from logly import logger
    
    # Register custom level
    logger.level("NOTICE", no=25, color="cyan", icon="ℹ️")
    
    # Use custom level
    logger.log("NOTICE", "Important notice", category="security")
    ```

=== "Remap Existing Level"
    ```python
    # Change SUCCESS color
    logger.level("SUCCESS", color="magenta")
    
    logger.success("Custom colored success")
    ```

=== "Multiple Custom Levels"
    ```python
    # Business-specific levels
    logger.level("AUDIT", no=22, color="blue", icon="📋")
    logger.level("SECURITY", no=45, color="red", icon="🔒")
    logger.level("PERFORMANCE", no=15, color="yellow", icon="⚡")
    
    logger.log("AUDIT", "User action logged", user="alice", action="login")
    logger.log("SECURITY", "Suspicious activity", ip="1.2.3.4")
    logger.log("PERFORMANCE", "Slow query", duration_ms=1500)
    ```

=== "Severity Numbers"
    ```python
    # Standard levels (reference)
    # TRACE: 5
    # DEBUG: 10
    # INFO: 20
    # SUCCESS: 20 (mapped to INFO)
    # WARNING: 30
    # ERROR: 40
    # CRITICAL: 50
    
    # Custom level between INFO and WARNING
    logger.level("NOTICE", no=25)
    
    logger.configure(level="NOTICE")  # Only NOTICE and above
    logger.info("Hidden")             # Below NOTICE (20 < 25)
    logger.log("NOTICE", "Shown")     # Exactly NOTICE
    logger.warning("Shown")           # Above NOTICE (30 > 25)
    ```

### Notes

!!! tip "When to Use level()"
    - **Custom Levels**: Domain-specific log levels (AUDIT, SECURITY, etc.)
    - **Color Customization**: Change colors for existing levels
    - **Severity Mapping**: Fine-tune log level filtering
    - **Icon/Emoji**: Add visual indicators to log levels

!!! info "Severity Numbers"
    Standard severity range: 1-50
    - **1-10**: Trace/Debug
    - **11-20**: Info/Success
    - **21-30**: Notice/Warning
    - **31-40**: Error
    - **41-50**: Critical/Fatal

!!! warning "Name Collisions"
    Registering an existing level name will **override** the original:
    ```python
    logger.level("INFO", color="red")  # Changes INFO color
    logger.info("Now red")  # INFO logs now appear in red
    ```

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
        logger.configure(level="DEBUG", color=True)
        logger.add("console")
        logger.add("logs/app.log", rotation="daily")
        
        # Disable noisy libraries
        logger.disable("urllib3")
        logger.disable("asyncio")
        
        # Enable only application modules
        logger.enable("myapp")
        
        # Register custom levels
        logger.level("AUDIT", no=22, color="blue", icon="📋")
        logger.level("SECURITY", no=45, color="red", icon="🔒")
        
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
2025-01-15 10:30:45 | INFO | Application started version=1.0.0
2025-01-15 10:30:45 | AUDIT | 📋 User login user=alice ip=192.168.1.1
2025-01-15 10:30:45 | DEBUG | Starting data processing
2025-01-15 10:30:45 | DEBUG | Data processing complete
2025-01-15 10:30:45 | SECURITY | 🔒 Access granted resource=/admin
2025-01-15 10:30:45 | SUCCESS | ✅ Application complete
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

# 2. Disable noisy third-party libraries
logger.disable("urllib3")
logger.disable("boto3")

# 3. Use custom levels for business logic
logger.level("AUDIT", no=22, color="blue")
logger.log("AUDIT", "Business event")

# 4. Enable only relevant modules during debugging
logger.disable("")
logger.enable("myapp.problematic_module")
```

### ❌ DON'T

```python
# 1. Don't forget to call complete()
logger.add("logs/app.log")
# ... application code ...
# ❌ Missing logger.complete() - data loss!

# 2. Don't disable all without re-enabling
logger.disable("")
logger.info("Hidden")  # ❌ Won't log

# ✅ Re-enable specific modules
logger.disable("")
logger.enable("myapp")
logger.info("Visible")

# 3. Don't use reserved level numbers
logger.level("CUSTOM", no=20)  # ❌ Conflicts with INFO (20)

# ✅ Use unique numbers
logger.level("CUSTOM", no=25)  # Between INFO (20) and WARNING (30)

# 4. Don't call complete() multiple times
logger.complete()
logger.complete()  # ❌ May cause errors
```

---

## Performance Tips

### Selective Logging

```python
# Production: disable debug modules
if production:
    logger.configure(level="INFO")
    logger.disable("myapp.debug")
    logger.disable("myapp.trace")

# Development: enable all
if development:
    logger.configure(level="DEBUG")
    logger.enable("")
```

### Module Filtering

```python
# Only log from critical modules
logger.disable("")
logger.enable("myapp.api")
logger.enable("myapp.auth")
logger.enable("myapp.payment")

# Reduces log volume by 80%+
```

### Async File Writes

```python
# Async writes for high-throughput
logger.add("logs/app.log", async_write=True)

# ... log thousands of messages ...

# Ensure all writes complete
logger.complete()
```
