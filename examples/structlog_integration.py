"""structlog integration example.

Bridges structlog processors and renderers with Logly for unified output.
"""

import structlog

from logly import logger
from logly.integrations.structlog import LoglyRenderer, logly_processor

# Option 1: Use logly_processor() - returns a full processor chain
# that includes merge_contextvars, add_log_level, TimeStamper, and Logly sink
structlog.configure(
    processors=logly_processor(),
    logger_factory=structlog.PrintLoggerFactory(),
)

log = structlog.get_logger()
log.info("hello", key="value")
log.warning("disk usage high", percent=92)

# Option 2: Use LoglyRenderer as a processor in your own chain
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        LoglyRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.BoundLogger,
)

log = structlog.get_logger()
log.info("structured event", request_id="abc-123")
log.error("something went wrong", retry=3)

logger.complete()
