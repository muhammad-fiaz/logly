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

**NEW in v0.1.5**: The logger is automatically configured on import with default settings (`console=True`, `auto_sink=True`). This means you can start logging immediately without calling `configure()`. Calling `configure()` is optional and only needed if you want to customize the settings.

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
    show_filename: bool = False,
    show_lineno: bool = False,
    console_levels: dict[str, bool] | None = None,
    time_levels: dict[str, bool] | None = None,
    color_levels: dict[str, bool] | None = None,
    storage_levels: dict[str, bool] | None = None,
    color_callback: callable | None = None,
    auto_sink: bool = True,
    auto_sink_levels: dict[str, str | dict[str, str]] | None = None,
    log_compact: bool = False
) -> None
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level: `"TRACE"`, `"DEBUG"`, `"INFO"`, `"SUCCESS"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`, `"FAIL"` |
| `color` | `bool` | `True` | Enable colored console output. When True, uses ANSI escape codes for coloring unless color_callback is provided. When False, disables all coloring regardless of other settings. Default colors: TRACE=cyan, DEBUG=blue, INFO=white, SUCCESS=green, WARNING=yellow, ERROR=red, CRITICAL=bright_red, FAIL=magenta |
| `level_colors` | `dict[str, str] \| None` | `None` | Custom colors for each log level. Supports both ANSI color codes and color names. If `None`, uses default color mapping (see above). Custom colors override defaults |
| `json` | `bool` | `False` | Output logs in JSON format instead of text |
| `pretty_json` | `bool` | `False` | Pretty-print JSON output (higher cost, more readable) |
| `console` | `bool` | `True` | **Global enable/disable ALL logging** (kill-switch). When `True` (default), all logging is enabled across all sinks (console and file). When `False`, **ALL logging is disabled globally**, equivalent to calling `logger.disable()`. This is different from per-sink enable/disable which controls individual outputs |
| `show_time` | `bool` | `True` | Show timestamps in console output |
| `show_module` | `bool` | `True` | Show module information in console output |
| `show_function` | `bool` | `True` | Show function information in console output |
| `show_filename` | `bool` | `False` | Show filename information in console output |
| `show_lineno` | `bool` | `False` | Show line number information in console output |
| `console_levels` | `dict[str, bool] \| None` | `None` | Per-level console output control. Maps level names to enable/disable console output |
| `time_levels` | `dict[str, bool] \| None` | `None` | Per-level time display control. Maps level names to enable/disable timestamps |
| `color_levels` | `dict[str, bool] \| None` | `None` | Per-level color control. Maps level names to enable/disable colors |
| `storage_levels` | `dict[str, bool] \| None` | `None` | Per-level storage control. Maps level names to enable/disable file logging |
| `color_callback` | `callable \| None` | `None` | Custom color callback function with signature `(level: str, text: str) -> str`. When provided, overrides built-in ANSI coloring. Allows integration with external libraries like Rich, colorama, or termcolor for advanced coloring and styling |
| `auto_sink` | `bool` | `True` | **NEW in v0.1.5**: Automatically create a console sink if no sinks exist. Since v0.1.5, `configure()` is called automatically on import, so when `auto_sink=True` (default), a console sink is created immediately when you import the logger. This enables "import and log" workflow with zero configuration. Set to `False` if you want full manual control over sinks. **Note**: `auto_sink` only affects console sinks - file sinks are NEVER created automatically and must be added explicitly with `logger.add(file_path)` |
| `auto_sink_levels` | `dict[str, str \| dict[str, str]] \| None` | `None` | **NEW in v0.1.5**: Automatically configure per-level sinks using declarative configuration. Maps log level names to either sink type strings (`"console"`, `"file"`) or sink configuration dictionaries with `type` and `path` keys. See [Auto-Sink Levels Example](../examples/auto-sink-levels.md) for detailed usage |
| `log_compact` | `bool` | `False` | Enable compact log format for Jupyter/Colab environments. When True, logs use a more condensed format suitable for notebook outputs with limited space. Reduces verbosity while maintaining readability |

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

