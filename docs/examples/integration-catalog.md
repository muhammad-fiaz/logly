---
title: Integration example catalog
description: Complete runnable integration example catalog for Logly.
---

# Integration example catalog

Each integration has a runnable source example in the repository's
`examples/` directory. The examples contain configuration and sample logging
calls only; they do not embed captured output. Run an example from the project
root with:

```powershell
uv run python examples\<example-name>.py
```

## Framework and local integrations

These examples can be inspected and exercised locally when their optional
package is installed:

- [APScheduler](https://github.com/muhammad-fiaz/logly/blob/main/examples/apscheduler_integration.py)
- [Celery](https://github.com/muhammad-fiaz/logly/blob/main/examples/celery_integration.py)
- [Click](https://github.com/muhammad-fiaz/logly/blob/main/examples/click_integration.py)
- [Django](https://github.com/muhammad-fiaz/logly/blob/main/examples/django_integration.py)
- [FastAPI](https://github.com/muhammad-fiaz/logly/blob/main/examples/fastapi_integration.py)
- [Flask](https://github.com/muhammad-fiaz/logly/blob/main/examples/flask_integration.py)
- [Gunicorn](https://github.com/muhammad-fiaz/logly/blob/main/examples/gunicorn_integration.py)
- [Rich](https://github.com/muhammad-fiaz/logly/blob/main/examples/rich_integration.py)
- [RQ](https://github.com/muhammad-fiaz/logly/blob/main/examples/rq_integration.py)
- [SQLAlchemy](https://github.com/muhammad-fiaz/logly/blob/main/examples/sqlalchemy_integration.py)
- [Starlette](https://github.com/muhammad-fiaz/logly/blob/main/examples/starlette_integration.py)
- [stdlib logging](https://github.com/muhammad-fiaz/logly/blob/main/examples/stdlib_integration.py)
- [structlog](https://github.com/muhammad-fiaz/logly/blob/main/examples/structlog_integration.py)
- [tqdm](https://github.com/muhammad-fiaz/logly/blob/main/examples/tqdm_integration.py)
- [Typer](https://github.com/muhammad-fiaz/logly/blob/main/examples/typer_integration.py)
- [Uvicorn](https://github.com/muhammad-fiaz/logly/blob/main/examples/uvicorn_integration.py)

## Network and service integrations

These examples are complete client configurations. Live execution requires
the corresponding endpoint, broker, database, collector, or credentials:

- [AWS CloudWatch](https://github.com/muhammad-fiaz/logly/blob/main/examples/aws_cloudwatch_integration.py)
- [Azure Monitor](https://github.com/muhammad-fiaz/logly/blob/main/examples/azure_monitor_integration.py)
- [Datadog](https://github.com/muhammad-fiaz/logly/blob/main/examples/datadog_integration.py)
- [Discord](https://github.com/muhammad-fiaz/logly/blob/main/examples/discord_integration.py)
- [Elasticsearch](https://github.com/muhammad-fiaz/logly/blob/main/examples/elasticsearch_integration.py)
- [Email](https://github.com/muhammad-fiaz/logly/blob/main/examples/email_integration.py)
- [Google Cloud Logging](https://github.com/muhammad-fiaz/logly/blob/main/examples/google_cloud_logging_integration.py)
- [Graylog](https://github.com/muhammad-fiaz/logly/blob/main/examples/graylog_integration.py)
- [HTTP](https://github.com/muhammad-fiaz/logly/blob/main/examples/http_integration.py)
- [Kafka](https://github.com/muhammad-fiaz/logly/blob/main/examples/kafka_integration.py)
- [Logstash](https://github.com/muhammad-fiaz/logly/blob/main/examples/logstash_integration.py)
- [Loki](https://github.com/muhammad-fiaz/logly/blob/main/examples/loki_integration.py)
- [MongoDB](https://github.com/muhammad-fiaz/logly/blob/main/examples/mongodb_integration.py)
- [New Relic](https://github.com/muhammad-fiaz/logly/blob/main/examples/newrelic_integration.py)
- [OpenTelemetry](https://github.com/muhammad-fiaz/logly/blob/main/examples/opentelemetry_integration.py)
- [PostgreSQL](https://github.com/muhammad-fiaz/logly/blob/main/examples/postgresql_integration.py)
- [Prometheus](https://github.com/muhammad-fiaz/logly/blob/main/examples/prometheus_integration.py)
- [RabbitMQ](https://github.com/muhammad-fiaz/logly/blob/main/examples/rabbitmq_integration.py)
- [Redis](https://github.com/muhammad-fiaz/logly/blob/main/examples/redis_integration.py)
- [Sentry](https://github.com/muhammad-fiaz/logly/blob/main/examples/sentry_integration.py)
- [Seq](https://github.com/muhammad-fiaz/logly/blob/main/examples/seq_integration.py)
- [Slack](https://github.com/muhammad-fiaz/logly/blob/main/examples/slack_integration.py)
- [Telemetry](https://github.com/muhammad-fiaz/logly/blob/main/examples/telemetry_integration.py)

## Core feature examples

- [Basic logging](https://github.com/muhammad-fiaz/logly/blob/main/examples/basic_logging.py)
- [Color markup](https://github.com/muhammad-fiaz/logly/blob/main/examples/color_markup.py)
- [Compression](https://github.com/muhammad-fiaz/logly/blob/main/examples/compression_example.py)
- [Concurrency](https://github.com/muhammad-fiaz/logly/blob/main/examples/concurrency.py)
- [Context binding](https://github.com/muhammad-fiaz/logly/blob/main/examples/context_binding.py)
- [Custom levels](https://github.com/muhammad-fiaz/logly/blob/main/examples/custom_levels.py)
- [Enable and disable](https://github.com/muhammad-fiaz/logly/blob/main/examples/enable_disable.py)
- [Exception handling](https://github.com/muhammad-fiaz/logly/blob/main/examples/exception_handling.py)
- [File logging](https://github.com/muhammad-fiaz/logly/blob/main/examples/file_logging.py)
- [Filtering](https://github.com/muhammad-fiaz/logly/blob/main/examples/filtering.py)
- [Formatting](https://github.com/muhammad-fiaz/logly/blob/main/examples/formatting.py)
- [JSON logging](https://github.com/muhammad-fiaz/logly/blob/main/examples/json_logging.py)
- [Lazy evaluation](https://github.com/muhammad-fiaz/logly/blob/main/examples/lazy_evaluation.py)
- [Multiple sinks](https://github.com/muhammad-fiaz/logly/blob/main/examples/multiple_sinks.py)
- [Patching](https://github.com/muhammad-fiaz/logly/blob/main/examples/patching.py)
- [Production configuration](https://github.com/muhammad-fiaz/logly/blob/main/examples/production_config.py)
- [Propagation](https://github.com/muhammad-fiaz/logly/blob/main/examples/propagate_integration.py)
- [Rotation](https://github.com/muhammad-fiaz/logly/blob/main/examples/rotation_example.py)
