"""Celery integration example.

Routes all Celery worker and task logs through Logly using the
on_after_configure signal.
"""

from celery import Celery

from logly import logger
from logly.integrations.celery import setup_celery_logging

app = Celery("myapp")

# Connect Logly to Celery's logging system
# This intercepts logs from celery, celery.app, celery.task, celery.worker
app.conf.on_after_configure.connect(setup_celery_logging)


@app.task
def add(x: int, y: int) -> int:
    logger.info("Computing {} + {}", x, y)
    return x + y


@app.task
def process_data(data: dict) -> str:
    logger.bind(task_name="process_data").info("Processing {}", data)
    result = str(data).upper()
    logger.success("Processing complete")
    return result


# Run worker with: celery -A examples.celery_integration worker --loglevel=INFO
