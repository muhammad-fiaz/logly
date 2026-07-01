---
title: Compression Options
description: All compression codecs and configuration options available in Logly
---

# Compression Options

Logly supports multiple compression codecs for compressing rotated log files. Compression is applied automatically when a file is rotated, reducing disk usage while keeping logs accessible.

## Supported Codecs

| Codec | String | Aliases | Extension | Status |
|-------|--------|---------|-----------|--------|
| None | `"none"` | `None` | N/A | Stable |
| gzip | `"gzip"` | `"gz"`, `"tar"`, `"tar.gz"`, `"tgz"` | `.gz` | Stable |
| zip | `"zip"` | N/A | `.zip` | Stable |
| bz2 | `"bz2"` | `"tar.bz2"` | `.bz2` | Stable |
| xz | `"xz"` | `"lzma"`, `"tar.xz"` | `.xz` | Stable |
| zstd | `"zstd"` | N/A | `.zst` | Stable |

## gzip

The most widely supported compression format. Good balance of speed and compression ratio.

```python
from logly import logger

logger.add(
    "app.log",
    rotation="daily",
    compression="gzip",
)

# Using alias
logger.add(
    "app.log",
    rotation="daily",
    compression="gz",
)
```

Output files: `app.log.1719045600.gz`

## zip

Standard ZIP archive format. Compatible with most archive tools.

```python
from logly import logger

logger.add(
    "app.log",
    rotation="daily",
    compression="zip",
)
```

Output files: `app.log.1719045600.zip`

## bz2

Bzip2 compression. Higher compression ratio than gzip but slower.

```python
from logly import logger

logger.add(
    "app.log",
    rotation="daily",
    compression="bz2",
)
```

Output files: `app.log.1719045600.bz2`

## xz

XZ/LZMA compression. Highest compression ratio but slowest.

```python
from logly import logger

# Using "xz"
logger.add(
    "app.log",
    rotation="daily",
    compression="xz",
)

# Using "lzma" alias
logger.add(
    "app.log",
    rotation="daily",
    compression="lzma",
)

# Using "tar.xz" alias
logger.add(
    "app.log",
    rotation="daily",
    compression="tar.xz",
)
```

Output files: `app.log.1719045600.xz`

## zstd

Zstandard compression. Fast compression with good ratio, modern alternative.

```python
from logly import logger

logger.add(
    "app.log",
    rotation="daily",
    compression="zstd",
)
```

Output files: `app.log.1719045600.zst`

## No Compression

```python
from logly import logger

# Explicit no compression
logger.add(
    "app.log",
    rotation="daily",
    compression="none",
)

# Or omit compression parameter
logger.add(
    "app.log",
    rotation="daily",
)
```

## Combining with Rotation

### Size-Based Rotation + Compression

```python
from logly import logger

# Rotate at 10 MB, compress with gzip
logger.add(
    "app.log",
    rotation="10 MB",
    compression="gzip",
)

# Rotate at 100 MB, compress with zstd
logger.add(
    "high-volume.log",
    rotation="100 MB",
    compression="zstd",
)
```

### Time-Based Rotation + Compression

```python
from logly import logger

# Daily rotation with gzip
logger.add(
    "daily.log",
    rotation="daily",
    compression="gzip",
)

# Hourly rotation with zip
logger.add(
    "hourly.log",
    rotation="hourly",
    compression="zip",
)

# Weekly rotation with bz2
logger.add(
    "weekly.log",
    rotation="weekly",
    compression="bz2",
)
```

### Clock Rotation + Compression

```python
from logly import logger

# Rotate at midnight, compress with gzip
logger.add(
    "midnight.log",
    rotation="00:00",
    compression="gzip",
)

# Rotate at noon, compress with zstd
logger.add(
    "noon.log",
    rotation="12:00",
    compression="zstd",
)
```

### Weekday Rotation + Compression

```python
from logly import logger

# Rotate every Monday, compress with gzip
logger.add(
    "monday.log",
    rotation="monday",
    compression="gzip",
)

# Rotate every Friday, compress with xz
logger.add(
    "friday.log",
    rotation="friday",
    compression="xz",
)
```

## Combining with Retention

### Count-Based Retention + Compression

