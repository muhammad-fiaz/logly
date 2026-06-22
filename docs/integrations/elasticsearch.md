---
title: Elasticsearch
description: Elasticsearch document indexing for log storage.
---

# Elasticsearch

`ElasticsearchSink` indexes log entries into Elasticsearch. Uses the official client if available, otherwise falls back to raw HTTP.

## Installation

This integration requires the `elasticsearch` package.

::: code-group

```bash [uv]
uv add logly[elasticsearch]
```

```bash [pip]
pip install "logly[elasticsearch]"
```

```bash [uv (without extras)]
uv add elasticsearch
```

```bash [pip (without extras)]
pip install elasticsearch
```

:::

::: warning Missing Dependency
If `elasticsearch` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'elasticsearch'
```
:::

## Usage

```python
from logly import logger
from logly.integrations.elasticsearch import ElasticsearchSink

logger.add(
    ElasticsearchSink(
        "http://localhost:9200",
        index="logs-{time:YYYY.MM.DD}",
    ),
    level="WARNING",
)
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `endpoint` | `http://localhost:9200` | Elasticsearch URL |
| `index` | `logly-logs` | Index name pattern |
| `timeout` | `5.0` | HTTP request timeout in seconds |
| `username` | `None` | Optional basic auth username |
| `password` | `None` | Optional basic auth password |

## Full Example

```python
from logly import logger
from logly.integrations.elasticsearch import ElasticsearchSink

logger.add(
    ElasticsearchSink(
        endpoint="http://elasticsearch:9200",
        index="myapp-logs-{time:YYYY.MM.DD}",
        timeout=10.0,
        username="elastic",
        password="changeme",
    ),
    level="INFO",
)

logger.info("User registered", user_id=456)
logger.error("Checkout failed", cart_id="cart-789")
```
