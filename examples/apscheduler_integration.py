"""APScheduler integration example.

Demonstrates how to route APScheduler job logs through Logly using
``APSchedulerHandler`` with a ``BackgroundScheduler``.
"""

from __future__ import annotations

import logging
import time

from apscheduler.schedulers.background import BackgroundScheduler

from logly import logger
from logly.integrations.apscheduler import APSchedulerHandler


def sample_job() -> None:
    """Simulate a scheduled job."""
    logger.info("Executing scheduled job")
    time.sleep(0.1)
    logger.success("Job completed successfully")


def main() -> None:
    """Set up scheduler and run a job."""
    # Attach Logly handler to the apscheduler logger
    handler = APSchedulerHandler()
    logging.getLogger("apscheduler").addHandler(handler)
    logging.getLogger("apscheduler").setLevel(logging.DEBUG)

    scheduler = BackgroundScheduler()
    scheduler.add_job(sample_job, "interval", seconds=1)
    scheduler.start()

    logger.info("Scheduler started – waiting for job execution")
    time.sleep(2)

    scheduler.shutdown()
    logger.info("Scheduler shut down")


if __name__ == "__main__":
    main()
