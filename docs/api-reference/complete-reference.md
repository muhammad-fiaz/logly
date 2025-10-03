---
title: Complete API Reference - Logly Python Logging
description: Complete reference of all Logly methods, parameters, and functionality in organized tables.
keywords: python, logging, api, reference, methods, parameters, complete, logly
---

# Complete API Reference

Comprehensive reference of all Logly functionality organized by category.

---

## Configuration Methods

### logger.configure()

Configure global logger settings.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level: `"TRACE"`, `"DEBUG"`, `"INFO"`, `"SUCCESS"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"` |
| `color` | `bool` | `True` | Enable ANSI colored console output |
| `level_colors` | `dict[str, str] \| None` | `None` | Custom colors for each log level (ANSI codes or color names) |
| `color_callback` | `callable \| None` | `None` | Custom color callback function with signature `(level: str, text: str) -> str` |
| `json` | `bool` | `False` | Output logs in JSON format |
| `pretty_json` | `bool` | `False` | Pretty-print JSON output (indented) |
| `console` | `bool` | `True` | Enable console output |
| `show_time` | `bool` | `True` | Show timestamps in console output |
| `show_module` | `bool` | `True` | Show module name in console output |
| `show_function` | `bool` | `True` | Show function name in console output |
| `show_filename` | `bool` | `False` | Show filename in console output |
| `show_lineno` | `bool` | `False` | Show line number in console output |
| `console_levels` | `dict[str, bool] \| None` | `None` | Per-level console output control |
| `time_levels` | `dict[str, bool] \| None` | `None` | Per-level timestamp display control |
| `color_levels` | `dict[str, bool] \| None` | `None` | Per-level color control |
| `storage_levels` | `dict[str, bool] \| None` | `None` | Per-level file storage control |

**Returns:** `None`

---

### logger.add()

Add a logging sink (output destination).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sink` | `str \| None` | `None` | `"console"` for stdout or file path for file logging |
| `rotation` | `str \| None` | `None` | Time-based rotation: `"daily"`, `"hourly"`, `"minutely"`, `"never"` |
| `size_limit` | `str \| None` | `None` | Size-based rotation: `"500B"`, `"5KB"`, `"10MB"`, `"1GB"` |
| `retention` | `int \| None` | `None` | Number of rotated files to keep (older files deleted) |
| `filter_min_level` | `str \| None` | `None` | Minimum log level for this sink |
| `filter_module` | `str \| None` | `None` | Filter logs from specific module |
| `filter_function` | `str \| None` | `None` | Filter logs from specific function |
| `async_write` | `bool` | `True` | Enable background async writing |
| `buffer_size` | `int` | `8192` | Buffer size in bytes for async writing |
| `flush_interval` | `int` | `100` | Flush interval in milliseconds |
| `max_buffered_lines` | `int` | `1000` | Maximum buffered lines before blocking |
| `date_style` | `str \| None` | `None` | Timestamp format: `"rfc3339"`, `"local"`, `"utc"` |
| `date_enabled` | `bool` | `False` | Include timestamp in output |
| `format` | `str \| None` | `None` | Custom format string with placeholders |
| `json` | `bool` | `False` | Output JSON format for this sink |

**Returns:** `int` - Handler ID for removal

---

### logger.remove()

Remove a logging sink by handler ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `handler_id` | `int` | Yes | Handler ID returned by `add()` |

**Returns:** `None`

---

### logger.reset()

Reset logger to default configuration.

**Parameters:** None  
**Returns:** `None`

---

## Logging Methods

All logging methods support structured fields via `**kwargs`.

| Method | Level | Color | Signature | Description |
|--------|-------|-------|-----------|-------------|
| `logger.trace()` | TRACE | Gray | `trace(message: str, **kwargs) -> None` | Detailed debugging, function traces |
| `logger.debug()` | DEBUG | Cyan | `debug(message: str, **kwargs) -> None` | Development debugging |
| `logger.info()` | INFO | White | `info(message: str, **kwargs) -> None` | General information |
| `logger.success()` | SUCCESS | Green | `success(message: str, **kwargs) -> None` | Successful operations |
| `logger.warning()` | WARNING | Yellow | `warning(message: str, **kwargs) -> None` | Warning messages |
| `logger.error()` | ERROR | Red | `error(message: str, **kwargs) -> None` | Error conditions |
| `logger.critical()` | CRITICAL | Bold Red | `critical(message: str, **kwargs) -> None` | Critical system errors |

**Common Parameters:**
- `message` (str): Log message text
- `**kwargs`: Additional structured fields (key-value pairs)

---

## Context Management

### logger.bind()

Create a logger with bound context fields.

| Parameter | Type | Description |
|-----------|------|-------------|
| `**fields` | `Any` | Key-value pairs to bind to logger |

**Returns:** `Logger` - New logger instance with bound context

**Example:**
```python
request_logger = logger.bind(request_id="abc123", user="alice")
request_logger.info("Request started")  # Includes request_id and user
```

---

### logger.contextualize()

Temporary context manager for adding fields.

| Parameter | Type | Description |
|-----------|------|-------------|
| `**fields` | `Any` | Key-value pairs for temporary context |

**Returns:** Context manager

**Example:**
```python
with logger.contextualize(transaction_id="tx-789"):
    logger.info("Processing")  # Includes transaction_id
