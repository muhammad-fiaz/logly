# Complete API Reference

Comprehensive professional reference for all Logly functionality with detailed tables, examples, and best practices.

---

## Overview

Logly is a high-performance Rust-powered Python logging library providing structured logging, async I/O, rotation, filtering, and extensive configuration options. This reference covers all 40+ methods available in the global `logger` instance.

---

## Logger Instance

Import the global logger instance:

```python
from logly import logger
```

All examples in this reference use this import pattern.

---

## Configuration Methods

### logger.configure()

Configure global logger settings including level, output format, colors, and display options.

#### Signature

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
    show_filename: bool = False,
    show_lineno: bool = False,
    console_levels: dict[str, bool] | None = None,
    time_levels: dict[str, bool] | None = None,
    color_levels: dict[str, bool] | None = None,
    storage_levels: dict[str, bool] | None = None,
    color_callback: callable | None = None
) -> None
```

#### Parameters Table

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Default minimum log level. Options: `"TRACE"`, `"DEBUG"`, `"INFO"`, `"SUCCESS"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`. |
| `color` | `bool` | `True` | Enable colored console output. Uses ANSI escape codes unless `color_callback` is provided. |
| `level_colors` | `dict[str, str] \| None` | `None` | Custom color mapping for log levels. Keys are level names, values are ANSI color codes (e.g., `"31"` for red) or color names (e.g., `"RED"`). |
| `json` | `bool` | `False` | Output logs in JSON format instead of text. Each log becomes a JSON object with fields like `level`, `message`, and extra fields. |
| `pretty_json` | `bool` | `False` | Pretty-print JSON output with indentation. Only applies when `json=True`. Higher cost but more readable. |
| `console` | `bool` | `True` | Enable console (stdout) output. When `False`, no logs appear in terminal (file sinks still work). |
| `show_time` | `bool` | `True` | Show timestamps in console output. Format depends on `date_style` in sinks. |
| `show_module` | `bool` | `True` | Show module name in console output (e.g., `app.auth`). |
| `show_function` | `bool` | `True` | Show function name in console output (e.g., `authenticate_user`). |
| `show_filename` | `bool` | `False` | Show source filename in console output (e.g., `api.py`). |
| `show_lineno` | `bool` | `False` | Show line number in console output (e.g., `42`). |
| `console_levels` | `dict[str, bool] \| None` | `None` | Per-level console output control. Example: `{"DEBUG": False, "INFO": True}` hides DEBUG from console. |
| `time_levels` | `dict[str, bool] \| None` | `None` | Per-level timestamp display. Example: `{"ERROR": True, "INFO": False}` shows time only for errors. |
| `color_levels` | `dict[str, bool] \| None` | `None` | Per-level color control. Example: `{"DEBUG": False}` disables colors for DEBUG logs. |
| `storage_levels` | `dict[str, bool] \| None` | `None` | Per-level file storage control. Example: `{"TRACE": False}` prevents TRACE from being written to files. |
| `color_callback` | `callable \| None` | `None` | Custom color function with signature `(level: str, text: str) -> str`. Overrides built-in ANSI coloring. Use for Rich, colorama, etc. |

#### Returns

- **Type:** `None`
- **Description:** Configuration is applied globally to all subsequent log calls.

#### Examples

=== "Basic Text Configuration"

    ```python
    from logly import logger

    logger.configure(level="INFO", color=True, show_time=True)
    logger.add("console")
    
    logger.info("Application started", version="1.0.0")
    logger.error("Connection failed", retry=3)
    ```

    **Explanation:** Configures logger with INFO level, colored output, and timestamps. The console sink displays logs with time, level, message, and extra fields.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | INFO     | __main__:main:4 - Application started version=1.0.0
    2025-01-15 14:30:46 | ERROR    | __main__:main:5 - Connection failed retry=3
    ```

=== "JSON Output"

    ```python
    from logly import logger

    logger.configure(level="INFO", json=True, pretty_json=False)
    logger.add("console")
    
    logger.info("User login", user="alice", ip="192.168.1.1")
    ```

    **Explanation:** Outputs logs as compact JSON (single line). Perfect for log aggregation systems like ELK Stack, Splunk, or CloudWatch. Extra fields are automatically included in JSON output.

    **Expected Output:**
    ```json
    {"timestamp":"2025-01-15T14:30:45.123Z","level":"INFO","module":"__main__","function":"main","message":"User login","user":"alice","ip":"192.168.1.1"}
    ```

=== "Pretty JSON"

    ```python
    from logly import logger

    logger.configure(level="DEBUG", json=True, pretty_json=True)
    logger.add("console")
    
    logger.debug("Processing request", request_id="abc123", step=1)
    ```

    **Explanation:** Pretty-prints JSON with indentation for readability. Use only in development as it increases output size and formatting cost. Great for debugging complex log structures.

    **Expected Output:**
    ```json
    {
      "timestamp": "2025-01-15T14:30:45.123Z",
      "level": "DEBUG",
      "module": "__main__",
      "function": "main",
      "message": "Processing request",
      "request_id": "abc123",
      "step": 1
    }
    ```

=== "Custom Level Colors (ANSI Codes)"

    ```python
    from logly import logger

    custom_colors = {
        "INFO": "32",      # Green
        "WARNING": "33",   # Yellow
        "ERROR": "91",     # Bright Red
        "CRITICAL": "95"   # Bright Magenta
    }

    logger.configure(level="INFO", color=True, level_colors=custom_colors)
    logger.add("console")

    logger.info("Success")
    logger.warning("Warning")
    logger.error("Error")
    ```

    **Explanation:** Customize colors per level using ANSI escape codes. Codes range from 30-37 (normal) and 90-97 (bright). Use this for terminal environments that support ANSI.

    **Expected Output:** (with ANSI colors)
    ```
    2025-01-15 14:30:45 | INFO     | __main__:main:12 - Success          (in green)
    2025-01-15 14:30:46 | WARNING  | __main__:main:13 - Warning          (in yellow)
    2025-01-15 14:30:47 | ERROR    | __main__:main:14 - Error            (in bright red)
    ```

=== "Custom Level Colors (Color Names)"

    ```python
    from logly import logger

    custom_colors = {
        "INFO": "GREEN",
        "WARNING": "YELLOW",
        "ERROR": "RED",
        "CRITICAL": "BRIGHT_MAGENTA"
    }

    logger.configure(level="INFO", color=True, level_colors=custom_colors)
    logger.add("console")

    logger.info("Green message")
    logger.warning("Yellow message")
    logger.error("Red message")
    ```

    **Explanation:** Use human-readable color names instead of ANSI codes. Logly automatically converts them to the appropriate ANSI codes. This makes configuration more readable.

    **Expected Output:** (with ANSI colors)
    ```
    2025-01-15 14:30:45 | INFO     | __main__:main:12 - Green message     (in green)
    2025-01-15 14:30:46 | WARNING  | __main__:main:13 - Yellow message    (in yellow)
    2025-01-15 14:30:47 | ERROR    | __main__:main:14 - Red message       (in red)
    ```

=== "Per-Level Controls"

    ```python
    from logly import logger

    logger.configure(
        level="DEBUG",
        console_levels={"DEBUG": False},  # Hide DEBUG from console
        time_levels={"ERROR": True, "INFO": False},  # Time only for errors
        storage_levels={"TRACE": False}  # Don't store TRACE in files
    )
    logger.add("console")
    logger.add("app.log")

    logger.debug("Debug message")  # To file only
    logger.info("Info message")    # To console and file, no time
    logger.error("Error message")  # To console and file, with time
    ```

    **Explanation:** Fine-grained control over where each level appears. DEBUG is written to file but not console. INFO shows without timestamp. ERROR shows with timestamp. Perfect for reducing console noise while keeping detailed file logs.

    **Expected Console Output:**
    ```
    INFO     | __main__:main:13 - Info message
    2025-01-15 14:30:46 | ERROR    | __main__:main:14 - Error message
    ```

    **Expected File Output (app.log):**
    ```
    DEBUG    | __main__:main:12 - Debug message
    INFO     | __main__:main:13 - Info message
    2025-01-15 14:30:46 | ERROR    | __main__:main:14 - Error message
    ```

