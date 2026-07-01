"""Kafka integration example - publish logs to Kafka topics.

Demonstrates KafkaHandler publishing log entries as JSON messages
to a Kafka topic using confluent-kafka.

Requires: pip install confluent-kafka
"""

from logly import logger
from logly.integrations.kafka import KafkaHandler

handler = KafkaHandler(
    "localhost:9092",
    topic="app-logs",
    client_id="logly-producer",
    acks="1",  # Leader acknowledgment only (fast)
    timeout=5.0,  # Delivery timeout in seconds
)

logger.add(handler, level="WARNING")

logger.info("Processing order")  # Won't reach Kafka
logger.warning("Inventory low")  # Published to Kafka
logger.error("Payment gateway timeout")  # Published to Kafka

# Use enqueue=True for non-blocking writes in production
logger.add(handler, level="ERROR", enqueue=True)

logger.complete()
