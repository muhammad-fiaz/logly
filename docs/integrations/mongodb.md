---
title: MongoDB
description: Insert log entries into MongoDB collections.
---

# MongoDB

`MongoHandler` inserts log entries into a MongoDB collection using `pymongo`.

## Installation

This integration requires the `pymongo` package.

::: code-group

```bash [uv]
uv add logly[mongodb]
```

```bash [pip]
pip install "logly[mongodb]"
```

```bash [uv (without extras)]
uv add pymongo
```

```bash [pip (without extras)]
pip install pymongo
```

:::

::: warning Missing Dependency
If `pymongo` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'pymongo'
```
:::

## Usage

```python
from logly import logger
from logly.integrations.mongodb import MongoHandler

handler = MongoHandler(
    "mongodb://localhost:27017",
    database="logs",
    collection="app_logs",
)
logger.add(handler, level="WARNING")
```

## Constructor Args

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `uri` | `str` | `mongodb://localhost:27017` | MongoDB connection URI |
| `database` | `str` | `logly` | Database name |
| `collection` | `str` | `logs` | Collection name |
| `timeout` | `float` | `5.0` | Socket timeout in seconds |

## Tips

- Create an index on the `timestamp` field for efficient querying.
- Use a dedicated database/collection for logs to avoid contention with application data.

## Full Example

```python
from logly import logger
from logly.integrations.mongodb import MongoHandler

handler = MongoHandler(
    uri="mongodb://user:pass@mongo-host:27017/",
    database="production",
    collection="app_logs",
    timeout=10.0,
)
logger.add(handler, level="INFO")

logger.info("User signed up", user_id="u-456")
logger.exception("Payment failed")
```
