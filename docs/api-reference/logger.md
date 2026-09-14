---
title: Logger API
description: Complete reference for the logly.Logger class
---

# Logger API

The `Logger` class is the primary interface for all logging operations. Import it from `logly`:

```python
from logly import logger
```

## Log Methods

### log(level, message, *args, **kwargs)

Log a message at the specified level.

```python
logger.log("INFO", "Message at INFO level")
logger.log("CUSTOM", "Message at custom level")
```

**Parameters:**
- `level` (`str | int`): Level name (e.g., `"INFO"`) or numeric priority (e.g., `20`)
- `message` (`object`): Format string or message (supports `str.format()` placeholders)
- `*args`: Positional format arguments
- `**kwargs`: Keyword format arguments

**Returns:** `dict[str, object] | None` - record dict if `opt(record=True)`, else `None`

---

### trace(message, *args, **kwargs)

Log at TRACE level (numeric 5).

```python
logger.trace("Fine-grained trace: {var}", var=value)
```

---

### debug(message, *args, **kwargs)

Log at DEBUG level (numeric 10).

```python
logger.debug("Debug info: {data}", data=payload)
```

---

### info(message, *args, **kwargs)

Log at INFO level (numeric 20).

```python
logger.info("Application started on port {port}", port=8000)
```

---

### notice(message, *args, **kwargs)

Log at NOTICE level (numeric 25).

```python
logger.notice("Configuration reloaded")
```

---

### success(message, *args, **kwargs)

Log at SUCCESS level (numeric 30).

```python
logger.success("Deployment completed!")
```

---

### warning(message, *args, **kwargs)

Log at WARNING level (numeric 40).

```python
logger.warning("Disk usage above {pct}%", pct=90)
```

---

### error(message, *args, **kwargs)

Log at ERROR level (numeric 50).

```python
logger.error("Database connection failed")
```

---

### fail(message, *args, **kwargs)

Log at FAIL level (numeric 55).

```python
logger.fail("Task failed: {reason}", reason="timeout")
```

---

### critical(message, *args, **kwargs)

Log at CRITICAL level (numeric 60).

```python
logger.critical("System memory exhausted")
```

---

### fatal(message, *args, **kwargs)

Log at FATAL level (numeric 70).

```python
logger.fatal("Unrecoverable error - shutting down")
```

---

### audit(message, *args, **kwargs)

Log at AUDIT level (must be registered first).

```python
logger.level("AUDIT", no=35, color="<green>")
logger.audit("User performed action")
```

## Configuration Methods

### add(sink, **kwargs)

Add a new sink to the logger. Returns an integer sink ID.

```python
sink_id = logger.add("app.log", level="INFO", rotation="daily")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sink` | `str \| Path \| Callable \| object` | | File path, callable, or sink object |
| `level` | `str \| int` | `"DEBUG"` | Minimum log level for this sink |
| `format` | `str \| Callable \| None` | built-in default | Custom format string or formatter callable |
| `rotation` | `str \| int \| object \| None` | `None` | Rotation policy (e.g., `"daily"`, `"10 MB"`) |
| `retention` | `str \| int \| object \| None` | `None` | Retention policy (e.g., `"30 days"`, `7`) |
| `compression` | `str \| object \| None` | `None` | Compression codec (e.g., `"gzip"`, `"zip"`) |
| `enqueue` | `bool` | `False` | Use queue-based async worker |
| `colorize` | `bool \| None` | `None` | Enable ANSI color output (`None` auto-detects) |
| `backtrace` | `bool` | `True` | Include backtrace on exceptions |
| `diagnose` | `bool` | `False` | Include variable values on exceptions |
| `filter` | `str \| Callable \| Mapping \| None` | `None` | Prefix string, filter callable, or extra-field mapping |
| `serialize` | `bool` | `False` | Output as JSON |
| `pretty_json` | `bool \| PrettyJsonConfig \| None` | `None` | `True` or JSON formatting options |
| `patch` | `Callable \| None` | `None` | Patch function for all records |
| `encoding` | `str` | `"utf-8"` | File encoding |
| `delay` | `bool` | `False` | Delay file opening until first write |
| `context` | `str \| BaseContext \| None` | `None` | Multiprocessing context for queue-based sinks |
| `catch` | `bool` | `True` | Catch sink errors silently |
| `mode` | `str` | `"a"` | File mode: `"a"` (append) or `"w"` (overwrite) |
| `buffering` | `int` | `1` | File buffering level |
| `loop` | `AbstractEventLoop \| None` | `None` | Event loop for async sinks |
| `opener` | `Callable \| None` | `None` | Custom file opener |

