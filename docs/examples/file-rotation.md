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

# Add file sink with rotation
logger.add(
    "app.log",
    rotation="10 MB",  # Rotate when file reaches 10MB
    retention=7        # Keep 7 rotated files
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

### Rotation Options

- **Size-based**: `"10 MB"`, `"1 GB"`, `"500 KB"`
- **Time-based**: `"1 day"`, `"1 week"`, `"1 month"`
- **Combined**: `"1 day", "10 MB"` (rotate on either condition)

### Retention Options

- **Count-based**: `retention=5` (keep 5 files)
- **Time-based**: Not directly supported, use external cleanup

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

**Directory listing after rotation:**
```
app.log                    # Current active log file
app.2025-01-15.log         # Today's rotated file
app.2025-01-14.log         # Yesterday's file
app.2025-01-13.log         # Previous day's file
...
app.2025-01-08.log         # 7th day (retention=7 keeps this)
# app.2025-01-07.log       # This would be deleted (over retention limit)
```

## Key Features Demonstrated

- **File output**: Logs written to files instead of console
- **Automatic rotation**: Files rotate based on size/time
- **Retention policy**: Old logs automatically cleaned up
- **File and line info**: Shows where log calls originated