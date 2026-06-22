"""File rotation example with size and time-based policies."""

from logly import logger

# Size-based rotation
sink_id = logger.add(
    "logs/size_rotate.log",
    rotation="10 MB",
    retention=5,
    compression="gzip",
)
logger.info("Size-based rotation (10MB, keep 5 files)")
logger.complete()
logger.remove(sink_id)

# Daily rotation
sink_id = logger.add(
    "logs/daily_rotate.log",
    rotation="daily",
    retention=30,
    compression="bz2",
)
logger.info("Daily rotation (keep 30 days)")
logger.complete()
logger.remove(sink_id)

# Hourly rotation
sink_id = logger.add(
    "logs/hourly_rotate.log",
    rotation="hourly",
    retention=168,  # 7 days
    compression="xz",
)
logger.info("Hourly rotation (keep 7 days)")
logger.complete()
logger.remove(sink_id)

# Weekly rotation
sink_id = logger.add(
    "logs/weekly_rotate.log",
    rotation="weekly",
    retention=12,
    compression="zip",
)
logger.info("Weekly rotation (keep 12 weeks)")
logger.complete()
logger.remove(sink_id)

# Monthly rotation
sink_id = logger.add(
    "logs/monthly_rotate.log",
    rotation="monthly",
    retention=12,
    compression="zstd",
)
logger.info("Monthly rotation (keep 12 months)")
logger.complete()
logger.remove(sink_id)

# No rotation (append mode)
sink_id = logger.add("logs/append.log", rotation=None)
logger.info("Append mode - no rotation")
logger.complete()
logger.remove(sink_id)
