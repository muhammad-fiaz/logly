---
title: Configuration API - Logly Python Logging
description: Logly configuration API reference. Learn how to configure logging levels, output formats, and manage sinks for the Python logging library.
keywords: python, logging, configuration, api, levels, formats, sinks, logly
---

# Configuration Methods

Methods for configuring the logger and managing output destinations.

---

## logger.configure()

Set global logger configuration including level, output format, and colors.

### Signature

```python
logger.configure(
    level: str = "INFO",
    color: bool = True,
    level_colors: dict[str, str] | None = None,
    json: bool = False,
    pretty_json: bool = False,
    console: bool = True,
    show_time: bool = True,
    show_module: bool = True,
    show_function: bool = True,
    console_levels: dict[str, bool] | None = None,
    time_levels: dict[str, bool] | None = None,
    color_levels: dict[str, bool] | None = None,
    storage_levels: dict[str, bool] | None = None
) -> None
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level: `"TRACE"`, `"DEBUG"`, `"INFO"`, `"SUCCESS"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"` |
| `color` | `bool` | `True` | Enable colored console output (ANSI colors) |
| `level_colors` | `dict[str, str] \| None` | `None` | Custom colors for each log level. Supports both ANSI color codes and color names. If `None`, uses default colors |
| `json` | `bool` | `False` | Output logs in JSON format instead of text |
| `pretty_json` | `bool` | `False` | Pretty-print JSON output (higher cost, more readable) |
| `console` | `bool` | `True` | Enable console output |
| `show_time` | `bool` | `True` | Show timestamps in console output |
| `show_module` | `bool` | `True` | Show module information in console output |
| `show_function` | `bool` | `True` | Show function information in console output |
| `console_levels` | `dict[str, bool] \| None` | `None` | Per-level console output control. Maps level names to enable/disable console output |
| `time_levels` | `dict[str, bool] \| None` | `None` | Per-level time display control. Maps level names to enable/disable timestamps |
| `color_levels` | `dict[str, bool] \| None` | `None` | Per-level color control. Maps level names to enable/disable colors |
| `storage_levels` | `dict[str, bool] \| None` | `None` | Per-level storage control. Maps level names to enable/disable file logging |

### Color Configuration

The `level_colors` parameter supports both ANSI color codes and user-friendly color names:

#### ANSI Color Codes

| Color | Code | Bright Color | Code |
|-------|------|--------------|------|
| Black | `"30"` | Bright Black | `"90"` |
| Red | `"31"` | Bright Red | `"91"` |
| Green | `"32"` | Bright Green | `"92"` |
| Yellow | `"33"` | Bright Yellow | `"93"` |
| Blue | `"34"` | Bright Blue | `"94"` |
| Magenta | `"35"` | Bright Magenta | `"95"` |
| Cyan | `"36"` | Bright Cyan | `"96"` |
| White | `"37"` | Bright White | `"97"` |

#### Color Names

You can also use color names directly:

| Color Name | ANSI Equivalent |
|------------|-----------------|
| `"BLACK"` | `"30"` |
| `"RED"` | `"31"` |
| `"GREEN"` | `"32"` |
| `"YELLOW"` | `"33"` |
| `"BLUE"` | `"34"` |
| `"MAGENTA"` | `"35"` |
| `"CYAN"` | `"36"` |
| `"WHITE"` | `"37"` |
| `"BRIGHT_BLACK"` or `"GRAY"` | `"90"` |
| `"BRIGHT_RED"` | `"91"` |
| `"BRIGHT_GREEN"` | `"92"` |
| `"BRIGHT_YELLOW"` | `"93"` |
| `"BRIGHT_BLUE"` | `"94"` |
| `"BRIGHT_MAGENTA"` | `"95"` |
| `"BRIGHT_CYAN"` | `"96"` |
| `"BRIGHT_WHITE"` | `"97"` |
| Blue | `"34"` | Bright Blue | `"94"` |
| Magenta | `"35"` | Bright Magenta | `"95"` |
| Cyan | `"36"` | Bright Cyan | `"96"` |
| White | `"37"` | Bright White | `"97"` |

### Returns

`None`

### Examples

=== "Text Output with Colors"

    ```python
    from logly import logger

    logger.configure(level="INFO", color=True, json=False)
    logger.add("console")
    
    logger.info("Colored text output", user="alice")
    ```
    
    Output:
    ```
    2025-01-15 10:30:45 | INFO     | Colored text output user=alice
    ```

=== "JSON Output"

    ```python
    logger.configure(level="INFO", json=True, pretty_json=False)
    logger.add("console")
    
    logger.info("JSON output", user="alice", ip="192.168.1.1")
    ```
    
    Output:
    ```json
    {"timestamp":"2025-01-15T10:30:45.123Z","level":"INFO","message":"JSON output","fields":{"user":"alice","ip":"192.168.1.1"}}
    ```

