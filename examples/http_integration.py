"""HTTP integration example.

Sends log entries to an HTTP endpoint with JSON or text format.
Uses stdlib urllib - no extra dependencies needed.
"""

from logly import logger
from logly.integrations.http import HttpHandler

# JSON format (default) - wraps message in {"message": "..."}
json_handler = HttpHandler(
    "https://httpbin.org/post",
    method="POST",
    headers={"Authorization": "Bearer your-token"},
    timeout=5.0,
    format="json",
)

# Text format - sends plain text body
text_handler = HttpHandler(
    "https://httpbin.org/post",
    method="POST",
    headers={"X-Custom-Header": "value"},
    timeout=5.0,
    format="text",
)

# Add handlers at different levels
logger.add(json_handler, level="ERROR")
logger.add(text_handler, level="WARNING")

# These will be sent to the endpoints
logger.warning("Disk usage threshold exceeded")
logger.error("Failed to connect to database")

logger.complete()
