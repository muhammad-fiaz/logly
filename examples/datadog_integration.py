"""Datadog integration example - send logs to Datadog Logs API.

Demonstrates DatadogSink with API key, service name, and custom tags.
No extra dependencies required (uses stdlib urllib).

Set your API key as an environment variable or pass directly:
    export DD_API_KEY=your-api-key-here
"""

import os

from logly import logger
from logly.integrations.datadog import DatadogSink

api_key = os.environ.get("DD_API_KEY", "your-datadog-api-key")

logger.add(
    DatadogSink(
        api_key=api_key,
        service="my-service",
        host="web-01.prod",
        tags=["env:production", "team:backend"],
        site="datadoghq.com",  # Use "datadoghq.eu" for EU site
    ),
    level="WARNING",
)

logger.info("Startup complete")  # Won't reach Datadog
logger.warning("Disk usage at 85%")  # Sent to Datadog
logger.error("API rate limit exceeded")  # Sent to Datadog

logger.complete()
