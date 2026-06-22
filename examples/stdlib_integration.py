"""Stdlib logging integration example."""

import logging

from logly import logger
from logly.integrations.stdlib import InterceptHandler

# Route stdlib logging through Logly
logging.basicConfig(
    handlers=[InterceptHandler()],
    level=logging.INFO,
    format="",
)

# These now go through Logly
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.info("Uvicorn request processed")

django_logger = logging.getLogger("django")
django_logger.warning("Django warning routed through Logly")

# Flask
flask_logger = logging.getLogger("flask")
flask_logger.error("Flask error routed through Logly")

logger.complete()
