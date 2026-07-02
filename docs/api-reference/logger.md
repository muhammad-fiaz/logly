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
- `level` (`str`): The log level name (e.g., `"INFO"`, `"ERROR"`)
- `message` (`str`): The log message
- `*args`: Format string arguments
- `**kwargs`: Additional context fields

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

Add a new sink to the logger. Returns a sink ID string.

```python
sink_id = logger.add("app.log", level="INFO", rotation="daily")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sink` | `str \| Path \| Callable \| object` | | File path, callable, or sink object |
| `level` | `str` | `"INFO"` | Minimum log level for this sink |
| `format` | `str \| None` | `None` | Custom format string |
| `rotation` | `str \| int \| None` | `None` | Rotation policy (e.g., `"daily"`, `"10 MB"`) |
| `retention` | `str \| int \| None` | `None` | Retention policy (e.g., `"30 days"`) |
| `compression` | `str \| None` | `None` | Compression codec (e.g., `"gzip"`, `"zip"`) |
| `enqueue` | `bool` | `False` | Use queue-based async worker |
| `colorize` | `bool \| None` | `None` | Enable ANSI color output |
| `backtrace` | `bool` | `False` | Include backtrace on exceptions |
| `diagnose` | `bool` | `False` | Include variable values on exceptions |
| `filter` | `Callable \| None` | `None` | Custom filter function |
| `serialize` | `bool` | `False` | Output as JSON |
| `pretty_json` | `dict \| PrettyJsonConfig \| None` | `None` | JSON formatting options |
| `patch` | `Callable \| None` | `None` | Patch function for all records |
| `encoding` | `str` | `"utf-8"` | File encoding |
| `delay` | `bool` | `False` | Delay file opening until first write |
| `context` | `Callable \| None` | `None` | Context variable factory |
| `catch` | `bool` | `True` | Catch sink errors silently |
| `mode` | `str` | `"append"` | File mode: `"append"` or `"overwrite"` |
| `buffering` | `int` | `-1` | File buffering level |
| `loop` | `AbstractEventLoop \| None` | `None` | Event loop for async sinks |
| `opener` | `Callable \| None` | `None` | Custom file opener |

**Returns:** `str` - sink ID for use with `remove()`

---

### remove(sink_id)

Remove a sink by its ID.

```python
logger.remove(sink_id)
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
print(level_obj.name)    # "INFO"
print(level_obj.no)      # 20
print(level_obj.color)   # None
print(level_obj.icon)    # None

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

### reinstall()

Re-add all previously configured sinks. Useful after context changes.

```python
logger.reinstall()
```

---

### enable(*module_names)

Enable logging for specific modules.

```python
logger.enable("myapp")
```

---

### disable(*module_names)

Disable logging for specific modules.

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

# Capture - capture context from specified keys
logger.opt(capture=["user_id"]).info("User action")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `exception` | `bool \| type \| tuple` | `None` | Include exception info |
| `record` | `bool` | `False` | Return record dict |
| `lazy` | `bool` | `False` | Defer string formatting |
| `colors` | `bool` | `False` | Enable ANSI color |
| `raw` | `bool` | `False` | Skip format processing |
| `depth` | `int` | `0` | Caller frame depth |
| `capture` | `list[str] \| None` | `None` | Keys to capture from context |
| `backtrace` | `bool \| None` | `None` | Override backtrace setting |
| `diagnose` | `bool \| None` | `None` | Override diagnose setting |
| `ansi` | `bool \| None` | `None` | Alias for colors |

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
| `default` | `Any` | `sentinel` | Default return value on exception |

## Parse Method

### parse(path, pattern=None, *, cast=None, chunk=65536, encoding="utf-8")

Parse log files using regex patterns. This is a **static method**.

```python
# Parse all log lines
entries = logger.parse("app.log")

# Custom pattern
entries = logger.parse(
    "app.log",
    pattern=r"(?P<time>\d{4}-\d{2}-\d{2}) (?P<level>\w+) (?P<message>.+)",
)

# With type casting
entries = logger.parse(
    "app.log",
    pattern=r"(?P<time>\S+) (?P<level>\w+) (?P<message>.+)",
    cast={"time": "datetime", "level": "int"},
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str \| Path` | | Log file path |
| `pattern` | `str \| None` | `None` | Regex pattern with named groups |
| `cast` | `dict \| None` | `None` | Type casting rules |
| `chunk` | `int` | `65536` | Read chunk size |
| `encoding` | `str` | `"utf-8"` | File encoding |

**Returns:** `list[dict]` - parsed log entries

## Properties

### levels

Get the current level registry.

```python
for level_name, level_no, color in logger.levels:
    print(f"{level_name}: {level_no}")
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
