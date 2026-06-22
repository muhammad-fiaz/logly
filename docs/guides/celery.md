# Celery Integration

Logly integrates with Celery to route worker task logs through the Rust-powered engine.

## Setup

```python
from celery import Celery
from logly.integrations.celery import setup_celery_logging

app = Celery("myapp")

# Connect Logly to Celery's logging
app.conf.on_after_configure.connect(setup_celery_logging)
```

## Configuration

```python
setup_celery_logging(
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)
```

## Patching Task Loggers

For per-task logging:

```python
@app.task
def my_task():
    from logly.integrations.celery import patch_task_logger
    patch_task_logger(my_task.get_logger())
    # Task logs now go through Logly
```

## How It Works

- Replaces Celery's logging handlers with `InterceptHandler` from `logly.integrations.stdlib`
- All Celery logs (worker, task, beat) are routed through Logly
- Supports all Logly features: rotation, filtering, custom levels, etc.