=== "Pretty JSON"

    ```python
    logger.configure(level="DEBUG", json=True, pretty_json=True)
    logger.add("console")
    
    logger.debug("Pretty JSON", step=1, phase="init")
    ```
    
    Output:
    ```json
    {
      "timestamp": "2025-01-15T10:30:45.123Z",
      "level": "DEBUG",
      "message": "Pretty JSON",
      "fields": {
        "step": 1,
        "phase": "init"
      }
    }
    ```

=== "Custom Level Colors with ANSI Codes"

    ```python
    from logly import logger

    # Custom ANSI colors for each level
    custom_colors = {
        "INFO": "32",      # Green
        "WARNING": "93",   # Bright Yellow
        "ERROR": "91",     # Bright Red
        "CRITICAL": "95"   # Bright Magenta
    }

    logger.configure(
        level="INFO",
        color=True,
        level_colors=custom_colors
    )
    logger.add("console")

    logger.info("This is green")
    logger.warning("This is bright yellow")
    logger.error("This is bright red")
    logger.critical("This is bright magenta")
    ```

=== "Custom Level Colors with Names"

    ```python
    from logly import logger

    # Custom colors using user-friendly names
    custom_colors = {
        "INFO": "GREEN",
        "WARNING": "YELLOW",
        "ERROR": "RED",
        "CRITICAL": "BRIGHT_MAGENTA"
    }

    logger.configure(
        level="INFO",
        color=True,
        level_colors=custom_colors
    )
    logger.add("console")

    logger.info("This is green")
    logger.warning("This is yellow")
    logger.error("This is red")
    logger.critical("This is bright magenta")
    ```

=== "Console Time Display Control"

    ```python
    from logly import logger

    # Show timestamps (default)
    logger.configure(level="INFO", show_time=True)
    logger.add("console")
    logger.info("Message with timestamp")

    # Hide timestamps
    logger.configure(level="INFO", show_time=False)
    logger.add("console")
    logger.info("Message without timestamp")
    ```

=== "Module and Function Display Control"

    ```python
    from logly import logger

    # Show module and function info (default)
    logger.configure(level="INFO", show_module=True, show_function=True)
    logger.add("console")
    logger.info("Message with module and function")

    # Hide module and function info
    logger.configure(level="INFO", show_module=False, show_function=False)
    logger.add("console")
    logger.info("Message without module and function")

    # Show only module, hide function
    logger.configure(level="INFO", show_module=True, show_function=False)
    logger.add("console")
    logger.info("Message with module only")
    ```

=== "Production Setup"

    ```python
    # Production configuration
    logger.configure(
        level="INFO",           # Info and above
        color=False,            # No colors for log aggregators
        json=True,              # Structured JSON
        pretty_json=False       # Compact for storage
    )
    logger.add("console")
    logger.add("logs/app.log", rotation="daily", retention=30)
    ```

### Notes

!!! info "Configuration Timing"
    Call `configure()` once at application startup before adding sinks.

!!! tip "Log Levels"
    Use `"DEBUG"` for development and `"INFO"` or `"WARNING"` for production.

!!! warning "Pretty JSON Performance"
    `pretty_json=True` adds formatting overhead. Use only in development.

---

## logger.reset()

Reset logger configuration to default settings.

### Signature

```python
logger.reset() -> None
```

### Description

Resets all logger settings to their default values, clearing any per-level controls and custom configurations. This is useful for testing or when you need to return to a clean state.

### Returns

`None`

### Examples

```python
# Configure with custom settings
logger.configure(level="DEBUG", console_levels={"INFO": False})

# Reset to defaults
logger.reset()
```

---

## logger.add()

Add a logging sink (output destination) with optional rotation, filtering, and async writing.

### Signature

```python
logger.add(
    sink: str,
    *,
    rotation: str | None = None,
    size_limit: str | None = None,
    retention: int | None = None,
    filter_min_level: str | None = None,
    filter_module: str | None = None,
    filter_function: str | None = None,
    async_write: bool = True,
    date_style: str | None = None,
    date_enabled: bool = False
) -> int
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sink` | `str` | Required | `"console"` for stdout or file path for file output |
| `rotation` | `str \| None` | `None` | Time-based rotation: `"daily"`, `"hourly"`, `"minutely"`, `"never"` |
| `size_limit` | `str \| None` | `None` | Maximum file size: `"500B"`, `"5KB"`, `"10MB"`, `"1GB"` |
| `retention` | `int \| None` | `None` | Number of rotated files to keep (older files auto-deleted) |
| `filter_min_level` | `str \| None` | `None` | Minimum level for this sink: `"INFO"`, `"ERROR"`, etc. |
| `filter_module` | `str \| None` | `None` | Only log from this module |
| `filter_function` | `str \| None` | `None` | Only log from this function |
| `async_write` | `bool` | `True` | Enable background async writing |
| `date_style` | `str \| None` | `None` | Date format: `"rfc3339"`, `"local"`, `"utc"`, `"before_ext"`, `"prefix"` |
| `date_enabled` | `bool` | `False` | Include timestamp in filenames |

