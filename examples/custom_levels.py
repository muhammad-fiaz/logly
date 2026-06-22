"""Custom log levels example.

Demonstrates how to register and use custom log levels with Logly.
"""

from logly import logger
from logly._logly import list_levels

# Register custom levels with priority ordering
logger.level("SECURITY", no=45, color="<red><bold>")
logger.level("METRIC", no=28, color="<blue>")

# Use custom levels via log()
logger.log("SECURITY", "Unauthorized access attempt")
logger.log("METRIC", "Response time: 235ms")

# Use the built-in AUDIT level (priority 35, between SUCCESS and WARNING)
logger.bind(user_id="12345").audit("Login successful")

# List all registered levels
logger.info("All registered levels: {}", list_levels())
