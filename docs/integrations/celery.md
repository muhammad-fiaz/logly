---
title: Celery
description: Task logging for Celery workers.
---

# Celery

`setup_celery_logging()` routes all Celery worker logs through Logly. `patch_task_logger()` patches individual task loggers.

## Installation

This integration requires the `celery` package.

::: code-group

```bash [uv]
uv add logly[celery]
```

```bash [pip]
pip install "logly[celery]"
```

```bash [uv (without extras)]
uv add celery
```

```bash [pip (without extras)]
pip install celery
```

:::

::: warning Missing Dependency
If `celery` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'celery'
```
:::

## Usage

```python
from celery import Celery
from logly.integrations.celery import setup_celery_logging

app = Celery("myapp")
app.conf.on_after_configure.connect(setup_celery_logging)
```

## Patch Task Logger

```python
@app.task
def my_task():
    from logly.integrations.celery import patch_task_logger
    patch_task_logger(my_task.get_logger())
    # ... task logic
```

## Full Example

```python
from celery import Celery
from logly.integrations.celery import setup_celery_logging, patch_task_logger

app = Celery("myapp")
app.conf.broker_url = "redis://localhost:6379/0"
app.conf.on_after_configure.connect(setup_celery_logging)

@app.task(bind=True)
def process_order(self, order_id):
    logger = self.get_logger()
    patch_task_logger(logger)
    logger.info("Processing order %s", order_id)
    # ... process order
    logger.info("Order %s completed", order_id)

@app.task
def send_email(recipient, subject, body):
    logger = send_email.get_logger()
    patch_task_logger(logger)
    logger.info("Sending email to %s", recipient)
    # ... send email
```