### Returns

`int` - Handler ID for removing the sink later with `remove()`

### Examples

=== "Console Output"

    ```python
    # Add console output
    handler_id = logger.add("console")
    logger.info("Console logging enabled")
    ```

=== "Basic File Output"

    ```python
    # Simple file logging
    logger.add("logs/app.log")
    logger.info("Logging to file")
    ```

=== "Daily Rotation"

    ```python
    # Rotate daily at midnight, keep last 7 files
    logger.add(
        "logs/app.log",
        rotation="daily",
        retention=7
    )
    
    # Files: app.log, app.2025-01-14.log, app.2025-01-13.log, ...
    ```

=== "Size-Based Rotation"

    ```python
    # Rotate when file reaches 10MB, keep last 5 files
    logger.add(
        "logs/app.log",
        size_limit="10MB",
        retention=5
    )
    ```

=== "Combined Rotation"

    ```python
    # Rotate daily OR when size reaches 500MB
    logger.add(
        "logs/app.log",
        rotation="daily",
        size_limit="500MB",
        retention=10
    )
    ```

=== "Filtered Sink"

    ```python
    # Only ERROR and above to error log
    logger.add(
        "logs/errors.log",
        filter_min_level="ERROR"
    )
    
    # Only logs from specific module
    logger.add(
        "logs/auth.log",
        filter_module="myapp.auth"
    )
    
    # Only logs from specific function
    logger.add(
        "logs/critical.log",
        filter_min_level="CRITICAL",
        filter_function="process_payment"
    )
    ```

=== "Production Setup"

    ```python
    # Console for monitoring
    logger.add("console")
    
    # All logs with daily rotation
    logger.add(
        "logs/app.log",
        rotation="daily",
        retention=30,
        async_write=True
    )
    
    # Errors to separate file
    logger.add(
        "logs/errors.log",
        filter_min_level="ERROR",
        retention=90
    )
    
    # Critical alerts
    logger.add(
        "logs/critical.log",
        filter_min_level="CRITICAL",
        retention=365
    )
    ```

### Rotation Examples

#### Time-Based Rotation

```python
# Daily rotation (new file at midnight)
logger.add("logs/app.log", rotation="daily")
# Files: app.log, app.2025-01-14.log, app.2025-01-13.log

# Hourly rotation (new file every hour)
logger.add("logs/app.log", rotation="hourly")
# Files: app.log, app.2025-01-15-10.log, app.2025-01-15-09.log

# Minutely rotation (for testing)
logger.add("logs/test.log", rotation="minutely")
```

#### Size-Based Rotation

```python
# Bytes
logger.add("logs/app.log", size_limit="500B")

# Kilobytes
logger.add("logs/app.log", size_limit="5KB")

# Megabytes
logger.add("logs/app.log", size_limit="10MB")

# Gigabytes
logger.add("logs/app.log", size_limit="1GB")
```

### Notes

!!! info "Async Writing"
    With `async_write=True` (default), file writes happen in a background thread for minimal latency.

!!! tip "Retention"
    Set `retention` to auto-delete old rotated files and manage disk space.

!!! warning "Multiple Sinks"
    You can add multiple sinks with different configurations. Each returns a unique handler ID.

!!! example "Common Pattern"
    ```python
    # Development
    logger.add("console")
    logger.add("logs/dev.log", rotation="daily", retention=3)
    
    # Production
    logger.add("console")
    logger.add("logs/app.log", rotation="daily", size_limit="500MB", retention=30)
    logger.add("logs/errors.log", filter_min_level="ERROR", retention=90)
    ```

---

## logger.remove()

Remove a logging sink by its handler ID.

### Signature

```python
logger.remove(handler_id: int) -> bool
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `handler_id` | `int` | Handler ID returned by `add()` |

### Returns

`bool` - `True` if sink was removed, `False` otherwise

### Example

```python
# Add sink
handler_id = logger.add("logs/temp.log")
logger.info("Temporary logging")

# Remove sink
success = logger.remove(handler_id)
print(f"Removed: {success}")  # True

# Logs after removal don't go to temp.log
logger.info("No longer logging to temp.log")
```

### Notes

!!! tip "Cleanup"
    Remove sinks when they're no longer needed to free resources.

!!! warning "Console Sink"
    Removing the console sink (ID 0) may not have visible effects depending on configuration.
