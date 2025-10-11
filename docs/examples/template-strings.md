---
title: Template String Formatting - Logly Examples
description: Template string formatting example showing how to use format placeholders in Logly for custom log output, including custom time format specifications.
keywords: python, logging, example, template, format, placeholders, custom, time format, datetime, logly
---

# Template String Formatting

This example demonstrates how to use Logly's template string formatting feature to customize log output with placeholders. Template strings allow you to control exactly how your logs appear.

## Overview

Template strings support placeholders that are replaced with actual log data:

- **Built-in placeholders**: `{time}`, `{level}`, `{message}`
- **Time format specs** (v0.1.6+): `{time:YYYY-MM-DD HH:mm:ss}` - Custom timestamp formatting
- **Extra field placeholders**: `{module}`, `{function}`, `{filename}`, `{lineno}`, `{any_custom_field}`
- **Special placeholders**: `{extra}` (all remaining fields as key=value pairs)

All placeholders are case-insensitive.

## Time Format Specifications (New in v0.1.6)

You can now customize timestamp formats using Loguru-style patterns:

### Supported Format Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| `YYYY` | 4-digit year | 2025 |
| `YY` | 2-digit year | 25 |
| `MMMM` | Full month name | October |
| `MMM` | Abbreviated month | Oct |
| `MM` | 2-digit month | 10 |
| `dddd` | Full weekday name | Saturday |
| `ddd` | Abbreviated weekday | Sat |
| `DD` | 2-digit day | 11 |
| `HH` | 2-digit hour (24h) | 13 |
| `hh` | 2-digit hour (12h) | 01 |
| `mm` | 2-digit minute | 45 |
| `ss` | 2-digit second | 32 |
| `SSS` | Milliseconds | 123 |
| `SSSSSS` | Microseconds | 123456 |
| `A` | AM/PM | AM |
| `a` | am/pm | am |
| `ZZ` | Timezone offset with colon | +00:00 |
| `Z` | Timezone offset | +0000 |

### Time Format Examples

```python
from logly import logger

# Date only
logger.add("logs/dates.log", format="{time:YYYY-MM-DD} | {level} | {message}")
logger.info("Date format example")
# Output: 2025-10-11 | INFO | Date format example

# Full datetime
logger.add("logs/datetime.log", format="{time:YYYY-MM-DD HH:mm:ss} [{level}] {message}")
logger.info("DateTime format")
# Output: 2025-10-11 13:45:32 [INFO] DateTime format

# With milliseconds
logger.add("logs/precise.log", format="{time:HH:mm:ss.SSS} | {message}")
logger.info("Precise timing")
# Output: 13:45:32.123 | Precise timing

# ISO 8601 style
logger.add("logs/iso.log", format="{time:YYYY-MM-DDTHH:mm:ss} {level} {message}")
logger.info("ISO format")
# Output: 2025-10-11T13:45:32 INFO ISO format

# Month names
logger.add("logs/readable.log", format="{time:DD MMM YYYY} | {message}")
logger.info("Readable date")
# Output: 11 Oct 2025 | Readable date

# European format
logger.add("logs/european.log", format="{time:DD/MM/YYYY HH:mm} {message}")
logger.info("European style")
# Output: 11/10/2025 13:45 European style

logger.complete()
```

## Code Example

```python
from logly import logger

# Configure logger with filename/lineno enabled
logger.configure(level="INFO", show_filename=True, show_lineno=True)

# Example 1: Simple format
logger.add("console", format="{time} [{level}] {message}")
logger.info("Application started")

# Example 2: Detailed format with placeholders
logger.add(
    "logs/detailed.log",
    format="{time} | {level:8} | {module}:{function} | {message}"
)
logger.info("Processing request", user_id=123, endpoint="/api/users")

# Example 3: Format with filename and line number
logger.add(
    "logs/debug.log",
    format="{level}: {filename}:{lineno} - {message}"
)
logger.info("Debug message with location info")

logger.info("Debug message with location info")

logger.complete()

# Read and display file contents
print("\nDetailed log content:")
with open("logs/detailed.log", 'r', encoding='utf-8') as f:
    print(f.read())

print("\nDebug log content:")
with open("logs/debug.log", 'r', encoding='utf-8') as f:
    print(f.read())

# Cleanup
logger.remove(1)
logger.remove(2)
logger.remove(3)
```

## Expected Output

```
2025-01-15T14:32:10.123456+00:00 [INFO] Starting application
2025-01-15T14:32:10.125789+00:00 | INFO     | __main__:main | Processing request | user_id=123 | endpoint=/api/users
INFO: template-strings.md:42 - Debug message with location info
```

### What Happens

**First sink (console with simple format):**
- Shows time, level in brackets, and message
- Extra fields (user_id, endpoint) are automatically appended with `|` separator

**Second sink (file with detailed format):**
- Uses `{module}:{function}` to show where the log came from
- `{level:8}` pads the level name to 8 characters for alignment
- Extra fields are appended after the message

**Third sink (file with filename:lineno format):**
- Uses `{filename}:{lineno}` to show the source location
- Only shows filename and lineno when `show_filename=True` and `show_lineno=True` are configured

## Key Concepts

### Placeholder Rules

1. **Case-insensitive**: `{TIME}`, `{time}`, and `{Time}` all work the same
2. **Auto-append**: Extra fields not in the format are automatically appended
3. **Missing placeholders**: Unknown placeholders like `{unknown}` are left as-is
4. **Width specification**: `{level:8}` pads the level to 8 characters

### Common Patterns

**Simple console logging:**
```python
logger.add("console", format="{time:HH:mm:ss} [{level}] {message}")
```

**Detailed file logging:**
```python
logger.add("app.log", format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:8} | {module}:{function} | {message} | {extra}")
```

**Structured JSON-like:**
```python
logger.add("structured.log", 
          format='{{"ts": "{time:YYYY-MM-DDTHH:mm:ss}", "lvl": "{level}", "msg": "{message}", "fields": "{extra}"}}')
```

**Request logging:**
```python
logger.add("requests.log",
          format="{time:YYYY-MM-DD HH:mm:ss} | {method} {path} | status={status_code} | duration={duration_ms}ms")
```

**Custom readable format:**
```python
logger.add("readable.log",
          format="{time:dddd, DD MMMM YYYY at HH:mm:ss} - {level} - {message}")
# Output: Saturday, 11 October 2025 at 13:45:32 - INFO - Application started
```

## Best Practices

1. **Console vs File**: Use simpler formats for console, detailed for files
2. **Include {extra}**: Use `{extra}` placeholder to explicitly capture all context fields
3. **Consistent width**: Use `{level:8}` for aligned output (note: format specs don't support width yet)
4. **Time formats**: Choose appropriate time format for your use case:
   - `HH:mm:ss` for console (quick reference)
   - `YYYY-MM-DD HH:mm:ss.SSS` for logs (precise timestamps)
   - `YYYY-MM-DDTHH:mm:ss` for ISO 8601 compatibility
5. **Performance**: Simpler formats are slightly faster to process
6. **Auto-append behavior**: Without `{extra}`, custom templates won't auto-append extra fields (v0.1.6+)

## See Also

- [Configuration API](../api-reference/configuration.md#format-placeholders) - Complete placeholder reference
- [Multi-Sink Setup](multi-sink.md) - Using different formats for different outputs
- [File Operations](../api-reference/file-operations.md) - Advanced file handling
