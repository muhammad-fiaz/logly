---
title: Filter Features
description: Complete guide to all filtering capabilities in Logly
---

# Filter Features

Logly provides multiple filtering mechanisms to control which log records reach each sink. Filters are applied per-sink and can be combined for complex routing logic.

## Level Filtering

The simplest filter is the `level` parameter on `add()`. Only records at or above the specified level are dispatched to the sink.

```python
from logly import logger

# Only WARNING and above
logger.add("warnings.log", level="WARNING")

# All levels (TRACE and above)
logger.add("debug.log", level="TRACE")

# Only ERROR and above
logger.add("errors.log", level="ERROR")

# Only CRITICAL and FATAL
logger.add("critical.log", level="CRITICAL")
```

### Level Hierarchy

| Level | Numeric |
|-------|---------|
| TRACE | 5 |
| DEBUG | 10 |
| INFO | 20 |
| NOTICE | 25 |
| SUCCESS | 30 |
| WARNING | 40 |
| ERROR | 50 |
| FAIL | 55 |
| CRITICAL | 60 |
| FATAL | 70 |

```python
from logly import logger

messages = []

def capture(msg: str) -> None:
    messages.append(msg)

# Only WARNING and above pass through
sink_id = logger.add(capture, level="WARNING")
logger.info("filtered out")
logger.warning("passes through")
logger.error("passes through")
logger.remove(sink_id)

print(len(messages))  # 2
```

## Prefix Filtering

Filter by logger name prefix using a string value:

```python
from logly import logger

# Only records from loggers starting with "myapp."
logger.add("myapp.log", filter={"name": "myapp."})

# Create a logger with the matching name
myapp = logger.bind(name="myapp.core")
myapp.info("This appears in myapp.log")
```

### Multiple Prefix Filters

```python
from logly import logger

# Route different modules to different files
logger.add("auth.log", filter={"name": "auth."})
logger.add("db.log", filter={"name": "database."})
logger.add("http.log", filter={"name": "http."})

# Usage
logger.bind(name="auth.login").info("User logged in")      # -> auth.log
logger.bind(name="database.query").info("SELECT *")        # -> db.log
logger.bind(name="http.request").info("GET /api/users")    # -> http.log
```

## Callable Filtering

Custom filter functions receive the record dict and return `True` to allow or `False` to reject.

### Signature

```python
def my_filter(record: dict[str, object]) -> bool:
    level = record.get("level", "")
    message = record.get("message", "")
    extra = record.get("extra", {})
    # Return True to allow, False to reject
    return True
```

### Filter by Level

```python
from logly import logger

def only_errors(record: dict[str, object]) -> bool:
    return record.get("level") in {"ERROR", "CRITICAL", "FAIL"}

logger.add("errors.log", filter=only_errors)
```

### Filter by Message Content

```python
from logly import logger

def important_messages(record: dict[str, object]) -> bool:
    msg = str(record.get("message", "")).lower()
    return "critical" in msg or "urgent" in msg

logger.add("important.log", filter=important_messages)
```

### Filter by Extra Fields

```python
from logly import logger

def production_only(record: dict[str, object]) -> bool:
    extra = record.get("extra", {})
    return extra.get("env") == "production"

logger.add("prod.log", filter=production_only)
```

### Filter by Module

```python
from logly import logger

def module_filter(record: dict[str, object]) -> bool:
    module = record.get("module", "")
    return module in {"auth", "security"}

logger.add("security.log", filter=module_filter)
```

### Block All Records

```python
from logly import logger

def block_all(record: dict[str, object]) -> bool:
    return False

logger.add("disabled.log", filter=block_all)
```

## Dictionary/Mapping Filtering

Filter by matching extra field values in a dictionary.

### Single Field

```python
from logly import logger

# Only records with extra["channel"] == "audit"
logger.add("audit.log", filter={"channel": "audit"})

# Usage
logger.bind(channel="audit").info("Permission changed")  # -> audit.log
logger.bind(channel="access").info("Page viewed")        # Not routed
```

### Multiple Fields (AND Logic)

```python
from logly import logger

# All fields must match
logger.add(
    "filtered.log",
    filter={"env": "production", "service": "api"},
)

# Usage
logger.bind(env="production", service="api").info("Request processed")   # -> filtered.log
logger.bind(env="production", service="web").info("Page rendered")       # Not routed
logger.bind(env="staging", service="api").info("Test request")          # Not routed
```

### Mapping Filter with Patch

```python
from logly import logger

def add_context(record: dict[str, object]) -> None:
    record.setdefault("extra", {})["service"] = "api"
    record.setdefault("extra", {})["env"] = "production"

sink_id = logger.add(
    "api.log",
    filter={"service": "api"},
    patch=add_context,
)
```

## Combining Filters

### Level + Callable Filter

```python
from logly import logger

# Only production errors
logger.add(
    "production-errors.log",
    level="ERROR",
    filter=lambda r: r.get("extra", {}).get("env") == "production",
)
```

### Level + Mapping Filter

```python
from logly import logger

# API warnings and above
logger.add(
    "api-warnings.log",
    level="WARNING",
    filter={"service": "api"},
)
```

### Multiple Filters on Different Sinks

```python
from logly import logger

# All messages at DEBUG
logger.add("all.log", level="DEBUG")

# Only errors
logger.add("errors.log", level="ERROR")

# Only API service logs
logger.add("api.log", filter={"service": "api"})

# Important warnings
logger.add(
    "important.log",
    level="WARNING",
    filter=lambda r: "critical" in r.get("message", "").lower(),
)
```

