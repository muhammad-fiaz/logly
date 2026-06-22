---
title: Kafka
description: Publish log entries to Kafka topics.
---

# Kafka

`KafkaHandler` publishes log entries to a Kafka topic using `confluent-kafka`.

## Installation

This integration requires the `confluent-kafka` package.

::: code-group

```bash [uv]
uv add logly[kafka]
```

```bash [pip]
pip install "logly[kafka]"
```

```bash [uv (without extras)]
uv add confluent-kafka
```

```bash [pip (without extras)]
pip install confluent-kafka
```

:::

::: warning Missing Dependency
If `confluent_kafka` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'confluent_kafka'
```
:::

## Usage

```python
from logly import logger
from logly.integrations.kafka import KafkaHandler

handler = KafkaHandler(
    "localhost:9092",
    topic="app-logs",
    client_id="logly-producer",
)
logger.add(handler, level="WARNING")
```

## Constructor Args

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `bootstrap_servers` | `str` | `localhost:9092` | Comma-separated list of broker addresses |
| `topic` | `str` | `logly-logs` | Kafka topic to publish to |
| `client_id` | `str` | `logly-producer` | Client identifier for the producer |
| `acks` | `str` | `"1"` | Acknowledgment mode: `"all"`, `"1"`, or `"0"` |
| `timeout` | `float` | `5.0` | Delivery timeout in seconds |

## Tips

- Use `acks="all"` for maximum durability at the cost of latency.
- Set a meaningful `client_id` for broker-side logging and debugging.

## Full Example

```python
from logly import logger
from logly.integrations.kafka import KafkaHandler

handler = KafkaHandler(
    bootstrap_servers="broker1:9092,broker2:9092",
    topic="myapp-logs",
    client_id="myapp-service",
    acks="all",
    timeout=10.0,
)
logger.add(handler, level="INFO")

logger.info("Processing request", request_id="req-123")
logger.error("Handler failed", error="timeout")
```
