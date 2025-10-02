---
title: File Logging with Rotation - Logly Examples
description: File logging example showing how to configure Logly for file output with automatic rotation based on size and time.
keywords: python, logging, example, file, rotation, size, time, logly
---

# File Logging with Rotation

This example shows how to configure Logly for file logging with automatic rotation based on file size and time intervals.

## Code Example

```python
from logly import logger
import time

# Configure for file logging with rotation
logger.configure(level="INFO", color=False)

# Time-based rotation (daily)
logger.add(
    "logs/app.log",
    rotation="daily",  # Rotate daily at midnight
    retention=7,       # Keep 7 days of logs
    date_enabled=True  # Add date to rotated filenames
)

# Size-based rotation
logger.add(
    "logs/large_app.log",
    size_limit="10MB",  # Rotate when file reaches 10MB
    retention=5         # Keep 5 rotated files
)

# Simulate logging activity
for i in range(100):
    logger.info("Processing item {item_id}", item_id=i)
    logger.debug("Debug info for item {item_id}", item_id=i)
    if i % 10 == 0:
        logger.warning("Checkpoint reached: {count} items processed", count=i+1)
    time.sleep(0.01)  # Small delay to simulate work

logger.info("Processing complete")
```

## Configuration Options

### Time-Based Rotation Options

- **`rotation="daily"`**: Rotate every day at midnight
- **`rotation="hourly"`**: Rotate every hour
- **`rotation="minutely"`**: Rotate every minute (for testing)

### Size-Based Rotation Options

- **`size_limit="10MB"`**: Rotate when file reaches 10 megabytes
- **`size_limit="100MB"`**: Rotate at 100MB
- **`size_limit="1GB"`**: Rotate at 1 gigabyte

### Combined Rotation

```python
# Rotate daily OR when file reaches 50MB (whichever comes first)
logger.add(
    "logs/app.log",
    rotation="daily",
    size_limit="50MB",
    retention=7
)
```

### Retention Options

- **Count-based**: `retention=7` keeps 7 rotated files (oldest are deleted)
- **Works with both**: Time-based and size-based rotation

## Output Files

After running, you'll see files like:

**app.log (current file):**
```
2025-01-15 10:30:45 | INFO | Processing item 0
2025-01-15 10:30:45 | WARNING | Checkpoint reached: 1 items processed
2025-01-15 10:30:45 | INFO | Processing item 1
...
2025-01-15 10:30:46 | INFO | Processing complete
```

**Directory listing after daily rotation with `date_enabled=True`:**
```
logs/
├── app.log                    # Current active log file
├── app_2025-01-15.log        # Today's rotated file
├── app_2025-01-14.log        # Yesterday's file
├── app_2025-01-13.log        # Previous day's file
├── app_2025-01-12.log
├── app_2025-01-11.log
├── app_2025-01-10.log
└── app_2025-01-09.log        # 7th day (retention=7 keeps this)
# app_2025-01-08.log          # Deleted (over retention limit)
```

**What happens:**
- Files rotate automatically based on your configuration
- The `date_enabled=True` parameter adds dates to rotated filenames
- Old files beyond the retention limit are automatically deleted
- Current logs always go to `app.log` (or your specified filename)

## Key Features Demonstrated

- **File output**: Logs written to files instead of console
- **Automatic rotation**: Files rotate based on size/time
- **Retention policy**: Old logs automatically cleaned up
- **File and line info**: Shows where log calls originated