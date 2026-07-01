---
title: Compression
description: Compress rotated log files with gzip, zip, bz2, xz, or zstd.
---

# Compression

Automatically compress log files when they rotate to save disk space.

## GZIP Compression

```python
from logly import logger

sink_id = logger.add("app.log", rotation="daily", compression="gzip")
logger.info("Rotated files will be .gz compressed")
logger.complete()
logger.remove(sink_id)
```

## ZIP Compression

```python
from logly import logger

sink_id = logger.add("app.log", rotation="daily", compression="zip")
logger.info("Rotated files will be .zip compressed")
logger.complete()
logger.remove(sink_id)
```

## BZ2 Compression

```python
from logly import logger

sink_id = logger.add("app.log", rotation="daily", compression="bz2")
logger.info("Rotated files will be .bz2 compressed")
logger.complete()
logger.remove(sink_id)
```

## XZ Compression

```python
from logly import logger

sink_id = logger.add("app.log", rotation="daily", compression="xz")
logger.info("Rotated files will be .xz compressed")
logger.complete()
logger.remove(sink_id)
```

## Zstandard Compression

```python
from logly import logger

sink_id = logger.add("app.log", rotation="daily", compression="zstd")
logger.info("Rotated files will be .zst compressed")
logger.complete()
logger.remove(sink_id)
```

## All Compression Formats

```python
from logly import logger

sink_id1 = logger.add("gzip.log", rotation="daily", compression="gzip")
sink_id2 = logger.add("zip.log", rotation="daily", compression="zip")
sink_id3 = logger.add("bz2.log", rotation="daily", compression="bz2")
sink_id4 = logger.add("xz.log", rotation="daily", compression="xz")
sink_id5 = logger.add("zstd.log", rotation="daily", compression="zstd")

logger.info("All compression formats supported")
logger.complete()
logger.remove(sink_id1)
logger.remove(sink_id2)
logger.remove(sink_id3)
logger.remove(sink_id4)
logger.remove(sink_id5)
```

## Combined with Size Rotation

```python
from logly import logger

sink_id = logger.add(
    "logs/app.log",
    rotation="50 MB",
    retention=30,
    compression="gzip",
)
logger.info("Size rotation + 30-day retention + gzip")
logger.complete()
logger.remove(sink_id)
```

## Combined with Time Rotation

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

## Compression with Clock Rotation

```python
from logly import logger

sink_id = logger.add(
    "logs/app.log",
    rotation="02:00",  # rotate at 2 AM
    retention=14,
    compression="gzip",
)
logger.info("Clock rotation + 14-day retention + gzip")
logger.complete()
logger.remove(sink_id)
```

## Compression with Weekday Rotation

```python
from logly import logger

sink_id = logger.add(
    "logs/app.log",
    rotation="weekly",  # rotate every Monday
    retention=8,  # keep 8 weeks
    compression="bz2",
)
logger.info("Weekly rotation + 8-week retention + bz2")
logger.complete()
logger.remove(sink_id)
```

## No Compression

```python
from logly import logger

sink_id = logger.add(
    "app.log",
    rotation="daily",
    compression="none",  # explicitly disable compression
)
logger.info("Rotated files will not be compressed")
logger.complete()
logger.remove(sink_id)
```

::: warning Disk I/O
Compression adds CPU overhead at rotation time. Use it with time or size rotation, not with `retention=0`.
:::