### Custom Color Callbacks

The `color_callback` parameter provides universal support for external color libraries and custom styling. When provided, it completely overrides logly's built-in ANSI coloring system.

#### Callback Signature

```python
def color_callback(level: str, text: str) -> str:
    """
    Custom color callback function.

    Args:
        level: Log level as string ("DEBUG", "INFO", "WARN", "ERROR", etc.)
        text: The fully formatted log message text

    Returns:
        The text with custom coloring/styling applied
    """
    # Your custom coloring logic here
    return styled_text
```

#### How It Works

1. **Precedence**: When `color_callback` is provided, it takes complete precedence over built-in ANSI coloring
2. **Integration**: Works with any color library (Rich, colorama, termcolor, etc.) - install libraries separately as needed
3. **Performance**: Callback is called for each log message that would be colored
4. **Flexibility**: Return any string - ANSI codes, Unicode styling, or plain text

#### Use Cases

- **External Libraries**: Integrate with Rich, colorama, or other coloring libraries (install separately)
- **Custom Styling**: Implement company-specific color schemes
- **Conditional Coloring**: Apply colors based on message content or context
- **Advanced Formatting**: Use Unicode box drawing, emojis, or special characters

### Returns

`None`

### Examples

=== "Default Colored Output (NEW v0.1.5)"

    ```python
    from logly import logger
    
    # Colors are automatic when color=True (default)
    logger.configure(color=True)
    
    # Each level gets its default color
    logger.trace("Trace message")      # Cyan
    logger.debug("Debug info")         # Blue
    logger.info("Information")         # White
    logger.success("Success!")         # Green
    logger.warning("Warning!")         # Yellow
    logger.error("Error occurred")     # Red
    logger.critical("Critical!")       # Bright Red
    logger.fail("Operation failed")    # Magenta (NEW)
    ```

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

=== "Custom Color Callback with Rich"

    **Note**: This example requires installing Rich separately: `pip install rich`

    ```python
    from rich.console import Console
    from logly import logger

    # Create a Rich console for coloring
    console = Console()

    def rich_color_callback(level, text):
        """Custom color callback using Rich library."""
        # Apply Rich markup based on level
        if level == "DEBUG":
            markup = f"[blue]{text}[/blue]"
        elif level == "INFO":
            markup = f"[green]{text}[/green]"
        elif level in ("WARN", "WARNING"):
            markup = f"[yellow]{text}[/yellow]"
        elif level == "ERROR":
            markup = f"[red]{text}[/red]"
        else:
            markup = text

        # Convert Rich markup to ANSI codes
        with console.capture() as capture:
            console.print(markup, end="")

        return capture.get()

    logger.configure(
        level="DEBUG",
        color_callback=rich_color_callback
    )
    logger.add("console")

    logger.debug("This is styled with Rich (blue)")
    logger.info("This is styled with Rich (green)")
    logger.warning("This is styled with Rich (yellow)")
    logger.error("This is styled with Rich (red)")
    ```

    **Explanation**: The `color_callback` parameter accepts a Python callable with signature `(level: str, text: str) -> str`. When provided, it completely overrides logly's built-in ANSI coloring. This example uses the Rich library to create advanced styling and converts Rich markup to ANSI escape codes for terminal display.

    **Expected Output** (with Rich styling converted to ANSI):
    ```
    [DEBUG] This is styled with Rich (blue)
    [INFO] This is styled with Rich (green)
    [WARN] This is styled with Rich (yellow)
    [ERROR] This is styled with Rich (red)
    ```