### Level + Mapping + Callable

```python
from logly import logger

def complex_filter(record: dict[str, object]) -> bool:
    extra = record.get("extra", {})
    # Allow production API errors or any critical message
    if extra.get("env") == "production" and extra.get("service") == "api":
        return True
    if record.get("level") in {"CRITICAL", "FATAL"}:
        return True
    return False

logger.add(
    "complex.log",
    level="ERROR",
    filter=complex_filter,
)
```

## Advanced Filtering Patterns

### Module-Based Routing

```python
from logly import logger

# Route by module name
logger.add("auth.log", filter={"name": "auth."})
logger.add("db.log", filter={"name": "database."})
logger.add("http.log", filter={"name": "http."})
logger.add("cache.log", filter={"name": "cache."})

# Usage
logger.bind(name="auth.core").info("Login successful")       # -> auth.log
logger.bind(name="database.pool").info("Connection acquired") # -> db.log
logger.bind(name="http.server").info("Request handled")       # -> http.log
logger.bind(name="cache.redis").info("Cache hit")             # -> cache.log
```

### Extra-Based Routing

```python
from logly import logger

# Route by extra fields
logger.add("requests.log", filter={"type": "request"})
logger.add("background.log", filter={"type": "background"})
logger.add("audit.log", filter={"channel": "audit"})

# Usage
logger.bind(type="request").info("GET /api")           # -> requests.log
logger.bind(type="background").info("Job completed")   # -> background.log
logger.bind(channel="audit").info("User modified")     # -> audit.log
```

### Message Content Routing

```python
from logly import logger

def security_filter(record: dict[str, object]) -> bool:
    msg = str(record.get("message", "")).lower()
    return any(word in msg for word in ["unauthorized", "forbidden", "breach", "intrusion"])

def performance_filter(record: dict[str, object]) -> bool:
    msg = str(record.get("message", "")).lower()
    return any(word in msg for word in ["slow query", "timeout", "latency", "memory"])

logger.add("security.log", filter=security_filter)
logger.add("performance.log", filter=performance_filter)
```

### Combined Pattern

```python
from logly import logger

# Complex filter combining multiple criteria
def production_api_errors(record: dict[str, object]) -> bool:
    level = record.get("level", "")
    extra = record.get("extra", {})
    message = str(record.get("message", "")).lower()

    # Must be production environment
    if extra.get("env") != "production":
        return False

    # Must be API service
    if extra.get("service") != "api":
        return False

    # Must be error or above, OR contain "critical"
    if level in {"ERROR", "CRITICAL", "FAIL"}:
        return True
    if "critical" in message:
        return True

    return False

logger.add("prod-api-errors.log", filter=production_api_errors)
```

## Performance Notes

::: info
- **Level filtering** is the fastest filter type - checked first and short-circuits
- **Prefix filtering** is fast - simple string comparison
- **Mapping filtering** is fast - dictionary key lookup
- **Callable filtering** is slower - invokes Python function per record
- For high-throughput logging, prefer level and mapping filters over callable filters
:::

### High-Performance Setup

```python
from logly import logger

# Fast: level + mapping filters
logger.add(
    "production.log",
    level="INFO",           # Fast level check
    filter={"env": "prod"}, # Fast mapping check
)

# Slower: callable filter (use only when needed)
logger.add(
    "custom.log",
    filter=lambda r: "important" in r.get("message", ""),
)
```

### Filter Evaluation Order

Filters are evaluated in this order:

1. **Level filter** (`level` parameter) - checked first
2. **Prefix/Mapping filter** (`filter` parameter) - checked if level passes
3. **Callable filter** (`filter` parameter) - checked last

```python
from logly import logger

# Evaluation order:
# 1. level="ERROR" (fast check)
# 2. filter={"service": "api"} (fast check)
# 3. callable filter (slower check)
logger.add(
    "filtered.log",
    level="ERROR",
    filter={"service": "api"},
    filter=lambda r: "timeout" in r.get("message", ""),
)
```

## Complete Example

```python
from logly import logger

# Route by module
logger.add("auth.log", filter={"name": "auth."})
logger.add("db.log", filter={"name": "database."})
logger.add("http.log", filter={"name": "http."})

# Route by severity
logger.add("stdout", level="INFO")
logger.add("stderr", level="ERROR")
logger.add("debug.log", level="TRACE")

# Route by context
logger.add("requests.log", filter={"type": "request"})
logger.add("background.log", filter={"type": "background"})

# Complex filter
def critical_filter(record: dict[str, object]) -> bool:
    level = record.get("level", "")
    extra = record.get("extra", {})
    return (
        level in {"ERROR", "CRITICAL", "FAIL"}
        or extra.get("priority") == "critical"
    )

logger.add("critical.log", filter=critical_filter)

# Production-only errors with callable
logger.add(
    "prod-errors.log",
    level="ERROR",
    filter=lambda r: r.get("extra", {}).get("env") == "production",
)

# Usage examples
logger.bind(name="auth.core").info("Login successful")                    # -> auth.log, stdout
logger.bind(name="database.pool").error("Connection failed")              # -> db.log, stderr
logger.bind(name="http.server").info("GET /api")                          # -> http.log, stdout
logger.bind(type="request").info("Processing request")                    # -> requests.log
logger.bind(env="production").error("Service down")                       # -> prod-errors.log, stderr
logger.opt(exception=True).error("Critical failure")                      # -> critical.log, stderr

logger.complete()
```
