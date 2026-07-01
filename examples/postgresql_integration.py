"""PostgreSQL integration example - insert logs into PostgreSQL tables.

Demonstrates PostgresHandler with DSN and automatic table creation.
The handler creates the log table if it doesn't exist.

Requires: pip install psycopg2-binary
"""

from logly import logger
from logly.integrations.postgresql import PostgresHandler

handler = PostgresHandler(
    "postgresql://user:password@localhost:5432/logs",
    table="app_logs",
    create_table=True,  # Auto-create table if missing
)

logger.add(handler, level="WARNING")

logger.info("Connection established")  # Won't be stored
logger.warning("Query timeout exceeded")  # Inserted into PostgreSQL
logger.error("Replication lag detected")  # Inserted into PostgreSQL

logger.complete()
