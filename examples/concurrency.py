"""Concurrency and background worker example."""

from logly import logger

# Enqueue mode - writes in background
sink_id = logger.add("async.log", enqueue=True)
for i in range(100):
    logger.info("Background message {}", i)
logger.complete()
logger.remove(sink_id)

# Enqueue with file rotation
sink_id = logger.add(
    "async_rotate.log",
    enqueue=True,
    rotation="daily",
    retention=7,
)
for i in range(50):
    logger.info("Async rotated message {}", i)
logger.complete()
logger.remove(sink_id)

# Synchronous mode (default)
sink_id = logger.add("sync.log", enqueue=False)
for i in range(10):
    logger.info("Sync message {}", i)
logger.complete()
logger.remove(sink_id)
