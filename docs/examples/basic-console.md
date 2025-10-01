---
title: Basic Console Logging - Logly Examples
description: Basic console logging example showing how to get started with Logly for simple console output with colored formatting.
keywords: python, logging, example, console, basic, colored, output, logly
---

# Basic Console Logging

This example demonstrates the simplest way to get started with Logly for console logging with beautiful colored output.

## Code Example

```python
from logly import logger

# Configure for console output with colors (console=True by default)
logger.configure(level="INFO", color=True, console=True)

# Log some messages
logger.info("Application started")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.debug("This debug message won't show (level is INFO)")

# Log with extra data
logger.info("User {user_id} logged in", user_id=12345)
logger.info("Processing {count} items", count=1000)
```

## Output

```
[INFO] Application started | module=__main__ | function=<module>
[WARN] This is a warning message | module=__main__ | function=<module>
[ERROR] This is an error message | module=__main__ | function=<module>
[INFO] User 12345 logged in | module=__main__ | function=<module>
[INFO] Processing 1000 items | module=__main__ | function=<module>
```

## Key Features Demonstrated

- **Simple setup**: Just import and configure
- **Colored output**: Automatic color coding by log level
- **Template strings**: Use `{variable}` syntax for formatting
- **Level filtering**: Only show messages at or above configured level
- **Console control**: Enable/disable console output with `console` parameter