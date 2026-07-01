"""Azure Monitor integration example.

Sends log entries to Azure Monitor / Application Insights via OpenTelemetry.
Requires: pip install opentelemetry-api opentelemetry-sdk azure-monitor-opentelemetry
"""

from logly import logger
from logly.integrations.azure_monitor import AzureMonitorSink

# Configure Azure Monitor sink
# Replace with your real connection string in production
# Format: "InstrumentationKey=<key>;IngestionEndpoint=<endpoint>"
logger.add(
    AzureMonitorSink(
        connection_string="InstrumentationKey=00000000-0000-0000-0000-000000000000;IngestionEndpoint=https://northcentralus-1.in.applicationinsights.azure.com/",
    ),
    level="WARNING",
)

# These will be sent to Azure Monitor
logger.warning("High CPU usage detected")
logger.error("Failed to process batch job")
logger.critical("Service health check failed")

# These will NOT be sent to Azure Monitor
logger.info("Normal operation")
logger.debug("Internal state updated")

logger.complete()
