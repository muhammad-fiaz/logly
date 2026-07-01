"""Graylog GELF integration example.

Sends log entries in GELF format over TCP or UDP. No extra dependencies required.
"""

from logly import logger
from logly.integrations.graylog import GraylogSink

# Option 1: UDP transport (default, faster but no delivery guarantee)
logger.add(
    GraylogSink(
        host="localhost",
        port=12201,
        protocol="udp",
        graylog_version="1.1",  # GELF 1.1 enables compression
        facility="my-application",
    ),
    level="INFO",
)

# Option 2: TCP transport (reliable delivery)
# logger.add(
#     GraylogSink(
#         host="graylog.example.com",
#         port=12201,
#         protocol="tcp",
#         facility="my-application",
#     ),
#     level="INFO",
# )

logger.info("User logged in from {}", "10.0.0.1")
logger.warning("Disk usage at 85%")
logger.error("Failed to connect to upstream service")

logger.complete()
