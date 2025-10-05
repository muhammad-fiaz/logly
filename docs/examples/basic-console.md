---
title: Basic Console Logging - Logly Examples
description: Basic console logging example showing how to get started with Logly for simple console output with colored formatting.
keywords: python, logging, example, console, basic, colored, output, logly
---

# Basic Console Logging

This example demonstrates the simplest way to get started with Logly for console logging with beautiful colored output.

## Simple Example (NEW in v0.1.5)

**No configuration needed** - just import and log with automatic colors:

```python
from logly import logger

# Start logging immediately with colored output
logger.trace("Entering main function")           # Cyan (most verbose)
logger.debug("Debug information")                # Blue
logger.info("Application started")               # White
logger.success("Database connected")             # Green
logger.warning("Cache is full")                  # Yellow
logger.error("Connection timeout")               # Red
logger.critical("System out of memory")          # Bright Red
logger.fail("Authentication failed", user="bob") # Magenta (NEW)

# Log with extra data
logger.info("User logged in", user_id=12345)
logger.success("Payment processed", amount=99.99, card_last4="1234")
logger.fail("Login failed", attempts=3, reason="invalid_password")
```

## Advanced Example (Customize Settings)

If you need custom settings:

```python
from logly import logger

# Customize console output (optional)
logger.configure(level="DEBUG", color=True)

# Log some messages
logger.debug("Debug messages now visible")
logger.info("Application started")
logger.warning("This is a warning message")
logger.error("This is an error message")

logger.complete()
```

## Expected Output

```
2025-01-15T14:30:00.123456+00:00 [TRACE] Entering main function
2025-01-15T14:30:00.124567+00:00 [DEBUG] Debug information
2025-01-15T14:30:00.125678+00:00 [INFO] Application started
2025-01-15T14:30:00.126789+00:00 [SUCCESS] Database connected
2025-01-15T14:30:00.127890+00:00 [WARN] Cache is full
2025-01-15T14:30:00.128901+00:00 [ERROR] Connection timeout
2025-01-15T14:30:00.129012+00:00 [CRITICAL] System out of memory
2025-01-15T14:30:00.130123+00:00 [FAIL] Authentication failed | user=bob
2025-01-15T14:30:00.131234+00:00 [INFO] User logged in | user_id=12345
2025-01-15T14:30:00.132345+00:00 [SUCCESS] Payment processed | amount=99.99 | card_last4=1234
2025-01-15T14:30:00.133456+00:00 [FAIL] Login failed | attempts=3 | reason=invalid_password
```

**Colors in Terminal:**
- TRACE appears in cyan
- DEBUG appears in blue
- INFO appears in white
- SUCCESS appears in green
- WARN appears in yellow
- ERROR appears in red
- CRITICAL appears in bright red
- FAIL appears in magenta (NEW)

### What Happens

1. **Auto-configuration on import**:
   - Logger is automatically configured with `color=True`
   - Console sink created automatically with `auto_sink=True`
   - Default colors applied to all log levels
   - No `configure()` call needed for basic usage

2. **Colored output**:
   - Each level gets its default color (customizable)
   - FAIL level (NEW) displays in magenta
   - Colors help distinguish severity at a glance

3. **Extra fields are appended**:
   - Fields like `user_id=12345` are automatically formatted
   - Multiple fields are separated by `|` characters

4. **Timestamps are included**:
   - ISO 8601 format with microsecond precision
   - Timezone aware (UTC by default)

## Key Features Demonstrated

- **Zero configuration**: Just import and log - works immediately
- **Automatic colors**: Default color mapping for all 8 log levels
- **FAIL level**: New level for operation failures (v0.1.5)
- **Level filtering**: Only show messages at or above configured level
- **Console control**: Enable/disable console output with `console` parameter