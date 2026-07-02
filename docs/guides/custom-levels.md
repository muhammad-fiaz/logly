# Custom Levels

Logly supports custom log levels with full control over name, numeric severity, ANSI color, and icon/emoji.

## Built-in Levels

| Level | Number | Color |
|-------|--------|-------|
| TRACE | 5 | dim |
| DEBUG | 10 | blue |
| INFO | 20 | - |
| NOTICE | 25 | cyan |
| SUCCESS | 30 | green |
| WARNING | 40 | yellow |
| ERROR | 50 | red |
| FAIL | 55 | magenta |
| CRITICAL | 60 | bold_red |
| FATAL | 70 | bold_red |

## Register a Custom Level

```python
from logly import logger

logger.level("VERBOSE", no=15, color="cyan", icon=">")
```

Parameters:

* `name` – Level name (e.g. `"VERBOSE"`, `"HTTP"`, `"SECURITY"`)
* `no` – Numeric severity (must be unique)
* `color` – ANSI color name (e.g. `"green"`, `"bold_red"`, `"#ff0000"`)
* `icon` – Optional icon/emoji displayed in formatted output

## Inspect a Level

```python
from logly import logger

info = logger.level("INFO")
print(info.name)    # "INFO"
print(info.no)      # 20
print(info.color)   # None
print(info.icon)    # None
```

Returns a `Level` object with `.name`, `.no`, `.color`, `.icon` attributes.

## Log with Custom Level

```python
from logly import logger

logger.level("METRIC", no=28, color="magenta", icon="#")

logger.log("METRIC", "request latency 42ms")
```

## Use Icon in Format Strings

```python
from logly import logger

logger.level("HTTP", no=21, color="blue", icon=">")

sink_id = logger.add(
    lambda msg: print(msg, end=""),
    format="{level_icon} {level} | {message}",
    level="TRACE",
)

logger.log("HTTP", "GET /api/users")
logger.info("Application started")

logger.remove(sink_id)
```

Output:

```text
> HTTP | GET /api/users
 INFO | Application started
```

Available format tokens:

| Token | Description |
|-------|-------------|
| `{level}` | Level name |
| `{level_no}` | Numeric priority |
| `{level_icon}` | Level icon/emoji |
| `{message}` | Log message |
| `{time}` | Timestamp |
| `{name}` | Logger name |
| `{file}` | Source file |
| `{line}` | Line number |
| `{function}` | Function name |

## Register Multiple Custom Levels

```python
from logly import logger

CUSTOM_LEVELS = [
    ("HTTP", 21, "blue", ">"),
    ("DATABASE", 22, "magenta", "*"),
    ("SECURITY", 35, "red", "!"),
    ("METRIC", 28, "cyan", "#"),
]

for name, no, color, icon in CUSTOM_LEVELS:
    logger.level(name, no=no, color=color, icon=icon)

logger.log("HTTP", "GET /api/users")
logger.log("DATABASE", "Connected to PostgreSQL")
logger.log("SECURITY", "Authentication failed")
logger.log("METRIC", "request latency 42ms")
```

## Modify Existing Levels

```python
from logly import logger

# Change the color of an existing level
logger.level("INFO", no=20, color="bold_green", icon="i")

# Verify the change
info = logger.level("INFO")
print(info.color)   # "bold_green"
print(info.icon)    # "i"
```

## List All Registered Levels

```python
from logly import list_levels

levels = list_levels()
print(levels)
# ["TRACE", "DEBUG", "INFO", "NOTICE", "SUCCESS", "WARNING", "ERROR", "FAIL", "CRITICAL", "FATAL", "HTTP", ...]
```

## Level Class Reference

```python
from logly import Level

# Level is a frozen dataclass
info = logger.level("INFO")
assert isinstance(info, Level)

# Access properties
assert info.name == "INFO"
assert info.no == 20
assert info.color is None
assert info.icon is None
```
