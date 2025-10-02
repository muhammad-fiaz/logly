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

# Configure for console output with colors
logger.configure(level="INFO", color=True)

# Log some messages
logger.info("Application started")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.debug("This debug message won't show (level is INFO)")

# Log with extra data
logger.info("User logged in", user_id=12345)
logger.info("Processing items", count=1000, status="active")

logger.complete()
```

## Expected Output

```
2025-01-15T14:30:00.123456+00:00 [INFO] Application started
2025-01-15T14:30:00.124567+00:00 [WARN] This is a warning message
2025-01-15T14:30:00.125678+00:00 [ERROR] This is an error message
2025-01-15T14:30:00.126789+00:00 [INFO] User logged in | user_id=12345
2025-01-15T14:30:00.127890+00:00 [INFO] Processing items | count=1000 | status=active
```

### What Happens

1. **`logger.configure(level="INFO", color=True)`**:
   - Sets minimum log level to INFO (debug messages are filtered out)
   - Enables colored output for terminal (INFO=cyan, WARN=yellow, ERROR=red)
   - Console sink is added automatically

2. **The debug message doesn't appear**:
   - Because level is set to INFO, DEBUG logs are filtered
   - Only INFO, WARN, ERROR, and CRITICAL messages show

3. **Extra fields are appended**:
   - Fields like `user_id=12345` are automatically formatted
   - Multiple fields are separated by `|` characters

4. **Timestamps are included**:
   - ISO 8601 format with microsecond precision
   - Timezone aware (UTC by default)

## Key Features Demonstrated

- **Simple setup**: Just import and configure
- **Colored output**: Automatic color coding by log level
- **Level filtering**: Only show messages at or above configured level
- **Console control**: Enable/disable console output with `console` parameter