---
title: FAQ
description: Frequently asked questions about Logly
---

# Frequently Asked Questions

## General

### What is Logly?

Logly is a high-performance logging library for Python powered by a Rust-native engine. It provides structured logging, flexible sinks, modern developer-friendly APIs, and comprehensive integrations with popular frameworks.

### Why use Logly over stdlib logging?

- **Rust-native performance** for high-throughput logging
- **11 built-in log levels** (including SUCCESS, NOTICE, FAIL, AUDIT)
- **Automatic file rotation** with size/time/clock policies
- **Built-in compression** (GZIP, ZIP, bz2, XZ, Zstd)
- **Retention policies** with automatic cleanup
- **Context binding** for structured logging
- **Exception catching** decorator pattern
- **Framework integrations** (FastAPI, Django, Rich, etc.)
- **Zero configuration** with sensible defaults

### Is Logly production-ready?

Yes. Logly is designed for production use with:

- Zero unsafe Rust code
- Comprehensive test suite (185+ Rust tests, 247+ Python tests)
- Thread-safe concurrent operations
- Memory-efficient queue-based async logging
- Built-in error handling and recovery

## Installation

### How do I install Logly?

```bash
# uv (recommended)
uv add logly

# pip
pip install logly
```

### What Python versions are supported?

Logly supports Python 3.10 and newer.

### Do I need Rust installed?

No. Logly ships with pre-built binaries. You only need Rust if building from source.

## Configuration

### How do I add a file sink?

```python
from logly import logger

logger.add("app.log", level="INFO")
```

### How do I rotate files?

```python
from logly import logger

# Size-based
logger.add("app.log", rotation="100 MB")

# Time-based
logger.add("app.log", rotation="daily")

# Clock-based
logger.add("app.log", rotation="00:00")  # Midnight
```

### How do I compress old logs?

```python
from logly import logger

logger.add(
    "app.log",
    rotation="daily",
    compression="gzip",  # gzip, zip, bz2, xz, zstd
)
```

### How do I set retention policies?

```python
from logly import logger

# Keep last 30 days
logger.add("app.log", retention="30 days")

# Keep last 100 MB
logger.add("app.log", retention="100 MB")

# Keep last 10 files
logger.add("app.log", retention=10)
```

## Usage

### How do I add context to logs?

```python
from logly import logger

# Bind context
logger.bind(user_id="12345").info("User logged in")

# Scoped context
with logger.contextualize(request_id="abc"):
    logger.info("Processing request")
    logger.info("Request complete")
```

### How do I catch exceptions?

```python
from logly import logger

# As decorator
@logger.catch
def risky_operation():
    ...

# As context manager
with logger.catch():
    risky_operation()

# With exclude
@logger.catch(exclude=ValueError)
def another_operation():
    ...
```

### How do I use lazy evaluation?

```python
from logly import logger

# Lazy format
logger.opt(lazy=True).debug("Result: {}", lambda: expensive_computation())
```

### How do I log JSON?

```python
from logly import logger

logger.add("app.json", serialize=True)
```

### How do I parse log files?

```python
from logly import logger

# Parse with pattern
entries = logger.parse(
    "app.log",
    pattern="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)
```

## Integrations

### How do I use with FastAPI?

```python
from fastapi import FastAPI
from logly.integrations.fastapi import LoglyMiddleware

app = FastAPI()
app.add_middleware(LoglyMiddleware)
```

### How do I use with Django?

```python
# settings.py
LOGGING = {
    "version": 1,
    "handlers": {
        "logly": {
            "class": "logly.integrations.django.DjangoLoglyHandler",
        },
    },
    "root": {
        "handlers": ["logly"],
        "level": "DEBUG",
    },
}
```

### How do I use with Rich?

```python
from logly.integrations.rich import install_rich_handler

install_rich_handler()
```

## Performance

### How do I improve logging performance?

1. **Use lazy evaluation** for expensive computations
2. **Use `enqueue=True`** for I/O-bound sinks
3. **Set appropriate log levels** to filter messages early
4. **Use simpler formats** in high-throughput scenarios
5. **Batch operations** when possible

### What is the overhead of Logly?

Logly adds minimal overhead:

- **Synchronous mode**: < 1μs per log call
- **Enqueue mode**: ~5μs per log call (queue overhead)
- **Rust engine**: Native performance for formatting and I/O

## Troubleshooting

### No output appears

See [Troubleshooting: No output](/guides/troubleshooting#no-output-appears).

### Messages appear twice

See [Troubleshooting: Messages appear twice](/guides/troubleshooting#messages-appear-twice).

### Memory usage growing

See [Troubleshooting: Memory usage growing](/guides/troubleshooting#memory-usage-growing).

## More Questions?

- Check the [API Reference](/api-reference/logger)
- Read the [Guides](/guides/sinks)
- Compare with [stdlib logging](/comparison)
