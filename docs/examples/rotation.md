---
title: Log Rotation
description: Rotate log files by size, time, or weekday.
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

You can also use exact byte counts: `"1_000_000"`, `"500 KB"`.

## Time-Based Rotation

```python
from logly import logger

# Rotate every day at midnight
sink_id = logger.add("daily.log", rotation="daily")

# Rotate every hour
sink_id2 = logger.add("hourly.log", rotation="hourly")

logger.info("Time-based rotation active")
logger.complete()
logger.remove(sink_id)
logger.remove(sink_id2)
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

## Weekday Rotation

```python
from logly import logger

# Rotate every Monday
sink_id = logger.add("weekly.log", rotation="weekly")
logger.info("Weekly rotation")
logger.complete()
logger.remove(sink_id)
```

::: tip Combine rotation with retention
Use `retention` alongside `rotation` to auto-delete old files:
```python
logger.add("app.log", rotation="daily", retention=14)
```
:::
