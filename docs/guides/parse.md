---
title: Log Parsing
description: Parse log files with Logger.parse() static method
---

# Log Parsing

The `Logger.parse()` static method reads log files and extracts structured data using regex patterns.

## Basic Usage

```python
from logly import logger

for record in logger.parse("app.log"):
    print(record)
    # {'message': '2026-06-21 14:30:45 | INFO | Hello world', ...}
```

## With Regex Pattern

Use named groups to extract specific fields:

```python
from logly import logger

pattern = r"(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (?P<level>\w+) \| (?P<message>.*)"

for record in logger.parse("app.log", pattern=pattern):
    print(f"[{record['level']}] {record['time']}: {record['message']}")
```

## With Type Casting

Cast extracted groups to specific types:

```python
from logly import logger

pattern = r"(?P<time>\d{4}-\d{2}-\d{2}) \| (?P<level>\w+) \| (?P<line>\d+) \| (?P<message>.*)"

for record in logger.parse(
    "app.log",
    pattern=pattern,
    cast={
        "line": int,
        "level": str.upper,
    },
):
    print(f"Line {record['line']}: {record['message']}")
```

## Parameters

```python
Logger.parse(
    path,          # str | Path - Path to the log file
    pattern=None,  # str | re.Pattern - Regex with named groups
    cast=None,     # dict[str, Callable] - Type casting functions
    chunk=65536,   # int - Read chunk size in bytes
    encoding="utf-8",  # str - File encoding
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str \| Path` | (required) | Path to the log file. |
| `pattern` | `str \| re.Pattern \| None` | `None` | Regex with named groups. If `None`, matches entire line. |
| `cast` | `dict[str, Callable] \| None` | `None` | Mapping of group names to casting functions. |
| `chunk` | `int` | `65536` | Read chunk size in bytes. |
| `encoding` | `str` | `"utf-8"` | File encoding. |

## Return Value

Each iteration yields a dictionary:

```python
{
    "message": "full line text",    # Always present
    "time": "2026-06-21 14:30:45",  # From named group
    "level": "INFO",                # From named group
    "message": "Hello world",       # From named group
}
```

The `"message"` key always contains the full line text. Named groups from the pattern are added as additional keys.

## Examples

### Parse ISO Timestamp Logs

```python
from logly import logger

pattern = r"(?P<time>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+) \| (?P<level>\w+) \| (?P<message>.*)"

for record in logger.parse("app.log", pattern=pattern):
    print(f"{record['time']} [{record['level']}] {record['message']}")
```

### Parse JSON-like Logs

```python
import json
from logly import logger

for record in logger.parse("app.json"):
    line = record["message"]
    try:
        data = json.loads(line)
        print(f"[{data['level']}] {data['message']}")
    except json.JSONDecodeError:
        continue
```

### Parse and Aggregate

```python
from collections import Counter
from logly import logger

pattern = r"(?P<level>\w+) \| (?P<message>.*)"
level_counts = Counter()

for record in logger.parse("app.log", pattern=pattern):
    level = record.get("level", "UNKNOWN")
    level_counts[level] += 1

for level, count in level_counts.most_common():
    print(f"{level}: {count}")
```

### Parse with Date Casting

```python
from datetime import datetime
from logly import logger

pattern = r"(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (?P<level>\w+) \| (?P<message>.*)"

for record in logger.parse(
    "app.log",
    pattern=pattern,
    cast={"time": lambda t: datetime.strptime(t, "%Y-%m-%d %H:%M:%S")},
):
    print(f"{record['time'].isoformat()} [{record['level']}] {record['message']}")
```

### Parse Rotated Log Files

```python
from pathlib import Path
from logly import logger

pattern = r"(?P<time>\S+) \| (?P<level>\w+) \| (?P<message>.*)"

for log_file in Path("logs").glob("app.log*"):
    print(f"--- {log_file.name} ---")
    for record in logger.parse(log_file, pattern=pattern):
        print(f"  [{record['level']}] {record['message']}")
```
