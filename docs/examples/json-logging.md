---
title: JSON Logging
description: Output structured JSON log records for machine parsing.
---

# JSON Logging

Enable `serialize=True` to produce structured JSON output.

## Basic JSON Output

```python
from logly import logger

sink_id = logger.add("app.json", serialize=True)
logger.info("JSON structured log")
logger.complete()
logger.remove(sink_id)
```

Output:

```json
{"text": "2026-06-22T12:00:00 | INFO | JSON structured log", "record": {"level": "INFO", "message": "JSON structured log", ...}}
```

## JSON with Rotation

```python
from logly import logger

sink_id = logger.add(
    "logs/app.json",
    serialize=True,
    rotation="daily",
    retention=30,
    compression="gzip",
)
logger.info("JSON logs with rotation and compression")
logger.complete()
logger.remove(sink_id)
```

## Custom JSON Formatter

```python
from logly import logger
import json

def custom_json(record):
    entry = {
        "ts": record["time"].isoformat(),
        "level": record["level"].name,
        "msg": record["message"],
        "extra": record["extra"],
    }
    return json.dumps(entry) + "\n"

sink_id = logger.add("custom.json", format=custom_json)
logger.info("Custom JSON format")
logger.complete()
logger.remove(sink_id)
```

::: tip Use JSON for structured logging
JSON output pairs well with log aggregation tools like Elasticsearch, Loki, or CloudWatch.
:::
