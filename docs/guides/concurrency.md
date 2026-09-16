---
title: Concurrency
description: Background workers, thread safety, and enqueue mode
---

# Concurrency

Logly is thread-safe and supports background writing for high-throughput scenarios.

## Thread Safety

All Logger operations are thread-safe:

```python
import threading
from logly import logger

logger.add("app.log", level="INFO")


def worker():
    for i in range(100):
        logger.info("Thread {} message {}", threading.current_thread().name, i)


threads = [threading.Thread(target=worker) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()

logger.complete()
```

## Enqueue Mode

Set `enqueue=True` to dispatch through a background worker:

```python
from logly import logger

# Background writes
logger.add("app.log", enqueue=True)

for i in range(10000):
    logger.info("Message {}", i)

# Must complete before exit
logger.complete()
```

### When to Use Enqueue

| Scenario | Recommended |
|----------|-------------|
| High-throughput logging | `enqueue=True` |
| Latency-sensitive code | `enqueue=True` |
| Simple scripts | `enqueue=False` (default) |
| File rotation with many writers | `enqueue=True` |

### Enqueue with Rotation

```python
from logly import logger

logger.add(
    "app.log",
    enqueue=True,
    rotation="daily",
    retention=7,
    compression="gzip",
)

for i in range(100000):
    logger.info("High-volume message {}", i)

logger.complete()
```

## Contextualize in Threads

```python
import threading
from logly import logger


def worker(worker_id: int):
    with logger.contextualize(worker_id=worker_id):
        logger.info("Worker started")
        # Each thread has its own context
        for i in range(10):
            logger.info("Processing item {}", i)
        logger.info("Worker finished")


threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()

logger.complete()
```

## Async Context

```python
import asyncio
from logly import logger


async def handle_request(request_id: str):
    with logger.contextualize(request_id=request_id):
        logger.info("Starting request")
        await asyncio.sleep(0.1)
        logger.info("Request complete")


async def main():
    await asyncio.gather(
        handle_request("req-1"),
        handle_request("req-2"),
        handle_request("req-3"),
    )


asyncio.run(main())
```

## Flushing

```python
from logly import logger

logger.add("app.log", enqueue=True)
logger.info("Important message")

# Drain the background queue
logger.complete()

# Process exits cleanly
```

::: warning
Always call `logger.complete()` before your process exits when using `enqueue=True`. Without it, queued messages may be lost.
:::

## Multiprocessing

Child processes started with `spawn` (the default on Windows and macOS)
should configure their own `Logger`: logging works normally there, including
file rotation and compression.

```python
import multiprocessing as mp

from logly import Logger


def worker():
    log = Logger()
    log.add("app.log", level="INFO")
    log.info("hello from child")
    log.complete()


if __name__ == "__main__":
    mp.Process(target=worker).start()
```

::: warning
Background (`enqueue=True`) workers are threads and do not survive `fork`:
drain them with `logger.complete()` before forking, and re-add enqueue sinks
in the child if needed. The `context` argument of `add()` is reserved and
must be `None`.
:::
