---
title: Template String Formatting - Logly Examples
description: Template string formatting example showing how to use format placeholders in Logly for custom log output.
keywords: python, logging, example, template, format, placeholders, custom, logly
---

# Template String Formatting

This example demonstrates how to use Logly's template string formatting feature to customize log output with placeholders. Template strings allow you to control exactly how your logs appear.

## Overview

Template strings support placeholders that are replaced with actual log data:

- **Built-in placeholders**: `{time}`, `{level}`, `{message}`
- **Extra field placeholders**: `{module}`, `{function}`, `{any_custom_field}`
- **Special placeholders**: `{extra}` (all remaining fields as key=value pairs)

All placeholders are case-insensitive.

## Code Example

```python
from logly import logger

# Configure logger
logger.configure(level="INFO")

# Example 1: Simple format
logger.add("console", format="{time} [{level}] {message}")
logger.info("Application started")

# Example 2: Detailed format with placeholders
logger.add(
    "logs/detailed.log",
    format="{time} | {level:8} | {module}:{function} | {message}"
)
logger.info("Processing request", user_id=123, endpoint="/api/users")

logger.complete() 
           user="charlie",
           module="myapp.api",
           function="handle_request")

# Read and display file content
with open(log_file, 'r', encoding='utf-8') as f:
    print(f"\nFile content:\n{f.read()}")

# Cleanup
logger.remove(1)
logger.remove(2)

# Example 7: Empty format (only message)
print("\n7. Message Only (no format):")
logger.add("console", format="{message}")
logger.info("Just the message, nothing else", extra_field="ignored_in_output")

print("\n" + "=" * 80)
print("Template formatting complete!")
print("=" * 80)

logger.complete()
```

## Expected Output

```
2025-01-15T14:32:10.123456+00:00 [INFO] Starting application
2025-01-15T14:32:10.125789+00:00 | INFO     | __main__:main | Processing request | user_id=123 | endpoint=/api/users
```

### What Happens

**First sink (console with simple format):**
- Shows time, level in brackets, and message
- Extra fields (user_id, endpoint) are automatically appended with `|` separator

**Second sink (file with detailed format):**
- Uses `{module}:{function}` to show where the log came from
- `{level:8}` pads the level name to 8 characters for alignment
- Extra fields are appended after the message

## Key Concepts

### Placeholder Rules

1. **Case-insensitive**: `{TIME}`, `{time}`, and `{Time}` all work the same
2. **Auto-append**: Extra fields not in the format are automatically appended
3. **Missing placeholders**: Unknown placeholders like `{unknown}` are left as-is
4. **Width specification**: `{level:8}` pads the level to 8 characters

### Common Patterns

**Simple console logging:**
```python
logger.add("console", format="{time} [{level}] {message}")
```

**Detailed file logging:**
```python
logger.add("app.log", format="{time} | {level:8} | {file}:{line} | {message} | {extra}")
```

**Structured JSON-like:**
```python
logger.add("structured.log", 
          format='{{"ts": "{time}", "lvl": "{level}", "msg": "{message}", "fields": {extra}}}')
```

**Request logging:**
```python
logger.add("requests.log",
          format="{time} | {method} {path} | status={status_code} | duration={duration_ms}ms | {extra}")
```

## Best Practices

1. **Console vs File**: Use simpler formats for console, detailed for files
2. **Include {extra}**: Always include `{extra}` to capture all context
3. **Consistent width**: Use `{level:8}` for aligned output
4. **JSON format**: Use proper JSON format for machine parsing
5. **Performance**: Simpler formats are slightly faster to process

## See Also

- [Configuration API](../api-reference/configuration.md#format-placeholders) - Complete placeholder reference
- [Multi-Sink Setup](multi-sink.md) - Using different formats for different outputs
- [JSON Logging](json-logging.md) - Structured JSON logging
