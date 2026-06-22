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

## ZIP, BZ2, XZ, Zstd

```python
from logly import logger

sink_id = logger.add("zip.log", rotation="daily", compression="zip")
sink_id2 = logger.add("bz2.log", rotation="daily", compression="bz2")
sink_id3 = logger.add("xz.log", rotation="daily", compression="xz")
sink_id4 = logger.add("zstd.log", rotation="daily", compression="zstd")

logger.info("All compression formats supported")
logger.complete()
logger.remove(sink_id)
logger.remove(sink_id2)
logger.remove(sink_id3)
logger.remove(sink_id4)
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

::: warning Disk I/O
Compression adds CPU overhead at rotation time. Use it with time or size rotation, not with `retention=0`.
:::
