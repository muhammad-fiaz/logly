---
title: Integrations API
description: Complete API reference for all Logly integrations
---

# Integrations API

All integrations are available as submodules of `logly.integrations`. Most use `importlib.util.find_spec` to check for optional dependencies - no installation required if you don't use them.

```python
from logly.integrations import fastapi, django, flask
```

---

## FastAPI

### LoglyMiddleware

```python
from logly.integrations.fastapi import LoglyMiddleware

app = FastAPI()
app.add_middleware(LoglyMiddleware, level="INFO")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `app` | `FastAPI` | | FastAPI application |
| `level` | `str` | `"INFO"` | Minimum log level |
| `format` | `str \| None` | `None` | Custom format string |
| `backtrace` | `bool` | `False` | Include backtrace on exceptions |
| `diagnose` | `bool` | `False` | Include variable values on exceptions |

---

## Django

### LoglyHandler

```python
# settings.py
LOGGING = {
    "handlers": {
        "logly": {
            "()": "logly.integrations.django.LoglyHandler",
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["logly"],
        "level": "INFO",
    },
}
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str \| int` | `"INFO"` | Minimum log level |
| `format` | `str \| None` | `None` | Custom format string |

### LoglyMiddleware

```python
MIDDLEWARE = [
    "logly.integrations.django.LoglyMiddleware",
    # ... other middleware
]
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `get_response` | `Callable \| None` | `None` | Django response callable |

---

## Flask

### LoglyHandler

```python
from flask import Flask
from logly.integrations.flask import LoglyHandler

app = Flask(__name__)
handler = LoglyHandler()
handler.init_app(app)
```

**Methods:**

#### `init_app(app, **kwargs)`

Initialize the handler with a Flask app.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `app` | `Flask` | | Flask application |
| `level` | `str` | `"INFO"` | Minimum log level |
| `format` | `str \| None` | `None` | Custom format string |

---

## Starlette

### LoglyMiddleware

```python
from starlette.applications import Starlette
from logly.integrations.starlette import LoglyMiddleware

app = Starlette()
app.add_middleware(LoglyMiddleware, level="INFO")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `app` | `Starlette` | | Starlette application |
| `level` | `str` | `"INFO"` | Minimum log level |
| `format` | `str \| None` | `None` | Custom format string |

---

## Stdlib Logging

### InterceptHandler

Bridge stdlib `logging` to Logly.

```python
import logging
from logly.integrations.stdlib import InterceptHandler

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `int` | `logging.NOTSET` | Minimum log level |

---

## Structlog

### logly_processor

```python
import structlog

structlog.configure(
    processors=[
        logly.integrations.structlog.logly_processor(
            logger_name="mylogger",
            wrapper_class=structlog.BoundLogger,
        ),
    ],
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `logger_name` | `str \| None` | `None` | Logger name key |
| `wrapper_class` | `type \| None` | `None` | Structlog wrapper class |
| `level` | `str` | `"INFO"` | Minimum log level |

### LoglyRenderer

```python
structlog.configure(
    processors=[
        logly.integrations.structlog.LoglyRenderer(level="INFO"),
    ],
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level |
| `format` | `str \| None` | `None` | Custom format string |

---

## Rich Console

### LoglyRichSink

```python
from logly import logger
from logly.integrations.rich import LoglyRichSink

logger.add(LoglyRichSink(), level="INFO")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file` | `IO \| None` | `None` | Output file (default: stderr) |

### RichHandler

```python
from logly.integrations.rich import RichHandler

handler = RichHandler(level="INFO", show_path=False)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `int` | `logging.NOTSET` | Minimum log level |
| `show_path` | `bool` | `True` | Show file path |
| `show_line_no` | `bool` | `False` | Show line number |
| `show_time` | `bool` | `True` | Show timestamp |
| `rich_tracebacks` | `bool` | `True` | Use Rich tracebacks |

---

## Gunicorn

### LoglyWorker

```python
# gunicorn.conf.py
from logly.integrations.gunicorn import LoglyWorker

worker_class = LoglyWorker
```

### setup_gunicorn_logging

```python
# gunicorn.conf.py
from logly.integrations.gunicorn import setup_gunicorn_logging

setup_gunicorn_logging(level="INFO")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level |
| `format` | `str \| None` | `None` | Custom format string |

---

## Uvicorn

### setup_uvicorn_logging

```python
# uvicorn config
from logly.integrations.uvicorn import setup_uvicorn_logging

setup_uvicorn_logging(level="INFO")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level |
| `format` | `str \| None` | `None` | Custom format string |

### get_log_config

```python
from logly.integrations.uvicorn import get_log_config

config = get_log_config(level="INFO")
# Use with uvicorn: uvicorn.run(app, log_config=config)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level |
| `format` | `str \| None` | `None` | Custom format string |

**Returns:** `dict` - Uvicorn-compatible log config

---

## Celery

### setup_celery_logging

```python
from logly.integrations.celery import setup_celery_logging

setup_celery_logging(level="INFO")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level |
| `format` | `str \| None` | `None` | Custom format string |

### patch_task_logger

```python
from logly.integrations.celery import patch_task_logger

@app.task
def my_task():
    patch_task_logger(app.task_logger, level="INFO")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task_logger` | `Logger` | | Celery task logger |
| `level` | `str` | `"INFO"` | Minimum log level |

---

## SQLAlchemy

### setup_sqlalchemy_logging

```python
from logly.integrations.sqlalchemy import setup_sqlalchemy_logging

setup_sqlalchemy_logging(level="WARNING", echo=False)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"WARNING"` | Minimum log level |
| `echo` | `bool` | `False` | Echo SQL statements |

### patch_engine

```python
from logly.integrations.sqlalchemy import patch_engine

engine = create_engine("sqlite:///db.sqlite3")
patch_engine(engine, level="INFO")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `engine` | `Engine` | | SQLAlchemy engine |
| `level` | `str` | `"INFO"` | Minimum log level |

---

## OpenTelemetry

### OTelLogSink

```python
from logly import logger
from logly.integrations.opentelemetry import OTelLogSink

logger.add(OTelLogSink(
    service_name="myapp",
    endpoint="http://localhost:4318",
    protocol="http",
))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `service_name` | `str` | `"logly"` | Service name |
| `endpoint` | `str` | `"http://localhost:4318"` | OTLP endpoint |
| `protocol` | `str` | `"http"` | Protocol: `"http"` or `"grpc"` |
| `headers` | `dict \| None` | `None` | Request headers |

---

## Prometheus

### PrometheusLogSink

```python
from logly import logger
from logly.integrations.prometheus import PrometheusLogSink

logger.add(PrometheusLogSink(namespace="logly"))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `namespace` | `str` | `"logly"` | Prometheus namespace |
| `Subsystem` | `str \| None` | `None` | Prometheus subsystem |

---

## Elasticsearch

### ElasticsearchSink

```python
from logly import logger
from logly.integrations.elasticsearch import ElasticsearchSink

logger.add(ElasticsearchSink(
    endpoint="http://localhost:9200",
    index="logs",
))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `endpoint` | `str` | | Elasticsearch endpoint |
| `index` | `str` | `"logly"` | Index name |
| `timeout` | `int` | `30` | Request timeout (seconds) |
| `username` | `str \| None` | `None` | Basic auth username |
| `password` | `str \| None` | `None` | Basic auth password |

---

## Sentry

### SentrySink

```python
from logly import logger
from logly.integrations.sentry import SentrySink

logger.add(SentrySink(
    dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
    environment="production",
    release="1.0.0",
    level="WARNING",
))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dsn` | `str` | | Sentry DSN |
| `environment` | `str \| None` | `None` | Environment name |
| `release` | `str \| None` | `None` | Release version |
| `level` | `str` | `"WARNING"` | Minimum log level |

---

## Redis

### RedisHandler

```python
from logly import logger
from logly.integrations.redis import RedisHandler

logger.add(RedisHandler(
    url="redis://localhost:6379",
    key="logs",
    mode="list",
))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | | Redis connection URL |
| `key` | `str` | `"logly:logs"` | Redis key |
| `mode` | `str` | `"list"` | Storage mode: `"list"` or `"stream"` |
| `timeout` | `int` | `5` | Connection timeout (seconds) |
| `max_stream_len` | `int` | `10000` | Max stream length |

---

## Kafka

### KafkaHandler

```python
from logly import logger
from logly.integrations.kafka import KafkaHandler

logger.add(KafkaHandler(
    bootstrap_servers="localhost:9092",
    topic="logs",
))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bootstrap_servers` | `str` | | Kafka broker addresses |
| `topic` | `str` | `"logly"` | Kafka topic |
| `client_id` | `str \| None` | `None` | Client ID |
| `acks` | `str \| int` | `"all"` | Acknowledgment mode |
| `timeout` | `int` | `10` | Request timeout (seconds) |

---

## MongoDB

### MongoHandler

```python
from logly import logger
from logly.integrations.mongodb import MongoHandler

logger.add(MongoHandler(
    uri="mongodb://localhost:27017",
    database="logs",
    collection="app_logs",
))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `uri` | `str` | | MongoDB connection URI |
| `database` | `str` | | Database name |
| `collection` | `str` | `"logs"` | Collection name |
| `timeout` | `int` | `5` | Connection timeout (seconds) |

---

## PostgreSQL

### PostgresHandler

```python
from logly import logger
from logly.integrations.postgresql import PostgresHandler

logger.add(PostgresHandler(
    dsn="postgresql://user:pass@localhost:5432/logs",
    table="app_logs",
))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dsn` | `str` | | PostgreSQL connection string |
| `table` | `str` | `"logs"` | Table name |
| `create_table` | `bool` | `True` | Auto-create table |

---

## Discord

### DiscordHandler

```python
from logly import logger
from logly.integrations.discord import DiscordHandler

logger.add(DiscordHandler(
    webhook_url="https://discord.com/api/webhooks/...",
    username="Logly Bot",
))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `webhook_url` | `str` | | Discord webhook URL |
| `timeout` | `int` | `10` | Request timeout (seconds) |
| `username` | `str \| None` | `None` | Override username |
| `avatar_url` | `str \| None` | `None` | Override avatar URL |

---

## Slack

### SlackHandler

```python
from logly import logger
from logly.integrations.slack import SlackHandler

logger.add(SlackHandler(
    webhook_url="https://hooks.slack.com/services/...",
    channel="#logs",
))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `webhook_url` | `str` | | Slack webhook URL |
| `channel` | `str \| None` | `None` | Override channel |
| `username` | `str` | `"Logly"` | Bot username |
| `icon_emoji` | `str` | `":robot_face:"` | Bot icon emoji |
| `timeout` | `int` | `10` | Request timeout (seconds) |

---

## Email

### EmailHandler

```python
from logly import logger
from logly.integrations.email import EmailHandler

logger.add(EmailHandler(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    from_addr="alerts@myapp.com",
    to_addrs=["admin@myapp.com"],
    username="alerts@myapp.com",
    password="app-password",
    use_tls=True,
))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `smtp_host` | `str` | | SMTP server host |
| `smtp_port` | `int` | | SMTP server port |
| `from_addr` | `str` | | Sender email address |
| `to_addrs` | `list[str]` | | Recipient email addresses |
| `username` | `str \| None` | `None` | SMTP username |
| `password` | `str \| None` | `None` | SMTP password |
| `use_tls` | `bool` | `True` | Use STARTTLS |
| `use_ssl` | `bool` | `False` | Use SSL/TLS |
| `timeout` | `int` | `30` | Connection timeout (seconds) |
| `subject_prefix` | `str` | `""` | Prefix for email subject |

---

## HTTP

### HttpHandler

```python
from logly import logger
from logly.integrations.http import HttpHandler

logger.add(HttpHandler(
    url="https://api.example.com/logs",
    method="POST",
    headers={"Authorization": "Bearer token"},
))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | | HTTP endpoint URL |
| `method` | `str` | `"POST"` | HTTP method |
| `headers` | `dict \| None` | `None` | Request headers |
| `timeout` | `int` | `10` | Request timeout (seconds) |
| `format` | `str \| None` | `None` | Custom format string |

---

## Loki

### LokiSink

```python
from logly import logger
from logly.integrations.loki import LokiSink

logger.add(LokiSink(
    endpoint="http://localhost:3100",
    labels={"app": "myapp", "env": "production"},
))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `endpoint` | `str` | | Loki endpoint URL |
| `labels` | `dict` | `{}` | Default labels |
| `timeout` | `int` | `10` | Request timeout (seconds) |
| `username` | `str \| None` | `None` | Basic auth username |
| `password` | `str \| None` | `None` | Basic auth password |

---

## Propagate

### PropagateHandler

```python
import logging
from logly.integrations.propagate import PropagateHandler

logging.getLogger("myapp").addHandler(PropagateHandler())
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | `"logly"` | Logger name |
| `level` | `int` | `logging.NOTSET` | Minimum log level |

---

## Telemetry

### TelemetrySink

```python
from logly import logger
from logly.integrations.telemetry import TelemetrySink

def send_to_collector(record):
    # Send to your telemetry backend
    pass

logger.add(TelemetrySink(emit=send_to_collector))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `emit` | `Callable` | | Emission function |
| `service_name` | `str` | `"logly"` | Service name |
| `environment` | `str \| None` | `None` | Environment name |

### HttpJsonSink

```python
from logly import logger
from logly.integrations.telemetry import HttpJsonSink

logger.add(HttpJsonSink(
    endpoint="https://api.example.com/telemetry",
    headers={"Authorization": "Bearer token"},
))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `endpoint` | `str` | | HTTP endpoint URL |
| `headers` | `dict \| None` | `None` | Request headers |
| `timeout` | `int` | `10` | Request timeout (seconds) |

---

## APScheduler

### APSchedulerHandler

```python
from logly.integrations.apscheduler import APSchedulerHandler

scheduler = APScheduler()
scheduler.add_job(my_job, "interval", seconds=60)
scheduler.add_listener(APSchedulerHandler(), EVENT_JOB_EXECUTED)
```

### setup_apscheduler_logging

```python
from logly.integrations.apscheduler import setup_apscheduler_logging

setup_apscheduler_logging(level="INFO")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level |

---

## RQ

### RQHandler

```python
from logly.integrations.rq import RQHandler

# Attach to RQ worker
```

### setup_rq_logging

```python
from logly.integrations.rq import setup_rq_logging

setup_rq_logging(level="INFO")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | `str` | `"INFO"` | Minimum log level |

---

## Click

### click_echo

```python
from logly.integrations.click import click_echo

click_echo("Processing...", nl=True, err=True)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | `str` | | Message to display |
| `file` | `IO \| None` | `None` | Output stream |
| `nl` | `bool` | `True` | Add newline |
| `err` | `bool` | `False` | Output to stderr |
| `color` | `bool \| None` | `None` | Enable color |

---

## Typer

### typer_echo

```python
from logly.integrations.typer import typer_echo

typer_echo("Processing...", nl=True, err=True)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | `str` | | Message to display |
| `file` | `IO \| None` | `None` | Output stream |
| `nl` | `bool` | `True` | Add newline |
| `err` | `bool` | `False` | Output to stderr |
| `color` | `bool \| None` | `None` | Enable color |

---

## RabbitMQ

### RabbitMQHandler

```python
from logly import logger
from logly.integrations.rabbitmq import RabbitMQHandler

logger.add(RabbitMQHandler(
    url="amqp://guest:guest@localhost:5672",
    queue="logs",
))
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | | RabbitMQ connection URL |
| `queue` | `str` | `"logly"` | Queue name |
| `exchange` | `str \| None` | `None` | Exchange name |
| `routing_key` | `str \| None` | `None` | Routing key |
| `durable` | `bool` | `True` | Durable queue |
| `timeout` | `int` | `10` | Connection timeout (seconds) |
