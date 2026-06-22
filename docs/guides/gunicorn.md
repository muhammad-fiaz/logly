---
title: Gunicorn Integration
description: Integrating Logly with Gunicorn
---

# Gunicorn Integration

## Basic Setup

Use the Logly logging hook for Gunicorn:

```python
# gunicorn.conf.py
from logly import logger

def on_starting(server):
    """Called just before the master process is initialized."""
    logger.add("gunicorn.log", level="INFO")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    logger.info("Worker spawned (pid: {})", worker.pid)
```

## Custom Error Logging

```python
# gunicorn.conf.py
from logly import logger

def post_worker_init(worker):
    """Called just after a worker has been initialized."""
    logger.add(
        f"worker-{worker.pid}.log",
        level="DEBUG",
        rotation="100 MB",
        retention="7 days",
    )

def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    logger.info("Worker exiting (pid: {})", worker.pid)
    logger.complete()
```

## Configuration

```bash
# Run Gunicorn with Logly config
gunicorn app:app -c gunicorn.conf.py --workers 4
```

::: tip
Call `logger.complete()` in the `worker_exit` hook to ensure all enqueued messages are flushed before the worker terminates.
:::
