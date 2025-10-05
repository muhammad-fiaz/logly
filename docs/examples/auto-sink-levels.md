---
title: Auto-Sink Levels - Automatic Log File Management
description: Learn how to use Logly's auto-sink levels feature to automatically create and manage separate log files for different log levels with a single configuration.
keywords: python, logging, auto-sink, levels, automatic, file management, log rotation, filtering
---

# Auto-Sink Levels

**NEW in v0.1.5**: Automatically create and manage separate log files for different log levels with a single configuration.

---

## Overview

The `auto_sink_levels` feature eliminates the need to manually add multiple sinks with `logger.add()`. Instead, you configure all your level-based sinks in one place using `logger.configure()`.

### Why Use Auto-Sink Levels?

**Without auto-sink levels** (manual approach):
```python
from logly import logger

logger.configure(level="DEBUG")
logger.add("logs/debug.log", filter_min_level="DEBUG")
logger.add("logs/info.log", filter_min_level="INFO")
logger.add("logs/warning.log", filter_min_level="WARNING")
logger.add("logs/error.log", filter_min_level="ERROR")
# ... more manual sink additions
```

**With auto-sink levels** (automatic approach):
```python
from logly import logger

logger.configure(
    level="DEBUG",
    auto_sink_levels={
        "DEBUG": "logs/debug.log",
        "INFO": "logs/info.log",
        "WARNING": "logs/warning.log",
        "ERROR": "logs/error.log",
    }
)
# Done! All sinks created automatically
```

---

## Basic Usage

### Simple String Paths

The simplest way to use auto-sink levels is with string paths:

```python
from logly import logger

logger.configure(
    level="DEBUG",
    auto_sink=True,  # Console output
    auto_sink_levels={
        "DEBUG": "logs/debug.log",      # All logs (DEBUG and above)
        "INFO": "logs/info.log",        # INFO and above
        "WARNING": "logs/warning.log",  # WARNING and above
        "ERROR": "logs/error.log",      # ERROR and above
    }
)

logger.debug("Debug message")      # → debug.log only
logger.info("Info message")        # → debug.log, info.log
logger.warning("Warning message")  # → debug.log, info.log, warning.log
logger.error("Error message")      # → all four files
```

**How it works:**
- Each log level gets a minimum level filter
- `"DEBUG"` sink captures DEBUG and all higher levels (INFO, WARNING, ERROR, etc.)
- `"INFO"` sink captures INFO and higher (skips DEBUG)
- `"ERROR"` sink captures only ERROR and higher (CRITICAL, FAIL)

---

## Advanced Configuration

### Dictionary Configuration

For advanced features like rotation, retention, and formatting, use dictionary configuration:

```python
logger.configure(
    level="DEBUG",
    auto_sink_levels={
        "DEBUG": {
            "path": "logs/debug.log",
            "rotation": "daily",
            "retention": 7,
            "date_enabled": True,
            "async_write": True,
        },
        "WARNING": {
            "path": "logs/warnings.log",
            "rotation": "hourly",
            "retention": 24,
            "size_limit": "10MB",
        },
        "ERROR": {
            "path": "logs/errors.log",
            "json": True,
            "async_write": True,
            "buffer_size": 16384,
        },
    }
)
```

**Supported options for each level:**
- `path` (required): File path for this sink
- `rotation`: Time-based rotation (`"daily"`, `"hourly"`, `"minutely"`)
- `size_limit`: Size-based rotation (`"1KB"`, `"10MB"`, `"1GB"`)
- `retention`: Number of old files to keep
- `date_enabled`: Include timestamps in output
- `date_style`: Date format (`"rfc3339"`, `"local"`, `"utc"`)
- `format`: Custom format string
- `json`: Output as JSON
- `async_write`: Enable async writing
- `buffer_size`: Async buffer size in bytes
- `flush_interval`: Async flush interval in ms
- `max_buffered_lines`: Max lines before blocking
- `filter_module`: Only log from specific module
- `filter_function`: Only log from specific function

---

## Complete Examples

### Example 1: All 8 Log Levels

Create separate files for all log levels:

```python
from logly import logger

logger.configure(
    level="TRACE",
    auto_sink=True,
    auto_sink_levels={
        "TRACE": "logs/trace.log",
        "DEBUG": "logs/debug.log",
        "INFO": "logs/info.log",
        "SUCCESS": "logs/success.log",
        "WARNING": "logs/warning.log",
        "ERROR": "logs/error.log",
        "CRITICAL": "logs/critical.log",
        "FAIL": "logs/fail.log",
    }
)

logger.trace("Detailed trace")
logger.debug("Debug info")
logger.info("General info")
logger.success("Operation succeeded")
logger.warning("Warning condition")
logger.error("Error occurred")
logger.critical("Critical failure")
logger.fail("Operation failed")
```

