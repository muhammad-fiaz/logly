---
title: Per-Level Controls - Logly Examples
description: Per-level logging controls example showing how to configure different behavior for each log level in Logly.
keywords: python, logging, example, per-level, controls, console, time, color, storage, logly
---

# Per-Level Controls

This example demonstrates how to use Logly's per-level controls to customize logging behavior for each log level individually. You can control console output, timestamps, colors, and file storage on a per-level basis.

## Code Example

```python
from logly import logger

# Configure with per-level controls
logger.configure(
    level="TRACE",  # Show all levels
    color=True,
    console=True,
    show_time=True,
    show_module=True,
    show_function=True,
    
    # Per-level console control - hide DEBUG and TRACE from console
    console_levels={
        "TRACE": False,
        "DEBUG": False,
        "INFO": True,
        "WARNING": True,
        "ERROR": True,
        "CRITICAL": True
    },
    
    # Per-level time control - show time only for WARNING and above
    time_levels={
        "TRACE": False,
        "DEBUG": False,
        "INFO": False,
        "WARNING": True,
        "ERROR": True,
        "CRITICAL": True
    },
    
    # Per-level color control - disable colors for INFO level
    color_levels={
        "INFO": False,
        "WARNING": True,
        "ERROR": True
    }
)

# Add file sink - all levels go to file regardless of console settings
logger.add("per_level_demo.log")

# Test different log levels
logger.trace("This trace message won't show in console")
logger.debug("This debug message won't show in console")
logger.info("This info message shows in console (no color, no time)")
logger.warning("This warning shows in console (with color and time)")
logger.error("This error shows in console (with color and time)")
logger.critical("This critical shows in console (with color and time)")

logger.complete()
```

## Console Output

```
[INFO] This info message shows in console (no color, no time) | module=__main__ | function=<module>
2025-01-15 14:30:45.123 | [WARNING] This warning shows in console (with color and time) | module=__main__ | function=<module>
2025-01-15 14:30:45.124 | [ERROR] This error shows in console (with color and time) | module=__main__ | function=<module>
2025-01-15 14:30:45.125 | [CRITICAL] This critical shows in console (with color and time) | module=__main__ | function=<module>
```

## File Output (per_level_demo.log)

```
2025-01-15 14:30:45.123 | [TRACE] This trace message won't show in console | module=__main__ | function=<module>
2025-01-15 14:30:45.123 | [DEBUG] This debug message won't show in console | module=__main__ | function=<module>
2025-01-15 14:30:45.123 | [INFO] This info message shows in console (no color, no time) | module=__main__ | function=<module>
2025-01-15 14:30:45.123 | [WARNING] This warning shows in console (with color and time) | module=__main__ | function=<module>
2025-01-15 14:30:45.124 | [ERROR] This error shows in console (with color and time) | module=__main__ | function=<module>
2025-01-15 14:30:45.125 | [CRITICAL] This critical shows in console (with color and time) | module=__main__ | function=<module>
```

## Advanced Example: Production Configuration

```python
# Production configuration with per-level controls
logger.configure(
    level="INFO",
    color=False,  # No colors in production
    console=True,
    show_time=True,
    show_module=False,  # Hide module info in production
    show_function=False,  # Hide function info in production
    
    # Only show WARNING and above in console
    console_levels={
        "INFO": False,
        "WARNING": True,
        "ERROR": True,
        "CRITICAL": True
    },
    
    # Show time for all levels in files
    time_levels={
        "TRACE": True,
        "DEBUG": True,
        "INFO": True,
        "WARNING": True,
        "ERROR": True,
        "CRITICAL": True
    },
    
    # Store all levels to file, but disable DEBUG storage for performance
    storage_levels={
        "DEBUG": False,  # Skip DEBUG level file storage
        "INFO": True,
        "WARNING": True,
        "ERROR": True,
        "CRITICAL": True
    }
)

# Add production file sinks
logger.add("logs/app.log", rotation="daily", retention=30)
logger.add("logs/errors.log", filter_min_level="ERROR", rotation="weekly")
```

## Key Features Demonstrated

- **Per-level console control**: Control which levels appear in console output
- **Per-level time control**: Show/hide timestamps per log level
- **Per-level color control**: Enable/disable colors per log level
- **Per-level storage control**: Control file logging per log level
- **Independent controls**: Console, time, color, and storage settings are independent
- **Production optimization**: Reduce noise and improve performance in production environments