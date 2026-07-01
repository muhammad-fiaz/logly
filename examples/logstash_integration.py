"""Logstash integration example.

Sends log entries as JSON over TCP or UDP. No extra dependencies required.
"""

from logly import logger
from logly.integrations.logstash import LogstashSink

# Add Logstash sink with tags
logger.add(
    LogstashSink(
        host="localhost",
        port=5959,
        protocol="tcp",
        message_type="logstash",
        tags=["app", "production", "python"],
        key_prefix="app.",  # Prefix all field names (e.g. "app.message")
    ),
    level="INFO",
)

# UDP variant
# logger.add(
#     LogstashSink(
#         host="logstash.example.com",
#         port=5044,
#         protocol="udp",
#         tags=["app", "staging"],
#     ),
#     level="DEBUG",
# )

logger.info("Application started on port {}", 8000)
logger.warning("Rate limit approaching for client {}", "192.168.1.1")
logger.error("Unhandled exception in worker thread")

logger.complete()
