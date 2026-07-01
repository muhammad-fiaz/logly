"""PropagateHandler integration example.

Bridges Logly messages back to Python's standard logging module.
Useful for feeding into existing stdlib-based monitoring tools.
"""

import logging

from logly import logger
from logly.integrations.propagate import PropagateHandler

# Configure stdlib logging first
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

# Route all Logly messages through stdlib logging
logger.add(PropagateHandler(name="myapp", level=logging.NOTSET))

# These go through Logly -> stdlib logging
logger.info("Application started")
logger.warning("Configuration using defaults for missing keys")
logger.error("Database query timeout after {}ms", 5000)

logger.complete()
