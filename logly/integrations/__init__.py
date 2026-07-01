"""Logly integrations - bridges to popular Python frameworks and tools.

All integrations are optional and handle missing dependencies gracefully
with clear installation instructions.

Integrations are organized into four categories:

**Framework Adapters** (use ``logging.Handler`` to bridge framework logs):
- ``stdlib`` - Python stdlib logging bridge
- ``django`` - Django middleware + handler
- ``flask`` - Flask request logging
- ``celery`` - Celery worker logging
- ``gunicorn`` - Gunicorn worker logging
- ``uvicorn`` - Uvicorn access/error logging
- ``starlette`` - Starlette middleware
- ``fastapi`` - FastAPI middleware
- ``structlog`` - structlog processor/renderer
- ``apscheduler`` - APScheduler job logging
- ``pydantic`` - Pydantic validation logging
- ``sqlalchemy`` - SQLAlchemy engine logging
- ``rq`` - RQ worker logging
- ``click`` - Click echo adapter
- ``typer`` - Typer echo adapter
- ``propagate`` - Bridge back to stdlib logging

**Console/UI**:
- ``rich`` - Rich console output

**External Service Sinks** (use Logly sink API, support all 10 builtin levels):
- ``elasticsearch`` - Elasticsearch indexing
- ``opentelemetry`` - OpenTelemetry log export
- ``prometheus`` - Prometheus metrics
- ``sentry`` - Sentry error capture
- ``datadog`` - Datadog log ingestion
- ``newrelic`` - New Relic log forwarder
- ``aws_cloudwatch`` - AWS CloudWatch Logs
- ``azure_monitor`` - Azure Monitor/Application Insights
- ``google_cloud_logging`` - Google Cloud Logging
- ``graylog`` - Graylog GELF (TCP/UDP)
- ``logstash`` - Logstash (TCP/UDP)
- ``seq`` - Seq structured log server
- ``loki`` - Grafana Loki push API

**Message Queue/Store Sinks**:
- ``kafka`` - Apache Kafka (confluent-kafka)
- ``redis`` - Redis lists/streams
- ``rabbitmq`` - RabbitMQ via pika
- ``mongodb`` - MongoDB collections
- ``postgresql`` - PostgreSQL tables
- ``http`` - Generic HTTP endpoint
- ``email`` - Email via SMTP
- ``discord`` - Discord webhooks
- ``slack`` - Slack webhooks
- ``telemetry`` - Custom telemetry callback + HTTP JSON

**Progress Bars**:
- ``tqdm`` - tqdm progress bar output

Install integrations with extras::

    # uv (recommended)
    uv add logly[fastapi]       # FastAPI/Starlette
    uv add logly[flask]         # Flask
    uv add logly[django]        # Django
    uv add logly[rich]          # Rich console
    uv add logly[gunicorn]      # Gunicorn
    uv add logly[sqlalchemy]    # SQLAlchemy
    uv add logly[structlog]     # structlog
    uv add logly[opentelemetry] # OpenTelemetry
    uv add logly[prometheus]    # Prometheus
    uv add logly[elasticsearch] # Elasticsearch
    uv add logly[sentry]        # Sentry
    uv add logly[redis]         # Redis
    uv add logly[kafka]         # Kafka
    uv add logly[mongodb]       # MongoDB
    uv add logly[postgresql]    # PostgreSQL
    uv add logly[discord]       # Discord
    uv add logly[slack]         # Slack
    uv add logly[email]         # Email
    uv add logly[http]          # HTTP
    uv add logly[click]         # Click
    uv add logly[typer]         # Typer
    uv add logly[apscheduler]   # APScheduler
    uv add logly[rq]            # RQ (Redis Queue)
    uv add logly[rabbitmq]      # RabbitMQ
    uv add logly[pydantic]      # Pydantic
    uv add logly[logstash]      # Logstash
    uv add logly[graylog]       # Graylog GELF
    uv add logly[aws]           # AWS CloudWatch
    uv add logly[gcloud]        # Google Cloud Logging
    uv add logly[azure]         # Azure Monitor
    uv add logly[datadog]       # Datadog
    uv add logly[newrelic]      # New Relic
    uv add logly[seq]           # Seq

    # pip
    pip install "logly[fastapi]"
    pip install "logly[flask]"
    pip install "logly[django]"
    pip install "logly[rich]"
    pip install "logly[redis]"
"""

from __future__ import annotations

from logly.integrations.telemetry import HttpJsonSink, TelemetrySink

__all__ = ["HttpJsonSink", "TelemetrySink"]

# Re-export for convenience
TelemetrySink = TelemetrySink
"""Telemetry sink for forwarding log events to custom backends."""

HttpJsonSink = HttpJsonSink
"""HTTP JSON sink for posting log events to HTTP endpoints."""
