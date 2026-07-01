---
title: Integrations
description: Complete guide to all Logly integrations for Python frameworks, observability tools, data stores, and message brokers.
---

# Integrations

Logly provides first-class integrations for popular Python frameworks, tools, and services. Each integration is a thin adapter that routes logs through Logly's Rust-powered engine.

## Frameworks & Libraries

| Integration | Description | Install |
|-------------|-------------|---------|
| [FastAPI](fastapi) | ASGI middleware with request context, status codes, and timing | `uv add logly[fastapi]` |
| [Django](django) | Middleware and `logging.Handler` for Django | `uv add logly[django]` |
| [Flask](flask) | Handler and request context for Flask | `uv add logly[flask]` |
| [Starlette](starlette) | ASGI middleware for plain Starlette apps | `uv add logly[starlette]` |
| [Stdlib Logging](stdlib) | Bridge Python's `logging` module to Logly | Built-in |
| [Gunicorn](gunicorn) | Worker hooks for Gunicorn | `uv add logly[gunicorn]` |
| [Uvicorn](uvicorn) | Log configuration for Uvicorn | `uv add logly[uvicorn]` |
| [SQLAlchemy](sqlalchemy) | Engine event listener for query logging | `uv add logly[sqlalchemy]` |
| [Structlog](structlog) | Processor for structlog | `uv add logly[structlog]` |
| [Rich](rich) | Beautiful terminal output via Rich | `uv add logly[rich]` |
| [Click](click) | Route Click CLI output through Logly | `uv add logly[click]` |
| [Typer](typer) | Route Typer CLI output through Logly | `uv add logly[typer]` |
| [APScheduler](apscheduler) | Route APScheduler job logs through Logly | `uv add logly[apscheduler]` |
| [RQ](rq) | Route RQ worker job logs through Logly | `uv add logly[rq]` |
| [Celery](celery) | Task logging for Celery workers | `uv add logly[celery]` |
| [Pydantic](pydantic) | Route Pydantic application logs through Logly | `uv add logly[pydantic]` |
| [tqdm](tqdm) | Log output through tqdm progress bars | `uv add logly[tqdm]` |
| [Propagate](propagate) | Propagate records to stdlib `logging` hierarchy | Built-in |

## Observability & Monitoring

| Integration | Description | Install |
|-------------|-------------|---------|
| [OpenTelemetry](opentelemetry) | Export log records to OTel collectors | `uv add logly[opentelemetry]` |
| [Prometheus](prometheus) | Expose log metrics via Prometheus | `uv add logly[prometheus]` |
| [Loki](loki) | Ship logs to Grafana Loki | `uv add logly[loki]` |
| [Sentry](sentry) | Forward error logs to Sentry | `uv add logly[sentry]` |
| [Elasticsearch](elasticsearch) | Index logs into Elasticsearch | `uv add logly[elasticsearch]` |
| [Datadog](datadog) | Send logs to Datadog Logs API | Built-in |
| [New Relic](newrelic) | Send logs to New Relic | `uv add logly[newrelic]` |
| [Seq](seq) | Send logs to Seq structured log server | Built-in |
| [AWS CloudWatch](aws_cloudwatch) | Send logs to AWS CloudWatch Logs | `uv add logly[aws]` |
| [Google Cloud Logging](google_cloud_logging) | Send logs to Google Cloud Logging | `uv add logly[gcloud]` |
| [Azure Monitor](azure_monitor) | Send logs to Azure Monitor | `uv add logly[azure]` |
| [Telemetry](telemetry) | Generic telemetry sink for custom backends | Built-in |

## Data Stores & Message Brokers

| Integration | Description | Install |
|-------------|-------------|---------|
| [Redis](redis) | Push logs to Redis lists or streams | `uv add logly[redis]` |
| [Kafka](kafka) | Publish logs to Kafka topics | `uv add logly[kafka]` |
| [MongoDB](mongodb) | Insert logs into MongoDB collections | `uv add logly[mongodb]` |
| [PostgreSQL](postgresql) | Insert logs into PostgreSQL tables | `uv add logly[postgresql]` |
| [RabbitMQ](rabbitmq) | Publish logs to RabbitMQ queues | `uv add logly[rabbitmq]` |
| [Logstash](logstash) | Send logs to Logstash via TCP/UDP | Built-in |
| [Graylog](graylog) | Send logs to Graylog in GELF format | Built-in |

## Notifications & Webhooks

| Integration | Description | Install |
|-------------|-------------|---------|
| [Discord](discord) | Send logs to Discord webhooks | Built-in |
| [Slack](slack) | Send logs to Slack webhooks | Built-in |
| [Email](email) | Send logs as emails via SMTP | Built-in |
| [HTTP](http) | Send logs to any HTTP endpoint | Built-in |
