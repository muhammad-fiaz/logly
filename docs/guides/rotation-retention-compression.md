---
title: Rotation, Retention & Compression
description: File rotation policies, retention strategies, and compression codecs
---

# Rotation, Retention & Compression

Logly supports automatic file rotation, retention policies, and compression for log management. All rotation and retention logic is handled in Rust for high performance.

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

**Supported size units:**

| Unit | Example | Bytes |
|------|---------|-------|
| `B` | `"500 B"` | 500 |
| `KB` | `"100 KB"` | 100,000 |
| `KiB` | `"100 KiB"` | 102,400 |
| `MB` | `"10 MB"` | 10,000,000 |
| `MiB` | `"10 MiB"` | 10,485,760 |
| `GB` | `"1 GB"` | 1,000,000,000 |
| `GiB` | `"1 GiB"` | 1,073,741,824 |

Bare numbers are treated as bytes:

```python
logger.add("app.log", rotation=10_000_000)  # 10 MB
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

**Supported time intervals:**

| String | Interval | Seconds |
|--------|----------|---------|
| `"minutely"` / `"minute"` | Every minute | 60 |
| `"hourly"` / `"hour"` | Every hour | 3,600 |
| `"daily"` / `"day"` | Every day | 86,400 |
| `"weekly"` / `"week"` | Every week | 604,800 |
| `"monthly"` / `"month"` | Every month | 2,592,000 |
| `"yearly"` / `"year"` | Every year | 31,536,000 |

### Clock Rotation

Rotate at a specific time of day (24-hour format):

```python
from logly import logger

# Rotate at midnight
logger.add("app.log", rotation="00:00")

# Rotate at noon
logger.add("app.log", rotation="12:00")

# Rotate at 2:30 AM
logger.add("app.log", rotation="02:30")

# Rotate at 11:59 PM
logger.add("app.log", rotation="23:59")
```

### Weekday Rotation

Rotate on a specific day of the week:

```python
from logly import logger

# Rotate every Monday
logger.add("app.log", rotation="monday")

# Rotate every Friday
logger.add("app.log", rotation="friday")

# Rotate every Sunday
logger.add("app.log", rotation="sunday")
```

**Supported weekday names:**

| String | Day |
|--------|-----|
| `"monday"` | Monday |
| `"tuesday"` | Tuesday |
| `"wednesday"` | Wednesday |
| `"thursday"` | Thursday |
| `"friday"` | Friday |
| `"saturday"` | Saturday |
| `"sunday"` | Sunday |

### No Rotation

```python
from logly import logger

# Append mode (default)
logger.add("app.log", rotation=None)

# Or use "never"
logger.add("app.log", rotation="never")

# Overwrite mode
logger.add("app.log", rotation=None, mode="w")
```

### Rotated File Naming

Rotated files are named with a Unix timestamp:

```
app.log.1719045600
```

If the rotated file already exists, a counter suffix is appended.

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

**Supported retention strings:**

| String | Seconds |
|--------|---------|
| `"30 seconds"` | 30 |
| `"5 minutes"` | 300 |
| `"2 hours"` | 7,200 |
| `"30 days"` | 2,592,000 |
| `"2 weeks"` | 1,209,600 |
| `"3 months"` | 7,776,000 |

**Abbreviations:**

| String | Equivalent |
|--------|------------|
| `"30s"` | `"30 seconds"` |
| `"5min"` | `"5 minutes"` |
| `"2h"` | `"2 hours"` |
| `"7d"` | `"7 days"` |
| `"2w"` | `"2 weeks"` |

### No Retention

```python
from logly import logger

# Keep all rotated files forever
logger.add("app.log", retention=None)
```

## Compression Codecs

### gzip

```python
from logly import logger

logger.add("app.log", rotation="daily", compression="gzip")
```

Output files: `app.log.gz`

### zip

```python
from logly import logger

logger.add("app.log", rotation="daily", compression="zip")
```

Output files: `app.log.zip`

### bz2

```python
from logly import logger

logger.add("app.log", rotation="daily", compression="bz2")
```

Output files: `app.log.bz2`

### xz / lzma

```python
from logly import logger

logger.add("app.log", rotation="daily", compression="xz")
# Or equivalently:
logger.add("app.log", rotation="daily", compression="lzma")
```

Output files: `app.log.xz`

### zstd

```python
from logly import logger

logger.add("app.log", rotation="daily", compression="zstd")
```

Output files: `app.log.zst`

### No Compression

```python
from logly import logger

logger.add("app.log", rotation="daily", compression=None)
```

### Supported Compression Summary

| Codec | String | Aliases | Extension |
|-------|--------|---------|-----------|
| None | `"none"` | `None` | N/A |
| gzip | `"gzip"` | `"gz"`, `"tar"`, `"tar.gz"`, `"tgz"` | `.gz` |
| zip | `"zip"` | N/A | `.zip` |
| bz2 | `"bz2"` | `"tar.bz2"` | `.bz2` |
| xz | `"xz"` | `"lzma"`, `"tar.xz"` | `.xz` |
| zstd | `"zstd"` | N/A | `.zst` |

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

### Clock Rotation at Midnight

```python
from logly import logger

logger.add(
    "logs/daily.log",
    rotation="00:00",
    retention="7 days",
    compression="gzip",
)
```
