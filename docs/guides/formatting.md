---
title: Formatting
description: Custom format strings, time formatting, JSON output, and callable formatters
---

# Formatting

## Template Format Strings

Logly uses format tokens in template strings:

```python
from logly import logger

logger.add(
    "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}",
)
```

### Available Tokens

| Token | Description | Example |
|-------|-------------|---------|
| `{time}` | Timestamp | datetime object |
| `{time:FORMAT}` | Formatted timestamp | `2026-06-21 14:30:45.123` |
| `{level}` | Level name | `INFO` |
| `{message}` | Log message | `Hello World` |
| `{name}` | Logger name | `logly` |
| `{function}` | Function name | `main` |
| `{line}` | Line number | `42` |
| `{module}` | Module name | `app` |
| `{process}` | Process ID | `12345` |
| `{thread}` | Thread name | `MainThread` |
| `{exception}` | Exception text | `ValueError: bad` |
| `{elapsed}` | Seconds since creation | `1.234` |
| `{extra[key]}` | Extra field by key | Custom value |
| `{extra.key}` | Extra field (dot notation) | Custom value |

### Time Formatting

```python
from logly import logger

# Full datetime
logger.add("app.log", format="{time:YYYY-MM-DD HH:mm:ss} | {message}")

# Date only
logger.add("app.log", format="{time:YYYY-MM-DD} | {message}")

# Time only
logger.add("app.log", format="{time:HH:mm:ss} | {message}")

# With milliseconds
logger.add("app.log", format="{time:HH:mm:ss.SSS} | {message}")

# Custom format
logger.add("app.log", format="{time:DD/MM/YYYY HH:mm} | {message}")
```

**Time format tokens:**

| Token | Python strftime | Example |
|-------|----------------|---------|
| `YYYY` | `%Y` | 2026 |
| `YY` | `%y` | 26 |
| `MMMM` | `%B` | June |
| `MMM` | `%b` | Jun |
| `MM` | `%m` | 06 |
| `DD` | `%d` | 21 |
| `dddd` | `%A` | Monday |
| `ddd` | `%a` | Mon |
| `HH` | `%H` | 14 |
| `hh` | `%I` | 02 |
| `mm` | `%M` | 30 |
| `ss` | `%S` | 45 |
| `SSS` | `%f` (trimmed) | 123 |
| `A` | `%p` | AM |
| `Z` | `%Z` | UTC |

## JSON Serialization

```python
from logly import logger

# JSON output
logger.add("app.json", serialize=True, rotation="daily")

# JSON to console
logger.add("stdout", serialize=True, colorize=True)

# JSON to stderr
logger.add("stderr", serialize=True)
```

JSON output format:

```json
{"elapsed":1.234,"exception":null,"extra":{"user_id":"12345"},"file":"","function":"main","level":"INFO","line":0,"message":"User logged in","module":"","name":"logly","process":12345,"thread":"MainThread","time":"2026-06-21T14:30:45.123000+00:00"}
```

## Pretty JSON

Use `PrettyJsonConfig` to control the formatting of serialized JSON output:

```python
from logly import logger
from logly.models import PrettyJsonConfig

# Default pretty JSON (4-space indent)
logger.add(
    "app.json",
    serialize=True,
    pretty_json=True,
)

# Custom formatting
logger.add(
    "app.json",
    serialize=True,
    pretty_json=PrettyJsonConfig(
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    ),
)
```

### PrettyJsonConfig Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `indent` | `int` | `4` | Number of spaces for indentation |
| `sort_keys` | `bool` | `False` | Sort dictionary keys alphabetically |
| `ensure_ascii` | `bool` | `False` | Escape non-ASCII characters |
| `separators` | `tuple[str, str] \| None` | `None` | Custom `(item_separator, key_separator)` tuple |

### Compact JSON

```python
from logly.models import PrettyJsonConfig

# Compact output (no extra whitespace)
logger.add(
    "app.json",
    serialize=True,
    pretty_json=PrettyJsonConfig(
        indent=0,
        separators=(", ", ": "),
    ),
)
```

## Callable Formatters

```python
from logly import logger

# Simple callable
logger.add(
    "app.log",
    format=lambda record: f"[{record['level']}] {record['message']}",
)

# With timestamp
from datetime import datetime

def my_formatter(record: dict) -> str:
    ts = record["time"].strftime("%H:%M:%S")
    return f"{ts} [{record['level']}] {record['message']}"

logger.add("app.log", format=my_formatter)

# With extra fields
def rich_formatter(record: dict) -> str:
    extra = record.get("extra", {})
    ctx = " ".join(f"{k}={v}" for k, v in extra.items())
    return f"[{record['level']}] {record['message']} {ctx}".strip()

logger.add("app.log", format=rich_formatter)
```

## Extra Field Formatting

```python
from logly import logger

# Using {extra[key]} syntax
logger.add(
    "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message} | user={extra[user_id]} req={extra[request_id]}",
)

# Using {extra.key} syntax
logger.add(
    "app.log",
    format="{message} | env={extra.env} region={extra.region}",
)

# Bind extra fields
bound = logger.bind(user_id="12345", request_id="abc-789")
bound.info("User logged in")
# Output: ... | INFO | User logged in | user=12345 req=abc-789

# With contextualize
with logger.contextualize(session_id="xyz-000"):
    logger.info("Session active")
    # Output includes: session_id=xyz-000
```

## Raw Mode

```python
from logly import logger

# Raw mode - no newline appended
logger.opt(raw=True).info("raw message")

# Raw with format
logger.opt(raw=True).info("no trailing newline")
```

## Format Examples

```python
from logly import logger

# Minimal
logger.add("app.log", format="{level} | {message}")

# Detailed
logger.add(
    "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}",
)

# JSON-like
logger.add("app.log", format='{"time":"{time:YYYY-MM-DD HH:mm:ss}","level":"{level}","message":"{message}"}')

# With context
logger.add(
    "app.log",
    format="{time:HH:mm:ss} | {level:<8} | {extra[service]}:{extra[request_id]} | {message}",
)
```
