---
title: PostgreSQL
description: Insert log entries into PostgreSQL tables.
---

# PostgreSQL

`PostgresHandler` inserts log entries into a PostgreSQL table using `psycopg2`. The table is created automatically if it does not exist.

## Installation

This integration requires the `psycopg2-binary` package.

::: code-group

```bash [uv]
uv add logly[postgresql]
```

```bash [pip]
pip install "logly[postgresql]"
```

```bash [uv (without extras)]
uv add psycopg2-binary
```

```bash [pip (without extras)]
pip install psycopg2-binary
```

:::

::: warning Missing Dependency
If `psycopg2` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'psycopg2'
```
:::

## Usage

```python
from logly import logger
from logly.integrations.postgresql import PostgresHandler

handler = PostgresHandler(
    "postgresql://user:pass@localhost:5432/logs",
    table="app_logs",
)
logger.add(handler, level="WARNING")
```

## Constructor Args

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `dsn` | `str` | `postgresql://localhost:5432/logly` | PostgreSQL connection string |
| `table` | `str` | `logly_logs` | Table name for log storage |
| `create_table` | `bool` | `True` | Automatically create table if it does not exist |

## Table Schema

The auto-created table has the following schema:

```sql
CREATE TABLE IF NOT EXISTS <table> (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    timestamp DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
)
```

## Tips

- Set `create_table=False` if you manage the schema yourself or want to add custom columns.
- Use connection pooling in production to avoid one connection per log message.

## Full Example

```python
from logly import logger
from logly.integrations.postgresql import PostgresHandler

handler = PostgresHandler(
    dsn="postgresql://dbuser:dbpass@db-host:5432/myapp",
    table="app_logs",
    create_table=True,
)
logger.add(handler, level="INFO")

logger.info("Order created", order_id="ord-789")
logger.error("Inventory sync failed")
```
