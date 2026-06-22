"""Logly integrations - bridges to popular Python frameworks and tools.

All integrations are optional and handle missing dependencies gracefully
with clear installation instructions.

Install integrations with extras::

    # uv (recommended)
    uv add logly[fastapi]      # FastAPI/Starlette
    uv add logly[flask]        # Flask
    uv add logly[django]       # Django
    uv add logly[rich]         # Rich console
    uv add logly[gunicorn]     # Gunicorn
    uv add logly[sqlalchemy]   # SQLAlchemy
    uv add logly[structlog]    # structlog
    uv add logly[opentelemetry] # OpenTelemetry
    uv add logly[prometheus]   # Prometheus
    uv add logly[elasticsearch] # Elasticsearch
    uv add logly[sentry]       # Sentry
    uv add logly[redis]        # Redis
    uv add logly[kafka]        # Kafka
    uv add logly[mongodb]      # MongoDB
    uv add logly[postgresql]   # PostgreSQL
    uv add logly[discord]      # Discord
    uv add logly[slack]        # Slack
    uv add logly[email]        # Email
    uv add logly[http]         # HTTP
    uv add logly[click]        # Click
    uv add logly[typer]        # Typer
    uv add logly[apscheduler]  # APScheduler
    uv add logly[rq]           # RQ (Redis Queue)
    uv add logly[rabbitmq]     # RabbitMQ
    uv add logly[all]          # All integrations

    # pip
    pip install "logly[fastapi]"
    pip install "logly[flask]"
    pip install "logly[django]"
    pip install "logly[rich]"
    pip install "logly[redis]"
    pip install "logly[all]"
"""

from __future__ import annotations

from logly.integrations.telemetry import HttpJsonSink, TelemetrySink

__all__ = ["HttpJsonSink", "TelemetrySink"]

# Re-export for convenience
TelemetrySink = TelemetrySink
"""Telemetry sink for forwarding log events to custom backends."""

HttpJsonSink = HttpJsonSink
"""HTTP JSON sink for posting log events to HTTP endpoints."""
