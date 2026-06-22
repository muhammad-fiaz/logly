---
title: Concurrency
description: Thread-safe logging with background workers.
---

# Concurrency

Logly is thread-safe by default. Use `enqueue=True` for non-blocking writes.

## Enqueue Mode

```python
from logly import logger

sink_id = logger.add("app.log", enqueue=True)
logger.info("Non-blocking write via background worker")
logger.complete()
logger.remove(sink_id)
```

## Multi-Threaded Logging

```python
import threading
from logly import logger

logger.add("threaded.log", enqueue=True)

def worker(name):
    for i in range(100):
        logger.info("Worker {} iteration {}", name, i)

threads = [threading.Thread(target=worker, args=(f"W{i}",)) for i in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()

logger.complete()
```

## Async Worker Pattern

```python
import asyncio
from logly import logger

sink_id = logger.add("async.log", enqueue=True)

async def process():
    logger.info("Async task started")
    await asyncio.sleep(0.1)
    logger.info("Async task finished")

asyncio.run(process())
logger.complete()
logger.remove(sink_id)
```

::: info
`enqueue=True` creates a background thread with a queue. Logs are serialized to the queue and written asynchronously, keeping the calling thread fast.
:::
