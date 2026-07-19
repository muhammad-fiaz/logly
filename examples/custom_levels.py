"""Custom log levels example.

Demonstrates how to register and use custom log levels with Logly.
"""

from logly import logger
from logly._logly import list_levels

# Register custom levels with priority ordering
logger.level("SECURITY", no=45, color="bold red")
logger.level("METRIC", no=28, color="blue")

# Use custom levels via log()
logger.log("SECURITY", "Unauthorized access attempt")
logger.log("METRIC", "Response time: 235ms")

# Bound context works with custom levels as well.
logger.bind(user_id="12345").log("SECURITY", "Login successful")

# List all registered levels
logger.info("All registered levels: {}", list_levels())
