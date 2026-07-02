---
title: Scheduler & Background Tasks
description: Manage periodic and scheduled background tasks with Logly
---

# Scheduler & Background Tasks

Logly provides `logger.start()` and `logger.stop()` methods for managing application lifecycle hooks. Use them for log rotation, health checks, metrics collection, and any task that needs to run at application startup or shutdown.

## Basic Usage

```python
from logly import logger

# Configure logger
logger.add("app.log", level="INFO")

# Start background processing
logger.start()

# Application runs...

# Flush and stop on shutdown
logger.stop()
```

::: info
`logger.start()` accepts optional lifecycle hooks for compatibility with service startup code. `logger.stop()` flushes all sinks and stops background workers.
:::

## Application Lifecycle

### Web Application

```python
import time
from logly import logger

logger.add(
    "app.log",
    level="INFO",
    rotation="daily",
    retention="30 days",
    compression="gzip",
)

# Start background processing
logger.start()

def run_server():
    # Simulate server workload
    for i in range(100):
        logger.info("Processing request {}", i)
        time.sleep(0.1)

try:
    run_server()
except KeyboardInterrupt:
    logger.warning("Shutting down")
finally:
    logger.stop()
```

### Background Worker

```python
import time
from logly import logger

logger.add("worker.log", enqueue=True, level="DEBUG")

# Start background processing
logger.start()

def background_worker():
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

background_worker()

# Flush and stop
logger.stop()
```

## Periodic Log Rotation

Use `logger.stop()` to flush before rotation, then `logger.reinstall()` to reset file handlers:

```python
import time
import signal
from logly import logger

logger.add(
    "app.log",
    level="INFO",
    rotation="daily",
    retention="30 days",
)

def rotate_logs(signum, frame):
    logger.info("Log rotation triggered")
    logger.stop()
    logger.reinstall()
    logger.add(
        "app.log",
        level="INFO",
        rotation="daily",
        retention="30 days",
    )

signal.signal(signal.SIGUSR1, rotate_logs)

logger.start()

# Application runs...
try:
    while True:
        logger.info("Heartbeat")
        time.sleep(60)
except KeyboardInterrupt:
    logger.info("Shutting down")
finally:
    logger.stop()
```

## Health Checks

```python
import time
from logly import logger

logger.add("app.log", level="INFO")

def health_check():
    try:
        status = "healthy"
        logger.debug("Health check: {}", status)
    except Exception as e:
        logger.error("Health check failed: {}", e)

logger.start()

# Run periodic health checks
for _ in range(10):
    health_check()
    time.sleep(30)

logger.stop()
```

## Metrics Collection

```python
import time
from logly import logger

request_count = 0
error_count = 0

logger.add("metrics.log", level="INFO")

def flush_metrics():
    global request_count, error_count
    logger.info(
        "Metrics: requests={} errors={}",
        request_count,
        error_count,
    )
    request_count = 0
    error_count = 0

logger.start()

# Simulate request handling
for i in range(100):
    request_count += 1
    if i % 10 == 0:
        error_count += 1
    if i % 20 == 0:
        flush_metrics()

logger.stop()
```

## Multiple Sinks with Enqueue

When using `enqueue=True`, `logger.stop()` flushes all queued messages:

```python
from logly import logger

logger.remove()

logger.add("app.log", level="INFO", enqueue=True)
logger.add("errors.log", level="ERROR", enqueue=True)
logger.add("debug.log", level="DEBUG", enqueue=True)

logger.start()

logger.info("Application started")
logger.error("Something went wrong")
logger.debug("Debug details")

logger.stop()  # Flushes all queued messages
print("All messages flushed")
```

## Signal Handling

```python
import signal
import sys
from logly import logger

logger.add("app.log", enqueue=True)

def shutdown(signum, frame):
    logger.warning("Received signal {}, shutting down", signum)
    logger.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

logger.start()

# Application runs...
logger.info("Application running")

# Note: In production, the process would run indefinitely
```

## Thread Safety

::: info
`logger.start()` and `logger.stop()` are thread-safe:

- Queued sinks use thread-safe queues
- `stop()` drains the queue and waits for all messages to be processed
- Multiple threads can safely log while `stop()` is in progress
:::

```python
import threading
import time
from logly import logger

logger.add("app.log", enqueue=True)

def worker(worker_id: int):
    for i in range(10):
        logger.info("Worker {} message {}", worker_id, i)
        time.sleep(0.01)

logger.start()

threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()

logger.stop()
```

## Complete Example

```python
import time
from logly import logger

# Configure logger
logger.add(
    "app.log",
    level="DEBUG",
    rotation="daily",
    retention="30 days",
    compression="gzip",
    enqueue=True,
)

# Start background processing
logger.start()

# Simulate application workload
for i in range(10):
    logger.info("Processing item {}", i)
    time.sleep(1)

# Cleanup
logger.stop()
logger.info("App shutting down")
```