```python
from logly import logger

# Keep 7 compressed files
logger.add(
    "app.log",
    rotation="daily",
    retention=7,
    compression="gzip",
)

# Keep 30 compressed error files
logger.add(
    "errors.log",
    rotation="daily",
    retention=30,
    compression="gzip",
    level="ERROR",
)
```

### Age-Based Retention + Compression

```python
from logly import logger

# Keep 30 days, compressed
logger.add(
    "app.log",
    rotation="daily",
    retention="30 days",
    compression="gzip",
)

# Keep 90 days of errors, compressed
logger.add(
    "errors.log",
    rotation="daily",
    retention="90 days",
    compression="gzip",
)

# Keep 6 months, compressed with zstd
logger.add(
    "archive.log",
    rotation="daily",
    retention="6 months",
    compression="zstd",
)
```

## Compression Aliases

Logly recognizes several common aliases for compression codecs:

| Input | Resolves To |
|-------|-------------|
| `"gzip"` | gzip |
| `"gz"` | gzip |
| `"tar"` | gzip |
| `"tar.gz"` | gzip |
| `"tgz"` | gzip |
| `"zip"` | zip |
| `"bz2"` | bz2 |
| `"tar.bz2"` | bz2 |
| `"xz"` | xz |
| `"lzma"` | xz |
| `"tar.xz"` | xz |
| `"zstd"` | zstd |
| `"none"` | none (no compression) |

::: tip
Compression strings are case-insensitive. `"GZIP"`, `"Gzip"`, and `"gzip"` all work identically.
:::

## Invalid Codec

```python
from logly import logger

# This raises ValueError
logger.add("app.log", compression="invalid_codec")
# ValueError: unsupported compression codec: invalid_codec
```

## Performance Considerations

| Codec | Speed | Ratio | CPU Usage | Best For |
|-------|-------|-------|-----------|----------|
| gzip | Fast | Good | Low | General purpose |
| zip | Fast | Good | Low | Archive compatibility |
| bz2 | Slow | High | High | Maximum compression |
| xz | Slowest | Highest | Highest | Long-term archival |
| zstd | Fastest | Good | Low | High-throughput |

::: info
- **gzip** is the recommended default for most use cases
- **zstd** offers the best speed-to-ratio tradeoff for high-volume logging
- **xz** is best for long-term archival where disk space is critical
- **bz2** provides higher compression than gzip at the cost of speed
:::

### Choosing a Codec

```python
from logly import logger

# General purpose (recommended default)
logger.add("app.log", rotation="daily", compression="gzip")

# High-throughput, fast compression
logger.add("throughput.log", rotation="100 MB", compression="zstd")

# Maximum compression for archival
logger.add("archive.log", rotation="daily", retention="365 days", compression="xz")

# Cross-platform compatibility
logger.add("shared.log", rotation="daily", compression="zip")
```

## Complete Production Example

```python
from logly import logger

# Application logs - daily rotation, 30 day retention, gzip
logger.add(
    "logs/app.log",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
    rotation="daily",
    retention="30 days",
    compression="gzip",
    enqueue=True,
)

# Error logs - daily rotation, 90 day retention, gzip
logger.add(
    "logs/errors.log",
    level="ERROR",
    rotation="daily",
    retention="90 days",
    compression="gzip",
    enqueue=True,
)

# Audit logs - weekly rotation, 1 year retention, no compression
logger.add(
    "logs/audit.log",
    level="INFO",
    rotation="weekly",
    retention="365 days",
    compression=None,
    filter={"channel": "audit"},
)

# Debug logs - size-based rotation, keep 5 files, zstd
logger.add(
    "logs/debug.log",
    level="DEBUG",
    rotation="50 MB",
    retention=5,
    compression="zstd",
)

# Structured JSON logs - daily rotation, 60 day retention, gzip
logger.add(
    "logs/structured.json",
    level="WARNING",
    serialize=True,
    rotation="daily",
    retention="60 days",
    compression="gzip",
)

logger.info("Application started")
logger.complete()
```

## Archive Cleanup

When rotation and retention are both configured, Logly automatically:

1. Rotates the current log file when the rotation condition is met
2. Compresses the rotated file using the configured codec
3. Checks retention policies and deletes old files that exceed limits

```python
from logly import logger

# This setup will:
# 1. Rotate daily
# 2. Compress rotated files with gzip
# 3. Delete files older than 7 days
logger.add(
    "app.log",
    rotation="daily",
    retention="7 days",
    compression="gzip",
)
```