=== "Custom Color Callback"

    ```python
    from logly import logger

    def custom_color(level, text):
        """Custom color function using ANSI codes."""
        colors = {
            "DEBUG": "\033[36m",    # Cyan
            "INFO": "\033[32m",     # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",    # Red
            "CRITICAL": "\033[35m"  # Magenta
        }
        reset = "\033[0m"
        color_code = colors.get(level, "")
        return f"{color_code}{text}{reset}"

    logger.configure(level="DEBUG", color_callback=custom_color)
    logger.add("console")

    logger.debug("Custom colored debug")
    logger.info("Custom colored info")
    logger.error("Custom colored error")
    ```

    **Explanation:** Implement custom color logic by providing a callback function. This allows integration with third-party libraries like Rich, Colorama, or custom terminal color schemes. The callback receives the level name and text, and returns the colored text.

    **Expected Output:** (with custom ANSI colors)
    ```
    2025-01-15 14:30:45 | DEBUG    | __main__:main:18 - Custom colored debug    (in cyan)
    2025-01-15 14:30:46 | INFO     | __main__:main:19 - Custom colored info     (in green)
    2025-01-15 14:30:47 | ERROR    | __main__:main:20 - Custom colored error    (in red)
    ```

#### Available Color Codes

| Color Name | ANSI Code | Bright Variant | ANSI Code |
|------------|-----------|----------------|-----------|
| `"BLACK"` | `"30"` | `"BRIGHT_BLACK"` / `"GRAY"` | `"90"` |
| `"RED"` | `"31"` | `"BRIGHT_RED"` | `"91"` |
| `"GREEN"` | `"32"` | `"BRIGHT_GREEN"` | `"92"` |
| `"YELLOW"` | `"33"` | `"BRIGHT_YELLOW"` | `"93"` |
| `"BLUE"` | `"34"` | `"BRIGHT_BLUE"` | `"94"` |
| `"MAGENTA"` | `"35"` | `"BRIGHT_MAGENTA"` | `"95"` |
| `"CYAN"` | `"36"` | `"BRIGHT_CYAN"` | `"96"` |
| `"WHITE"` | `"37"` | `"BRIGHT_WHITE"` | `"97"` |

#### Do's and Don'ts

✅ **DO:**
- Call `configure()` once at application startup
- Use `"INFO"` or `"WARNING"` level in production
- Use `"DEBUG"` level during development
- Use `json=True` for log aggregation (ELK, Splunk)
- Use `pretty_json=True` only in development
- Use per-level controls for fine-grained output

❌ **DON'T:**
- Call `configure()` multiple times (creates inconsistency)
- Use `"TRACE"` level in production (too verbose)
- Use `pretty_json=True` in production (performance cost)
- Disable console in development (hard to debug)
- Forget to add sinks after configuring

---

### logger.reset()

Reset logger configuration to default settings.

#### Signature

```python
logger.reset() -> None
```

#### Parameters

None

#### Returns

- **Type:** `None`
- **Description:** All settings return to default values. Clears per-level controls and custom configurations.

#### Examples

=== "Basic Reset"

    ```python
    from logly import logger

    # Custom configuration
    logger.configure(level="DEBUG", json=True, show_time=False)
    logger.info("Custom config")

    # Reset to defaults
    logger.reset()
    logger.info("Default config")
    ```

    **Explanation:** The reset() method restores all logger settings to their initial state. This includes level, format, colors, and per-level controls. Sinks are NOT removed, so you'll see output from existing sinks with default formatting.

    **Expected Output:**
    ```json
    {"level":"INFO","message":"Custom config"}
    ```
    ```
    2025-01-15 14:30:45 | INFO     | __main__:main:9 - Default config
    ```

=== "Test Cleanup"

    ```python
    import pytest
    from logly import logger

    @pytest.fixture(autouse=True)
    def reset_logger():
        yield
        logger.reset()  # Clean state for next test
    ```

    **Explanation:** Using reset() in pytest fixtures ensures each test starts with default logger configuration. This prevents test pollution where one test's custom configuration affects another test. The autouse=True makes this run after every test automatically.

    **Use Case:** Ensures test isolation and prevents flaky tests due to shared logger state.

#### Use Cases

- 🧪 **Testing:** Clean state between tests
- 🔄 **Reconfiguration:** Reset before applying new config
- 🐛 **Debugging:** Return to known default state

#### Do's and Don'ts

✅ **DO:**
- Use in test teardown for clean state
- Reset before major reconfiguration
- Document when reset is called

❌ **DON'T:**
- Reset in production without reconfiguring
- Reset during active logging
- Assume sinks are removed (reset only affects config)

---

## Sink Management Methods

### logger.add()

Add a logging sink (output destination) with optional rotation, filtering, and async writing.

#### Signature

```python
logger.add(
    sink: str | None = None,
    rotation: str | None = None,
    size_limit: str | None = None,
    retention: int | None = None,
    filter_min_level: str | None = None,
    filter_module: str | None = None,
    filter_function: str | None = None,
    async_write: bool = True,
    buffer_size: int = 8192,
    flush_interval: int = 100,
    max_buffered_lines: int = 1000,
    date_style: str | None = None,
    date_enabled: bool = False,
    format: str | None = None,
    json: bool = False
) -> int
```

#### Parameters Table

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sink` | `str \| None` | `None` | Output destination: `"console"` for stdout or file path. If `None`, defaults to console. |
| `rotation` | `str \| None` | `None` | Time-based rotation: `"daily"`, `"hourly"`, `"minutely"`, `"never"`. |
| `size_limit` | `str \| None` | `None` | Size-based rotation: `"500B"`, `"5KB"`, `"10MB"`, `"1GB"`. Rotates when file reaches this size. |
| `retention` | `int \| None` | `None` | Number of rotated files to keep. Older files auto-deleted. |
| `filter_min_level` | `str \| None` | `None` | Minimum log level for this sink: `"TRACE"`, `"DEBUG"`, `"INFO"`, `"SUCCESS"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`. |
| `filter_module` | `str \| None` | `None` | Filter by module name (e.g., `"app.auth"`). Only logs from this module go to this sink. |
| `filter_function` | `str \| None` | `None` | Filter by function name (e.g., `"process_payment"`). Only logs from this function go to this sink. |
| `async_write` | `bool` | `True` | Enable async (non-blocking) writing. Logs written in background thread. |
| `buffer_size` | `int` | `8192` | Buffer size in bytes for async writing. Range: 1024-65536. |
| `flush_interval` | `int` | `100` | Flush interval in milliseconds. Lower = less latency, higher = better throughput. |
| `max_buffered_lines` | `int` | `1000` | Maximum buffered lines before forcing flush. Prevents memory overflow. |
| `date_style` | `str \| None` | `None` | Timestamp format: `"rfc3339"`, `"local"`, `"utc"`. |
| `date_enabled` | `bool` | `False` | Include timestamps in output. |
| `format` | `str \| None` | `None` | Custom format string with placeholders: `{time}`, `{level}`, `{message}`, `{module}`, `{function}`, `{filename}`, `{lineno}`, `{extra}`. |
| `json` | `bool` | `False` | Output logs as JSON objects. |

#### Returns

- **Type:** `int`
- **Description:** Handler ID for this sink. Use with `remove()`, `read()`, `delete()`, etc.

#### Examples

See [Sink Management API](sink-management.md) for 20+ detailed examples with outputs.

**Quick Examples:**

```python
from logly import logger

# Console sink
logger.add("console")

# File with daily rotation
id1 = logger.add("app.log", rotation="daily", retention=7)

# Error-only sink
id2 = logger.add("errors.log", filter_min_level="ERROR")

# JSON sink
id3 = logger.add("data.log", json=True, async_write=True)

# Custom format
id4 = logger.add("custom.log", format="{time} [{level}] {message}")