# transaction_id removed after block
```

---

## Callback Management

### logger.add_callback()

Register a callback function for log events.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `callback` | `Callable[[dict], None]` | Yes | Function to call on each log event |
| `min_level` | `str \| None` | No | Minimum level to trigger callback (default: all) |

**Returns:** `int` - Callback ID for removal

**Callback receives dict with:**
- `timestamp`: ISO 8601 timestamp
- `level`: Log level string
- `message`: Log message
- All extra fields from log call
- All bound context fields

**Example:**
```python
def alert_on_error(record):
    if record["level"] == "ERROR":
        send_alert(record["message"])

callback_id = logger.add_callback(alert_on_error, min_level="ERROR")
```

---

### logger.remove_callback()

Remove a callback by ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `callback_id` | `int` | Yes | Callback ID returned by `add_callback()` |

**Returns:** `None`

---

## Exception Handling

### logger.exception()

Log exception with full traceback at ERROR level.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | `str` | `""` | Custom error message |
| `**kwargs` | `Any` | - | Additional context fields |

**Returns:** `None`

**Example:**
```python
try:
    risky_operation()
except Exception:
    logger.exception("Operation failed", user_id=123)
```

---

### @logger.catch()

Decorator to automatically catch and log exceptions.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `reraise` | `bool` | `False` | Re-raise exception after logging |
| `level` | `str` | `"ERROR"` | Log level for caught exceptions |
| `message` | `str \| None` | `None` | Custom error message |

**Returns:** Decorated function

**Example:**
```python
@logger.catch(reraise=True)
def process_data():
    # Exceptions automatically logged
    return 1 / 0
