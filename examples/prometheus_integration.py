"""Prometheus integration example.

Exposes log metrics (count by level, message size) via Prometheus client.
Requires: pip install prometheus-client
"""

from prometheus_client import start_http_server

from logly import logger
from logly.integrations.prometheus import PrometheusLogSink

# Add Prometheus sink - counts log messages by level and tracks sizes
logger.add(PrometheusLogSink(namespace="myapp"), level="INFO")

# Start Prometheus metrics server on port 8000
# Access metrics at http://localhost:8000/metrics
start_http_server(8000)

# Generate some log traffic
logger.info("Application started")
logger.warning("Configuration loaded from env")
logger.error("Database connection retry")
logger.info("Request processed")
logger.warning("Cache miss for key user:123")

# View metrics:
#   myapp_log_total{level="INFO"} 2
#   myapp_log_total{level="WARNING"} 2
#   myapp_log_total{level="ERROR"} 1
#   myapp_log_message_size_bytes_bucket{...}

logger.complete()
