"""File logging example with rotation, retention, and compression."""

from logly import logger

# Simple file logging
sink_id = logger.add("app.log", level="DEBUG")
logger.info("Logging to file!")
logger.complete()
logger.remove(sink_id)

# Daily rotation with 7-day retention and gzip compression
sink_id = logger.add(
    "logs/daily.log",
    level="DEBUG",
    rotation="daily",
    retention=7,
    compression="gzip",
)
logger.info("This log will be rotated daily")
logger.complete()
logger.remove(sink_id)

# Size-based rotation (10MB limit)
sink_id = logger.add("logs/app.log", rotation="10 MB", retention=5)
logger.info("This log will be rotated when file reaches 10MB")
logger.complete()
logger.remove(sink_id)

# Hourly rotation
sink_id = logger.add("logs/hourly.log", rotation="hourly", retention=24)
logger.info("Hourly rotation with 24 hour retention")
logger.complete()
logger.remove(sink_id)

# Monthly rotation
sink_id = logger.add("logs/monthly.log", rotation="monthly", retention=12)
logger.info("Monthly rotation with 12 month retention")
logger.complete()
logger.remove(sink_id)
