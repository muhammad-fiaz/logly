"""Elasticsearch integration example - index logs into Elasticsearch.

Demonstrates ElasticsearchSink with index patterns and optional
basic authentication.

Requires: pip install elasticsearch
"""

from logly import logger
from logly.integrations.elasticsearch import ElasticsearchSink

# Index with date-based pattern for daily rotation
logger.add(
    ElasticsearchSink(
        "http://localhost:9200",
        index="logs-{time:YYYY.MM.DD}",
        timeout=5.0,
    ),
    level="WARNING",
)

# With basic authentication
# logger.add(
#     ElasticsearchSink(
#         "http://localhost:9200",
#         index="logs-production",
#         username="elastic",
#         password="changeme",
#     ),
#     level="ERROR",
# )

logger.info("Request processed")  # Won't be indexed
logger.warning("High memory usage")  # Indexed
logger.error("Service unavailable")  # Indexed

logger.complete()
