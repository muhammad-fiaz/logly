# Examples

 runnable examples covering every major Logly feature. Each file is self-contained and can be executed directly.

## Quick Start

```bash
pip install logly
python examples/basic_logging.py
```

## Core Features

| Example | Description |
|---------|-------------|
| [basic_logging.py](basic_logging.py) | Console output with all 10 built-in log levels. |
| [formatting.py](formatting.py) | Custom format templates with `{time}`, `{level}`, `{file}`, `{line}` tokens. |
| [filtering.py](filtering.py) | Level gates, prefix filters, extra-field filters, and composable filter chains. |
| [context_binding.py](context_binding.py) | Bind key-value pairs to loggers for structured context. |
| [patching.py](patching.py) | Mutate log records before dispatch with patchers. |
| [custom_levels.py](custom_levels.py) | Register custom log levels with names, priorities, colors, and icons. |
| [concurrency.py](concurrency.py) | Thread-safe and async-safe logging with enqueue mode. |
| [enable_disable.py](enable_disable.py) | Enable/disable logger names at runtime. |
| [lazy_evaluation.py](lazy_evaluation.py) | Defer expensive string formatting until the record is actually emitted. |
| [exception_handling.py](exception_handling.py) | Catch, format, and log exceptions with backtrace support. |

## File Management

| Example | Description |
|---------|-------------|
| [file_logging.py](file_logging.py) | Write logs to files with rotation, retention, and compression. |
| [rotation_example.py](rotation_example.py) | Size-based, time-based, and clock-based log rotation. |
| [compression_example.py](compression_example.py) | Compress rotated logs with Gzip, Zip, Bz2, Xz, or Zstd. |
| [multiple_sinks.py](multiple_sinks.py) | Route logs to multiple destinations simultaneously. |
| [production_config.py](production_config.py) | Production-ready setup with file rotation, error callbacks, and structured output. |
| [json_logging.py](json_logging.py) | Structured JSON log output for log aggregation systems. |
| [color_markup.py](color_markup.py) | ANSI colors, styles, 256-color, and RGB markup in console output. |

## Integrations

### Web Frameworks

| Example | Description |
|---------|-------------|
| [fastapi_integration.py](fastapi_integration.py) | Request-scoped logging with context binding in FastAPI. |
| [django_integration.py](django_integration.py) | Integration with Django's logging config. |
| [flask_integration.py](flask_integration.py) | Request context logging in Flask. |
| [starlette_integration.py](starlette_integration.py) | ASGI middleware logging for Starlette. |
| [uvicorn_integration.py](uvicorn_integration.py) | Uvicorn server logging configuration. |
| [gunicorn_integration.py](gunicorn_integration.py) | Gunicorn worker logging with process-aware output. |

### Task Queues & Workers

| Example | Description |
|---------|-------------|
| [celery_integration.py](celery_integration.py) | Celery task logging with worker context. |
| [rq_integration.py](rq_integration.py) | RQ job logging with queue context. |
| [apscheduler_integration.py](apscheduler_integration.py) | APScheduler job logging. |

### Observability & Monitoring

| Example | Description |
|---------|-------------|
| [opentelemetry_integration.py](opentelemetry_integration.py) | OpenTelemetry span-aware logging. |
| [prometheus_integration.py](prometheus_integration.py) | Prometheus metrics and log correlation. |
| [sentry_integration.py](sentry_integration.py) | Sentry error tracking integration. |
| [datadog_integration.py](datadog_integration.py) | Datadog log forwarding. |
| [newrelic_integration.py](newrelic_integration.py) | New Relic log management. |
| [seq_integration.py](seq_integration.py) | Structured log ingestion for Seq. |
| [loki_integration.py](loki_integration.py) | Grafana Loki log forwarding. |
| [logstash_integration.py](logstash_integration.py) | Logstash JSON log forwarding. |
| [graylog_integration.py](graylog_integration.py) | Graylog GELF log forwarding. |

### Cloud Providers

| Example | Description |
|---------|-------------|
| [aws_cloudwatch_integration.py](aws_cloudwatch_integration.py) | AWS CloudWatch Logs integration. |
| [google_cloud_logging_integration.py](google_cloud_logging_integration.py) | Google Cloud Logging integration. |
| [azure_monitor_integration.py](azure_monitor_integration.py) | Azure Monitor log forwarding. |

### Data Stores & Brokers

| Example | Description |
|---------|-------------|
| [elasticsearch_integration.py](elasticsearch_integration.py) | Elasticsearch document indexing. |
| [redis_integration.py](redis_integration.py) | Redis log publishing. |
| [kafka_integration.py](kafka_integration.py) | Kafka topic log streaming. |
| [mongodb_integration.py](mongodb_integration.py) | MongoDB document logging. |
| [postgresql_integration.py](postgresql_integration.py) | PostgreSQL table logging. |
| [rabbitmq_integration.py](rabbitmq_integration.py) | RabbitMQ message log forwarding. |
| [sqlalchemy_integration.py](sqlalchemy_integration.py) | SQLAlchemy ORM logging. |

### Notifications & Webhooks

| Example | Description |
|---------|-------------|
| [slack_integration.py](slack_integration.py) | Slack channel log alerts. |
| [discord_integration.py](discord_integration.py) | Discord webhook log forwarding. |
| [email_integration.py](email_integration.py) | Email log alerts for critical events. |
| [http_integration.py](http_integration.py) | Generic HTTP webhook log forwarding. |

### CLI & Terminal

| Example | Description |
|---------|-------------|
| [click_integration.py](click_integration.py) | Click CLI application logging. |
| [typer_integration.py](typer_integration.py) | Typer CLI application logging. |
| [tqdm_integration.py](tqdm_integration.py) | tqdm progress bar compatible logging. |
| [rich_integration.py](rich_integration.py) | Rich console rendered log output. |

### Other

| Example | Description |
|---------|-------------|
| [stdlib_integration.py](stdlib_integration.py) | Bridge Python `logging` to Logly. Use this for Pydantic apps too. |
| [structlog_integration.py](structlog_integration.py) | Structlog processor integration. |
| [propagate_integration.py](propagate_integration.py) | Log propagation across library boundaries. |
| [telemetry_integration.py](telemetry_integration.py) | OpenTelemetry and distributed tracing integration. |
