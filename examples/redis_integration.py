"""Redis integration example - push logs to Redis lists or streams.

Demonstrates RedisHandler with both list and stream modes for
sending log entries to Redis.

Requires: pip install redis
"""

from logly import logger
from logly.integrations.redis import RedisHandler

# List mode (default) - uses LPUSH, good for simple consumers
list_handler = RedisHandler(
    "redis://localhost:6379/0",
    key="app:logs:list",
    mode="list",
)

# Stream mode - uses XADD with maxlen, good for persistent consumers
stream_handler = RedisHandler(
    "redis://localhost:6379/0",
    key="app:logs:stream",
    mode="stream",
    max_stream_len=5000,
)

# Add both handlers
logger.add(list_handler, level="INFO")
logger.add(stream_handler, level="WARNING")

logger.info("User logged in")
logger.warning("Rate limit approaching")
logger.error("Payment processing failed")

logger.complete()
