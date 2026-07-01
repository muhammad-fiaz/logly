"""Grafana Loki integration example.

Pushes log entries to Loki via HTTP. No extra dependencies required.
"""

from logly import logger
from logly.integrations.loki import LokiSink

# Add Loki sink with custom labels for stream identification
logger.add(
    LokiSink(
        endpoint="http://localhost:3100/loki/api/v1/push",
        labels={
            "app": "my-service",
            "env": "production",
            "region": "us-east-1",
        },
    ),
    level="INFO",
)

# With basic auth
# logger.add(
#     LokiSink(
#         endpoint="http://loki.example.com:3100/loki/api/v1/push",
#         labels={"app": "my-service"},
#         username="admin",
#         password="secret",
#     ),
#     level="INFO",
# )

logger.info("Request handled in {}ms", 42)
logger.warning("Cache miss rate above threshold")
logger.error("Failed to serialize payload")

logger.complete()
