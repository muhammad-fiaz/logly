---
title: Configuration Models
description: Stdlib dataclass models for Logly configuration
---

# Configuration Models

Logly uses stdlib dataclasses with targeted runtime validation for type-safe configuration. There are no validation-framework dependencies. Import them from `logly.models`:

```python
from logly.models import (
    RotationPolicy,
    RetentionPolicy,
    CompressionPolicy,
    PrettyJsonConfig,
    SinkConfig,
    LoggerConfig,
)
```

---

## RotationPolicy

Controls when log files are rotated.

```python
from logly.models import RotationPolicy

# Rotate daily
policy = RotationPolicy(kind="clock", value="daily")

# Rotate at 10 MB
policy = RotationPolicy(kind="size", value="10 MB")

# Rotate every week on Monday
policy = RotationPolicy(kind="weekday", value="monday")

# Never rotate
policy = RotationPolicy(kind="never")

# Custom rotation function
policy = RotationPolicy(kind="callable", value=my_rotation_func)
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `kind` | `str` | `"never"` | Rotation type: `"never"`, `"size"`, `"interval"`, `"clock"`, `"weekday"`, `"callable"` |
| `value` | `int \| str \| None` | `None` | Rotation parameter (size, interval, weekday, or callable) |

### Rotation Kinds

| Kind | Value | Example |
|------|-------|---------|
| `"never"` | None | No rotation |
| `"size"` | Size string | `"10 MB"`, `"1 GB"`, `"500 KB"` |
| `"interval"` | Time string | `"daily"`, `"hourly"`, `"weekly"`, `"monthly"` |
| `"clock"` | Time string | `"daily"`, `"midnight"`, `"weekly"` |
| `"weekday"` | Day name | `"monday"`, `"friday"`, `"sunday"` |
| `"callable"` | Function | `lambda msg: "archive" in msg.path` |

---

## RetentionPolicy

Controls when old log files are deleted.

```python
from logly.models import RetentionPolicy

# Keep 30 most recent files
policy = RetentionPolicy(count=30)

# Keep files for 7 days
policy = RetentionPolicy(seconds=7 * 24 * 3600)
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `count` | `int \| None` | `None` | Maximum number of files to keep |
| `seconds` | `int \| None` | `None` | Maximum age in seconds |

---

## CompressionPolicy

Controls how old log files are compressed.

```python
from logly.models import CompressionPolicy

# Gzip compression
policy = CompressionPolicy(codec="gzip")

# Zip archive
policy = CompressionPolicy(codec="zip")

# No compression
policy = CompressionPolicy(codec="none")
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `codec` | `str` | `"none"` | Compression codec |

### Supported Codecs

| Codec | Extension | Description |
|-------|-----------|-------------|
| `"none"` | | No compression |
| `"gzip"` / `"gz"` | `.gz` | Gzip compression |
| `"zip"` | `.zip` | Zip archive |
| `"bz2"` | `.bz2` | Bzip2 compression |
| `"xz"` / `"lzma"` | `.xz` | XZ/LZMA compression |
| `"zstd"` | `.zst` | Zstandard compression |
| `"tar"` | `.gz` | Alias for gzip |
| `"tar.gz"` / `"tgz"` | `.gz` | Alias for gzip |
| `"tar.bz2"` | `.bz2` | Alias for bz2 |
| `"tar.xz"` | `.xz` | Alias for xz |

---

## PrettyJsonConfig

Controls JSON serialization formatting.

```python
from logly.models import PrettyJsonConfig

# Default formatting
config = PrettyJsonConfig()

# Custom formatting
config = PrettyJsonConfig(
    indent=2,
    sort_keys=True,
    ensure_ascii=True,
    separators=(", ", ": "),
)
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `indent` | `int` | `4` | JSON indentation spaces |
| `sort_keys` | `bool` | `False` | Sort dictionary keys |
| `ensure_ascii` | `bool` | `False` | Escape non-ASCII characters |
| `separators` | `tuple[str, str] \| None` | `None` | `(item_separator, key_separator)` |

### Examples

```python
# Compact JSON
config = PrettyJsonConfig(indent=None, separators=(",", ":"))

# Pretty JSON with sorted keys
config = PrettyJsonConfig(indent=2, sort_keys=True)

# ASCII-safe JSON
config = PrettyJsonConfig(ensure_ascii=True)
```

---

## SinkConfig

Complete sink configuration model.

```python
from logly.models import (
    CompressionPolicy,
    RetentionPolicy,
    RotationPolicy,
    SinkConfig,
)

config = SinkConfig(
    level="INFO",
    format="{time} | {level} | {message}",
    rotation=RotationPolicy(kind="size", value=10_000_000),
    retention=RetentionPolicy(count=7),
    compression=CompressionPolicy(codec="gzip"),
    enqueue=True,
    colorize=True,
    serialize=False,
    pretty_json=None,
    append=True,
    mode="append",
)
```

String shorthands like `rotation="daily"` are accepted by `logger.add(...)`, not by `SinkConfig` — pass model instances (or plain dicts, which are coerced) here.

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level |
| `format` | `str` | `"{level} \| {message}"` | Format template string |
| `rotation` | `RotationPolicy \| dict \| None` | `None` | Rotation policy model or dict |
| `retention` | `RetentionPolicy \| dict \| None` | `None` | Retention policy model or dict |
| `compression` | `CompressionPolicy \| dict \| None` | `None` | Compression policy model or dict |
| `enqueue` | `bool` | `False` | Queue-based async |
| `colorize` | `bool \| None` | `None` | ANSI color output |
| `serialize` | `bool` | `False` | JSON serialization |
| `pretty_json` | `PrettyJsonConfig \| dict \| None` | `None` | JSON formatting |
| `append` | `bool` | `True` | Append to existing file |
| `mode` | `"append" \| "overwrite"` | `"append"` | File open mode |

---

## LoggerConfig

Complete logger configuration model.

```python
from logly.models import LoggerConfig, SinkConfig

config = LoggerConfig(
    sinks=[
        SinkConfig(level="INFO", format="{time} | {level} | {message}"),
        SinkConfig(level="DEBUG"),
    ],
    disabled={"debug-only-logger"},
)
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sinks` | `list[SinkConfig]` | `[]` | List of sink configurations (dicts are coerced) |
| `disabled` | `set[str]` | `set()` | Disabled logger names |

---

## Native serialization

```python
from logly.models import SinkConfig

config = SinkConfig(level="INFO")

# Serialize to a plain dict
data = config.to_dict()
assert data["level"] == "INFO"

# Build back from a plain mapping (validated)
restored = SinkConfig.from_dict({"level": "DEBUG"})
assert restored.level == "DEBUG"
```

Validation errors raise `logly.models.ValidationError` (a `ValueError`
subclass), so `except ValueError` keeps working.
