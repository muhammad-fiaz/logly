---
title: Rotation, Retention & Compression
description: File rotation policies, retention strategies, and compression codecs
---

# Rotation, Retention & Compression

Logly supports automatic file rotation, retention policies, and compression for log management.

## Rotation Policies

### Size-Based Rotation

Rotate when the file exceeds a size limit:

```python
from logly import logger

# Rotate at 10 MB
logger.add("app.log", rotation="10 MB")

# Rotate at 1 MB
logger.add("app.log", rotation="1 MB")

# Rotate at 100 KB
logger.add("app.log", rotation="100 KB")

# Rotate at 1 GB
logger.add("app.log", rotation="1 GB")

# Rotate at 500 bytes
logger.add("app.log", rotation="500 B")
```

### Time-Based Rotation

Rotate at fixed time intervals:

```python
from logly import logger

# Daily rotation
logger.add("app.log", rotation="daily")

# Hourly rotation
logger.add("app.log", rotation="hourly")

# Weekly rotation
logger.add("app.log", rotation="weekly")

# Monthly rotation
logger.add("app.log", rotation="monthly")

# Yearly rotation
logger.add("app.log", rotation="yearly")

# Every minute
logger.add("app.log", rotation="minutely")
```

### Rotation with Retention

```python
from logly import logger

# Daily rotation, keep 7 days
logger.add("app.log", rotation="daily", retention=7)

# Hourly rotation, keep 24 hours
logger.add("app.log", rotation="hourly", retention=24)

# Weekly rotation, keep 12 weeks
logger.add("app.log", rotation="weekly", retention=12)

# Size-based, keep 5 files
logger.add("app.log", rotation="10 MB", retention=5)
```

### No Rotation

```python
from logly import logger

# Append mode (default)
logger.add("app.log", rotation=None)

# Overwrite mode
logger.add("app.log", rotation=None, mode="w")
```

## Retention Policies

### Count-Based

Keep a fixed number of rotated files:

```python
from logly import logger

# Keep 7 most recent files
logger.add("app.log", retention=7)

# Keep 30 files
logger.add("app.log", retention=30)
```

### Age-Based

Delete files older than a time period:

```python
from logly import logger

# Keep last 7 days
logger.add("app.log", retention="7 days")

# Keep last 24 hours
logger.add("app.log", retention="24 hours")

# Keep last 4 weeks
logger.add("app.log", retention="4 weeks")

# Keep last 6 months
logger.add("app.log", retention="6 months")
```

### Combined

```python
from logly import logger

# Daily rotation, keep 30 days, compress with gzip
logger.add(
    "app.log",
    rotation="daily",
    retention="30 days",
    compression="gzip",
)

# Size-based, keep 10 files, compress with zip
logger.add(
    "app.log",
    rotation="10 MB",
    retention=10,
    compression="zip",
)
```

## Compression Codecs

### gzip

```python
from logly import logger

logger.add("app.log.gz", compression="gzip")
logger.add("app.log", rotation="daily", compression="gzip")
```

### zip

```python
from logly import logger

logger.add("app.log.zip", compression="zip")
logger.add("app.log", rotation="daily", compression="zip")
```

### bz2

```python
from logly import logger

logger.add("app.log.bz2", compression="bz2")
logger.add("app.log", rotation="daily", compression="bz2")
```

### xz / lzma

```python
from logly import logger

logger.add("app.log.xz", compression="xz")
logger.add("app.log", rotation="daily", compression="lzma")
```

### zstd

```bash
pip install logly[zstd]
```

```python
from logly import logger

logger.add("app.log.zst", compression="zstd")
logger.add("app.log", rotation="daily", compression="zstd")
```

## Complete Examples

### Production Setup

```python
from logly import logger

# Application logs
logger.add(
    "logs/app.log",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
    rotation="daily",
    retention="30 days",
    compression="gzip",
)

# Error logs
logger.add(
    "logs/errors.log",
    level="ERROR",
    rotation="daily",
    retention="90 days",
    compression="gzip",
    serialize=True,
)

# Debug logs (development)
logger.add(
    "logs/debug.log",
    level="DEBUG",
    rotation="10 MB",
    retention=5,
)
```

### High-Volume Setup

```python
from logly import logger

# Rotate frequently, keep limited history
logger.add(
    "logs/throughput.log",
    level="INFO",
    rotation="100 MB",
    retention=3,
    compression="gzip",
    enqueue=True,  # Background writes
)
```

### Audit Trail

```python
from logly import logger

# Long-term retention, no compression
logger.add(
    "logs/audit.log",
    level="INFO",
    filter={"channel": "audit"},
    rotation="daily",
    retention="365 days",
    compression=None,
)
```
