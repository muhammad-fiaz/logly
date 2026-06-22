"""JSON structured logging example."""

from logly import logger

# JSON output to file
sink_id = logger.add("app.json", serialize=True, rotation="daily")
logger.info("JSON formatted log")
logger.bind(user_id=123).warning("JSON warning with data")
logger.bind(error_code=500).error("JSON error")
logger.complete()
logger.remove(sink_id)

# JSON output to console with color
sink_id = logger.add("stdout", serialize=True, colorize=True)
logger.info("JSON to console with color")
logger.complete()
logger.remove(sink_id)

# JSON to stderr
sink_id = logger.add("stderr", serialize=True)
logger.error("JSON error to stderr")
logger.complete()
logger.remove(sink_id)