Result:
```
logs/
├── trace.log      # Contains all 8 levels
├── debug.log      # Contains DEBUG and above (7 levels)
├── info.log       # Contains INFO and above (6 levels)
├── success.log    # Contains SUCCESS and above (5 levels)
├── warning.log    # Contains WARNING and above (4 levels)
├── error.log      # Contains ERROR and above (3 levels)
├── critical.log   # Contains CRITICAL and above (2 levels)
└── fail.log       # Contains FAIL only
```

---

### Example 2: Production Deployment

Typical production configuration with rotation and retention:

```python
from logly import logger

logger.configure(
    level="INFO",
    auto_sink=True,  # Console for monitoring
    auto_sink_levels={
        # General application logs
        "INFO": {
            "path": "logs/app.log",
            "rotation": "daily",
            "retention": 30,  # Keep 30 days
            "date_enabled": True,
            "async_write": True,
        },
        # Warnings with size limit
        "WARNING": {
            "path": "logs/warnings.log",
            "rotation": "daily",
            "size_limit": "50MB",
            "retention": 14,  # Keep 2 weeks
        },
        # Errors as JSON for analysis
        "ERROR": {
            "path": "logs/errors.json",
            "json": True,
            "rotation": "hourly",
            "retention": 168,  # Keep 1 week of hourly files
            "async_write": True,
        },
        # Critical alerts
        "CRITICAL": {
            "path": "logs/critical.log",
            "retention": 90,  # Keep 90 days
            "date_enabled": True,
        },
    }
)
```

---

### Example 3: Development Environment

Debug-focused configuration for development:

```python
from logly import logger

logger.configure(
    level="DEBUG",
    color=True,
    auto_sink=True,  # Colored console output
    auto_sink_levels={
        # Detailed debug logs
        "DEBUG": {
            "path": "logs/dev/debug.log",
            "format": "{time} | {level} | {module}:{function} | {message}",
            "date_enabled": True,
        },
        # Application flow
        "INFO": {
            "path": "logs/dev/app.log",
            "format": "{time} | {message}",
        },
        # Issues to investigate
        "WARNING": {
            "path": "logs/dev/issues.log",
            "format": "{time} | [{level}] {message} | {module}:{lineno}",
        },
    }
)
```

---

### Example 4: Module-Specific Filtering

Create separate logs for different modules:

```python
from logly import logger

logger.configure(
    level="INFO",
    auto_sink_levels={
        # Database module logs
        "INFO": {
            "path": "logs/modules/database.log",
            "filter_module": "myapp.database",
            "format": "{time} | {message}",
        },
        # API module logs
        "INFO": {
            "path": "logs/modules/api.log",
            "filter_module": "myapp.api",
            "json": True,
        },
        # Authentication module logs
        "INFO": {
            "path": "logs/modules/auth.log",
            "filter_module": "myapp.auth",
            "filter_function": "authenticate",
        },
    }
)
```

---

### Example 5: Combined with Manual Sinks

Auto-sinks coexist with manually added sinks:

```python
from logly import logger

logger.configure(
    level="INFO",
    auto_sink=True,
    auto_sink_levels={
        "INFO": "logs/auto/info.log",
        "ERROR": "logs/auto/error.log",
    }
)

# Add custom sinks for specific needs
logger.add(
    "logs/manual/critical_alerts.log",
    filter_min_level="CRITICAL",
    format="🚨 {time} | {message}",
)

logger.add(
    "logs/manual/success_tracking.log",
    filter_min_level="SUCCESS",
    json=True,
)

logger.info("Goes to: console, auto/info.log")
logger.error("Goes to: console, auto/info.log, auto/error.log")
logger.critical("Goes to: console, auto/info.log, auto/error.log, manual/critical_alerts.log")
logger.success("Goes to: console, auto/info.log, manual/success_tracking.log")
```

---

## Best Practices

### ✅ DO

```python
# 1. Use auto-sink for standard level-based filtering
logger.configure(
    auto_sink_levels={
        "INFO": "logs/info.log",
        "ERROR": "logs/error.log",
    }
)

# 2. Combine rotation and retention
logger.configure(
    auto_sink_levels={
        "INFO": {
            "path": "logs/info.log",
            "rotation": "daily",
            "retention": 30,
        }
    }
)

# 3. Use JSON for structured error logs
logger.configure(
    auto_sink_levels={
        "ERROR": {
            "path": "logs/errors.json",
            "json": True,
        }
    }
)

# 4. Enable async writing for performance
logger.configure(
    auto_sink_levels={
        "INFO": {
            "path": "logs/info.log",
            "async_write": True,
        }
    }
)
```

