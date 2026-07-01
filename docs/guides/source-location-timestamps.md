---
title: Source Location & Timestamps
description: Enable, disable, and customize source file info and timestamps in Logly
---

# Source Location & Timestamps

Logly captures source file location and timestamps by default. You can customize or disable both.

## Source Location

### How It Works

When you call a log method, Logly inspects the call stack to capture:
- **File**: Absolute path to the source file
- **Line**: Line number in the source file
- **Function**: Function name where the call was made
- **Module**: Filename without extension

### Enable/Disable Source Capture

Source capture is **enabled by default** (`capture=True`):

```python
from logly import logger

# Source info captured (default)
logger.info("Has file/line/function info")

# Disable source capture
logger.opt(capture=False).info("No source info captured")
```

### Source Location in Format Strings

Use these tokens to include source info in output:

```python
from logly import logger

logger.add(
    "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {file}:{line} {function} | {message}",
)

logger.info("Hello")
# Output: 2026-06-22 14:30:45 | INFO     | app.py:42 main | Hello
```

### Available Source Tokens

| Token | Description | Example |
|-------|-------------|---------|
| `{file}` | Full source file path | `/home/user/app.py` |
| `{filename}` | Just the filename | `app.py` |
| `{line}` | Line number | `42` |
| `{function}` | Function name | `main` |
| `{module}` | Module name (no extension) | `app` |
| `{file_line}` | Combined `file:line` | `/home/user/app.py:42` |
| `{function_location}` | `function (file:line)` | `main (app.py:42)` |

### Source with Depth

For decorators or wrappers, use `depth` to skip stack frames:

```python
from logly import logger

def log_wrapper(func):
    def wrapper(*args, **kwargs):
        # depth=1 skips the wrapper, points to the caller
        logger.opt(depth=1).info(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_wrapper
def my_function():
    pass

my_function()
# Source points to my_function, not log_wrapper
```

### Source Context (Rust Feature)

The Rust `source` crate can read surrounding lines from source files:

```rust
// Rust API (internal)
let context = source_context(&file_path, line_number, 2); // 2 lines before/after
// Returns formatted output like:
//    40 |     fn main() {
//    41 |         let x = 42;
//  >> 42 |         println!("{x}");
//    43 |     }
```

## Timestamps

### Default Format

The default timestamp format is `%Y-%m-%d %H:%M:%S` (local timezone):

```python
from logly import logger

logger.info("Current time")
# Output: 2026-06-22 14:30:45 | INFO | Current time
```

### Custom Timestamp Formats

Use `{time:FORMAT}` in your format string:

```python
from logly import logger

# Date only
logger.add("app.log", format="{time:YYYY-MM-DD} | {message}")

# Time only
logger.add("app.log", format="{time:HH:mm:ss} | {message}")

# With milliseconds
logger.add("app.log", format="{time:HH:mm:ss.SSS} | {message}")

# Custom date format
logger.add("app.log", format="{time:DD/MM/YYYY HH:mm} | {message}")

# ISO format
logger.add("app.log", format="{time:YYYY-MM-DDTHH:mm:ss} | {message}")
```

### Time Format Tokens

Logly supports both brace-style datetime tokens and strftime tokens:

| Token | strftime Equivalent | Example |
|-------------|-------------------|---------|
| `YYYY` | `%Y` | 2026 |
| `YY` | `%y` | 26 |
| `MMMM` | `%B` | June |
| `MMM` | `%b` | Jun |
| `MM` | `%m` | 06 |
| `DD` | `%d` | 21 |
| `dddd` | `%A` | Monday |
| `ddd` | `%a` | Mon |
| `HH` | `%H` | 14 (24h) |
| `hh` | `%I` | 02 (12h) |
| `mm` | `%M` | 30 |
| `ss` | `%S` | 45 |
| `SSS` | `%.3f` | 123 (ms) |
| `A` | `%p` | AM |

### Disable Timestamps

Remove the `{time}` token from your format string:

```python
from logly import logger

# No timestamp
logger.add("app.log", format="{level:<8} | {message}")

# Minimal
logger.add("app.log", format="{message}")
```

### Timestamp in JSON Output

When `serialize=True`, timestamps are ISO 8601:

```python
from logly import logger

logger.add("app.json", serialize=True)
logger.info("JSON log")
```

Output:
```json
{"time": "2026-06-22T14:30:45.123000+00:00", "level": "INFO", "message": "JSON log", ...}
```

## Elapsed Time

Track time since logger creation with `{elapsed}`:

```python
from logly import logger
import time

logger.add("app.log", format="{elapsed} | {level:<8} | {message}")

time.sleep(1)
logger.info("After 1 second")
# Output: 1.000 | INFO | After 1 second
```

## Combined Example

```python
from logly import logger

logger.remove()

# Detailed format with source and timestamp
logger.add(
    "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {file}:{line} {function} | {message}",
    rotation="daily",
    retention="30 days",
)

# Minimal console format
logger.add(
    "stderr",
    format="{time:HH:mm:ss} | {level:<8} | {message}",
    colorize=True,
)

logger.info("Application started")
# Console: 14:30:45 | INFO     | Application started
# File:    2026-06-22 14:30:45.123 | INFO     | app.py:42 main | Application started
```
