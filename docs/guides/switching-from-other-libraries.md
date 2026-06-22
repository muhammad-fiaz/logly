---
title: Switching from Other Libraries
description: How to migrate from Loguru, structlog, or stdlib logging to Logly
---

# Switching from Other Libraries

## From Loguru

Logly provides a familiar API. Migration is mostly changing imports.

### Basic Migration

```python
# Before (Loguru)
from loguru import logger

logger.add("app.log", rotation="10 MB", retention="7 days")
logger.info("Hello World")

# After (Logly)
from logly import logger

logger.add("app.log", rotation="10 MB", retention="7 days")
logger.info("Hello World")
```

### Key Differences

| Feature | Loguru | Logly |
|---------|--------|-------|
| Import | `from loguru import logger` | `from logly import logger` |
| Async sink | `add_async_sink()` | `add(sink, enqueue=True)` |
| `opt(extra=...)` | Supported | Use `bind()` instead |
| `catch()` params | `exception, message` | `exclude, onerror, default` |
| Format tokens | `YYYY-MM-DD` | `YYYY-MM-DD` or `%Y-%m-%d` |
| AUDIT level | Built-in | Register with `logger.level("AUDIT", no=35)` |

### catch() Migration

```python
# Before (Loguru)
with logger.catch(Exception, message="Something failed"):
    do_something()

# After (Logly)
with logger.catch(exclude=Exception):
    do_something()

# With callback
with logger.catch(onerror=lambda e: print(f"Failed: {e}")):
    do_something()
```

### opt() Migration

```python
# Before (Loguru)
logger.opt(exception=True, extra={"key": "value"}).info("msg")

# After (Logly)
logger.opt(exception=True).info("msg")
logger.bind(key="value").info("msg")
```

### Async Migration

```python
# Before (Loguru)
logger.add_async_sink(my_sink, level="INFO")

# After (Logly)
logger.add(my_sink, level="INFO", enqueue=True)
```

---

## From structlog

Logly provides built-in structlog integration.

### Basic Migration

```python
# Before (structlog)
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

log = structlog.get_logger()
log.info("hello", user_id="123")

# After (Logly)
from logly import logger

logger.add("stdout", level="INFO")
logger.bind(user_id="123").info("hello")
```

### Processor Migration

```python
# Before (structlog)
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)

# After (Logly)
from logly import logger

logger.add(
    "app.json",
    level="INFO",
    serialize=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {name} | {level} | {message}",
)
```

### Using Logly with structlog

You can use Logly as a structlog processor:

```python
import structlog
from logly.integrations.structlog import logly_processor, LoglyRenderer

structlog.configure(
    processors=[
        logly_processor(logger_name="myapp"),
        LoglyRenderer(level="INFO"),
    ],
)
```

### Key Differences

| Feature | structlog | Logly |
|---------|-----------|-------|
| Configuration | `structlog.configure()` | `logger.add()` per sink |
| Binding | `logger.bind(key=val)` | `logger.bind(key=val)` |
| Context | Processor-based | Built-in `bind()`/`contextualize()` |
| JSON | `JSONRenderer()` | `serialize=True` |
| Colors | `ConsoleRenderer()` | `colorize=True` |
| File rotation | Not built-in | `rotation=` parameter |
| Compression | Not built-in | `compression=` parameter |
| Exception catching | Not built-in | `logger.catch()` |

---

## From stdlib logging

### Basic Migration

```python
# Before (stdlib)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Hello World")

# After (Logly)
from logly import logger

logger.info("Hello World")
```

### Handler Migration

```python
# Before (stdlib)
handler = logging.FileHandler("app.log")
handler.setLevel(logging.INFO)
logger.addHandler(handler)

# After (Logly)
logger.add("app.log", level="INFO")
```

### Formatter Migration

```python
# Before (stdlib)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# After (Logly)
logger.add(
    "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {name} | {level} | {message}"
)
```

### Level Migration

