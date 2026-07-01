---
title: Seq
description: Send log records to Seq structured log server.
---

# Seq

`SeqHandler` sends structured log events to Seq via the HTTP Ingest API. No extra dependencies required.

## Installation

No extra dependencies are needed (stdlib only).

::: code-group

```bash [uv]
uv add logly
```

```bash [pip]
pip install logly
```

:::

## Usage

```python
from logly import logger
from logly.integrations.seq import SeqHandler

logger.add(
    SeqHandler(
        server_url="http://localhost:5341",
    )
)
```

## Full Example

```python
from logly import logger
from logly.integrations.seq import SeqHandler

logger.add(
    SeqHandler(
        server_url="http://localhost:5341",
        api_key="your-api-key",
        event_type="MyApp",
    ),
    level="INFO",
)

logger.info("Order placed", order_id="ord-456", total=99.99)
logger.warning("Stock low", product_widget=3)
```
