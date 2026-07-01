---
title: Log Rotation
description: Rotate log files by size, time, clock, or weekday.
---

# Log Rotation

Prevent unbounded file growth by rotating logs automatically.

## Size-Based Rotation

```python
from logly import logger

sink_id = logger.add("app.log", rotation="10 MB")
logger.info("Rotates when file exceeds 10 MB")
logger.complete()
logger.remove(sink_id)
```

Supported size units: `"10 MB"`, `"500 KB"`, `"1 GB"`, `"500_000"` (bytes)

## Time-Based Rotation

```python
from logly import logger

# Rotate every day at midnight
sink_id = logger.add("daily.log", rotation="daily")

# Rotate every hour
sink_id2 = logger.add("hourly.log", rotation="hourly")

# Rotate every minute
sink_id3 = logger.add("minute.log", rotation="minutely")

logger.info("Time-based rotation active")
logger.complete()
logger.remove(sink_id)
logger.remove(sink_id2)
logger.remove(sink_id3)
```

## Clock-Based Rotation

```python
from logly import logger

# Rotate at a specific clock time
sink_id = logger.add("scheduled.log", rotation="00:00")
logger.info("Rotates at midnight")
logger.complete()
logger.remove(sink_id)
```

Other clock examples: `"02:30"`, `"12:00"`, `"18:45"`

## Weekday Rotation

```python
from logly import logger

# Rotate every Monday
sink_id = logger.add("weekly.log", rotation="weekly")
logger.info("Weekly rotation")
logger.complete()
logger.remove(sink_id)
```

Supported weekday names: `"monday"`, `"tuesday"`, `"wednesday"`, `"thursday"`, `"friday"`, `"saturday"`, `"sunday"`

## Size + Time Rotation

```python
from logly import logger

sink_id = logger.add(
    "app.log",
    rotation="50 MB",  # rotate at 50 MB
)
logger.info("Size-based rotation")
logger.complete()
logger.remove(sink_id)
```

## Clock + Retention

```python
from logly import logger

sink_id = logger.add(
    "app.log",
    rotation="02:00",  # rotate at 2 AM
    retention=14,  # keep 14 files
)
logger.info("Clock rotation + retention")
logger.complete()
logger.remove(sink_id)
```

## Size + Retention + Compression

```python
from logly import logger

sink_id = logger.add(
    "logs/app.log",
    rotation="100 MB",
    retention=30,
    compression="gzip",
)
logger.info("Size rotation + 30-file retention + gzip")
logger.complete()
logger.remove(sink_id)
```

## Daily + Retention + Compression

```python
from logly import logger

sink_id = logger.add(
    "logs/app.log",
    rotation="daily",
    retention="30 days",
    compression="zstd",
)
logger.info("Daily rotation + 30-day retention + zstd")
logger.complete()
logger.remove(sink_id)
```

## Weekly + Retention

```python
from logly import logger

sink_id = logger.add(
    "logs/app.log",
    rotation="weekly",
    retention=8,  # keep 8 weeks
)
logger.info("Weekly rotation + 8-week retention")
logger.complete()
logger.remove(sink_id)
```

## No Rotation

```python
from logly import logger

sink_id = logger.add(
    "app.log",
    rotation=None,  # explicitly disable rotation
)
logger.info("No rotation - file grows indefinitely")
logger.complete()
logger.remove(sink_id)
```

## Overwrite Mode

```python
from logly import logger

sink_id = logger.add(
    "app.log",
    rotation="daily",
    mode="w",  # overwrite on startup
)
logger.info("File overwritten on startup, then rotated daily")
logger.complete()
logger.remove(sink_id)
```

::: tip Combine rotation with retention
Use `retention` alongside `rotation` to auto-delete old files:
```python
logger.add("app.log", rotation="daily", retention=14)
```
:::
