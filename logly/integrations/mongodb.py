"""MongoDB integration for Logly.

Provides ``MongoHandler`` that inserts log entries into MongoDB collections.

Requires ``pymongo``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[mongodb]

    # Option 2: pip
    pip install "logly[mongodb]"

    # Option 3: uv without extras
    uv add pymongo

    # Option 4: pip without extras
    pip install pymongo
"""

from __future__ import annotations

import importlib.util
import time

_IMPORT_MSG = (
    "pymongo is required for Logly MongoDB integration.\n"
    "Install with one of:\n"
    "  uv add logly[mongodb]       # recommended\n"
    "  pip install logly[mongodb]\n"
    "  uv add pymongo\n"
    "  pip install pymongo"
)


class MongoHandler:
    """Insert log entries into a MongoDB collection.

    Usage::

        from logly import logger
        from logly.integrations.mongodb import MongoHandler

        handler = MongoHandler(
            "mongodb://localhost:27017",
            database="logs",
            collection="app_logs",
        )
        logger.add(handler, level="WARNING")

    Args:
        uri: MongoDB connection URI.
        database: Database name.
        collection: Collection name.
        timeout: Socket timeout in seconds.
    """

    def __init__(
        self,
        uri: str = "mongodb://localhost:27017",
        *,
        database: str = "logly",
        collection: str = "logs",
        timeout: float = 5.0,
    ) -> None:
        """Initialize the MongoDB handler.

        Args:
            uri: MongoDB connection URI.
            database: Database name.
            collection: Collection name.
            timeout: Socket timeout in seconds.

        Raises:
            ImportError: If ``pymongo`` is not installed.
        """
        if importlib.util.find_spec("pymongo") is None:
            raise ImportError(_IMPORT_MSG)

        from pymongo import MongoClient  # noqa: PLC0415

        self._client = MongoClient(
            uri,
            serverSelectionTimeoutMS=int(timeout * 1000),
        )
        self._collection = self._client[database][collection]

    def write(self, message: str) -> None:
        """Insert one log entry into MongoDB."""
        self._collection.insert_one(
            {
                "message": message.rstrip("\n"),
                "timestamp": time.time(),
            }
        )

    def flush(self) -> None:
        """No-op for MongoDB handler."""

    def close(self) -> None:
        """Close the MongoDB client."""
        self._client.close()
