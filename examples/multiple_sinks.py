"""Multiple sinks example - log to console, file, and error file simultaneously."""

from logly import logger

# Console output
logger.add("stderr", level="INFO", format="{level:<8} | {message}")

# Application logs (all levels)
logger.add("app.log", level="DEBUG", rotation="daily", retention=30)

# Error-only file
logger.add("errors.log", level="ERROR", rotation="daily", retention=90)

# JSON output
logger.add("structured.json", serialize=True, level="WARNING", rotation="daily")

# This goes to all sinks
logger.info("This is an info message")
logger.warning("This is a warning")
logger.error("This is an error")

# This only goes to stderr, app.log, and errors.log
logger.debug("Debug details")

logger.complete()
