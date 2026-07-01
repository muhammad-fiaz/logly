"""New Relic integration example.

Sends log entries to New Relic via the agent API. Requires: newrelic (pip install logly[newrelic])
"""

from logly import logger
from logly.integrations.newrelic import NewRelicSink

# Add New Relic sink
logger.add(
    NewRelicSink(
        license_key="your-license-key",  # Or set NEW_RELIC_LICENSE_KEY env var
        app_name="My Application",  # Or set NEW_RELIC_APP_NAME env var
    ),
    level="WARNING",
)

logger.info("Startup complete - below threshold")
logger.warning("Response time degraded for endpoint /api/search")
logger.error("Payment processing failed for user {}", "user-42")
logger.critical("Circuit breaker opened for payment gateway")

logger.complete()