```python
# Before (stdlib)
logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL

# After (Logly)
# Same names, plus additional levels:
"TRACE", "DEBUG", "INFO", "NOTICE", "SUCCESS",
"WARNING", "ERROR", "FAIL", "CRITICAL", "FATAL"
```

### Exception Handling

```python
# Before (stdlib)
try:
    1 / 0
except ZeroDivisionError:
    logger.exception("Division by zero")

# After (Logly)
try:
    1 / 0
except ZeroDivisionError:
    logger.exception("Division by zero")
    # Or use the catch() decorator
    @logger.catch
    def divide():
        1 / 0
```

### Custom Levels

```python
# Before (stdlib)
logging.addLevelName(25, "NOTICE")
logging.NOTICE = 25

# After (Logly)
logger.level("SECURITY", no=45, color="<red><bold>")
logger.log("SECURITY", "Unauthorized access")
```

### Configuration Comparison

```python
# Before (stdlib)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log"),
    ]
)

# After (Logly)
from logly import logger

logger.add(sys.stderr, level="INFO")
logger.add("app.log", level="INFO")
```

### Using Logly with stdlib

You can bridge stdlib to Logly:

```python
import logging
from logly.integrations.stdlib import InterceptHandler

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
```

---

## Feature Comparison

| Feature | Logly | Loguru | structlog | stdlib |
|---------|-------|--------|-----------|--------|
| **Engine** | Rust (PyO3) | Pure Python | Pure Python | Pure Python |
| **10 built-in levels** | ✅ | ✅ | ❌ | ❌ |
| **Custom levels** | ✅ | ✅ | ❌ | Manual |
| **Multiple sinks** | ✅ | ✅ | ❌ | ✅ |
| **File rotation** | ✅ | ✅ | ❌ | Handler dependent |
| **Compression** | ✅ | ✅ | ❌ | ❌ |
| **Context binding** | ✅ | ✅ | ✅ | Adapter based |
| **Exception catching** | ✅ | ✅ | ❌ | ❌ |
| **JSON serialization** | ✅ | ✅ | ✅ | Formatter dependent |
| **Lazy evaluation** | ✅ | ✅ | ❌ | ❌ |
| **Record patching** | ✅ | ✅ | ❌ | ❌ |
| **Background workers** | ✅ | ✅ | ❌ | QueueHandler |
| **Network logging** | ✅ | ✅ | ❌ | ❌ |
| **Framework integrations** | ✅ | ✅ | ❌ | ❌ |
| **Type stubs** | ✅ | ❌ | ✅ | ❌ |
| **Pydantic config** | ✅ | ❌ | ❌ | ❌ |

---

## Migration Checklists

### From Loguru

- [ ] Change `from loguru import logger` to `from logly import logger`
- [ ] Replace `add_async_sink()` with `add(sink, enqueue=True)`
- [ ] Replace `opt(extra={...})` with `bind(...)`
- [ ] Update `catch()` parameters: `exclude`, `onerror`, `default`
- [ ] Register custom levels with `logger.level()`
- [ ] Run test suite

### From structlog

- [ ] Replace `structlog.get_logger()` with `from logly import logger`
- [ ] Replace `structlog.configure()` processors with `logger.add()` sinks
- [ ] Replace `JSONRenderer()` with `serialize=True`
- [ ] Replace `ConsoleRenderer()` with `colorize=True`
- [ ] Add file rotation with `rotation=` parameter
- [ ] Run test suite

### From stdlib

- [ ] Replace `logging.getLogger()` with `from logly import logger`
- [ ] Replace `handler.setLevel()` with `level=` in `add()`
- [ ] Replace `formatter` with `format=` in `add()`
- [ ] Replace `RotatingFileHandler` with `rotation=`
- [ ] Replace `TimedRotatingFileHandler` with `rotation=`
- [ ] Add `retention=` for log cleanup
- [ ] Add `compression=` for compression
- [ ] Replace `logging.exception()` with `logger.exception()` or `@logger.catch`
- [ ] Replace custom levels with `logger.level()`
- [ ] Update format strings to use Logly tokens
- [ ] Test all logging paths