logger.info("Test message", user="alice")
```

**Explanation:** Demonstrates adding multiple sinks with different purposes: console for development, rotating file for general logs, error-only file for critical issues, JSON file for structured data, and custom format file for specific needs.

**Expected Output (console):**
```
2025-01-15 14:30:45 | INFO     | __main__:main:15 - Test message user=alice
```

**Expected Output (app.log, errors.log, data.log, custom.log):**
Each file receives the log according to its configuration. See [Sink Management API](sink-management.md) for detailed outputs.

#### Do's and Don'ts

✅ **DO:**
- Use multiple sinks for different purposes
- Enable `async_write=True` for high throughput
- Set `retention` to manage disk space
- Use `filter_min_level` to reduce noise
- Store handler IDs for later removal

❌ **DON'T:**
- Create too many sinks (> 20)
- Use `async_write=False` without good reason
- Forget to set `retention` on production logs
- Hardcode file paths (use config files)

---

### logger.remove()

Remove a logging sink by handler ID.

#### Signature

```python
logger.remove(handler_id: int) -> bool
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `handler_id` | `int` | Handler ID returned by `add()`. |

#### Returns

- **Type:** `bool`
- **Description:** `True` if removed successfully, `False` if ID not found.

#### Example

```python
from logly import logger

handler = logger.add("temp.log")
logger.info("Temporary message")

success = logger.remove(handler)
print(f"Removed: {success}")  # True

logger.info("This won't go to temp.log")
```

**Explanation:** Creates a temporary sink, logs a message, then removes the sink. Subsequent logs won't be written to that sink. Returns True if removal was successful.

**Expected Output:**
```
Removed: True
```

---

### logger.remove_all()

Remove all logging sinks.

#### Signature

```python
logger.remove_all() -> int
```

#### Returns

- **Type:** `int`
- **Description:** Number of sinks removed.

#### Example

```python
from logly import logger

logger.add("app.log")
logger.add("error.log")
logger.add("console")

count = logger.remove_all()
print(f"Removed {count} sinks")  # 3

logger.info("This log goes nowhere")
```

**Explanation:** Removes all active sinks at once. Returns the count of sinks removed. After removal, logs are discarded until new sinks are added. Useful for cleanup or reconfiguration.

**Expected Output:**
```
Removed 3 sinks
```

---

### logger.sink_count()

Get number of active sinks.

#### Signature

```python
logger.sink_count() -> int
```

#### Returns

- **Type:** `int`
- **Description:** Total number of active sinks.

#### Example

```python
from logly import logger

logger.add("app.log")
logger.add("error.log")
logger.add("console")

count = logger.sink_count()
print(f"Active sinks: {count}")  # 3

logger.remove_all()
count = logger.sink_count()
print(f"Active sinks: {count}")  # 0
```

**Explanation:** Returns the number of currently active sinks. Useful for debugging configuration or ensuring expected number of outputs. Changes dynamically as sinks are added or removed.

**Expected Output:**
```
Active sinks: 3
Active sinks: 0
```

---

### logger.list_sinks()

List all sink handler IDs.

#### Signature

```python
logger.list_sinks() -> list[int]
```

#### Returns

- **Type:** `list[int]`
- **Description:** List of handler IDs for all active sinks.

#### Example

```python
from logly import logger

id1 = logger.add("app.log")
id2 = logger.add("error.log")
id3 = logger.add("console")

ids = logger.list_sinks()
print(f"Sink IDs: {ids}")  # [1, 2, 3]

# Remove one sink
logger.remove(id2)
ids = logger.list_sinks()
print(f"Sink IDs: {ids}")  # [1, 3]
```

**Explanation:** Returns all handler IDs for active sinks. Useful for iterating over sinks, selective removal, or debugging. IDs are assigned sequentially starting from 1.

**Expected Output:**
```
Sink IDs: [1, 2, 3]
Sink IDs: [1, 3]
```

---

### logger.sink_info()

Get detailed information about a specific sink.

#### Signature

```python
logger.sink_info(handler_id: int) -> dict | None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `handler_id` | `int` | Handler ID to query. |

#### Returns

- **Type:** `dict | None`
- **Description:** Dictionary with sink configuration, or `None` if not found.

#### Response Fields Table

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Handler ID |
| `path` | `str` | File path or `"console"` |
| `rotation` | `str \| None` | Rotation policy |
| `size_limit` | `str \| None` | Size rotation limit |
| `retention` | `int \| None` | Files to retain |
| `filter_min_level` | `str \| None` | Level filter |
| `filter_module` | `str \| None` | Module filter |
| `filter_function` | `str \| None` | Function filter |
| `async_write` | `bool` | Async enabled |
| `buffer_size` | `int` | Buffer size (bytes) |
| `flush_interval` | `int` | Flush interval (ms) |
| `max_buffered_lines` | `int` | Max buffered lines |
| `format` | `str \| None` | Custom format |
| `json` | `bool` | JSON output |
| `date_enabled` | `bool` | Timestamps enabled |
| `date_style` | `str \| None` | Timestamp format |

#### Example

```python
from logly import logger

id = logger.add("app.log", rotation="daily", async_write=True)

info = logger.sink_info(id)
print(f"Path: {info['path']}")
print(f"Rotation: {info['rotation']}")
print(f"Async: {info['async_write']}")
```

**Explanation:** Returns a dictionary with all configuration details for a specific sink. Useful for debugging, auditing, or dynamically adjusting behavior based on sink configuration.

**Expected Output:**
```
Path: app.log
Rotation: daily
Async: True
```

---

### logger.all_sinks_info()

Get information about all sinks.

#### Signature

```python
logger.all_sinks_info() -> list[dict]
```

#### Returns

- **Type:** `list[dict]`
- **Description:** List of dictionaries with sink configurations (same format as `sink_info()`).

#### Example

```python
from logly import logger

logger.add("app.log", rotation="daily")
logger.add("error.log", filter_min_level="ERROR", json=True)

for sink in logger.all_sinks_info():
    print(f"{sink['path']}: rotation={sink['rotation']}, json={sink['json']}")
```

**Explanation:** Returns a list of dictionaries, one for each sink, containing complete configuration. Perfect for logging system introspection or generating configuration reports.

**Expected Output:**
```
app.log: rotation=daily, json=False
error.log: rotation=None, json=True
```

---

## File Operations Methods

### logger.delete()

Delete log file for a specific sink (keeps sink active).

#### Signature

```python
logger.delete(handler_id: int) -> bool
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `handler_id` | `int` | Sink handler ID. |

#### Returns

- **Type:** `bool`
- **Description:** `True` if file deleted, `False` if failed or sink not found.

#### Example

```python
from logly import logger

id = logger.add("app.log")
logger.info("Some logs")

success = logger.delete(id)  # Deletes file, sink remains
print(f"Deleted: {success}")  # True

logger.info("Creates new file")  # New app.log created
```

**Explanation:** Deletes the physical log file but keeps the sink configuration active. The next log message will create a fresh file. Useful for clearing old logs without reconfiguring sinks.

**Expected Output:**
```
Deleted: True
```

#### Behavior

- ✅ Deletes the log file
- ✅ Sink remains active
- ✅ Next log creates new file
- ❌ Does not remove sink configuration

---

### logger.delete_all()

Delete all log files (keeps sinks active).

#### Signature

```python
logger.delete_all() -> int
```

#### Returns

- **Type:** `int`
- **Description:** Number of files deleted.

#### Example

```python
from logly import logger

logger.add("app.log")
logger.add("error.log")
logger.info("Logs")

count = logger.delete_all()
print(f"Deleted {count} files")  # 2

logger.info("Fresh start")  # Creates new files
```

**Explanation:** Deletes all log files while keeping sinks active. Useful for log rotation, testing, or starting fresh without reconfiguring. Sinks will create new files on next write.

**Expected Output:**
```
Deleted 2 files
```

---

### logger.read()

Read log content from a sink's file.

#### Signature

```python
logger.read(handler_id: int) -> str | None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `handler_id` | `int` | Sink handler ID. |

#### Returns

- **Type:** `str | None`
- **Description:** File contents as string, or `None` if file doesn't exist or sink not found.

#### Example

```python
from logly import logger

id = logger.add("app.log")
logger.info("Message 1")
logger.info("Message 2")

