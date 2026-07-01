"""MongoDB integration example - insert logs into MongoDB collections.

Demonstrates MongoHandler with URI, database, and collection settings.

Requires: pip install pymongo
"""

from logly import logger
from logly.integrations.mongodb import MongoHandler

handler = MongoHandler(
    "mongodb://localhost:27017",
    database="logs",
    collection="app_logs",
    timeout=5.0,
)

logger.add(handler, level="WARNING")

logger.info("User signed up")  # Won't be stored
logger.warning("Cache miss rate high")  # Inserted into MongoDB
logger.error("Order processing failed")  # Inserted into MongoDB

logger.complete()
