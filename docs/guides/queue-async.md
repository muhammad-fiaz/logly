---
title: Queue-Based Async Logging
description: Non-blocking logging with Logly's queue-based dispatch system
---

# Queue-Based Async Logging

Logly supports queue-based async logging to decouple log calls from actual I/O operations. This prevents logging from blocking your application, especially for high-throughput or network-based sinks.

## `enqueue=True` in `add()`

Enable queue-based logging by setting `enqueue=True` when adding a sink:

```python
from logly import logger

logger.remove()

# Enable background worker for this sink
logger.add("app.log", enqueue=True)

# All log calls are now non-blocking
for i in range(10000):
    logger.info("Message {}", i)

# Must complete before exit to flush the queue
logger.complete()
```

::: warning
Always call `logger.complete()` before your process exits when using `enqueue=True`. Without it, queued messages may be lost.
:::

### How It Works

When `enqueue=True`:

1. Each log call places the message in a thread-safe queue
2. A background worker thread processes messages from the queue
3. The calling thread continues immediately without waiting for I/O
4. `logger.complete()` drains the queue and waits for all messages to be processed

## Background Worker Threads

Logly spawns a single background worker thread per sink with `enqueue=True`:

```python
from logly import logger
import threading

logger.remove()

# This sink has a background worker
logger.add("app.log", enqueue=True)

# This sink is synchronous
logger.add("stderr")

def worker():
    for i in range(100):
        logger.info("Thread {} message {}", threading.current_thread().name, i)

# Multiple threads can log simultaneously
threads = [threading.Thread(target=worker) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# Flush all queued messages
logger.complete()
```

### Worker Behavior

- **Single worker per sink**: Each sink with `enqueue=True` gets its own background thread
- **Thread-safe queue**: Multiple threads can safely enqueue messages
- **Order preservation**: Messages are processed in FIFO order
- **Error handling**: Worker errors are caught and logged to stderr

## Backpressure Modes

When the queue fills up (e.g., during high-throughput logging), Logly applies backpressure. Configure the backpressure mode with the `backpressure` parameter:

### Block Mode (Default)

Blocks the calling thread until the queue has space:

```python
from logly import logger

logger.remove()

logger.add(
    "app.log",
    enqueue=True,
    backpressure="block",  # Default behavior
)

# If queue is full, this call blocks until space is available
for i in range(100000):
    logger.info("Message {}", i)

logger.complete()
```

**When to use**: When you must not lose any messages and can tolerate the calling thread blocking.

### DropNewest Mode

Drops the newest message when the queue is full:

```python
from logly import logger

logger.remove()

logger.add(
    "app.log",
    enqueue=True,
    backpressure="drop_newest",
)

# If queue is full, newest messages are dropped
for i in range(100000):
    logger.info("Message {}", i)

logger.complete()
```

**When to use**: When you need non-blocking logging and can tolerate losing some messages during bursts.

### Grow Mode

Increases queue size when full:

```python
from logly import logger

logger.remove()

logger.add(
    "app.log",
    enqueue=True,
    backpressure="grow",
)

# Queue grows as needed (memory usage increases)
for i in range(1000000):
    logger.info("Message {}", i)

logger.complete()
```

**When to use**: When you have sufficient memory and want to avoid blocking or dropping messages.

::: warning
`backpressure="grow"` can cause memory exhaustion if logging is faster than processing for extended periods. Use with caution.
:::

### Backpressure Comparison

| Mode | Behavior | Message Loss | Memory | Latency |
|------|----------|--------------|--------|---------|
| `block` | Blocks caller when full | None | Bounded | May increase |
| `drop_newest` | Drops new messages | Some | Bounded | Low |
| `grow` | Increases queue size | None | Unbounded | Low |

## `complete()` for Flushing

The `complete()` method waits for all pending log messages to be processed:

```python
from logly import logger

logger.remove()

logger.add("app.log", enqueue=True)
logger.add("errors.log", enqueue=True)

logger.info("Important message")
logger.error("Error message")

# Wait for all queued messages to be written
logger.complete()

# All messages are now guaranteed to be written
print("Done")
```

### In Application Lifecycle

```python
from logly import logger

def main():
    logger.add("app.log", enqueue=True)

    try:
        run_application()
    finally:
        # Always flush before exit
        logger.complete()

if __name__ == "__main__":
    main()
```

### With Multiple Sinks

```python
from logly import logger

logger.remove()

# Multiple queued sinks
logger.add("app.log", enqueue=True)
logger.add("errors.log", enqueue=True, level="ERROR")
logger.add("audit.log", enqueue=True, level="SUCCESS")

logger.info("Info message")
logger.error("Error message")
logger.success("Success message")

# Flush all sinks at once
logger.complete()
```

### Timeout

Specify a timeout to avoid waiting indefinitely:

```python
from logly import logger

logger.remove()
logger.add("app.log", enqueue=True)

logger.info("Message")

# Wait up to 5 seconds
logger.complete(timeout=5)
```

::: tip
Call `complete()` in your application's shutdown handler or `finally` block to ensure all messages are flushed.
:::

## Thread Safety with `contextualize()`

Use `contextualize()` to attach thread-specific context when logging from multiple threads:

```python
import threading
from logly import logger

logger.remove()

logger.add("app.log", enqueue=True)

def worker(worker_id: int):
    with logger.contextualize(worker_id=worker_id):
        logger.info("Worker started")
        # Each thread has its own context
        for i in range(10):
            logger.info("Processing item {}", i)
        logger.info("Worker finished")

threads = [threading.Thread(target=worker, args=(i, for i in range(4))]
for t in threads:
    t.start()
for t in threads:
    t.join()

logger.complete()
```

### Async Context