### ❌ DON'T

```python
# 1. Don't mix auto-sink with redundant manual adds
logger.configure(auto_sink_levels={"INFO": "logs/info.log"})
logger.add("logs/info.log")  # ❌ Duplicate!

# 2. Don't use auto-sink for complex filtering
# If you need function-specific or custom filtering, use logger.add()
logger.configure(
    auto_sink_levels={
        "INFO": {  # ❌ Too complex for auto-sink
            "path": "logs/info.log",
            "filter_module": "module1",
            "filter_function": "func1",
        }
    }
)

# Instead, use manual add:
logger.add(
    "logs/info.log",
    filter_min_level="INFO",
    filter_module="module1",
    filter_function="func1",
)

# 3. Don't forget to set level appropriately
logger.configure(
    level="ERROR",  # ❌ DEBUG/INFO won't be logged!
    auto_sink_levels={
        "DEBUG": "logs/debug.log",
        "INFO": "logs/info.log",
    }
)
```

---

## Configuration Reference

### Minimal Configuration

```python
logger.configure(
    auto_sink_levels={
        "INFO": "logs/info.log",
    }
)
```

### Full Configuration

```python
logger.configure(
    level="DEBUG",
    auto_sink=True,
    auto_sink_levels={
        "DEBUG": {
            "path": "logs/debug.log",
            "rotation": "daily",
            "size_limit": "100MB",
            "retention": 7,
            "date_enabled": True,
            "date_style": "rfc3339",
            "format": "{time} | {level} | {message}",
            "json": False,
            "async_write": True,
            "buffer_size": 8192,
            "flush_interval": 1000,
            "max_buffered_lines": 1000,
            "filter_module": None,
            "filter_function": None,
        }
    }
)
```

---

## Disabling Auto-Sink Levels

To disable auto-sink levels and use manual control:

```python
logger.configure(
    level="INFO",
    auto_sink=False,  # Disable console auto-sink
    auto_sink_levels=None,  # Disable level auto-sinks
)

# Now manually add sinks
logger.add("console")
logger.add("logs/app.log")
```

---

## FAQ

**Q: Can I use both auto-sink levels and manual logger.add()?**  
A: Yes! Auto-sinks and manual sinks coexist. Auto-sinks are created during `configure()`, and you can add manual sinks anytime.

**Q: What happens if I specify the same file path twice?**  
A: Each sink is independent. If you use the same path in auto-sink and manual add, both sinks will write to the file (not recommended).

**Q: Can I reconfigure auto-sink levels?**  
A: Yes! Call `logger.configure()` again with new `auto_sink_levels`. Old auto-sinks remain unless you call `logger.reset()` first.

**Q: Do auto-sink levels support all logger.add() options?**  
A: Yes! Auto-sink levels support all options available in `logger.add()` when using dictionary configuration.

**Q: Can I disable console output with auto-sink levels?**  
A: Yes! Set `auto_sink=False` to disable console output while still using `auto_sink_levels` for file logging.

**Q: What's the performance impact of multiple auto-sinks?**  
A: Minimal! Enable `async_write=True` for each sink to ensure non-blocking writes. Each sink operates independently with its own buffer.

---

## Comparison with Manual Sinks

### Key Differences

| Feature | Auto-Sink Levels | Manual Sinks (logger.add()) |
|---------|------------------|------------------------------|
| **Configuration location** | Single `configure()` call | Multiple `add()` calls |
| **Level filtering** | Automatic by level name | Manual with `filter_min_level` |
| **Code clarity** | High (declarative) | Medium (imperative) |
| **Flexibility** | Medium (level-based only) | High (any filter combination) |
| **Best for** | Standard level-based logging | Complex filtering logic |
| **Maintainability** | Excellent (centralized) | Good (distributed) |
| **Dynamic updates** | Requires reconfigure | Can add/remove anytime |
| **Error handling** | Validates at configure time | Validates per add() call |

### Detailed Comparison

#### **1. Configuration Style**

**Auto-Sink Levels (Declarative):**
```python
# Define WHAT you want, framework handles HOW
logger.configure(
    auto_sink_levels={
        "DEBUG": "logs/debug.log",
        "ERROR": {
            "path": "logs/error.log",
            "rotation": "daily",
            "retention": 7
        }
    }
)
# All sinks created automatically in one place
```

