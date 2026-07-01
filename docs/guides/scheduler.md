---
title: Scheduler & Background Tasks
description: Manage periodic and scheduled background tasks with Logly's built-in scheduler
---

# Scheduler & Background Tasks

Logly includes a built-in scheduler powered by Rust for managing periodic background tasks. Use it for log rotation, health checks, metrics collection, and any task that needs to run at regular intervals.

## Interval

The `Interval` class defines the time between task runs.

### `Interval.from_secs()`

```python
from logly._logly import Interval

# Run every 30 seconds
interval = Interval.from_secs(30)
```

### `Interval.from_mins()`

```python
from logly._logly import Interval

# Run every 5 minutes
interval = Interval.from_mins(5)
```

### `Interval.duration()`

Returns the `Duration` between runs.

```python
from logly._logly import Interval
from datetime import timedelta

interval = Interval.from_mins(2)
print(interval.duration())  # timedelta(seconds=120)
```

### Using `Duration` Directly

```python
from logly._logly import Interval
from datetime import timedelta

# Custom interval using timedelta
interval = Interval(timedelta(seconds=45))
```

## ScheduledTask

A `ScheduledTask` wraps a function and runs it periodically on a background thread.

### Creating and Starting a Task

```python
import time
from logly._logly import ScheduledTask, Interval

def collect_metrics():
    print("Collecting metrics...")

# Task starts immediately on creation
task = ScheduledTask("metrics", Interval.from_secs(10), collect_metrics)

time.sleep(35)  # Let it run a few cycles
task.stop()
```

### Task Properties

```python
from logly._logly import ScheduledTask, Interval

def my_task():
    pass

task = ScheduledTask("health-check", Interval.from_mins(1), my_task)

print(task.name())       # "health-check"
print(task.interval())   # Interval object with 60s duration
task.stop()
```

### Stopping a Task

```python
from logly._logly import ScheduledTask, Interval

def background_work():
    print("working...")

task = ScheduledTask("worker", Interval.from_secs(5), background_work)
# ... later
task.stop()  # Cleanly stops the background thread
```

::: warning
Always call `stop()` before the task goes out of scope. The `Drop` implementation will attempt to join the thread, but explicit stopping is preferred.
:::

## Scheduler

The `Scheduler` class manages multiple `ScheduledTask` instances as a group.

### Creating a Scheduler

```python
from logly._logly import Scheduler

scheduler = Scheduler()
print(scheduler.task_count())  # 0
```

### Scheduling Tasks

```python
import time
from logly._logly import Scheduler, Interval

scheduler = Scheduler()

# Schedule multiple tasks
scheduler.schedule("log-rotation", Interval.from_mins(60), lambda: print("rotating"))
scheduler.schedule("health-check", Interval.from_secs(30), lambda: print("checking"))
scheduler.schedule("metrics", Interval.from_mins(5), lambda: print("metrics"))

print(scheduler.task_count())  # 3

time.sleep(100)  # Let tasks run
scheduler.stop_all()
```

### Stopping All Tasks

```python
from logly._logly import Scheduler, Interval

scheduler = Scheduler()

scheduler.schedule("task1", Interval.from_secs(10), lambda: print("t1"))
scheduler.schedule("task2", Interval.from_secs(20), lambda: print("t2"))

# Stop all tasks at once
scheduler.stop_all()
print(scheduler.task_count())  # 0
```

::: tip
The `Scheduler` also stops all tasks automatically when it is dropped (goes out of scope).
:::

### Task Count

```python
from logly._logly import Scheduler, Interval

scheduler = Scheduler()
scheduler.schedule("a", Interval.from_secs(60), lambda: None)
scheduler.schedule("b", Interval.from_secs(60), lambda: None)
scheduler.schedule("c", Interval.from_secs(60), lambda: None)

print(scheduler.task_count())  # 3
scheduler.stop_all()
```

## Use Cases

### Periodic Log Rotation

```python
import time
from logly import logger
from logly._logly import Scheduler, Interval

def rotate_logs():
    logger.reinstall()  # Reset all file handlers
    logger.info("Log rotation completed")

scheduler = Scheduler()
scheduler.schedule("log-rotation", Interval.from_mins(60), rotate_logs)

# Application runs...
time.sleep(3600)
scheduler.stop_all()
```

### Health Checks

```python
import time
from logly import logger
from logly._logly import Scheduler, Interval

def health_check():
    try:
        # Simulate health check
        status = "healthy"
        logger.debug("Health check: {}", status)
    except Exception as e:
        logger.error("Health check failed: {}", e)

scheduler = Scheduler()
scheduler.schedule("health", Interval.from_secs(30), health_check)
```

### Metrics Collection

```python
import time
from logly import logger
from logly._logly import Scheduler, Interval

request_count = 0
error_count = 0

def flush_metrics():
    global request_count, error_count
    logger.info(
        "Metrics: requests={} errors={}",
        request_count,
        error_count,
    )
    request_count = 0
    error_count = 0

scheduler = Scheduler()
scheduler.schedule("metrics", Interval.from_mins(1), flush_metrics)

# In request handlers:
request_count += 1
```

### Combined Scheduler Setup

```python
import time
from logly import logger
from logly._logly import Scheduler, Interval

scheduler = Scheduler()

# Log rotation every hour
scheduler.schedule("rotation", Interval.from_mins(60), lambda: logger.reinstall())

# Health check every 30 seconds
scheduler.schedule("health", Interval.from_secs(30), lambda: logger.debug("alive"))

# Metrics flush every 5 minutes
scheduler.schedule("metrics", Interval.from_mins(5), lambda: logger.info("flush metrics"))

logger.info("Scheduler started with {} tasks", scheduler.task_count())

# Run application
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    scheduler.stop_all()
    logger.info("Scheduler stopped")
```

## Thread Safety

::: info
All scheduler primitives are thread-safe:

- `Scheduler` uses a `Mutex` internally to protect the task list
- `ScheduledTask` uses `AtomicBool` for the running flag
- Tasks run on dedicated background threads
- `stop()` and `stop_all()` safely join threads
:::

```python
import threading
from logly import logger
from logly._logly import Scheduler, Interval

scheduler = Scheduler()

def thread_safe_task():
    # This runs on a background thread
    logger.info("Task running from thread: {}", threading.current_thread().name)

scheduler.schedule("threaded", Interval.from_secs(5), thread_safe_task)
```

## Complete Example

```python
import time
from logly import logger
from logly._logly import Scheduler, Interval

# Configure logger
logger.add(
    "app.log",
    level="DEBUG",
    rotation="daily",
    retention="30 days",
    compression="gzip",
)

# Create scheduler
scheduler = Scheduler()

# Background log rotation
def rotate_logs():
    logger.reinstall()
    logger.info("Logs rotated")

# Background health check
def health_check():
    logger.debug("Health OK")

# Schedule tasks
scheduler.schedule("rotation", Interval.from_mins(60), rotate_logs)
scheduler.schedule("health", Interval.from_secs(30), health_check)

logger.info("App started with {} scheduled tasks", scheduler.task_count())

# Simulate application workload
for i in range(10):
    logger.info("Processing item {}", i)
    time.sleep(1)

# Cleanup
scheduler.stop_all()
logger.complete()
logger.info("App shutting down")
```
