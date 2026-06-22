---
title: Filtering
description: Level, prefix, callable, and mapping filters for per-sink log filtering
---

# Filtering

Filters control which log records reach each sink. Logly supports level filtering, prefix matching, callable filters, and mapping filters.

## Level Filtering

The simplest filter is the `level` parameter on `add()`:

```python
from logly import logger

# Only WARNING and above
logger.add("warnings.log", level="WARNING")

# All levels (TRACE and above)
logger.add("debug.log", level="TRACE")

# Only ERROR and CRITICAL
logger.add("errors.log", level="ERROR")
```

## Prefix Filter

Filter by logger name prefix:

```python
from logly import logger

# Only records from loggers starting with "myapp."
logger.add("myapp.log", filter={"name": "myapp."})

# Records from "myapp." go to this sink
myapp = logger.bind(name="myapp.module")
myapp.info("This appears in myapp.log")
```

## Callable Filter

Custom filter function that receives the record dict:

```python
from logly import logger

# Filter by message content
def important_only(record: dict) -> bool:
    return "important" in record.get("message", "").lower()

logger.add("important.log", filter=important_only)

# Filter by level
def errors_and_critical(record: dict) -> bool:
    return record.get("level") in {"ERROR", "CRITICAL", "FAIL"}

logger.add("errors.log", filter=errors_and_critical)

# Filter by extra fields
def production_only(record: dict) -> bool:
    extra = record.get("extra", {})
    return extra.get("env") == "production"

logger.add("prod.log", filter=production_only)

# Combine conditions
def combined_filter(record: dict) -> bool:
    level = record.get("level", "")
    extra = record.get("extra", {})
    return level in {"ERROR", "CRITICAL"} and extra.get("service") == "api"
```

## Mapping Filter

Filter by extra field values:

```python
from logly import logger

# Single field
logger.add("audit.log", filter={"channel": "audit"})

# Multiple fields (AND logic)
logger.add(
    "filtered.log",
    filter={"env": "production", "service": "api"},
)

# Usage
logger.bind(channel="audit").info("Permission changed")
# This goes to audit.log

logger.bind(env="production", service="api").info("Request processed")
# This goes to filtered.log
```

## Combining Filters

```python
from logly import logger

# Level + callable filter
logger.add(
    "production-errors.log",
    level="ERROR",
    filter=lambda r: r.get("extra", {}).get("env") == "production",
)

# Level + mapping filter
logger.add(
    "api-warnings.log",
    level="WARNING",
    filter={"service": "api"},
)

# Multiple filters on different sinks
logger.add("all.log", level="DEBUG")
logger.add("errors.log", level="ERROR")
logger.add("api.log", filter={"service": "api"})
logger.add("important.log", level="WARNING", filter=lambda r: "critical" in r.get("message", "").lower())
```

## Filter Examples

```python
from logly import logger

# Example 1: Route by logger name
logger.add("auth.log", filter={"name": "auth."})
logger.add("db.log", filter={"name": "database."})
logger.add("http.log", filter={"name": "http."})

# Example 2: Route by severity
logger.add("stdout", level="INFO")
logger.add("stderr", level="ERROR")
logger.add("debug.log", level="TRACE")

# Example 3: Route by context
logger.add("requests.log", filter={"type": "request"})
logger.add("background.log", filter={"type": "background"})

# Example 4: Complex filter
def complex_filter(record: dict) -> bool:
    level = record.get("level", "")
    extra = record.get("extra", {})
    message = record.get("message", "")

    # Allow all errors
    if level in {"ERROR", "CRITICAL", "FAIL"}:
        return True

    # Allow production warnings
    if level == "WARNING" and extra.get("env") == "production":
        return True

    # Allow messages containing "audit"
    if "audit" in message.lower():
        return True

    return False

logger.add("filtered.log", filter=complex_filter)
```