=== "Custom Color Callback with ANSI"

    ```python
    from logly import logger

    def ansi_color_callback(level, text):
        """Custom color callback using direct ANSI codes."""
        colors = {
            "DEBUG": "\033[34m",    # Blue
            "INFO": "\033[32m",     # Green
            "WARN": "\033[33m",     # Yellow
            "WARNING": "\033[33m",  # Yellow (alias)
            "ERROR": "\033[31m",    # Red
        }
        reset = "\033[0m"
        color_code = colors.get(level, "")
        return f"{color_code}{text}{reset}"

    logger.configure(
        level="DEBUG",
        color_callback=ansi_color_callback
    )
    logger.add("console")

    logger.debug("This is blue")
    logger.info("This is green")
    logger.warning("This is yellow")
    logger.error("This is red")
    ```

    **Explanation**: This example shows how to create a custom color callback using direct ANSI escape codes. The callback receives the log level and formatted text, then returns the text wrapped with appropriate ANSI color codes. This approach gives you complete control over coloring and works with any terminal that supports ANSI colors.

    **Expected Output** (with ANSI color codes):
    ```
    [DEBUG] This is blue
    [INFO] This is green
    [WARN] This is yellow
    [ERROR] This is red
    ```

    **Note**: The actual terminal display will show these messages in blue, green, yellow, and red respectively. The plain text above represents the logical output structure.

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

=== "Filename and Line Number Display Control"

    ```python
    from logly import logger

    # Show filename and line number info
    logger.configure(level="INFO", show_filename=True, show_lineno=True)
    logger.add("console")
    logger.info("Message with filename and lineno")

    # Hide filename and line number info (default)
    logger.configure(level="INFO", show_filename=False, show_lineno=False)
    logger.add("console")
    logger.info("Message without filename and lineno")

    # Show only filename, hide line number
    logger.configure(level="INFO", show_filename=True, show_lineno=False)
    logger.add("console")
    logger.info("Message with filename only")
    ```

=== "Rich Console Output with Color Callback"

    ```python
    from rich.console import Console
    from logly import logger

    # Create a Rich console for coloring
    console = Console()

    def rich_color_callback(level, text):
        """Custom color callback using Rich library for advanced styling."""
        # Apply Rich markup based on level with advanced styling
        if level == "DEBUG":
            markup = f"[dim blue]{text}[/dim blue]"
        elif level == "INFO":
            markup = f"[bold green]{text}[/bold green]"
        elif level in ("WARN", "WARNING"):
            markup = f"[bold yellow on red]{text}[/bold yellow on red]"
        elif level == "ERROR":
            markup = f"[bold red blink]{text}[/bold red blink]"
        else:
            markup = text

        # Convert Rich markup to ANSI codes
        with console.capture() as capture:
            console.print(markup, end="")

        return capture.get()

    logger.configure(
        level="INFO",
        color_callback=rich_color_callback
    )
    logger.add("console")

    logger.info("This uses Rich for advanced styling")
    logger.warning("Rich styling: bold yellow on red background")
    logger.error("Rich styling: bold red with blinking")
    ```

    The `color_callback` parameter allows integration with external libraries like Rich for advanced coloring and styling capabilities beyond basic ANSI colors.

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
    sink: str | None = None,
    *,
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

### Parameters