**Manual Sinks (Imperative):**
```python
# Define HOW to create each sink step-by-step
logger.configure(level="DEBUG")
logger.add("logs/debug.log", filter_min_level="DEBUG")
logger.add(
    "logs/error.log",
    filter_min_level="ERROR",
    rotation="daily",
    retention=7
)
# Each sink created individually
```

---

#### **2. Filter Capabilities**

**Auto-Sink Levels:**
- ✅ Level-based filtering (e.g., ERROR and above)
- ❌ Cannot filter by module
- ❌ Cannot filter by function
- ❌ Cannot combine multiple filter types
- ✅ Simpler for standard use cases

**Manual Sinks:**
- ✅ Level-based filtering
- ✅ Module filtering (`filter_module="my_module"`)
- ✅ Function filtering (`filter_function="my_function"`)
- ✅ Can combine all filter types
- ✅ Maximum flexibility

**Example - Complex filtering (requires manual sinks):**
```python
# ❌ Cannot do this with auto-sink levels
logger.configure(
    auto_sink_levels={
        "ERROR": {  # Cannot add module/function filters!
            "path": "logs/database_errors.log",
            "filter_module": "database",  # ❌ Not supported in auto-sink
        }
    }
)

# ✅ Use manual sinks instead
logger.add(
    "logs/database_errors.log",
    filter_min_level="ERROR",
    filter_module="database",  # ✅ Supported
    filter_function="connect"   # ✅ Supported
)
```

---

#### **3. When to Use Each Approach**

**Use Auto-Sink Levels When:**

✅ **Standard level-based logging**
```python
# Perfect use case: separate files for each level
auto_sink_levels={
    "INFO": "logs/info.log",
    "WARNING": "logs/warning.log",
    "ERROR": "logs/error.log"
}
```

✅ **Centralized configuration**
```python
# All log destinations defined in one place
logger.configure(
    level="DEBUG",
    auto_sink_levels={...}  # Everything configured here
)
```

✅ **Production deployments with rotation**
```python
# Standard production setup
auto_sink_levels={
    "INFO": {
        "path": "logs/app.log",
        "rotation": "daily",
        "retention": 30
    }
}
```

**Use Manual Sinks When:**

✅ **Module-specific logging**
```python
# Different modules → different files
logger.add("logs/api.log", filter_module="api")
logger.add("logs/database.log", filter_module="database")
```

✅ **Function-specific logging**
```python
# Capture specific function calls
logger.add(
    "logs/critical_function.log",
    filter_function="process_payment"
)
```

✅ **Dynamic sink management**
```python
# Add/remove sinks at runtime
sink_id = logger.add("logs/temp.log")
# ... do work ...
logger.remove(sink_id)  # Remove when done
```

✅ **Custom format per sink**
```python
# Different formats for different sinks
logger.add("logs/plain.log", format="{message}")
logger.add("logs/detailed.log", format="{time} | {level} | {module}:{function} | {message}")
```

---

#### **4. Error Handling**

**Auto-Sink Levels:**
- Validates ALL configurations at `configure()` time
- Fails fast with clear error messages
- All-or-nothing: either all sinks created or none

```python
try:
    logger.configure(
        auto_sink_levels={
            "INVALID": "logs/test.log"  # ❌ Will raise ValueError immediately
        }
    )
except ValueError as e:
    print(f"Configuration error: {e}")
    # Error: Invalid level 'INVALID' in auto_sink_levels
```

**Manual Sinks:**
- Validates each sink independently
- Allows partial success
- Can continue after failed sink creation

```python
logger.add("logs/valid.log", filter_min_level="INFO")  # ✅ Created
try:
    logger.add("logs/test.log", filter_min_level="INVALID")  # ❌ Raises error
except ValueError:
    pass  # First sink still works
logger.add("logs/another.log", filter_min_level="ERROR")  # ✅ Also created
```

---

#### **5. Performance Considerations**

**Auto-Sink Levels:**
- Creates all sinks upfront during `configure()`
- No runtime overhead for sink creation
- Best for static configurations

**Manual Sinks:**
- Can add sinks on-demand
- Allows lazy creation
- Best for dynamic configurations

---

#### **6. Code Examples**

**Scenario: Application with 3 log levels**

**Auto-Sink (Recommended for this case):**
```python
# ✅ Clean, concise, maintainable
from logly import logger

logger.configure(
    level="DEBUG",
    auto_sink_levels={
        "DEBUG": "logs/debug.log",
        "WARNING": "logs/warnings.log",
        "ERROR": "logs/errors.log"
    }
)
```
**Lines of code:** 9  
**Maintainability:** Excellent  
**Readability:** Excellent

