"""Google Cloud Logging integration example.

Sends log entries to Google Cloud Logging (formerly Stackdriver).
Requires: google-cloud-logging (pip install logly[google-cloud-logging])
"""

from logly import logger
from logly.integrations.google_cloud_logging import GoogleCloudLoggingSink

# Add Google Cloud Logging sink - uses Application Default Credentials
logger.add(
    GoogleCloudLoggingSink(
        project_id="my-gcp-project",
        log_name="my-app",
    ),
    level="WARNING",  # Only send warnings and above to Cloud Logging
)

logger.info("This goes to console only (below WARNING threshold)")
logger.warning("This goes to both console and Google Cloud Logging")
logger.error("Errors are sent with ERROR severity")

logger.complete()
