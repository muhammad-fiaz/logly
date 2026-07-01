"""Slack integration example.

Sends log entries to a Slack incoming webhook for team notifications.
Uses stdlib urllib - no extra dependencies needed.
"""

from logly import logger
from logly.integrations.slack import SlackHandler

# Configure Slack webhook handler
# Replace with your real webhook URL in production
handler = SlackHandler(
    webhook_url="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX",
    channel="#alerts",
    username="Logly Bot",
    icon_emoji=":robot_face:",
    timeout=10.0,
)

# Only send warnings and above to Slack
logger.add(handler, level="WARNING")

# These will be sent to Slack
logger.warning("High memory usage detected")
logger.error("Service unavailable: connection refused")

# These will NOT be sent to Slack
logger.info("Request processed successfully")
logger.debug("Cache hit for key user:123")

logger.complete()
