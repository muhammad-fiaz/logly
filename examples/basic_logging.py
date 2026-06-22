"""Basic logging example - console output with different levels."""

from logly import logger

# Log at all built-in levels
logger.trace("Detailed trace information")
logger.debug("Debug information")
logger.info("Application started")
logger.notice("Notice message")
logger.success("Operation completed!")
logger.warning("Warning message")
logger.error("Error occurred")
logger.fail("Operation failed")
logger.critical("Critical system error!")
logger.fatal("Fatal system failure!")

# Format string with arguments
logger.info("User {} logged in from {}", "alice", "10.0.0.1")

# Flush all sinks
logger.complete()
