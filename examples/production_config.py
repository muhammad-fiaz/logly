"""Production configuration example - comprehensive setup."""

from logly import logger

# Production setup with all features
logger.add(
    "logs/app.log",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}",
    rotation="daily",
    retention="30 days",
    compression="gzip",
    enqueue=True,
    serialize=False,
)

# Error monitoring
logger.add(
    "logs/errors.log",
    level="ERROR",
    rotation="daily",
    retention="90 days",
    compression="gzip",
    enqueue=True,
)

# JSON structured logs
logger.add(
    "logs/structured.json",
    level="WARNING",
    serialize=True,
    rotation="daily",
    retention="60 days",
    compression="gzip",
)

# Console output
logger.add("stderr", level="INFO", colorize=True)

logger.info("Application started")
logger.warning("Configuration loaded from env")
logger.error("Database connection retry")
logger.critical("Service degradation detected")
logger.complete()