```

---

## Utility Methods

### logger.enable()

Enable logging (resume after disable).

**Parameters:** None  
**Returns:** `None`

---

### logger.disable()

Disable all logging temporarily.

**Parameters:** None  
**Returns:** `None`

---

### logger.level()

Register custom log level alias.

**Parameters:**
- `name` (str): Custom level name
- `mapped_to` (str): Existing level to map to

**Returns:** `None`

---

### logger.reset()

Reset logger configuration to default settings.

**Parameters:** None  
**Returns:** `None`

---

### logger.complete()

Flush all buffers and close all sinks gracefully.

**Parameters:** None  
**Returns:** `None`

**Note:** Always call before program exit to ensure all logs are written.

---

## Format String Placeholders

Custom format strings support these placeholders:

| Placeholder | Description | Example Output |
|-------------|-------------|----------------|
| `{time}` | Timestamp (ISO 8601) | `2025-01-15T14:32:10.123456+00:00` |
| `{level}` | Log level | `INFO`, `ERROR`, `DEBUG` |
| `{message}` | Log message text | `User logged in` |
| `{extra}` | All extra fields | `user=alice \| session=abc123` |
| `{module}` | Module name | `myapp.auth` |
| `{function}` | Function name | `login_user` |
| `{filename}` | Source filename | `app.py` |
| `{lineno}` | Line number | `42` |
| `{any_key}` | Any custom field | Value of that field |

**Placeholder Rules:**
- Case-insensitive: `{TIME}` = `{time}` = `{Time}`
- Missing placeholders: Unknown placeholders left as-is
- Extra fields: Only fields included in the template or `{extra}` are displayed

---

## Color Names

Supported color names for `level_colors` parameter:

### Standard Colors

| Color Name | ANSI Code |
|------------|-----------|
| `"BLACK"` | `"30"` |
| `"RED"` | `"31"` |
| `"GREEN"` | `"32"` |
| `"YELLOW"` | `"33"` |
| `"BLUE"` | `"34"` |
| `"MAGENTA"` | `"35"` |
| `"CYAN"` | `"36"` |
| `"WHITE"` | `"37"` |

### Bright Colors

| Color Name | ANSI Code |
|------------|-----------|
| `"BRIGHT_BLACK"` or `"GRAY"` | `"90"` |
| `"BRIGHT_RED"` | `"91"` |
| `"BRIGHT_GREEN"` | `"92"` |
| `"BRIGHT_YELLOW"` | `"93"` |
| `"BRIGHT_BLUE"` | `"94"` |
| `"BRIGHT_MAGENTA"` | `"95"` |
| `"BRIGHT_CYAN"` | `"96"` |
| `"BRIGHT_WHITE"` | `"97"` |

---

## Size Units

For `size_limit` parameter:

| Unit | Description | Example |
|------|-------------|---------|
| `B` | Bytes | `"1024B"` |
| `KB` | Kilobytes | `"500KB"` |
| `MB` | Megabytes | `"10MB"` |
| `GB` | Gigabytes | `"1GB"` |

---

## Rotation Options

For `rotation` parameter:

| Value | Description |
|-------|-------------|
| `"daily"` | Rotate at midnight each day |
| `"hourly"` | Rotate at the start of each hour |
| `"minutely"` | Rotate at the start of each minute |
| `"never"` | Disable time-based rotation |

**Note:** Can combine time and size rotation. File rotates when either condition is met.

---

## Log Levels

Complete list of log levels (lowest to highest):

| Level | Numeric Value | Description |
|-------|---------------|-------------|
| `TRACE` | 5 | Most verbose, detailed traces |
| `DEBUG` | 10 | Debug information |
| `INFO` | 20 | General information |
| `SUCCESS` | 25 | Successful operations |
| `WARNING` | 30 | Warning messages |
| `ERROR` | 40 | Error conditions |
| `CRITICAL` | 50 | Critical system failures |

---

## Best Practices

### Configuration
- ✅ Call `configure()` once at startup
- ✅ Use `"INFO"` or `"WARNING"` in production
- ✅ Enable `json=True` for log aggregation
- ✅ Disable `color=True` for log collectors
- ✅ Use `pretty_json=False` in production

### Sinks
- ✅ Add console for development
- ✅ Add file with rotation for production
- ✅ Use separate sinks for different log levels
- ✅ Enable `async_write=True` for high volume
- ✅ Set appropriate `retention` to manage disk space

### Logging
- ✅ Use structured fields (`**kwargs`) over string formatting
- ✅ Use `.bind()` for request/session context
- ✅ Use `.contextualize()` for temporary context
- ✅ Call `logger.complete()` before exit

### Exception Handling
- ✅ Use `logger.exception()` in except blocks
- ✅ Use `@logger.catch()` decorator for automatic logging
- ✅ Include context fields for debugging

---

## Quick Reference

### Essential Operations

```python
# Configuration
logger.configure(level="INFO", json=True, color=True)

# Add sinks
logger.add("console")
logger.add("app.log", rotation="daily", retention=7)

# Logging
logger.info("Message", key="value")
logger.error("Error", error_code=500)

# Context
bound_logger = logger.bind(request_id="123")
with logger.contextualize(step="validation"):
    logger.debug("Validating")

# Callbacks
callback_id = logger.add_callback(my_callback, min_level="ERROR")
logger.remove_callback(callback_id)

# Exception handling
try:
    risky()
except:
    logger.exception("Failed", user_id=42)

# Cleanup
logger.complete()
```

---

## See Also

- [Configuration API](configuration.md) - Detailed configuration reference
- [Logging Methods](logging.md) - All logging methods
- [Context Management](context.md) - Context binding details
- [Callbacks](callbacks.md) - Callback system
- [Exception Handling](exceptions.md) - Exception handling
- [Utilities](utilities.md) - Utility methods
