"""Seq structured log server integration example.

Sends structured log records to a Seq server via HTTP API. No extra dependencies.
"""

from logly import logger
from logly.integrations.seq import SeqSink

# Add Seq sink with optional API key
logger.add(
    SeqSink(
        server_url="http://localhost:5341",
        api_key="your-seq-api-key",  # Optional, omit for unauthenticated
        event_template={  # Merged into every event
            "app": "my-service",
            "env": "production",
        },
    ),
    level="WARNING",
)

logger.info("This is below threshold - console only")
logger.warning("Request latency exceeded 500ms")
logger.error("Order processing failed for order {}", "ORD-12345")
logger.critical("Service health check failed")

logger.complete()