**Manual Sinks (Also works, but more verbose):**
```python
# ✅ Works, but more code
from logly import logger

logger.configure(level="DEBUG")
logger.add("logs/debug.log", filter_min_level="DEBUG")
logger.add("logs/warnings.log", filter_min_level="WARNING")
logger.add("logs/errors.log", filter_min_level="ERROR")
```
**Lines of code:** 6  
**Maintainability:** Good  
**Readability:** Good

---

**Scenario: Module-specific logging**

**Manual Sinks (Required for this case):**
```python
# ✅ Only manual sinks support module filtering
logger.add("logs/api.log", filter_module="api", filter_min_level="INFO")
logger.add("logs/db.log", filter_module="database", filter_min_level="DEBUG")
```

**Auto-Sink (❌ Cannot do this):**
```python
# ❌ Auto-sink levels don't support module filtering
auto_sink_levels={
    "INFO": {"path": "logs/api.log", "filter_module": "api"}  # Not supported!
}
```

---

### Migration Guide

**From Manual to Auto-Sink:**

**Before (Manual):**
```python
logger.configure(level="INFO")
logger.add("logs/info.log", filter_min_level="INFO")
logger.add("logs/error.log", filter_min_level="ERROR", rotation="daily")
```

**After (Auto-Sink):**
```python
logger.configure(
    level="INFO",
    auto_sink_levels={
        "INFO": "logs/info.log",
        "ERROR": {
            "path": "logs/error.log",
            "rotation": "daily"
        }
    }
)
```

**Benefits:**
- ✅ 1 configuration call instead of 3
- ✅ All settings in one place
- ✅ Easier to understand and maintain
- ✅ Better for version control (fewer diffs)

---

### Combining Both Approaches

You can use **both** auto-sink levels and manual sinks together:

```python
# Auto-sink for standard levels
logger.configure(
    level="DEBUG",
    auto_sink_levels={
        "DEBUG": "logs/debug.log",
        "INFO": "logs/info.log",
        "ERROR": "logs/error.log"
    }
)

# Manual sinks for special cases
logger.add(
    "logs/api_module.log",
    filter_module="api",
    filter_min_level="INFO"
)

logger.add(
    "logs/payment_function.log",
    filter_module="payment",
    filter_function="process_payment",
    filter_min_level="WARNING"
)
```

**Result:**
- Standard logs → auto-created level files
- API module logs → `logs/api_module.log`
- Payment function logs → `logs/payment_function.log`

---

### Summary Table

| Scenario | Use Auto-Sink | Use Manual | Reason |
|----------|---------------|------------|--------|
| Level-based file separation | ✅ | ⚠️ | Auto-sink is cleaner |
| Module-specific logging | ❌ | ✅ | Requires filter_module |
| Function-specific logging | ❌ | ✅ | Requires filter_function |
| Production with rotation | ✅ | ✅ | Both work, auto is cleaner |
| Dynamic sink management | ⚠️ | ✅ | Manual allows add/remove |
| Development debugging | ✅ | ✅ | Either works |
| Centralized config | ✅ | ⚠️ | Auto-sink is centralized |
| Complex multi-filter | ❌ | ✅ | Requires manual approach |

**Legend:**
- ✅ **Recommended** - Best choice for this scenario
- ⚠️ **Works but not optimal** - Can be done but there's a better way
- ❌ **Not supported** - Cannot achieve this requirement

---

## Comparison with Manual Sinks (OLD - kept for reference)

| Feature | Auto-Sink Levels | Manual Sinks |
|---------|------------------|--------------|
| Configuration location | Single `configure()` call | Multiple `add()` calls |
| Level filtering | Automatic by level name | Manual with `filter_min_level` |
| Code clarity | High (declarative) | Medium (imperative) |
| Flexibility | Medium | High |
| Best for | Standard level-based logging | Complex filtering logic |
| Maintainability | Excellent | Good |

**Use auto-sink levels when:**
- You need standard level-based file separation
- You want centralized configuration
- You prefer declarative style

**Use manual sinks when:**
- You need complex filtering (module + function)
- You need dynamic sink management
- You need full programmatic control

---

## Related Documentation

- [Configuration API](../api-reference/configuration.md) - Full configure() options
- [File Rotation](file-rotation.md) - Rotation and retention details
- [Multi-Sink Logging](multi-sink.md) - Advanced multi-sink patterns
- [JSON Logging](json-logging.md) - JSON output format
- [Production Deployment](../guides/production-deployment.md) - Production best practices
