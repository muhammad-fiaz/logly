"""Discord integration example - send logs to Discord webhooks.

Demonstrates DiscordHandler forwarding error-level logs to a Discord
channel via webhook. No extra dependencies required.

Create a webhook at: Server Settings > Integrations > Webhooks
"""

from logly import logger
from logly.integrations.discord import DiscordHandler

# Replace with your actual Discord webhook URL
webhook_url = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"

handler = DiscordHandler(
    webhook_url,
    username="Logly Bot",  # Override webhook display name
    avatar_url=None,  # Optional: override avatar
    timeout=10.0,
)

# Only send errors and above to Discord
logger.add(handler, level="ERROR")

logger.info("Server started")  # Won't reach Discord
logger.warning("Low memory")  # Won't reach Discord
logger.error("Database down")  # Sent to Discord
logger.critical("Service offline")  # Sent to Discord

logger.complete()