content = logger.read(id)
print(content)
```

**Explanation:** Returns the entire content of a sink's log file as a string. Useful for programmatic log analysis, testing, or displaying logs in UI. Returns None if file doesn't exist.

**Expected Output:**
```
2025-01-15 14:30:45 | INFO     | __main__:main:4 - Message 1
2025-01-15 14:30:46 | INFO     | __main__:main:5 - Message 2
```

---

### logger.read_all()

Read log content from all sinks.

#### Signature

```python
logger.read_all() -> dict[int, str]
```

#### Returns

- **Type:** `dict[int, str]`
- **Description:** Dictionary mapping handler IDs to file contents.

#### Example

```python
from logly import logger

id1 = logger.add("app.log")
id2 = logger.add("error.log", filter_min_level="ERROR")
logger.info("Info message")
logger.error("Error message")

all_logs = logger.read_all()
for sink_id, content in all_logs.items():
    print(f"Sink {sink_id}:\n{content}\n")
```

**Explanation:** Reads content from all sink files and returns a dictionary mapping handler IDs to file contents. Great for aggregating logs or exporting all logging data at once.

**Expected Output:**
```
Sink 1:
2025-01-15 14:30:45 | INFO     | __main__:main:5 - Info message
2025-01-15 14:30:46 | ERROR    | __main__:main:6 - Error message

Sink 2:
2025-01-15 14:30:46 | ERROR    | __main__:main:6 - Error message

```

---

### logger.file_size()

Get file size in bytes.

#### Signature

```python
logger.file_size(handler_id: int) -> int | None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `handler_id` | `int` | Sink handler ID. |

#### Returns

- **Type:** `int | None`
- **Description:** File size in bytes, or `None` if file doesn't exist.

#### Example

```python
from logly import logger

id = logger.add("app.log")
logger.info("Hello world")

size = logger.file_size(id)
print(f"Log file is {size} bytes")
```

**Explanation:** Returns the file size in bytes. Useful for monitoring log growth, implementing custom rotation logic, or checking if logs are being written. Returns None if file doesn't exist.

**Expected Output:**
```
Log file is 78 bytes
```

---

### logger.file_metadata()

Get detailed file metadata.

#### Signature

```python
logger.file_metadata(handler_id: int) -> dict | None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `handler_id` | `int` | Sink handler ID. |

#### Returns

- **Type:** `dict | None`
- **Description:** Dictionary with metadata fields, or `None` if file doesn't exist.

#### Metadata Fields Table

| Field | Type | Description |
|-------|------|-------------|
| `size` | `int` | File size in bytes |
| `created` | `str` | Creation timestamp (ISO 8601) |
| `modified` | `str` | Last modified timestamp (ISO 8601) |
| `path` | `str` | Absolute file path |

#### Example

```python
from logly import logger

id = logger.add("app.log")
logger.info("Test")

metadata = logger.file_metadata(id)
print(f"Size: {metadata['size']} bytes")
print(f"Created: {metadata['created']}")
print(f"Modified: {metadata['modified']}")
print(f"Path: {metadata['path']}")
```

**Explanation:** Returns comprehensive file metadata including size, timestamps, and absolute path. Perfect for monitoring, auditing, or displaying file information in dashboards.

**Expected Output:**
```
Size: 65 bytes
Created: 2025-01-15T14:30:45.123Z
Modified: 2025-01-15T14:30:45.456Z
Path: E:\Projects\logly\app.log
```

---

### logger.read_lines()

Read specific lines from a log file.

#### Signature

```python
logger.read_lines(handler_id: int, start: int, end: int) -> str | None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `handler_id` | `int` | Sink handler ID. |
| `start` | `int` | Starting line (1-indexed). Negative for end-relative (e.g., `-5` = 5th from end). |
| `end` | `int` | Ending line (inclusive). Negative for end-relative (e.g., `-1` = last line). |

#### Returns

- **Type:** `str | None`
- **Description:** Selected lines as string, or `None` if file doesn't exist.

#### Examples

=== "Read First Lines"

    ```python
    from logly import logger

    id = logger.add("app.log")
    for i in range(20):
        logger.info(f"Message {i}")

    # Read first 5 lines
    lines = logger.read_lines(id, 1, 5)
    print(lines)
    ```

    **Explanation:** Reads lines 1 through 5 from the log file. Line numbers are 1-indexed. Perfect for previewing the start of log files without loading the entire file.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | INFO     | __main__:main:5 - Message 0
    2025-01-15 14:30:45 | INFO     | __main__:main:5 - Message 1
    2025-01-15 14:30:45 | INFO     | __main__:main:5 - Message 2
    2025-01-15 14:30:45 | INFO     | __main__:main:5 - Message 3
    2025-01-15 14:30:45 | INFO     | __main__:main:5 - Message 4
    ```

=== "Read Last Lines"

    ```python
    # Read last 3 lines
    lines = logger.read_lines(id, -3, -1)
    print(lines)
    ```

    **Explanation:** Negative indices count from the end. -3 is the 3rd line from the end, -1 is the last line. Great for tailing logs or showing recent errors.

    **Expected Output:**
    ```
    2025-01-15 14:30:46 | INFO     | __main__:main:5 - Message 17
    2025-01-15 14:30:46 | INFO     | __main__:main:5 - Message 18
    2025-01-15 14:30:46 | INFO     | __main__:main:5 - Message 19
    ```

=== "Read Middle Lines"

    ```python
    # Read lines 10-15
    lines = logger.read_lines(id, 10, 15)
    print(lines)
    ```

    **Explanation:** Reads a specific range of lines (10 through 15). Useful for pagination, extracting specific log sections, or analyzing particular time periods.

---

### logger.line_count()

Count lines in a log file.

#### Signature

```python
logger.line_count(handler_id: int) -> int | None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `handler_id` | `int` | Sink handler ID. |

#### Returns

- **Type:** `int | None`
- **Description:** Number of lines in file, or `None` if file doesn't exist.

#### Example

```python
from logly import logger

id = logger.add("app.log")
logger.info("Line 1")
logger.info("Line 2")
logger.info("Line 3")

count = logger.line_count(id)
print(f"Lines: {count}")  # 3
```

**Explanation:** Returns the total number of lines in the log file. Perfect for monitoring log volume, implementing pagination, or detecting unexpected log growth.

**Expected Output:**
```
Lines: 3
```

---

### logger.read_json()

Read and parse JSON log file.

#### Signature

```python
logger.read_json(handler_id: int, pretty: bool = False) -> str | None
```

#### Parameters Table

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `handler_id` | `int` | - | Sink handler ID. |
| `pretty` | `bool` | `False` | Pretty-print JSON with indentation. |

#### Returns

- **Type:** `str | None`
- **Description:** JSON-formatted string, or `None` if file doesn't exist.

#### Examples

=== "Compact JSON"

    ```python
    from logly import logger

    id = logger.add("app.log", json=True)
    logger.info("Test", user="alice", action="login")

    json_logs = logger.read_json(id)
    print(json_logs)
    ```

    **Explanation:** Reads JSON log file and returns it as a string. Each line is a separate JSON object (NDJSON format). Great for feeding into JSON parsers or analytics tools.

    **Expected Output:**
    ```json
    {"timestamp":"2025-01-15T14:30:45.123Z","level":"INFO","module":"__main__","function":"main","message":"Test","user":"alice","action":"login"}
    ```

=== "Pretty JSON"

    ```python
    pretty_logs = logger.read_json(id, pretty=True)
    print(pretty_logs)
    ```

    **Explanation:** Pretty-prints the JSON with indentation for human readability. Each log entry is formatted with newlines and indents. Useful for debugging or displaying in UIs.

    **Expected Output:**
    ```json
    {
      "timestamp": "2025-01-15T14:30:45.123Z",
      "level": "INFO",
      "module": "__main__",
      "function": "main",
      "message": "Test",
      "user": "alice",
      "action": "login"
    }
    ```

---

### logger.clear()

Clear console display.

#### Signature

```python
logger.clear() -> None
```

#### Returns

- **Type:** `None`
- **Description:** Clears terminal screen (platform-specific).

#### Example

```python
from logly import logger

logger.add("console")
logger.info("Message 1")
logger.info("Message 2")
logger.clear()  # Clears console
logger.info("Message 3")
```

