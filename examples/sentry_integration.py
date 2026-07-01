"""Sentry integration example - forward errors to Sentry.

Demonstrates SentrySink capturing error-level logs to Sentry with
level filtering. Only WARNING and above are forwarded by default.

Requires: pip install sentry-sdk
"""

from logly import logger
from logly.integrations.sentry import SentrySink

# In production, replace with your real DSN
# The sink initializes sentry_sdk.init() internally
logger.add(
    SentrySink(
        dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
        environment="development",
        release="my-app@1.0.0",
        level="WARNING",  # Only forward WARNING and above to Sentry
    ),
    level="INFO",  # Console still shows INFO and above
)

logger.info("Application started")  # Won't reach Sentry
logger.debug("Debug details")  # Won't reach Sentry
logger.warning("Low disk space")  # Reaches Sentry
logger.error("Database connection failed")  # Reaches Sentry

logger.complete()