**Returns:** `int` - sink ID for use with `remove()` / `reinstall()`

**Built-in Sink Objects:**

| Sink | Description |
|------|-------------|
| `HttpJsonSink` | HTTP JSON log shipping |
| `BatchHttpJsonSink` | Batched HTTP JSON log shipping |
| `TcpSink` | TCP socket logging |
| `UdpSink` | UDP socket logging |
| `SyslogSink` | System syslog logging |

**Example with BatchHttpJsonSink:**

```python
from logly import BatchHttpJsonSink, logger

sink = BatchHttpJsonSink(
    url="https://logs.example.com/ingest",
    batch_size=100,
    flush_interval=5.0,
)
logger.add(sink, level="INFO")
```

---

### remove(handler_id=None)

Remove a sink by its ID, or all sinks when omitted.

```python
logger.remove(sink_id)
logger.remove()  # remove all sinks
```

---

### configure(**kwargs)

Configure the logger with a complete configuration dict.

```python
logger.configure(
    handlers=[
        {"sink": "stdout", "level": "INFO"},
        {"sink": "app.log", "level": "DEBUG"},
    ],
    extra={"app_name": "myapp"},
)
```

**Parameters:**
- `handlers` (`list[dict[str, Any]]`): List of sink configuration dicts
- `extra` (`dict[str, Any]`): Default extra fields for all records
- `levels` (`list[dict[str, Any]]`): Custom level definitions
- `patcher` (`Callable`): Global patcher function
- `activation` (`list[tuple[str, bool]]`): Level activation pairs

---

### level(name, no=None, color=None, icon=None)

Get or create a custom log level.

```python
# Get existing level
level_obj = logger.level("INFO")
print(level_obj.name)  # "INFO"
print(level_obj.no)  # 20
print(level_obj.color)  # None
print(level_obj.icon)  # None

# Create custom level
logger.level("AUDIT", no=35, color="<green><bold>", icon="🔒")
```

**Parameters:**
- `name` (`str`): Level name
- `no` (`int | None`): Numeric value
- `color` (`str | None`): ANSI color markup
- `icon` (`str | None`): Level icon

**Returns:** `Level` - level object with `.name`, `.no`, `.color`, `.icon` attributes

---

### reinstall(handler_id=None)

Remove and re-add sinks with their original configuration. Useful to reset file handlers after external rotation.

```python
logger.reinstall()
logger.reinstall(sink_id)  # reinstall one sink
```

---

### enable(name)

Enable log emission for a logger name previously passed to `disable`.

```python
logger.enable("myapp")
```

---

### disable(name)

Disable log emission for a logger name. Matching `log()` calls (including structured logging) are silently discarded.

```python
logger.disable("myapp")
```

---

### complete()

Wait for all pending log messages to be processed (async workers).

```python
logger.complete()
```

---

### root_dir(path)

Set the root directory for relative file paths.

```python
logger.root_dir("/var/log/myapp")
```

## Optimization Methods

### opt(**kwargs)

Configure logging behavior for subsequent calls.

```python
# Record mode - return the record dict
record = logger.opt(record=True).info("Hello")

# Lazy evaluation - defer string formatting
logger.opt(lazy=True).info("Expensive: {data}", data=compute())

# Raw mode - skip format processing
logger.opt(raw=True).info("Raw message: {time}")

# Exception mode - include exception info
logger.opt(exception=True).info("Failed")

# Colors mode - enable ANSI color in message
logger.opt(colors=True).info("<green>Success!</green>")

# Depth mode - capture caller info from N frames up
logger.opt(depth=2).info("Called from caller")

# Backtrace - include backtrace on exception
logger.opt(backtrace=True).info("Error context")

# Diagnose - include variable values on exception
logger.opt(diagnose=True).info("Debug context")

# Capture - disable caller file/line/function capture for speed
logger.opt(capture=False).info("Hot path")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `exception` | `BaseException \| bool \| None` | `None` | Exception instance or `True` to capture the active one |
| `record` | `bool` | `False` | Return record dict |
| `lazy` | `bool` | `False` | Defer string formatting |
| `colors` | `bool` | `False` | Enable ANSI color codes in output |
| `raw` | `bool` | `False` | Skip format string interpolation |
| `depth` | `int` | `0` | Additional stack frames to skip for caller info |
| `capture` | `bool` | `True` | Capture caller file/line/function info |
| `backtrace` | `bool` | `True` | Include backtrace in exception output |
| `diagnose` | `bool` | `False` | Include diagnostic info in exceptions |
| `ansi` | `bool` | `False` | Treat message as ANSI-formatted (implies `colors`) |

---

### bind(**kwargs)

Create a new logger with persistent context fields.

```python
user_logger = logger.bind(user_id="12345", request_id="abc")
user_logger.info("Action performed")
# Output includes: user_id=12345 request_id=abc
```

**Returns:** `Self` - new logger with bound context

---

### patch(patcher)

Create a new logger with a record patcher function.

```python
patched = logger.patch(lambda record: record.update({"env": "production"}))
patched.info("Running in production")
```

**Parameters:**
- `patcher` (`Callable[[dict], None]`): Function that modifies the record dict

**Returns:** `Self` - new logger with patcher applied

---

### contextualize(**kwargs)

Context manager for scoped context fields.

```python
with logger.contextualize(request_id="abc-123"):
    logger.info("Scoped to request")
    # request_id is automatically included