**Explanation:** Clears the terminal screen using platform-specific commands (cls on Windows, clear on Unix). Useful for resetting console output during development or interactive sessions.

**Expected Behavior:** Console is cleared, then "Message 3" appears as the first visible log.

#### Platform Behavior

| Platform | Command |
|----------|---------|
| Windows | `cls` |
| Unix/Linux/macOS | `clear` |

---

## Logging Methods

### logger.trace()

Log at TRACE level (most verbose).

#### Signature

```python
logger.trace(message: str, *args, **kwargs) -> None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Log message. Can include `%s`, `%d` placeholders for `args`. |
| `*args` | `Any` | Positional arguments for message formatting. |
| `**kwargs` | `Any` | Extra fields added to log record (e.g., `user="alice"`). |

#### Example

```python
from logly import logger

logger.configure(level="TRACE")
logger.add("console")

logger.trace("Detailed trace", request_id="abc123", step=1)
```

**Explanation:** TRACE is the most verbose level, typically used for very detailed debugging. Requires configuring level to TRACE to see these logs.

**Expected Output:**
```
2025-01-15 14:30:45 | TRACE    | __main__:main:5 - Detailed trace request_id=abc123 step=1
```

**Use Case:** Very detailed debugging, function entry/exit, variable inspection.

---

### logger.debug()

Log at DEBUG level.

#### Signature

```python
logger.debug(message: str, *args, **kwargs) -> None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Log message. |
| `*args` | `Any` | Message formatting args. |
| `**kwargs` | `Any` | Extra fields. |

#### Example

```python
from logly import logger

logger.configure(level="DEBUG")
logger.add("console")

item_id = "item_42"
logger.debug("Processing item %s", item_id, user="alice", status="active")
```

**Explanation:** DEBUG level for development debugging. The %s placeholder is replaced with item_id value. Extra kwargs (user, status) are appended to the log.

**Expected Output:**
```
2025-01-15 14:30:45 | DEBUG    | __main__:main:6 - Processing item item_42 user=alice status=active
```

**Use Case:** Development debugging, state inspection, flow tracking.

---

### logger.info()

Log at INFO level.

#### Signature

```python
logger.info(message: str, *args, **kwargs) -> None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Log message. |
| `*args` | `Any` | Message formatting args. |
| `**kwargs` | `Any` | Extra fields. |

#### Example

```python
from logly import logger

logger.add("console")

logger.info("User logged in", user_id=42, ip="192.168.1.1")
```

**Explanation:** INFO level for general informational messages about normal operations. This is the default logging level for production.

**Expected Output:**
```
2025-01-15 14:30:45 | INFO     | __main__:main:5 - User logged in user_id=42 ip=192.168.1.1
```

**Use Case:** General information, normal operations, user actions.

---

### logger.success()

Log at SUCCESS level.

#### Signature

```python
logger.success(message: str, *args, **kwargs) -> None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Log message. |
| `*args` | `Any` | Message formatting args. |
| `**kwargs` | `Any` | Extra fields. |

#### Example

```python
from logly import logger

logger.add("console")

logger.success("Payment processed", amount=100.50, transaction_id="tx123")
```

**Explanation:** SUCCESS level is unique to Logly, sitting between INFO and WARNING. Perfect for highlighting successful operations that deserve special attention.

**Expected Output:**
```
2025-01-15 14:30:45 | SUCCESS  | __main__:main:5 - Payment processed amount=100.5 transaction_id=tx123
```

**Use Case:** Successful operations, completion notifications, positive outcomes.

---

### logger.warning()

Log at WARNING level.

#### Signature

```python
logger.warning(message: str, *args, **kwargs) -> None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Log message. |
| `*args` | `Any` | Message formatting args. |
| `**kwargs` | `Any` | Extra fields. |

#### Example

```python
from logly import logger

logger.add("console")

logger.warning("Rate limit approaching", current=95, limit=100)
```

**Explanation:** WARNING level indicates potential issues that don't prevent normal operation but should be reviewed. Often colored yellow/orange.

**Expected Output:**
```
2025-01-15 14:30:45 | WARNING  | __main__:main:5 - Rate limit approaching current=95 limit=100
```

**Use Case:** Warnings, deprecated features, recoverable issues.

---

### logger.error()

Log at ERROR level.

#### Signature

```python
logger.error(message: str, *args, **kwargs) -> None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Log message. |
| `*args` | `Any` | Message formatting args. |
| `**kwargs` | `Any` | Extra fields. |

#### Example

```python
from logly import logger

logger.add("console")

logger.error("Database connection failed", db="postgres", retry=3)
```

**Explanation:** ERROR level for failures and exceptions. Use this for errors that prevent specific operations but don't crash the entire system.

**Expected Output:**
```
2025-01-15 14:30:45 | ERROR    | __main__:main:5 - Database connection failed db=postgres retry=3
```

**Use Case:** Errors, failures, exceptions (without traceback).

---

### logger.critical()

Log at CRITICAL level (most severe).

#### Signature

```python
logger.critical(message: str, *args, **kwargs) -> None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Log message. |
| `*args` | `Any` | Message formatting args. |
| `**kwargs` | `Any` | Extra fields. |

#### Example

```python
from logly import logger

logger.add("console")

logger.critical("System shutdown", reason="out_of_memory")
```

**Explanation:** CRITICAL is the highest severity level for catastrophic failures that require immediate attention. Often triggers alerts in production.

**Expected Output:**
```
2025-01-15 14:30:45 | CRITICAL | __main__:main:5 - System shutdown reason=out_of_memory
```

**Use Case:** Critical failures, system shutdown, data corruption.

---

### logger.log()

Log at custom or aliased level.

#### Signature

```python
logger.log(level: str, message: str, *args, **kwargs) -> None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `level` | `str` | Log level name (built-in or custom alias). |
| `message` | `str` | Log message. |
| `*args` | `Any` | Message formatting args. |
| `**kwargs` | `Any` | Extra fields. |

#### Example

```python
from logly import logger

logger.add("console")

# Create custom level alias
logger.level("NOTICE", "INFO")

# Use custom level
logger.log("NOTICE", "Custom message", priority=5)
```

**Explanation:** The log() method allows logging at custom or aliased levels. Here, NOTICE is aliased to INFO level, so it has INFO's severity but displays as NOTICE.

**Expected Output:**
```
2025-01-15 14:30:45 | NOTICE   | __main__:main:8 - Custom message priority=5
```

---

## Log Level Hierarchy

| Level | Numeric Value | Use Case |
|-------|---------------|----------|
| `TRACE` | 5 | Very detailed debugging, function traces |
| `DEBUG` | 10 | Development debugging, state inspection |
| `INFO` | 20 | General information, normal operations |
| `SUCCESS` | 25 | Successful operations, positive outcomes |
| `WARNING` | 30 | Warnings, deprecated features |
| `ERROR` | 40 | Errors, failures, exceptions |
| `CRITICAL` | 50 | Critical failures, system shutdown |

**Filtering:** When `filter_min_level="INFO"`, logs at INFO, SUCCESS, WARNING, ERROR, and CRITICAL are included. TRACE and DEBUG are excluded.

---

## Context Management Methods

### logger.bind()

Create logger with bound context fields.

#### Signature

```python
logger.bind(**kwargs) -> LoggerProxy
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `**kwargs` | `Any` | Key-value pairs to bind to all logs from this logger instance. |

#### Returns

- **Type:** `LoggerProxy`
- **Description:** New logger instance with bound context. All logs include these fields.

#### Examples

=== "Request Context"

    ```python
    from logly import logger

    logger.add("console")

    # Create request-scoped logger
    request_logger = logger.bind(request_id="abc123", user="alice")

    request_logger.info("Processing request")
    request_logger.info("Validating data")
    request_logger.info("Request complete")
    ```

    **Explanation:** Creates a new logger instance with request_id and user permanently bound. Every log from request_logger automatically includes these fields without re-specifying them. Perfect for web request tracking.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | INFO     | __main__:main:7 - Processing request request_id=abc123 user=alice
    2025-01-15 14:30:46 | INFO     | __main__:main:8 - Validating data request_id=abc123 user=alice
    2025-01-15 14:30:47 | INFO     | __main__:main:9 - Request complete request_id=abc123 user=alice
    ```

