"""AWS CloudWatch Logs integration example.

Sends log entries to CloudWatch with automatic batching.
Requires: boto3 (pip install logly[aws])
"""

from logly import logger
from logly.integrations.aws_cloudwatch import CloudWatchSink

# Add CloudWatch sink with batching options
logger.add(
    CloudWatchSink(
        log_group="/app/production",
        log_stream="api-server",
        region="us-east-1",
        batch_size=10000,  # Max events per put_log_events call
        flush_interval=5.0,  # Flush every 5 seconds
        create_group=True,  # Auto-create log group if missing
        create_stream=True,  # Auto-create log stream if missing
    ),
    level="INFO",
)

logger.info("Request processed for user {}", "alice")
logger.warning("High memory usage detected")
logger.error("Database connection failed")

logger.complete()  # Flushes remaining buffered events
