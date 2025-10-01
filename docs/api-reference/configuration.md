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
    json: bool = False,
    pretty_json: bool = False
) -> None
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level: `"TRACE"`, `"DEBUG"`, `"INFO"`, `"SUCCESS"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"` |
| `color` | `bool` | `True` | Enable colored console output (ANSI colors) |
| `json` | `bool` | `False` | Output logs in JSON format instead of text |
| `pretty_json` | `bool` | `False` | Pretty-print JSON output (higher cost, more readable) |

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
