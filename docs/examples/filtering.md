---
title: Filtering
description: Filter log records by level, prefix, callable, or dictionary.
---

# Filtering

Control which records reach each sink.

## Level Filtering

```python
from logly import logger

# Only WARNING and above
sink_id = logger.add("warnings.log", level="WARNING")
logger.info("Not captured")
logger.warning("Captured!")
logger.complete()
logger.remove(sink_id)
```

## Prefix Filtering

```python
from logly import logger

# Only records from loggers starting with "myapp."
sink_id = logger.add("app.log", filter={"name": "myapp."})
logger.info("Only myapp.* records appear here")
logger.complete()
logger.remove(sink_id)
```

## Callable Filter

```python
from logly import logger

def important_only(record):
    return "important" in record["message"].lower()

sink_id = logger.add("filtered.log", filter=important_only)
logger.info("This is skipped")
logger.warning("This is IMPORTANT")
logger.complete()
logger.remove(sink_id)
```

## Dictionary Filter

```python
from logly import logger

sink_id = logger.add(
    "filtered.log",
    filter={"name": "myapp.", "extra.status": "active"},
)
logger.info("Matches both name prefix and extra field")
logger.complete()
logger.remove(sink_id)
```

::: info
Filters are applied per-sink, so different sinks can have different filter rules.
:::
