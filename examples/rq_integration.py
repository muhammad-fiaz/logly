"""RQ (Redis Queue) integration example.

Demonstrates how to route RQ worker logs through Logly using ``RQHandler``.
This example shows handler setup and log forwarding; a real Redis server
is not required for the demo.
"""

from __future__ import annotations

import logging

from logly import logger
from logly.integrations.rq import RQHandler


def main() -> None:
    """Set up RQ logging handlers and emit sample logs."""
    handler = RQHandler()

    rq_logger = logging.getLogger("rq")
    rq_logger.handlers = [handler]
    rq_logger.setLevel(logging.DEBUG)
    rq_logger.propagate = False

    rq_worker_logger = logging.getLogger("rq.worker")
    rq_worker_logger.handlers = [handler]
    rq_worker_logger.setLevel(logging.DEBUG)
    rq_worker_logger.propagate = False

    logger.info("RQ logging configured – emitting sample logs")

    rq_logger.info("RQ scheduler started")
    rq_worker_logger.info("Worker listening for jobs")
    rq_worker_logger.warning("Queue depth high")

    logger.success("RQ integration demo completed")


if __name__ == "__main__":
    main()