=== "Service Context"

    ```python
    # Service-level logger
    payment_logger = logger.bind(service="payment", version="2.0")

    payment_logger.info("Payment initiated", amount=100.50)
    payment_logger.success("Payment completed", transaction="tx123")
    ```

    **Explanation:** Binds service and version to all logs. Great for microservices where every log should identify which service produced it.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | INFO     | __main__:main:4 - Payment initiated service=payment version=2.0 amount=100.5
    2025-01-15 14:30:46 | SUCCESS  | __main__:main:5 - Payment completed service=payment version=2.0 transaction=tx123
    ```

=== "Nested Context"

    ```python
    # Create nested context
    app_logger = logger.bind(app="myapp", env="production")
    auth_logger = app_logger.bind(component="auth")

    auth_logger.info("User login")
    # Output: INFO: User login app=myapp env=production component=auth
    ```

    **Explanation:** Demonstrates context chaining. The auth_logger inherits bindings from app_logger (app, env) and adds its own (component). This creates hierarchical context perfect for complex applications.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | INFO     | __main__:main:5 - User login app=myapp env=production component=auth
    ```

#### Use Cases

- 🌐 **Request Tracking:** Bind request ID, user, session
- 🏗️ **Component Context:** Bind service name, version
- 👤 **User Context:** Bind user ID, role, tenant
- 🔧 **Environment Context:** Bind environment, region, instance

---

### logger.contextualize()

Temporarily attach context fields (context manager).

#### Signature

```python
logger.contextualize(**kwargs)
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `**kwargs` | `Any` | Temporary context fields for logs within the `with` block. |

#### Returns

- **Type:** Context manager
- **Description:** Context fields active only within `with` block.

#### Examples

=== "Temporary Context"

    ```python
    from logly import logger

    logger.add("console")

    logger.info("Before")  # No context

    with logger.contextualize(request_id="xyz789"):
        logger.info("During")  # Includes request_id

    logger.info("After")  # No context
    ```

    **Explanation:** Context fields are added only within the `with` block. Logs before and after the block don't have the request_id field. Perfect for temporary context that shouldn't persist.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | INFO     | __main__:main:5 - Before
    2025-01-15 14:30:46 | INFO     | __main__:main:8 - During request_id=xyz789
    2025-01-15 14:30:47 | INFO     | __main__:main:10 - After
    ```

=== "Nested Context"

    ```python
    with logger.contextualize(user="alice"):
        logger.info("Outer")  # user=alice
        
        with logger.contextualize(action="login"):
            logger.info("Inner")  # user=alice action=login
        
        logger.info("Back to outer")  # user=alice
    ```

    **Explanation:** Contexts can be nested. Inner contexts inherit fields from outer contexts and can add their own. When exiting inner context, only its fields are removed.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | INFO     | __main__:main:2 - Outer user=alice
    2025-01-15 14:30:46 | INFO     | __main__:main:5 - Inner user=alice action=login
    2025-01-15 14:30:47 | INFO     | __main__:main:7 - Back to outer user=alice
    ```

=== "Function Scope"

    ```python
    def process_payment(user_id, amount):
        with logger.contextualize(user_id=user_id, amount=amount):
            logger.info("Starting payment")
            # validate_payment()
            logger.success("Payment complete")

    process_payment("alice", 100.50)
    ```

    **Explanation:** Using contextualize() in function scope ensures all logs within the function have the function's parameters automatically attached. Great for tracing function execution.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | INFO     | __main__:process_payment:4 - Starting payment user_id=alice amount=100.5
    2025-01-15 14:30:46 | SUCCESS  | __main__:process_payment:6 - Payment complete user_id=alice amount=100.5
    ```

#### Bind vs Contextualize

| Feature | `bind()` | `contextualize()` |
|---------|----------|-------------------|
| **Scope** | Creates new logger | Temporary context |
| **Lifetime** | Persists until logger discarded | Only within `with` block |
| **Return** | New logger instance | Context manager |
| **Use Case** | Long-lived context (request, service) | Short-lived context (function, block) |

---

## Exception Handling Methods

### logger.exception()

Log exception with full traceback.

#### Signature

```python
logger.exception(message: str = "", **kwargs) -> None
```

#### Parameters Table

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | `str` | `""` | Optional message describing the exception. |
| `**kwargs` | `Any` | - | Extra fields to include in log. |

#### Returns

- **Type:** `None`
- **Description:** Logs at ERROR level with full traceback.

#### Examples

=== "Basic Exception Logging"

    ```python
    from logly import logger

    logger.add("console")

    try:
        result = 1 / 0
    except ZeroDivisionError:
        logger.exception("Math error occurred")
    ```

    **Explanation:** Automatically captures the active exception and logs it with full traceback. Must be called inside an except block. Logs at ERROR level by default.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | ERROR    | __main__:main:8 - Math error occurred
    Traceback (most recent call last):
      File "app.py", line 6, in <module>
        result = 1 / 0
                 ~~^~~
    ZeroDivisionError: division by zero
    ```

=== "Exception with Context"

    ```python
    try:
        amount = -100
        if amount < 0:
            raise ValueError("Amount must be positive")
    except ValueError as e:
        logger.exception("Payment validation failed", amount=amount, user="alice")
    ```

    **Explanation:** Extra kwargs (amount, user) are included in the log along with the traceback. This provides rich context for debugging exceptions.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | ERROR    | __main__:main:6 - Payment validation failed amount=-100 user=alice
    Traceback (most recent call last):
      File "app.py", line 4, in <module>
        raise ValueError("Amount must be positive")
    ValueError: Amount must be positive
    ```

=== "Exception in Request Handler"

    ```python
    def handle_request(request_id, data):
        try:
            if not data:
                raise ValueError("Empty data")
            # validate_data(data)
            # process_data(data)
        except Exception as e:
            logger.exception(
                "Request processing failed",
                request_id=request_id,
                error_type=type(e).__name__
            )
            raise

    handle_request("req-123", None)
    ```

    **Explanation:** Logs exception with context then re-raises it. This pattern allows centralized logging while still propagating errors for higher-level handling.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | ERROR    | __main__:handle_request:9 - Request processing failed request_id=req-123 error_type=ValueError
    Traceback (most recent call last):
      File "app.py", line 5, in handle_request
        raise ValueError("Empty data")
    ValueError: Empty data
    ```

#### Use Cases

- 🐛 **Debugging:** Full traceback for error investigation
- 📊 **Monitoring:** Track exception types and frequency
- 🔍 **Troubleshooting:** Context-rich error logs
- 🚨 **Alerting:** Trigger alerts on critical exceptions

---

### logger.catch()

Decorator and context manager to catch exceptions.

#### Signature

```python
logger.catch(
    exception: type[Exception] | tuple[type[Exception], ...] = Exception,
    level: str = "ERROR",
    reraise: bool = False,
    message: str = ""
)
```

#### Parameters Table

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `exception` | `type[Exception] \| tuple` | `Exception` | Exception type(s) to catch. |
| `level` | `str` | `"ERROR"` | Log level for caught exceptions. |
| `reraise` | `bool` | `False` | Re-raise exception after logging. |
| `message` | `str` | `""` | Custom message for caught exceptions. |

#### Returns

- **Type:** Decorator or context manager
- **Description:** Catches and logs exceptions automatically.

#### Examples

=== "Context Manager"

    ```python
    from logly import logger

    logger.add("console")

    with logger.catch():
        result = 1 / 0  # ZeroDivisionError
        print("This won't execute")
    
    print("Execution continues")
    ```

    **Explanation:** Catches all exceptions within the block, logs them, and suppresses them (reraise=False by default). Code execution continues after the with block.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | ERROR    | __main__:main:6 - Caught exception
    Traceback (most recent call last):
      File "app.py", line 6, in <module>
        result = 1 / 0
    ZeroDivisionError: division by zero
    Execution continues
    ```