```python
import asyncio
from logly import logger

logger.remove()
logger.add("app.log", enqueue=True)

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
logger.complete()
```

### Bind vs Contextualize

| Feature | `bind()` | `contextualize()` |
|---------|----------|-------------------|
| Scope | Persistent | Scoped to block |
| Thread safety | Create new logger | Thread-local |
| Use case | Logger-level context | Request-level context |

## Performance Characteristics

### Throughput Comparison

```python
from logly import logger
import time

logger.remove()

# Synchronous logging
logger.add("sync.log")
start = time.time()
for i in range(100000):
    logger.info("Sync message {}", i)
sync_time = time.time() - start
logger.complete()

# Queue-based logging
logger.add("async.log", enqueue=True)
start = time.time()
for i in range(100000):
    logger.info("Async message {}", i)
logger.complete()
async_time = time.time() - start

print(f"Sync: {sync_time:.2f}s")
print(f"Async: {async_time:.2f}s")
```

### Memory Usage

```python
from logly import logger
import sys

logger.remove()

# Queue uses a bounded buffer by default
logger.add("app.log", enqueue=True)
logger.info("Message")
logger.complete()
```

### Latency

| Mode | Typical Latency | P99 Latency |
|------|-----------------|-------------|
| Sync | < 1ms | < 5ms |
| Enqueue (block) | < 1ms | < 10ms |
| Enqueue (drop_newest) | < 1ms | < 1ms |
| Enqueue (grow) | < 1ms | < 5ms |

## When to Use Enqueue vs Sync

### Use Enqueue When

| Scenario | Reason |
|----------|--------|
| High-throughput logging | Avoid blocking application threads |
| Network sinks | I/O latency doesn't block app |
| File rotation with many writers | Single writer prevents contention |
| Latency-sensitive code | Logging overhead must be minimal |
| Background tasks | Don't slow down main thread |

### Use Sync When

| Scenario | Reason |
|----------|--------|
| Simple scripts | No background thread overhead |
| Low-throughput logging | Simple is better |
| Debug logging | Immediate output guaranteed |
| Small files | No queue overhead needed |
| Error logging only | Critical messages must be immediate |

### Decision Guide

```python
from logly import logger

logger.remove()

# High-throughput: use enqueue
logger.add("app.log", enqueue=True, rotation="100 MB")

# Network sink: use enqueue
logger.add(http_sink, enqueue=True)

# Low-throughput: sync is fine
logger.add("errors.log", level="ERROR")

# Debug: sync for immediate output
logger.add("stderr", level="DEBUG")
```

## Common Patterns

### High-Throughput Logging

```python
from logly import logger
import time

logger.remove()

# High-throughput with bounded queue
logger.add(
    "app.log",
    enqueue=True,
    backpressure="block",
    rotation="100 MB",
    retention="7 days",
    compression="gzip",
)

def process_batch(items):
    """Process a batch of items with logging."""
    for item in items:
        logger.debug("Processing {}", item)
        result = transform(item)
        logger.trace("Transformed {}", result)
    logger.info("Batch complete: {} items", len(items))

# Process millions of items
for batch in get_batches():
    process_batch(batch)

logger.complete()
```

### Web Server Logging

```python
from logly import logger

logger.remove()

# Request logging (high throughput)
logger.add(
    "access.log",
    enqueue=True,
    backpressure="drop_newest",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
)

# Error logging (must not lose)
logger.add(
    "errors.log",
    enqueue=True,
    backpressure="block",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {message}",
    backtrace=True,
)

def handle_request(request):
    with logger.contextualize(request_id=request["id"]):
        logger.info("{} {} {}", request["method"], request["path"], request["status"])
```

### Background Task Worker

```python
from logly import logger
import threading

logger.remove()

logger.add("worker.log", enqueue=True)

def background_worker():
    """Background worker with its own logging context."""
    with logger.contextualize(worker_id=threading.current_thread().name):
        while True:
            task = get_task()
            if task is None:
                break
            logger.info("Processing task {}", task["id"])
            try:
                result = execute(task)
                logger.success("Task {} completed", task["id"])
            except Exception:
                logger.exception("Task {} failed", task["id"])

# Start multiple workers
workers = [threading.Thread(target=background_worker) for _ in range(4)]
for w in workers:
    w.start()
for w in workers:
    w.join()

logger.complete()
```

### Application Lifecycle

```python
from logly import logger
import signal
import sys

def shutdown(signum, frame):
    """Graceful shutdown handler."""
    logger.warning("Received signal {}, shutting down", signum)
    logger.complete()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

def main():
    logger.remove()

    logger.add("app.log", enqueue=True)
    logger.add("errors.log", enqueue=True, level="ERROR")

    logger.info("Application started")

    try:
        run_application()
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
    except Exception:
        logger.exception("Fatal error")
    finally:
        logger.complete()

if __name__ == "__main__":
    main()
```

### Mixed Sync and Async

```python
from logly import logger

logger.remove()

# Sync for critical errors (immediate output)
logger.add(
    "stderr",
    level="ERROR",
    format="<red>{time:HH:mm:ss}</red> | <level>{level:<8}</level> | {message}",
    colorize=True,
)

# Async for high-throughput files
logger.add(
    "app.log",
    enqueue=True,
    rotation="daily",
)

# Async for network sink
logger.add(http_sink, enqueue=True)

logger.info("This goes to app.log and http_sink (async)")
logger.error("This goes to stderr (sync), app.log (async), and http_sink (async)")
logger.complete()
```

### Enqueue with Rotation

```python
from logly import logger

logger.remove()

logger.add(
    "app.log",
    enqueue=True,
    rotation="daily",
    retention=30,
    compression="gzip",
)

for i in range(100000):
    logger.info("High-volume message {}", i)

logger.complete()
```
