"""Enable/disable logging example."""

from logly import logger

# Basic info logging
logger.info("This appears")

# Disable logging for a specific name
logger.disable("myapp")
logger.info("This won't appear")

# Re-enable
logger.enable("myapp")
logger.info("This appears again")

# Disable for a different name
logger.disable("other_app")
logger.info("This still appears (different name)")

logger.complete()