=== "Decorator"

    ```python
    @logger.catch(reraise=True)
    def process_data(data):
        if not data:
            raise ValueError("No data provided")
        # transform(data)
        # save(data)
        return data
    
    try:
        process_data(None)
    except ValueError:
        print("Caught re-raised exception")
    ```

    **Explanation:** Decorator logs exceptions from the entire function. With reraise=True, exceptions are logged AND propagated, allowing calling code to handle them.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | ERROR    | __main__:process_data:3 - Exception in function
    Traceback (most recent call last):
      File "app.py", line 3, in process_data
        raise ValueError("No data provided")
    ValueError: No data provided
    Caught re-raised exception
    ```

=== "Specific Exception Types"

    ```python
    @logger.catch(exception=(ValueError, TypeError), level="WARNING")
    def parse_input(value):
        return int(value)
    
    result1 = parse_input("abc")  # ValueError caught and logged at WARNING
    result2 = parse_input(123)    # TypeError caught and logged at WARNING
    print(f"Results: {result1}, {result2}")  # Both None (suppressed exceptions)
    ```

    **Explanation:** Only catches specified exception types (ValueError, TypeError). Other exceptions propagate normally. Logs at WARNING level instead of ERROR.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | WARNING  | __main__:parse_input:3 - Exception caught
    Traceback (most recent call last):
      File "app.py", line 3, in parse_input
        return int(value)
    ValueError: invalid literal for int() with base 10: 'abc'
    2025-01-15 14:30:46 | WARNING  | __main__:parse_input:3 - Exception caught
    Traceback (most recent call last):
      File "app.py", line 3, in parse_input
        return int(value)
    TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'
    Results: None, None
    ```

=== "Custom Message"

    ```python
    with logger.catch(message="Database operation failed"):
        # db.connect()
        raise ConnectionError("Could not connect")
    ```

    **Explanation:** Custom message appears in the log instead of generic "Exception caught". Helps identify which catch block triggered.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | ERROR    | __main__:main:3 - Database operation failed
    Traceback (most recent call last):
      File "app.py", line 3, in <module>
        raise ConnectionError("Could not connect")
    ConnectionError: Could not connect
    ```

#### Decorator vs Context Manager

| Usage | Syntax | Use Case |
|-------|--------|----------|
| **Decorator** | `@logger.catch()` | Protect entire function |
| **Context Manager** | `with logger.catch():` | Protect specific block |
| **Reraise** | `reraise=True` | Log and propagate |
| **Suppress** | `reraise=False` | Log and suppress |

---

## Callback Methods

### logger.add_callback()

Register callback function for log messages.

#### Signature

```python
logger.add_callback(callback: callable) -> int
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `callback` | `callable` | Function with signature `(record: dict) -> None`. Called for each log message. |

#### Returns

- **Type:** `int`
- **Description:** Callback ID for later removal.

#### Callback Record Fields

| Field | Type | Description |
|-------|------|-------------|
| `level` | `str` | Log level (`"INFO"`, `"ERROR"`, etc.) |
| `message` | `str` | Log message text |
| `timestamp` | `str` | ISO 8601 timestamp |
| Extra fields | `Any` | All `kwargs` from log call |

#### Examples

=== "Error Alerting"

    ```python
    from logly import logger

    logger.add("console")

    def alert_on_error(record):
        if record.get("level") == "ERROR":
            print(f"🚨 ALERT: {record['message']}")
            # send_email(admin_email, record)

    callback_id = logger.add_callback(alert_on_error)

    logger.info("Normal log")  # No alert
    logger.error("Database failed", retry=3)  # Triggers alert
    ```

    **Explanation:** Callback is invoked for every log message. It checks the level and triggers alerts for errors. Great for real-time monitoring and notification systems.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | INFO     | __main__:main:13 - Normal log
    🚨 ALERT: Database failed
    2025-01-15 14:30:46 | ERROR    | __main__:main:14 - Database failed retry=3
    ```

=== "Metrics Collection"

    ```python
    error_count = 0

    def count_errors(record):
        global error_count
        if record.get("level") in ["ERROR", "CRITICAL"]:
            error_count += 1

    logger.add_callback(count_errors)

    logger.info("Info log")
    logger.error("Error 1")
    logger.error("Error 2")
    logger.critical("Critical error")
    print(f"Total errors: {error_count}")  # 3
    ```

    **Explanation:** Callbacks can maintain state and collect metrics. This example counts ERROR and CRITICAL logs, useful for real-time dashboards or alerting thresholds.

    **Expected Output:**
    ```
    Total errors: 3
    ```

=== "Custom Formatting"

    ```python
    def custom_format(record):
        level = record.get("level")
        message = record.get("message")
        timestamp = record.get("timestamp", "unknown")
        
        print(f"[{timestamp}] {level}: {message}")

    logger.add_callback(custom_format)
    logger.info("Custom formatted log")
    ```

    **Explanation:** Callbacks can implement completely custom formatting logic. This example extracts fields and prints in a custom format, useful for integration with third-party systems.

    **Expected Output:**
    ```
    [2025-01-15T14:30:45.123Z] INFO: Custom formatted log
    ```

=== "Conditional Processing"

    ```python
    payments_db = []

    def process_payment_logs(record):
        if record.get("event_type") == "payment":
            amount = record.get("amount")
            user = record.get("user")
            payments_db.append({"user": user, "amount": amount})

    logger.add_callback(process_payment_logs)
    
    logger.info("Payment received", event_type="payment", amount=100, user="alice")
    logger.info("User login", event_type="auth", user="bob")  # Not processed
    
    print(f"Payments: {payments_db}")
    ```

    **Explanation:** Callbacks can filter logs by fields and process specific types. This example only processes payment events, useful for event-driven architectures or specialized log routing.

    **Expected Output:**
    ```
    Payments: [{'user': 'alice', 'amount': 100}]
    ```

#### Use Cases

- 🚨 **Alerting:** Send notifications for errors
- 📊 **Metrics:** Collect statistics from logs
- 💾 **Storage:** Send logs to external systems
- 🎨 **Formatting:** Custom output formatting
- 🔍 **Filtering:** Process specific log types

---

### logger.remove_callback()

Remove callback by ID.

#### Signature

```python
logger.remove_callback(callback_id: int) -> bool
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `callback_id` | `int` | Callback ID returned by `add_callback()`. |

#### Returns

- **Type:** `bool`
- **Description:** `True` if removed, `False` if ID not found.

#### Example

```python
from logly import logger

logger.add("console")

def my_callback(record):
    print(f"📝 Callback: {record['message']}")

callback_id = logger.add_callback(my_callback)
logger.info("With callback")

logger.remove_callback(callback_id)
logger.info("Without callback")
```

**Explanation:** Removes a callback by its ID. After removal, the callback is no longer invoked for new logs. Returns True if removed successfully.

**Expected Output:**
```
📝 Callback: With callback
2025-01-15 14:30:45 | INFO     | __main__:main:9 - With callback
2025-01-15 14:30:46 | INFO     | __main__:main:12 - Without callback
```

---

## Utility Methods

### logger.enable()

Enable logging (resume after `disable()`).

#### Signature

```python
logger.enable() -> None
```

#### Example

```python
from logly import logger

logger.add("console")

logger.disable()
logger.info("Not logged")

logger.enable()
logger.info("Logged")
```

**Explanation:** Re-enables logging after it was disabled. All log calls after enable() will be processed normally.

**Expected Output:**
```
2025-01-15 14:30:45 | INFO     | __main__:main:8 - Logged
```

---

### logger.disable()

Disable logging temporarily.

#### Signature

```python
logger.disable() -> None
```

#### Example

```python
from logly import logger

logger.add("console")

logger.info("Logged")

logger.disable()
logger.info("Not logged")
logger.error("Not logged either")

logger.enable()
logger.info("Logged again")
```

**Explanation:** Temporarily disables all logging. No logs are written to any sink while disabled. Useful for suppressing logs during specific operations or tests.

**Expected Output:**
```
2025-01-15 14:30:45 | INFO     | __main__:main:5 - Logged
2025-01-15 14:30:48 | INFO     | __main__:main:12 - Logged again
```

#### Use Cases

- 🧪 **Testing:** Silence logs during tests
- 🎛️ **Feature Flags:** Conditional logging
- 🔇 **Quiet Mode:** Suppress logs temporarily

---

