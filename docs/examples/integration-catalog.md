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

- [APScheduler](../../examples/apscheduler_integration.py)
- [Celery](../../examples/celery_integration.py)
- [Click](../../examples/click_integration.py)
- [Django](../../examples/django_integration.py)
- [FastAPI](../../examples/fastapi_integration.py)
- [Flask](../../examples/flask_integration.py)
- [Gunicorn](../../examples/gunicorn_integration.py)
- [Pydantic](../../examples/pydantic_integration.py)
- [Rich](../../examples/rich_integration.py)
- [RQ](../../examples/rq_integration.py)
- [SQLAlchemy](../../examples/sqlalchemy_integration.py)
- [Starlette](../../examples/starlette_integration.py)
- [stdlib logging](../../examples/stdlib_integration.py)
- [structlog](../../examples/structlog_integration.py)
- [tqdm](../../examples/tqdm_integration.py)
- [Typer](../../examples/typer_integration.py)
- [Uvicorn](../../examples/uvicorn_integration.py)

## Network and service integrations

These examples are complete client configurations. Live execution requires
the corresponding endpoint, broker, database, collector, or credentials:

- [AWS CloudWatch](../../examples/aws_cloudwatch_integration.py)
- [Azure Monitor](../../examples/azure_monitor_integration.py)
- [Datadog](../../examples/datadog_integration.py)
- [Discord](../../examples/discord_integration.py)
- [Elasticsearch](../../examples/elasticsearch_integration.py)
- [Email](../../examples/email_integration.py)
- [Google Cloud Logging](../../examples/google_cloud_logging_integration.py)
- [Graylog](../../examples/graylog_integration.py)
- [HTTP](../../examples/http_integration.py)
- [Kafka](../../examples/kafka_integration.py)
- [Logstash](../../examples/logstash_integration.py)
- [Loki](../../examples/loki_integration.py)
- [MongoDB](../../examples/mongodb_integration.py)
- [New Relic](../../examples/newrelic_integration.py)
- [OpenTelemetry](../../examples/opentelemetry_integration.py)
- [PostgreSQL](../../examples/postgresql_integration.py)
- [Prometheus](../../examples/prometheus_integration.py)
- [RabbitMQ](../../examples/rabbitmq_integration.py)
- [Redis](../../examples/redis_integration.py)
- [Sentry](../../examples/sentry_integration.py)
- [Seq](../../examples/seq_integration.py)
- [Slack](../../examples/slack_integration.py)
- [Telemetry](../../examples/telemetry_integration.py)

## Core feature examples

- [Basic logging](../../examples/basic_logging.py)
- [Color markup](../../examples/color_markup.py)
- [Compression](../../examples/compression_example.py)
- [Concurrency](../../examples/concurrency.py)
- [Context binding](../../examples/context_binding.py)
- [Custom levels](../../examples/custom_levels.py)
- [Enable and disable](../../examples/enable_disable.py)
- [Exception handling](../../examples/exception_handling.py)
- [File logging](../../examples/file_logging.py)
- [Filtering](../../examples/filtering.py)
- [Formatting](../../examples/formatting.py)
- [JSON logging](../../examples/json_logging.py)
- [Lazy evaluation](../../examples/lazy_evaluation.py)
- [Multiple sinks](../../examples/multiple_sinks.py)
- [Patching](../../examples/patching.py)
- [Production configuration](../../examples/production_config.py)
- [Propagation](../../examples/propagate_integration.py)
- [Rotation](../../examples/rotation_example.py)
