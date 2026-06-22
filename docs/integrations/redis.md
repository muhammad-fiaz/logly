---
title: Redis
description: Push log entries to Redis lists or streams.
---

# Redis

`RedisHandler` pushes log entries to Redis lists (LPUSH) or streams (XADD).

## Installation

This integration requires the `redis` package.

::: code-group

```bash [uv]
uv add logly[redis]
```

```bash [pip]
pip install "logly[redis]"
```

```bash [uv (without extras)]
uv add redis
```

```bash [pip (without extras)]
pip install redis
```

:::

::: warning Missing Dependency
If `redis` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'redis'
```
:::

## Usage

```python
from logly import logger
from logly.integrations.redis import RedisHandler

handler = RedisHandler(
    "redis://localhost:6379/0",
    key="app:logs",
    mode="list",
)
logger.add(handler, level="WARNING")
```

## Constructor Args

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `url` | `str` | `redis://localhost:6379/0` | Redis connection URL |
| `key` | `str` | `logly:logs` | Redis key for log storage |
| `mode` | `"list" \| "stream"` | `"list"` | Storage mode: LPUSH for lists, XADD for streams |
| `timeout` | `float` | `5.0` | Socket timeout in seconds |
| `max_stream_len` | `int` | `10000` | Maximum stream/list length |

## Tips

- Use `mode="list"` for simple log queuing and `mode="stream"` for consumer group support.
- Set `max_stream_len` to cap memory usage for high-volume logs.

## Full Example

```python
from logly import logger
from logly.integrations.redis import RedisHandler

# List mode
handler = RedisHandler(
    "redis://localhost:6379/0",
    key="app:logs",
    mode="list",
    max_stream_len=5000,
)
logger.add(handler, level="WARNING")

# Stream mode
stream_handler = RedisHandler(
    "redis://localhost:6379/0",
    key="app:logs:stream",
    mode="stream",
    max_stream_len=10000,
)
logger.add(stream_handler, level="ERROR")

logger.warning("Disk usage critical")
logger.error("Connection pool exhausted")
```