### logger.complete()

Flush all pending async writes to disk.

#### Signature

```python
logger.complete() -> None
```

#### Returns

- **Type:** `None`
- **Description:** Blocks until all buffered logs are written to files.

#### Examples

=== "Before Shutdown"

    ```python
    from logly import logger
    import sys

    logger.add("app.log", async_write=True)
    logger.info("Final message")
    logger.complete()  # Ensure all written
    # sys.exit(0)
    ```

    **Explanation:** Flushes all buffered logs to disk before shutdown. Critical for ensuring no logs are lost when the program exits, especially with async writes enabled.

    **Use Case:** Always call before sys.exit(), os._exit(), or process termination.

=== "Before Reading Logs"

    ```python
    id = logger.add("app.log", async_write=True)
    logger.info("Important message")

    logger.complete()  # Flush before reading
    content = logger.read(id)
    print(f"Content: {content[:50]}...")  # First 50 chars
    ```

    **Explanation:** With async writes, logs may still be buffered when you try to read. Call complete() to ensure all logs are written before reading the file.

    **Expected Output:**
    ```
    Content: 2025-01-15 14:30:45 | INFO     | __main__:main...
    ```

=== "Test Cleanup"

    ```python
    def test_logging():
        logger.info("Test message")
        logger.complete()  # Ensure written
        assert "Test message" in logger.read(log_id)
    ```

#### Use Cases

- 🚪 **Shutdown:** Flush before exit
- 📖 **Reading:** Ensure data written before read
- 🧪 **Testing:** Deterministic log writes
- 💾 **Checkpointing:** Force persistence

---

### logger.level()

Register custom level alias.

#### Signature

```python
logger.level(name: str, mapped_to: str) -> None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | New level name (alias). |
| `mapped_to` | `str` | Existing level to map to. |

#### Returns

- **Type:** `None`
- **Description:** Creates alias that can be used with `log()`.

#### Examples

=== "Custom Level Names"

    ```python
    from logly import logger

    logger.add("console")

    # Create aliases
    logger.level("NOTICE", "INFO")
    logger.level("FATAL", "CRITICAL")
    logger.level("VERBOSE", "DEBUG")

    logger.configure(level="DEBUG")  # Enable DEBUG and above

    # Use aliases
    logger.log("NOTICE", "Notice message")
    logger.log("FATAL", "Fatal error")
    logger.log("VERBOSE", "Verbose debug")
    ```

    **Explanation:** Creates custom level names that map to existing levels. NOTICE logs at INFO level, FATAL at CRITICAL, VERBOSE at DEBUG. Great for matching terminology from other logging systems.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | NOTICE   | __main__:main:12 - Notice message
    2025-01-15 14:30:46 | FATAL    | __main__:main:13 - Fatal error
    2025-01-15 14:30:47 | VERBOSE  | __main__:main:14 - Verbose debug
    ```

=== "Business Logic Levels"

    ```python
    # Business-specific levels
    logger.level("AUDIT", "INFO")
    logger.level("SECURITY", "WARNING")
    logger.level("COMPLIANCE", "INFO")

    logger.log("AUDIT", "User action", action="login", user="alice")
    logger.log("SECURITY", "Suspicious activity", ip="1.2.3.4")
    logger.log("COMPLIANCE", "Data access", resource="customers.db")
    ```

    **Explanation:** Create domain-specific log levels for business requirements. AUDIT and COMPLIANCE map to INFO, SECURITY maps to WARNING. Perfect for regulatory compliance and auditing.

    **Expected Output:**
    ```
    2025-01-15 14:30:45 | AUDIT      | __main__:main:6 - User action action=login user=alice
    2025-01-15 14:30:46 | SECURITY   | __main__:main:7 - Suspicious activity ip=1.2.3.4
    2025-01-15 14:30:47 | COMPLIANCE | __main__:main:8 - Data access resource=customers.db
    ```

#### Use Cases

- 📋 **Compliance:** Audit, security levels
- 🏢 **Business Logic:** Domain-specific levels
- 🔄 **Migration:** Match existing level names
- 🎨 **Clarity:** More descriptive level names

---

## Advanced Usage

### Custom Logger Instances

Create independent logger instances with different configurations.

#### Example

```python
from logly import logger, PyLogger

# Method 1: Using callable syntax (recommended)
custom_logger = logger(auto_update_check=False)
custom_logger.configure(level="DEBUG", color=False)

# Method 2: Using PyLogger directly
direct_logger = PyLogger(auto_update_check=False)
direct_logger.configure(level="DEBUG", color=False)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `auto_update_check` | `bool` | `True` | Enable automatic PyPI version check on startup. |

#### Use Cases

- 🔧 **Multiple Configs:** Different loggers for different components
- 🧪 **Testing:** Isolated logger per test
- 🚫 **No Version Check:** Disable for air-gapped environments

---

## Complete Workflow Example

```python
from logly import logger

# Step 1: Configure global settings
logger.configure(level="INFO", color=True, show_time=True)

# Step 2: Add sinks
app_log = logger.add("app.log", rotation="daily", retention=7)
error_log = logger.add("errors.log", filter_min_level="ERROR")
json_log = logger.add("data.log", json=True, async_write=True)

# Step 3: Create context logger
request_logger = logger.bind(request_id="abc123")

# Step 4: Log with context
request_logger.info("Processing request", user="alice")
request_logger.success("Request complete", duration_ms=150)

# Step 5: File operations
size = logger.file_size(app_log)
metadata = logger.file_metadata(app_log)
content = logger.read(app_log)
lines = logger.read_lines(app_log, 1, 10)

# Step 6: Sink management
sinks = logger.list_sinks()
info = logger.sink_info(app_log)
all_info = logger.all_sinks_info()

# Step 7: Exception handling
try:
    risky_operation()
except Exception:
    logger.exception("Operation failed", request_id="abc123")

# Step 8: Cleanup
logger.complete()      # Flush async writes
logger.delete_all()    # Delete files
logger.remove_all()    # Remove sinks
```

---

## Method Summary Table

| Category | Method | Description |
|----------|--------|-------------|
| **Configuration** | `configure()` | Set global logger settings |
| | `reset()` | Reset to defaults |
| **Sink Management** | `add()` | Add logging sink |
| | `remove()` | Remove sink by ID |
| | `remove_all()` | Remove all sinks |
| | `sink_count()` | Get sink count |
| | `list_sinks()` | List sink IDs |
| | `sink_info()` | Get sink details |
| | `all_sinks_info()` | Get all sink details |
| **File Operations** | `delete()` | Delete log file |
| | `delete_all()` | Delete all files |
| | `read()` | Read log file |
| | `read_all()` | Read all files |
| | `file_size()` | Get file size |
| | `file_metadata()` | Get file metadata |
| | `read_lines()` | Read specific lines |
| | `line_count()` | Count lines |
| | `read_json()` | Read JSON logs |
| | `clear()` | Clear console |
| **Logging** | `trace()` | Log at TRACE level |
| | `debug()` | Log at DEBUG level |
| | `info()` | Log at INFO level |
| | `success()` | Log at SUCCESS level |
| | `warning()` | Log at WARNING level |
| | `error()` | Log at ERROR level |
| | `critical()` | Log at CRITICAL level |
| | `log()` | Log at custom level |
| **Context** | `bind()` | Create context logger |
| | `contextualize()` | Temporary context |
| **Exceptions** | `exception()` | Log with traceback |
| | `catch()` | Catch and log exceptions |
| **Callbacks** | `add_callback()` | Register callback |
| | `remove_callback()` | Remove callback |
| **Utilities** | `enable()` | Enable logging |
| | `disable()` | Disable logging |
| | `complete()` | Flush pending writes |
| | `level()` | Register level alias |

**Total:** 40+ methods across 7 categories

---

## See Also

- **[Sink Management](sink-management.md)** - Detailed sink management with 20+ examples
- **[File Operations](file-operations.md)** - Comprehensive file operations guide
- **[Configuration Guide](../guides/configuration.md)** - Advanced configuration patterns
- **[Production Deployment](../guides/production-deployment.md)** - Production best practices
- **[Examples](../examples/index.md)** - Practical usage examples
