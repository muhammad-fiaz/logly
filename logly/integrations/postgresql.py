"""PostgreSQL integration for Logly.

Provides ``PostgresHandler`` that inserts log entries into PostgreSQL tables.

Requires ``psycopg2``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[postgresql]

    # Option 2: pip
    pip install "logly[postgresql]"

    # Option 3: uv without extras
    uv add psycopg2-binary

    # Option 4: pip without extras
    pip install psycopg2-binary
"""

from __future__ import annotations

import importlib.util
import time

_IMPORT_MSG = (
    "psycopg2 is required for Logly PostgreSQL integration.\n"
    "Install with one of:\n"
    "  uv add logly[postgresql]       # recommended\n"
    "  pip install logly[postgresql]\n"
    "  uv add psycopg2-binary\n"
    "  pip install psycopg2-binary"
)

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS {table} (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    timestamp DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
)
"""


class PostgresHandler:
    """Insert log entries into a PostgreSQL table.

    Usage::

        from logly import logger
        from logly.integrations.postgresql import PostgresHandler

        handler = PostgresHandler(
            "postgresql://user:pass@localhost:5432/logs",
            table="app_logs",
        )
        logger.add(handler, level="WARNING")

    Args:
        dsn: PostgreSQL connection string.
        table: Table name for log storage.
        create_table: Automatically create table if it does not exist.
    """

    def __init__(
        self,
        dsn: str = "postgresql://localhost:5432/logly",
        *,
        table: str = "logly_logs",
        create_table: bool = True,
    ) -> None:
        """Initialize the PostgreSQL handler.

        Args:
            dsn: PostgreSQL connection string.
            table: Table name for log storage.
            create_table: Automatically create table if it does not exist.

        Raises:
            ImportError: If ``psycopg2`` is not installed.
        """
        if importlib.util.find_spec("psycopg2") is None:
            raise ImportError(_IMPORT_MSG)

        import psycopg2 as _psycopg2  # noqa: PLC0415

        self._conn = _psycopg2.connect(dsn)
        self._table = table

        if create_table:
            self._ensure_table()

    def _ensure_table(self) -> None:
        """Create the log table if it does not exist."""
        with self._conn.cursor() as cur:
            cur.execute(_CREATE_TABLE_SQL.format(table=self._table))
        self._conn.commit()

    def write(self, message: str) -> None:
        """Insert one log entry into PostgreSQL."""
        with self._conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {self._table} (message, timestamp) VALUES (%s, %s)",
                (message.rstrip("\n"), time.time()),
            )
        self._conn.commit()

    def flush(self) -> None:
        """Commit any pending transaction."""
        self._conn.commit()

    def close(self) -> None:
        """Close the PostgreSQL connection."""
        self._conn.close()