```

## Exception Methods

### catch(exception=Exception, level="ERROR", reraise=False, onerror=None, exclude=None, default=None)

Context manager for automatic exception logging.

```python
# Basic usage
with logger.catch():
    risky_operation()

# Exclude specific exceptions
with logger.catch(exclude=(ValueError, KeyError)):
    optional_operation()

# Custom error handling
with logger.catch(onerror=lambda e: send_alert(str(e))):
    critical_operation()

# Return default on exception
result = logger.catch(default=None)(risky_function)()

# Re-raise after logging
with logger.catch(reraise=True):
    dangerous_operation()
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `exception` | `type \| tuple` | `Exception` | Exception types to catch |
| `level` | `str` | `"ERROR"` | Log level for caught exceptions |
| `reraise` | `bool` | `False` | Re-raise after logging |
| `onerror` | `Callable \| None` | `None` | Callback on exception |
| `exclude` | `type \| tuple \| None` | `None` | Exception types to exclude (re-raise) |
| `default` | `Any` | `None` | Default return value on exception (decorator mode) |

## Lifecycle Methods

### start(*args, **kwargs)

Compatibility hook for application startup code. Accepts arbitrary arguments and performs no work; queued sinks start their workers when registered.

```python
logger.start()
```

### stop()

Flush sinks and stop logger-managed background workers. Equivalent to `complete()`.

```python
logger.stop()
```

### warn(message, *args, **kwargs)

Alias for `warning`.

### exception(message, *args, exc_info=True, **kwargs)

Log at `ERROR` level, attaching the currently active exception when present.

## Parse Method

### parse(path, pattern=None, *, cast=None, chunk=65536, encoding="utf-8")

Parse log files using regex patterns. This is a **static method** returning a generator — iterate it or wrap with `list()`.

```python
# Parse all log lines
entries = list(logger.parse("app.log"))

# Custom pattern
entries = list(logger.parse(
    "app.log",
    pattern=r"(?P<time>\d{4}-\d{2}-\d{2}) (?P<level>\w+) (?P<message>.+)",
))

# With type casting (values are callables, e.g. int)
entries = list(logger.parse(
    "app.log",
    pattern=r"(?P<time>\S+) (?P<level>\w+) (?P<message>.+)",
    cast={"level": int},
))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str \| Path` | | Log file path (missing files yield nothing) |
| `pattern` | `str \| Pattern \| None` | `None` | Regex pattern with named groups |
| `cast` | `dict[str, Callable] \| None` | `None` | Per-group casting functions (bad values keep the raw string) |
| `chunk` | `int` | `65536` | Read block size in bytes |
| `encoding` | `str` | `"utf-8"` | File encoding |

**Returns:** `Generator[dict, None, None]` - parsed log entries, one dict per matched line

## Properties

### levels

List of registered level names in severity order.

```python
for level_name in logger.levels:
    print(level_name)
```

## Builtin Levels

| Level | Numeric | Color |
|-------|---------|-------|
| `TRACE` | 5 | Gray |
| `DEBUG` | 10 | Blue |
| `INFO` | 20 | Green |
| `NOTICE` | 25 | Cyan |
| `SUCCESS` | 30 | Green (bold) |
| `WARNING` | 40 | Yellow |
| `ERROR` | 50 | Red |
| `FAIL` | 55 | Red (bold) |
| `CRITICAL` | 60 | Red (bold, bg) |
| `FATAL` | 70 | Red (bold, bg) |
