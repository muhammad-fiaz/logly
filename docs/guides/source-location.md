---
title: Source Location Tracking
description: Enable and configure source file location capture for log messages in Logly
---

# Source Location Tracking

Logly automatically captures source file location information for every log message. This guide covers enabling, disabling, and customizing source capture to help you trace log messages back to their origin.

## How Source Capture Works

When you call a log method, Logly inspects the call stack to capture metadata about where the call was made:

- **File** - Absolute path to the source file
- **Line** - Line number in the source file
- **Function** - Function name where the call was made
- **Module** - Filename without extension

This information is captured at the Rust level using PyO3 for minimal performance overhead.

## Enabling and Disabling Source Capture

Source capture is **enabled by default** (`capture=True`):

```python
from logly import logger

# Source info is captured by default
logger.info("Has file/line/function info")

# Disable source capture for a single call
logger.opt(capture=False).info("No source info captured")

# Disable source capture for an entire sink
logger.add("app.log", capture=False, format="{time} | {level} | {message}")
```

::: tip Performance
Source capture adds a small overhead per log call since it must inspect the call stack. For high-throughput logging where source location is not needed, disable it with `capture=False`.
:::

## Source Tokens

Use these tokens in format strings to include source information in output:

| Token | Description | Example |
|-------|-------------|---------|
| `{file}` | Full source file path | `/home/user/app.py` |
| `{filename}` | Just the filename | `app.py` |
| `{line}` | Line number | `42` |
| `{function}` | Function name | `main` |
| `{module}` | Module name (no extension) | `app` |
| `{file_line}` | Combined `file:line` | `/home/user/app.py:42` |
| `{function_location}` | `function (file:line)` | `main (app.py:42)` |

### Basic Token Usage

```python
from logly import logger

logger.remove()

# Include file and line
logger.add(
    "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {file}:{line} | {message}",
)
logger.info("Hello")
# Output: 2026-07-01 14:30:45 | INFO     | /home/user/app.py:12 | Hello

# Include function name
logger.add(
    "app.log",
    format="{time:HH:mm:ss} | {level:<8} | {function} | {message}",
)
logger.info("Processing")
# Output: 14:30:45 | INFO     | main | Processing

# Include module name
logger.add(
    "app.log",
    format="{time:HH:mm:ss} | {level:<8} | {module} | {message}",
)
logger.info("Module-level log")
# Output: 14:30:45 | INFO     | app | Module-level log
```

### Combined Location Token

Use `{function_location}` for a concise single-token format:

```python
from logly import logger

logger.remove()

logger.add(
    "app.log",
    format="{time:HH:mm:ss} | {level:<8} | {function_location} | {message}",
)
logger.info("Something happened")
# Output: 14:30:45 | INFO     | main (app.py:15) | Something happened
```

### Custom Format with All Source Info

```python
from logly import logger

logger.remove()

logger.add(
    "app.log",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | "
        "{filename}:{line} in {function} | {message}"
    ),
)
logger.info("Detailed source info")
# Output: 2026-07-01 14:30:45.123 | INFO     | app.py:20 in main | Detailed source info
```

## Source Context Display

Logly can read surrounding lines from source files to provide context around the log call site. This is useful for understanding the code context without opening the file.

### Configuring Context Lines

```python
from logly import logger

logger.remove()

# Show 2 lines before and after the log call
logger.add(
    "app.log",
    format="{time} | {level} | {file}:{line}\n{source}\n{message}",
    source_context=2,  # lines of context before/after
)
```

### Example Output

When `source_context=2` and the log call is on line 42:

```
2026-07-01 14:30:45 | INFO | app.py:42
   40 |     for item in data:
   41 |         result = process(item)
>> 42 |         logger.info("Processed item")
   43 |         results.append(result)
   44 |     return results
Processed item
```

::: info
Source context reads the actual source file at log time. This feature requires the source file to be accessible on disk.
:::

## Depth Parameter for Decorator Wrapping

When using decorators or wrapper functions, the source location points to the wrapper instead of the original call site. Use the `depth` parameter to skip stack frames.

### How Depth Works

Each `depth` value skips one stack frame:

| Depth | Points To |
|-------|-----------|
| `0` | The current frame (default) |
| `1` | One frame up (caller of the current function) |
| `2` | Two frames up |
| `N` | N frames up |

### Basic Depth Example

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
# Source points to the line calling my_function, not the wrapper
```

### Nested Wrappers

```python
from logly import logger

