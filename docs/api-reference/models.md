---
title: Configuration Models
description: Stdlib dataclass models for Logly configuration
---

# Configuration Models

Logly uses stdlib dataclasses with targeted runtime validation for type-safe configuration (no Pydantic required). Import them from `logly.models`:

> Core installs stay light: `pip install logly` pulls zero validation dependencies. Only install `uv add logly[pydantic]` if you want to nest these models inside your own pydantic `BaseModel` or validate them with `pydantic.TypeAdapter` — the dataclasses expose `__get_pydantic_core_schema__` and accept pydantic instances in `model_validate()` when pydantic is present.

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
from logly.models import SinkConfig

config = SinkConfig(
    level="INFO",
    format="{time} | {level} | {message}",
    rotation="daily",
    retention="30 days",
    compression="gzip",
    enqueue=True,
    colorize=True,
    serialize=False,
    pretty_json=None,
    append=True,
    mode="append",
)
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level |
| `format` | `str \| None` | `None` | Custom format string |
| `rotation` | `str \| int \| None` | `None` | Rotation policy |
| `retention` | `str \| int \| None` | `None` | Retention policy |
| `compression` | `str \| None` | `None` | Compression codec |
| `enqueue` | `bool` | `False` | Queue-based async |
| `colorize` | `bool \| None` | `None` | ANSI color output |
| `serialize` | `bool` | `False` | JSON serialization |
| `pretty_json` | `dict \| PrettyJsonConfig \| None` | `None` | JSON formatting |
| `append` | `bool` | `True` | Append to existing file |
| `mode` | `str` | `"append"` | File mode: `"append"` or `"overwrite"` |

---

## LoggerConfig

Complete logger configuration model.

```python
from logly.models import LoggerConfig, SinkConfig

config = LoggerConfig(
    sinks=[
        SinkConfig(level="INFO", format="{time} | {level} | {message}"),
        SinkConfig(level="DEBUG", rotation="daily"),
    ],
    extra={"app_name": "myapp"},
)
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sinks` | `list[SinkConfig]` | `[]` | List of sink configurations |
| `extra` | `dict[str, Any]` | `{}` | Default extra fields |
| `disabled` | `set[str]` | `set()` | Disabled level names |

---

## Optional Pydantic interop (`logly[pydantic]`)

```bash
uv add logly[pydantic]  # or: pip install "logly[pydantic]"
```

```python
from pydantic import BaseModel, TypeAdapter

from logly.models import SinkConfig, is_pydantic_available

assert is_pydantic_available()

# Validate a Logly model with pydantic
adapter = TypeAdapter(SinkConfig)
config = adapter.validate_python({"level": "INFO"})
assert config.level == "INFO"

# Nest Logly models inside your own BaseModel
class AppConfig(BaseModel):
    sink: SinkConfig

app = AppConfig.model_validate({"sink": {"level": "DEBUG"}})
assert app.sink.level == "DEBUG"

# model_validate also unwraps pydantic instances
config2 = SinkConfig.model_validate(app.sink)
```

Validation errors raise `logly.models.ValidationError` (a `ValueError`
subclass), so `except ValueError` keeps working with and without pydantic.
