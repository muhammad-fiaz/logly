---
title: Patching
description: Modify log records before they reach sinks.
---

# Patching

Inject fields or transform records globally or per-sink.

## Global Patcher

```python
from logly import logger

def add_service(record):
    record["extra"]["service"] = "auth-api"
    record["extra"]["env"] = "production"

logger.add("app.log", patch=add_service)
logger.info("Patched with service info")
logger.complete()
```

## Per-Sink Patcher

```python
from logly import logger

def enrich_record(record):
    record["extra"]["version"] = "2.3.1"
    record["extra"]["region"] = "eu-west-1"

# Only this sink gets the patch
sink_id = logger.add("enriched.log", patch=enrich_record)
logger.info("Only enriched.log has extra fields")
logger.complete()
logger.remove(sink_id)
```

## Modify Existing Fields

```python
from logly import logger

def uppercase_messages(record):
    record["message"] = record["message"].upper()

logger.add("upper.log", patch=uppercase_messages)
logger.info("this message will be uppercased")
logger.complete()
```

::: tip Use patching for enrichment
Patchers are ideal for adding deployment version, environment, hostname, or trace IDs to every record.
:::