def outer_wrapper(func):
    def wrapper(*args, **kwargs):
        # depth=2 skips both outer_wrapper and wrapper
        logger.opt(depth=2).info(f"Outer call to {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

def inner_wrapper(func):
    def wrapper(*args, **kwargs):
        # depth=1 skips only inner_wrapper
        logger.opt(depth=1).info(f"Inner call to {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@outer_wrapper
@inner_wrapper
def decorated_function():
    pass

decorated_function()
```

### Depth in a Logger Class

```python
from logly import logger

class UserService:
    def __init__(self):
        self.log = logger.bind(service="user")

    def create_user(self, name: str):
        # depth=1 points to the caller of create_user
        self.log.opt(depth=1).info(f"Creating user: {name}")
        return {"name": name}

service = UserService()
service.create_user("Alice")
# Source points to the line calling create_user
```

## Link Formats

Logly supports generating clickable links to source locations in various editors and terminals. Configure the link format when adding a sink:

### VSCode

```python
from logly import logger

logger.remove()

logger.add(
    "app.log",
    format="{time} | {level:<8} | {vscode_link} | {message}",
)
logger.info("Click the link to jump to source")
# Output includes: vscode://file/home/user/app.py:42
```

### JetBrains (IntelliJ, PyCharm)

```python
from logly import logger

logger.remove()

logger.add(
    "app.log",
    format="{time} | {level:<8} | {jetbrains_link} | {message}",
)
logger.info("JetBrains link")
# Output includes: file:///home/user/app.py?line=42
```

### Sublime Text

```python
from logly import logger

logger.remove()

logger.add(
    "app.log",
    format="{time} | {level:<8} | {sublime_link} | {message}",
)
logger.info("Sublime link")
# Output includes: /home/user/app.py:42
```

### Vim

```python
from logly import logger

logger.remove()

logger.add(
    "app.log",
    format="{time} | {level:<8} | {vim_link} | {message}",
)
logger.info("Vim link")
# Output includes: /home/user/app.py +42
```

### Emacs

```python
from logly import logger

logger.remove()

logger.add(
    "app.log",
    format="{time} | {level:<8} | {emacs_link} | {message}",
)
logger.info("Emacs link")
# Output includes: /home/user/app.py:42
```

### Terminal Hyperlinks

For terminals that support clickable links (most modern terminals):

```python
from logly import logger

logger.remove()

logger.add(
    "app.log",
    format="{time} | {level:<8} | {hyperlink} | {message}",
    colorize=True,
)
logger.info("Clickable terminal link")
# Output includes: \033]8;;file:///home/user/app.py:42\033\\link\033]8;;\033\\
```

### Custom Link Format

```python
from logly import logger

logger.remove()

# Use individual tokens for a custom link format
logger.add(
    "app.log",
    format="{time} | {level:<8} | {file}:{line} ({function}) | {message}",
)
logger.info("Custom format")
# Output: 2026-07-01 14:30:45 | INFO     | /home/user/app.py:42 (main) | Custom format
```

## Performance Impact of Source Capture

Source capture has different performance characteristics depending on configuration:

| Configuration | Overhead | Notes |
|---------------|----------|-------|
| `capture=False` | None | Skip all source capture |
| `capture=True` (default) | Low | Captures file/line/function via stack inspection |
| `source_context=N` | Medium | Reads source file from disk per call |
| `depth=N` | Low | Additional stack frame traversal |

### Optimizing for Performance

```python
from logly import logger

logger.remove()

# High-throughput: disable source capture entirely
logger.add(
    "app.log",
    level="INFO",
    capture=False,
    enqueue=True,
    rotation="100 MB",
)

# Debug only: enable full source context
logger.add(
    "debug.log",
    level="DEBUG",
    source_context=3,
    format="{time} | {level:<8} | {file}:{line} | {source} | {message}",
)

# Production: minimal source info
logger.add(
    "prod.log",
    level="WARNING",
    format="{time} | {level:<8} | {filename}:{line} | {message}",
)
```

::: warning
Avoid using `source_context` in production for high-throughput logging. Reading the source file from disk on every log call adds significant I/O overhead. Use it during development and debugging only.
:::

## Complete Examples

### Development Logging Setup

```python
from logly import logger

logger.remove()

# Console with full source info
logger.add(
    "stderr",
    level="DEBUG",
    format=(
        "<green>{time:HH:mm:ss.SSS}</green> | "
        "<level>{level:<8}</level> | "
        "<cyan>{filename}:{line}</cyan>:<cyan>{function}</cyan> | "
        "<level>{message}</level>"
    ),
    colorize=True,
)

# File with source context
logger.add(
    "debug.log",
    level="DEBUG",
    source_context=2,
    format=(
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | "
        "{file}:{line} in {function}\n{source}\n{message}"
    ),
)

def process_data(items):
    results = []
    for item in items:
        logger.debug("Processing item: {}", item)
        results.append(item * 2)
    return results

process_data([1, 2, 3])
```

### Production Logging Setup

```python
from logly import logger

logger.remove()

# Console without source (high-throughput)
logger.add(
    "stderr",
    level="INFO",
    format="{time:HH:mm:ss} | <level>{level:<8}</level> | <level>{message}</level>",
    colorize=True,
    capture=False,
)

# File with minimal source info
logger.add(
    "app.log",
    level="WARNING",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {filename}:{line} | {message}",
    rotation="daily",
    retention="90 days",
    compression="gzip",
    enqueue=True,
)

# Error file with function names
logger.add(
    "errors.log",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {function_location} | {message}",
    rotation="daily",
    retention="365 days",
    enqueue=True,
)

logger.info("Application started")
logger.warning("Disk usage high")
logger.error("Connection failed")
```

### Decorator with Depth

```python
from logly import logger

logger.remove()

logger.add(
    "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {function_location} | {message}",
)

def traced(func):
    """Decorator that logs function calls with correct source location."""
    def wrapper(*args, **kwargs):
        logger.opt(depth=1).info("Entering {}", func.__name__)
        result = func(*args, **kwargs)
        logger.opt(depth=1).info("Exiting {}", func.__name__)
        return result
    return wrapper

@traced
def calculate(x, y):
    return x + y

@traced
def main():
    result = calculate(1, 2)
    logger.info("Result: {}", result)

main()
# Source locations point to the actual call sites, not the decorator
```

### Editor Link Format Examples

```python
from logly import logger

logger.remove()

# VSCode links
logger.add(
    "vscode.log",
    format="{time} | {level:<8} | {vscode_link} | {message}",
)

# JetBrains links
logger.add(
    "jetbrains.log",
    format="{time} | {level:<8} | {jetbrains_link} | {message}",
)

# Multiple editors in one format
logger.add(
    "stderr",
    format=(
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level:<8}</level> | "
        "<cyan>{filename}:{line}</cyan> | "
        "<level>{message}</level>"
    ),
    colorize=True,
)

logger.info("Test message with editor links")
```
