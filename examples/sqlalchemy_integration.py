"""SQLAlchemy integration example.

Demonstrates how to route SQLAlchemy engine and query logs through Logly
using ``setup_sqlalchemy_logging``.
"""

from __future__ import annotations

from sqlalchemy import create_engine, text

from logly import logger
from logly.integrations.sqlalchemy import setup_sqlalchemy_logging


def main() -> None:
    """Set up logging and run a simple query."""
    # Configure SQLAlchemy logging via Logly
    setup_sqlalchemy_logging(level="INFO")

    logger.info("Creating SQLAlchemy engine")
    engine = create_engine("sqlite:///:memory:", echo=False)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        logger.info("Query result: {}", result.scalar())

    logger.success("SQLAlchemy demo completed")


if __name__ == "__main__":
    main()
