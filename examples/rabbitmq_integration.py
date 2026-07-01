"""RabbitMQ integration example.

Publishes log entries to a RabbitMQ queue. Requires: pika (pip install logly[rabbitmq])
"""

from logly import logger
from logly.integrations.rabbitmq import RabbitMQHandler

# Add RabbitMQ handler
logger.add(
    RabbitMQHandler(
        "amqp://guest:guest@localhost:5672/",
        queue="app-logs",
        exchange="",  # Default exchange
        routing_key="app-logs",  # Routing key defaults to queue name
        durable=True,  # Queue survives broker restart
    ),
    level="INFO",
)

logger.info("Order {} placed by user {}", "ORD-001", "alice")
logger.warning("Inventory low for product {}", "SKU-123")
logger.error("Payment gateway returned 503")

logger.complete()
