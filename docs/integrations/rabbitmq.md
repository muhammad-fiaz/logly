---
title: RabbitMQ
description: Publish log entries to RabbitMQ queues.
---

# RabbitMQ

`RabbitMQHandler` publishes log entries to a RabbitMQ queue using `pika`. Connections are established lazily on first write.

## Installation

This integration requires the `pika` package.

::: code-group

```bash [uv]
uv add logly[rabbitmq]
```

```bash [pip]
pip install "logly[rabbitmq]"
```

```bash [uv (without extras)]
uv add pika
```

```bash [pip (without extras)]
pip install pika
```

:::

::: warning Missing Dependency
If `pika` is not installed, you'll see:

```
pika is required for Logly RabbitMQ integration.
Install with one of:
  uv add logly[rabbitmq]       # recommended
  pip install logly[rabbitmq]
  uv add pika
  pip install pika
```
:::

## Usage

```python
from logly import logger
from logly.integrations.rabbitmq import RabbitMQHandler

handler = RabbitMQHandler(
    "amqp://guest:guest@localhost:5672/",
    queue="app-logs",
)
logger.add(handler, level="WARNING")
```

## Constructor Args

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `url` | `str` | `amqp://guest:guest@localhost:5672/` | RabbitMQ connection URL |
| `queue` | `str` | `logly-logs` | Queue name to publish messages to |
| `exchange` | `str` | `""` | Exchange name (empty string for default exchange) |
| `routing_key` | `str \| None` | `None` | Routing key (defaults to queue name) |
| `durable` | `bool` | `True` | Whether the queue/exchange should survive restarts |
| `timeout` | `float` | `5.0` | Connection timeout in seconds |

## Tips

- Use `durable=True` (default) so log messages survive RabbitMQ restarts.
- Use a dedicated exchange and routing key for log routing in complex topologies.

## Full Example

```python
from logly import logger
from logly.integrations.rabbitmq import RabbitMQHandler

handler = RabbitMQHandler(
    url="amqp://user:pass@rabbit-host:5672/",
    queue="production-logs",
    exchange="logs",
    routing_key="app.logs",
    durable=True,
    timeout=10.0,
)
logger.add(handler, level="WARNING")

logger.warning("Queue depth high", queue="orders", depth=5000)
logger.error("Consumer lag detected", consumer="worker-3")
```