!!! info "Fixed Issue #77"
    Retention now works correctly with `size_limit`. When you set `retention=5`, 
    the library will keep exactly 5 files total (including the current one), 
    not 5 old files plus the current one.
    See [Issue #77](https://github.com/muhammad-fiaz/logly/issues/77) for details.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sink` | `str \| None` | `None` | `"console"` for stdout or file path for file output. Defaults to console. |
| `rotation` | `str \| None` | `None` | Time-based rotation: `"daily"`, `"hourly"`, `"minutely"`, `"never"` |
| `size_limit` | `str \| None` | `None` | Maximum file size before rotation. Supports: `"100"` (bytes), `"500B"` or `"500b"`, `"5KB"` or `"5kb"`, `"10MB"` or `"10mb"`, `"1GB"` or `"1gb"`, `"2TB"` or `"2tb"`. Case-insensitive, short forms (`"5K"`, `"10M"`, `"1G"`) also supported. |
| `retention` | `int \| None` | `None` | Number of total files to keep (including current). Works with both `rotation` and `size_limit`. Older files auto-deleted. |
| `filter_min_level` | `str \| None` | `None` | Exact log level for this sink: `"INFO"`, `"ERROR"`, etc. Only messages with this exact level will be logged to this sink |
| `filter_module` | `str \| None` | `None` | Only log from this module |
| `filter_function` | `str \| None` | `None` | Only log from this function |
| `async_write` | `bool` | `True` | Enable background async writing |
| `buffer_size` | `int` | `8192` | Buffer size in bytes for async writing |
| `flush_interval` | `int` | `100` | Flush interval in milliseconds for async writing |
| `max_buffered_lines` | `int` | `1000` | Maximum number of buffered lines before blocking |
| `date_style` | `str \| None` | `None` | Timestamp format: `"rfc3339"`, `"local"`, `"utc"` |
| `date_enabled` | `bool` | `False` | Include timestamp in log output |
| `format` | `str \| None` | `None` | **NEW in v0.1.6+**: Custom format string with placeholders like `"{level}"`, `"{message}"`, `"{time}"`, `"{extra}"`, or any extra field key. **Time Format Specifications** are now supported: use `{time:FORMAT}` to customize timestamp display with Loguru-style patterns (e.g., `{time:YYYY-MM-DD HH:mm:ss}`). Supported patterns: `YYYY`, `MM`, `DD`, `HH`, `mm`, `ss`, `SSS`, `MMMM`, `MMM`, `dddd`, `ddd`, `hh`, `A`, `a`, `ZZ`, `Z`, `zz`, `X`. See [Template Strings Documentation](../examples/template-strings.md) for complete pattern reference |
| `json` | `bool` | `False` | Format logs as JSON for this sink |

### How Rotation, Retention, and Size Limit Work Together

The `rotation`, `retention`, and `size_limit` parameters work together to provide flexible log file management. Here's how they interact:

#### Size-Based Rotation Only

When you specify `size_limit` without `rotation`, files rotate based on size alone:

```python
logger.add("logs/app.log", size_limit="5KB", retention=5)
```

**Behavior:**
- New rotation file created when current file reaches 5KB
- Keeps maximum of 5 total files (including current)
- Oldest files auto-deleted when limit exceeded
- Rotated files use timestamp naming: `app.2025-01-15_14-30-45.log`

#### Time-Based Rotation Only

When you specify `rotation` without `size_limit`, files rotate based on time:

```python
logger.add("logs/app.log", rotation="daily", retention=7)
```

**Behavior:**
- New file created at each rotation period (daily at midnight)
- Keeps maximum of 7 total files
- Older files auto-deleted beyond retention
- Rotated files use period naming: `app.2025-01-15.log`

#### Combined Time and Size Rotation

When both `rotation` and `size_limit` are specified, **BOTH conditions are checked** - file rotates on WHICHEVER comes first:

```python
logger.add("logs/app.log", rotation="daily", size_limit="100MB", retention=30)
```

**Behavior:**
- Rotates when: time period changes OR file reaches 100MB (whichever first)
- If size limit hit before midnight: creates `app.2025-01-15_14-30-45.log`
- If midnight reached first: creates `app.2025-01-16.log`
- Retention of 30 means keeps 30 most recent files total
- Both rotation triggers respected

#### Retention Behavior

The `retention` parameter always works the same way regardless of rotation type:

- **Counts total files** including the current active file
- **Deletes oldest files** when total exceeds retention limit
- **Works with both** time-based and size-based rotation
- **No retention** (default): files accumulate indefinitely

#### Common Patterns

**High-Volume Logs with Size Limits:**
```python
# Rotate every 500MB, keep only last 10 files
logger.add("logs/high_volume.log", size_limit="500MB", retention=10)
```

**Daily Logs with Size Safety:**
```python
# Rotate daily, but also if file exceeds 1GB
logger.add("logs/app.log", rotation="daily", size_limit="1GB", retention=30)
```

**Development (Small Retention):**
```python
# Keep only 3 most recent files
logger.add("logs/dev.log", size_limit="10MB", retention=3)
```

**Production (Large Retention):**
```python
# Keep 90 days of daily logs
logger.add("logs/prod.log", rotation="daily", retention=90)
```

**Error Logs (Size + Filter):**
```python
# Errors only, rotate at 100MB, keep 50 files
logger.add("logs/errors.log", 
          filter_min_level="ERROR", 
          size_limit="100MB", 
          retention=50)
```

!!! warning "Retention Edge Cases"
    - `retention=1`: Keeps only current file (deletes on rotation)
    - `retention=None` (default): No limit, files accumulate
    - Retention counts ALL matching files, not just rotated ones

!!! tip "Fixes Issue #77"
    Retention now correctly works with `size_limit`. When `retention=5` is set, 
    the system maintains **exactly 5 total files** (including current), deleting 
    the oldest when a new rotation is triggered.
    See [Issue #77](https://github.com/muhammad-fiaz/logly/issues/77).

### Returns

`int` - Handler ID for removing the sink later with `remove()`

### Format Placeholders

The `format` parameter supports template strings with placeholders that are replaced with actual log data. Placeholders are case-insensitive and enclosed in curly braces `{}`.

#### Built-in Placeholders

| Placeholder | Description | Example Output |
|-------------|-------------|----------------|
| `{time}` | Timestamp in ISO 8601 format | `2023-01-01T12:00:00Z` |
| `{level}` | Log level | `INFO`, `ERROR`, `DEBUG` |
| `{message}` | Log message text | `User logged in` |

#### Extra Fields Placeholders

| Placeholder | Description | Example Output |
|-------------|-------------|----------------|
| `{extra}` | All extra fields formatted as `key=value` pairs joined by ` \| ` | `user=alice \| session_id=12345` |
| `{module}` | Module name (if provided in extra fields) | `myapp.auth` |
| `{function}` | Function name (if provided in extra fields) | `login_user` |
| `{filename}` | Source filename (if provided in extra fields) | `app.py` |
| `{lineno}` | Line number (if provided in extra fields) | `42` |
| `{any_key}` | Any extra field key from the log record | Custom value |

#### Placeholder Behavior

- **Case-insensitive**: `{TIME}`, `{time}`, and `{Time}` all work the same
- **Extra fields**: Any key-value pair passed to the log call becomes available as a placeholder
- **Automatic appending**: If `{extra}` is not used in the format string, unused extra fields are automatically appended at the end of the log message
- **Missing placeholders**: Unmatched placeholders (e.g., `{unknown}`) are left as-is in the output

#### Examples

```python
import logly

# Basic placeholders
logger.add("console", format="{time} [{level}] {message}")

# Include specific extra fields
logger.add("console", format="{time} [{level}] {message} | user={user}")

# Use {extra} for all remaining fields
logger.add("console", format="{time} [{level}] {message} | {extra}")

# JSON format with {extra}
logger.add("logs/structured.log", 
           format='{{"timestamp": "{time}", "level": "{level}", "message": "{message}", "extra": {extra}}}')

logger.info("User action", user="alice", action="login", session_id="12345")
# Output: {"timestamp": "2023-01-01T12:00:00Z", "level": "INFO", "message": "User action", "extra": user=alice | action=login | session_id=12345}

# **NEW in v0.1.6+**: Time Format Specifications
# Customize timestamp display using Loguru-style patterns
logger.add("console", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
# Output: 2025-10-11 13:46:27 | INFO | User logged in

# Date-only format
logger.add("logs/daily.log", format="{time:YYYY-MM-DD} [{level}] {message}")
# Output: 2025-10-11 [INFO] Request processed

# Milliseconds precision
logger.add("logs/precise.log", format="{time:HH:mm:ss.SSS} {level} {message}")
# Output: 13:46:27.324 INFO Database query completed

# ISO 8601 format
logger.add("logs/api.log", format="{time:YYYY-MM-DDTHH:mm:ss} {level} {message}")
# Output: 2025-10-11T13:46:27 INFO API request

# Month names and 12-hour time
logger.add("console", format="{time:MMMM DD, YYYY hh:mm:ss A} - {message}")
# Output: October 11, 2025 01:46:27 PM - System initialized
```

**Supported Time Format Patterns** (v0.1.6+):
See [Template Strings Documentation](../examples/template-strings.md) for complete pattern reference including `YYYY`, `MM`, `DD`, `HH`, `mm`, `ss`, `SSS`, `MMMM`, `MMM`, `dddd`, `ddd`, `hh`, `A`, `a`, `ZZ`, `Z`, `zz`, `X`.

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
    
    # Various size formats (all case-insensitive):
    logger.add("logs/small.log", size_limit="100")      # 100 bytes
    logger.add("logs/tiny.log", size_limit="500B")      # 500 bytes
    logger.add("logs/kb.log", size_limit="5kb")         # 5 kilobytes (lowercase)
    logger.add("logs/mb.log", size_limit="10M")         # 10 megabytes (short form)
    logger.add("logs/gb.log", size_limit="1gb")         # 1 gigabyte (lowercase)
    logger.add("logs/huge.log", size_limit="2TB")       # 2 terabytes
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

=== "JSON Logging"

    ```python
    # JSON console output
    logger.add("console", json=True)
    
    # JSON file output
    logger.add("logs/app.jsonl", json=True)
    
    # JSON with rotation
    logger.add("logs/events.jsonl", json=True, rotation="daily", retention=30)
    ```
    
    JSON logging automatically formats all log data as structured JSON objects, including:
    - Timestamp in ISO 8601 format
    - Log level
    - Message text
    - All extra fields passed to the log call
    - Context from `.bind()` and `.contextualize()`

=== "Custom Format"

    ```python
    # Custom format with timestamp and level
    logger.add(
        "console",
        format="{time} [{level}] {message}"
    )
    
    # JSON format for structured logging
    logger.add(
        "logs/structured.log",
        format='{{"timestamp": "{time}", "level": "{level}", "message": "{message}", "extra": {extra}}}',
        date_enabled=True
    )
    
    # Simple format for debugging
    logger.add(
        "logs/debug.log",
        format="{level}: {message} {extra}",
        filter_min_level="DEBUG"
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

---

## Logger Initialization

### Creating Logger Instances

Logly supports creating multiple logger instances with different configurations:

```python
from logly import logger

# Method 1: Using callable syntax (recommended)
custom_logger = logger(auto_update_check=False)
custom_logger.configure(level="DEBUG", color=False)

# Method 2: Using PyLogger directly
from logly import PyLogger
direct_logger = PyLogger(auto_update_check=False)
direct_logger.configure(level="DEBUG", color=False)
```

### Automatic Version Checking

By default, Logly automatically checks for new versions on startup:

- **Enabled by default**: The global `logger` instance checks for updates
- **Asynchronous**: Version checks don't block logger operations
- **Network timeout**: 2-second timeout for version check requests
- **Error handling**: Network failures are silently ignored

To disable version checking:

```python
# Disable for specific instances
custom_logger = logger(auto_update_check=False)

# Or disable globally by creating a new instance
from logly import PyLogger
no_check_logger = PyLogger(auto_update_check=False)
```

!!! info "Version Check Behavior"
    - Checks PyPI for the latest version
    - Displays upgrade warnings to stderr if a newer version is available
    - Only runs once per process, even with multiple logger instances
    - Safe for air-gapped environments (fails gracefully)
