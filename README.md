<div align="center">
<img src="https://github.com/user-attachments/assets/565fc3dc-dd2c-47a6-bab6-2f545c551f26" alt="logly logo" width="400" />

<a href="https://pypi.org/project/logly/"><img src="https://img.shields.io/pypi/v/logly" alt="PyPI"></a>
<a href="https://pypistats.org/packages/logly"><img src="https://img.shields.io/pypi/dm/logly" alt="PyPI - Downloads"></a>
<a href="https://muhammad-fiaz.github.io/logly/"><img src="https://img.shields.io/badge/docs-muhammad--fiaz.github.io-blue" alt="Documentation"></a>
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-%3E%3D3.10-brightgreen.svg" alt="Supported Python"></a>
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/github/stars/muhammad-fiaz/logly" alt="GitHub stars"></a>
<a href="https://github.com/muhammad-fiaz/logly/issues"><img src="https://img.shields.io/github/issues/muhammad-fiaz/logly" alt="GitHub issues"></a>
<a href="https://github.com/muhammad-fiaz/logly/pulls"><img src="https://img.shields.io/github/issues-pr/muhammad-fiaz/logly" alt="GitHub pull requests"></a>
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/github/last-commit/muhammad-fiaz/logly" alt="GitHub last commit"></a>
<a href="https://github.com/muhammad-fiaz/logly/releases"><img src="https://img.shields.io/github/v/release/muhammad-fiaz/logly" alt="GitHub release"></a>
<a href="https://codecov.io/gh/muhammad-fiaz/logly"><img src="https://codecov.io/gh/muhammad-fiaz/logly/graph/badge.svg?token=1G3MU8SDX1" alt="codecov"></a>
<a href="https://github.com/muhammad-fiaz/logly"><img src="https://img.shields.io/github/license/muhammad-fiaz/logly" alt="License"></a>
<a href="https://github.com/muhammad-fiaz/logly/actions/workflows/testing.yml"><img src="https://github.com/muhammad-fiaz/logly/actions/workflows/testing.yml/badge.svg" alt="Testing"></a>
<a href="https://github.com/muhammad-fiaz/logly/actions/workflows/pypi_publish.yml"><img src="https://github.com/muhammad-fiaz/logly/actions/workflows/pypi_publish.yml/badge.svg" alt="PyPI Publish"></a>
<a href="https://github.com/muhammad-fiaz/logly/actions/workflows/docs_publish.yml"><img src="https://github.com/muhammad-fiaz/logly/actions/workflows/docs_publish.yml/badge.svg" alt="Docs Deploy"></a>
<img src="https://img.shields.io/badge/platforms-linux%20%7C%20windows%20%7C%20macos-blue" alt="Supported Platforms">
<a href="https://github.com/muhammad-fiaz/logly/releases/latest"><img src="https://img.shields.io/github/v/release/muhammad-fiaz/logly?label=Latest%20Release&style=flat-square" alt="Latest Release"></a>
<a href="https://github.com/sponsors/muhammad-fiaz"><img src="https://img.shields.io/badge/Sponsor-&#x1F496;-pink?style=social&logo=github" alt="GitHub Sponsors"></a>

<p><em>A Rust-powered, high-performance logging library for Python.</em></p>

<b><a href="https://muhammad-fiaz.github.io/logly/">Documentation</a> |
<a href="https://muhammad-fiaz.github.io/logly/api-reference/logger/">API Reference</a> |
<a href="https://muhammad-fiaz.github.io/logly/getting-started/">Quick Start</a> |
<a href="CONTRIBUTING.md">Contributing</a></b>

</div>

A Rust-powered, high-performance logging library for Python with structured sinks, custom levels, rotation, compression, and telemetry integrations.

> [!NOTE]
> This project is under active development. If you encounter any issues, bugs, or have feature requests, please open an issue on GitHub. Contributions are welcome!

**If you love `logly`, make sure to give it a star!**

---

<details>
<summary><strong>Table of Contents</strong> (click to expand)</summary>

- [Installation](#installation)
  - [pip](#pip)
  - [uv](#uv)
  - [From Source](#from-source)
- [Quick Start](#quick-start)
- [Custom Levels](#custom-levels)
- [Usage Examples](#usage-examples)
  - [File Logging](#file-logging)
  - [Context Binding](#context-binding)
  - [Exception Catching](#exception-catching)
  - [Multiple Sinks](#multiple-sinks)
  - [Independent Loggers](#independent-loggers)
  - [Lazy Evaluation](#lazy-evaluation)
- [Log Levels](#log-levels)
- [Features](#features)
- [Architecture](#architecture)
- [Building from Source](#building-from-source)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Acknowledgements](#acknowledgements)
- [License](#license)
- [Links](#links)

</details>

----

<details>
<summary><strong>Features of Logly</strong> (click to expand)</summary>

| Feature | Description | Documentation |
|---------|-------------|---------------|
| **Rust-native engine** | High-performance logging via PyO3 with zero unsafe Rust | [Docs](https://muhammad-fiaz.github.io/logly/) |
| **10 built-in levels** | TRACE, DEBUG, INFO, NOTICE, SUCCESS, WARNING, ERROR, FAIL, CRITICAL, FATAL | [Docs](https://muhammad-fiaz.github.io/logly/getting-started/) |
| **Custom levels** | Define your own levels with custom priorities and colors | [Docs](https://muhammad-fiaz.github.io/logly/guides/custom-levels/) |
| **Multiple sinks** | Console, file, callable, and network outputs simultaneously | [Docs](https://muhammad-fiaz.github.io/logly/guides/sinks/) |
| **File rotation** | Size-based, time-based, clock-based, and weekday rotation | [Docs](https://muhammad-fiaz.github.io/logly/guides/rotation-retention-compression/) |
| **Compression** | gzip, zip, bz2, xz, zstd, tar support out of the box | [Docs](https://muhammad-fiaz.github.io/logly/guides/rotation-retention-compression/) |
| **JSON logging** | Structured JSON output for storage and analysis | [Docs](https://muhammad-fiaz.github.io/logly/guides/formatting/) |
| **Context binding** | Attach persistent key-value pairs to logs | [Docs](https://muhammad-fiaz.github.io/logly/guides/context-binding/) |
| **Exception catching** | `catch()` decorator and context manager | [Docs](https://muhammad-fiaz.github.io/logly/guides/exception-handling/) |
| **Background workers** | Non-blocking writes with `enqueue=True` | [Docs](https://muhammad-fiaz.github.io/logly/guides/queue-async/) |
| **40+ integrations** | FastAPI, Django, Flask, Rich, Redis, Kafka, and more | [Docs](https://muhammad-fiaz.github.io/logly/integrations/) |
| **Thread-safe** | Safe concurrent logging from multiple threads | [Docs](https://muhammad-fiaz.github.io/logly/guides/concurrency/) |
| **Source location** | Optional clickable `file:line` output | [Docs](https://muhammad-fiaz.github.io/logly/guides/source-location/) |
| **Network logging** | HTTP, TCP, UDP, Syslog sinks | [Docs](https://muhammad-fiaz.github.io/logly/guides/network-logging/) |
| **Color themes** | Custom ANSI color themes per level | [Docs](https://muhammad-fiaz.github.io/logly/guides/custom-colors/) |
| **Independent loggers** | Separate sink sets per logger instance | [Docs](https://muhammad-fiaz.github.io/logly/guides/independent-loggers/) |

</details>

----

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Python** | 3.10+ | Download from [python.org](https://www.python.org/downloads/) |
| **Rust** | Latest stable | Only needed for building from source |
| **Operating System** | Linux, macOS, Windows | Cross-platform support |

## Installation

### Quick Install

```bash
pip install logly
# or
uv add logly
```

> [!TIP]
> Install with optional extras for integrations: `pip install "logly[rich,fastapi]"`

<details>
<summary>All Optional Extras (42 integrations)</summary>

```bash
# Core
pip install logly                            # core only (no optional deps)

# Frameworks & Libraries
pip install "logly[rich]"                    # Rich console output
pip install "logly[fastapi]"                 # FastAPI middleware
pip install "logly[starlette]"               # Starlette middleware
pip install "logly[django]"                  # Django handler + middleware
pip install "logly[flask]"                   # Flask handler
pip install "logly[gunicorn]"                # Gunicorn worker hooks
pip install "logly[uvicorn]"                 # Uvicorn log config
pip install "logly[sqlalchemy]"              # SQLAlchemy query logging
pip install "logly[structlog]"               # Structlog processor
pip install "logly[celery]"                  # Celery task logging
pip install "logly[click]"                   # Click CLI output
pip install "logly[typer]"                   # Typer CLI output
pip install "logly[apscheduler]"             # APScheduler job logging
pip install "logly[rq]"                      # RQ worker logging
pip install "logly[pydantic]"                # Pydantic log handler
pip install "logly[tqdm]"                    # tqdm progress bar sink

# Monitoring & Observability
pip install "logly[opentelemetry]"           # OpenTelemetry export
pip install "logly[prometheus]"              # Prometheus metrics
pip install "logly[elasticsearch]"           # Elasticsearch indexing
pip install "logly[sentry]"                  # Sentry error tracking
pip install "logly[datadog]"                 # Datadog Logs API (stdlib)
pip install "logly[newrelic]"                # New Relic agent
pip install "logly[seq]"                     # Seq structured logs (stdlib)
pip install "logly[telemetry]"               # Generic telemetry (stdlib)

# Cloud Providers
pip install "logly[aws]"                     # AWS CloudWatch Logs
pip install "logly[gcloud]"                  # Google Cloud Logging
pip install "logly[azure]"                   # Azure Monitor

# Data Stores
pip install "logly[redis]"                   # Redis lists/streams
pip install "logly[kafka]"                   # Kafka topics (requires librdkafka)
pip install "logly[mongodb]"                 # MongoDB collections
pip install "logly[postgresql]"              # PostgreSQL tables
pip install "logly[rabbitmq]"                # RabbitMQ queues

# Log Aggregation
pip install "logly[logstash]"                # Logstash TCP/UDP (stdlib)
pip install "logly[graylog]"                 # Graylog GELF (stdlib)
pip install "logly[loki]"                    # Grafana Loki

# Notifications
pip install "logly[discord]"                 # Discord webhooks (stdlib)
pip install "logly[slack]"                   # Slack webhooks (stdlib)
pip install "logly[email]"                   # Email via SMTP (stdlib)
pip install "logly[http]"                    # HTTP endpoint (stdlib)

# Utilities
pip install "logly[compression]"             # Zstandard compression

# Everything
pip install "logly[all]"                     # all of the above
```

> [!NOTE]
> Several integrations (`datadog`, `seq`, `logstash`, `graylog`, `discord`, `slack`, `email`, `http`, `telemetry`) use only Python stdlib and require no extra dependencies.

> [!WARNING]
> The `kafka` extra requires `librdkafka` to be installed on your system. See [Kafka integration docs](https://muhammad-fiaz.github.io/logly/integrations/kafka/) for details.

</details>

<details>
<summary>uv Install Commands</summary>

```bash
# Core
uv add logly

# Frameworks & Libraries
uv add "logly[rich]"
uv add "logly[fastapi]"
uv add "logly[starlette]"
uv add "logly[django]"
uv add "logly[flask]"
uv add "logly[gunicorn]"
uv add "logly[uvicorn]"
uv add "logly[sqlalchemy]"
uv add "logly[structlog]"
uv add "logly[celery]"
uv add "logly[click]"
uv add "logly[typer]"
uv add "logly[apscheduler]"
uv add "logly[rq]"
uv add "logly[pydantic]"
uv add "logly[tqdm]"

# Monitoring & Observability
uv add "logly[opentelemetry]"
uv add "logly[prometheus]"
uv add "logly[elasticsearch]"
uv add "logly[sentry]"
uv add "logly[datadog]"
uv add "logly[newrelic]"
uv add "logly[seq]"
uv add "logly[telemetry]"

# Cloud Providers
uv add "logly[aws]"
uv add "logly[gcloud]"
uv add "logly[azure]"

# Data Stores
uv add "logly[redis]"
uv add "logly[kafka]"
uv add "logly[mongodb]"
uv add "logly[postgresql]"
uv add "logly[rabbitmq]"

# Log Aggregation
uv add "logly[logstash]"
uv add "logly[graylog]"
uv add "logly[loki]"

# Notifications
uv add "logly[discord]"
uv add "logly[slack]"
uv add "logly[email]"
uv add "logly[http]"

# Utilities
uv add "logly[compression]"

# Everything
uv add "logly[all]"
```

</details>

### From Source

```bash
git clone https://github.com/muhammad-fiaz/logly.git
cd logly
uv sync
uv run maturin develop
```

## Quick Start

```python
from logly import logger

logger.trace("Detailed trace")
logger.debug("Debug info")
logger.info("Application started")
logger.notice("Notice message")
logger.success("Operation completed!")
logger.warning("Warning message")
logger.error("Error occurred")
logger.fail("Operation failed")
logger.critical("Critical system error!")
logger.fatal("Fatal system failure!")

logger.complete()
```

## Custom Levels

```python
from logly import logger

# Register a custom level with icon and color
logger.level("HTTP", no=21, color="blue", icon=">")
logger.level("DATABASE", no=22, color="magenta", icon="*")
logger.level("SECURITY", no=35, color="red", icon="!")

# Log with custom levels
logger.log("HTTP", "GET /api/users")
logger.log("DATABASE", "Connected to PostgreSQL")
logger.log("SECURITY", "Authentication failed")

# Use icon in format strings
sink_id = logger.add(
    lambda msg: print(msg, end=""),
    format="{level_icon} {level} | {message}",
    level="TRACE",
)
logger.log("HTTP", "GET /api/users")
logger.remove(sink_id)
# Output: > HTTP | GET /api/users
```

## Usage Examples

### File Logging

```python
from logly import logger

logger.add(
    "logs/app.log",
    level="INFO",
    rotation="daily",
    retention="30 days",
    compression="gzip",
)

logger.info("Application started")
logger.complete()
```

### Context Binding

```python
from logly import logger

user_logger = logger.bind(user_id="12345", request_id="abc-789")
user_logger.info("User logged in")
# Output includes: user_id=12345 request_id=abc-789
```

### Exception Catching

```python
from logly import logger

with logger.catch():
    risky_operation()

# With options
with logger.catch(exclude=ValueError, onerror=lambda e: print(f"Failed: {e}")):
    dangerous_call()
```

### Multiple Sinks

```python
from logly import logger

logger.add("app.log", level="DEBUG", rotation="daily")
logger.add("errors.log", level="ERROR", retention="90 days")
logger.add("stdout", level="INFO", colorize=True)

logger.info("All three sinks receive this")
```

### Independent Loggers

Use `Logger()` when a subsystem needs a separate set of sinks that does not
write to the global logger.

```python
from logly import Logger

api_logger = Logger()
worker_logger = Logger()

api_logger.add("api.log", level="INFO")
worker_logger.add("worker.log", level="DEBUG")

api_logger.info("request accepted")
worker_logger.debug("job claimed")
```

### Lazy Evaluation

```python
from logly import logger

logger.opt(lazy=True).debug("Result: {}", lambda: expensive_computation())
```

For more examples, see the [documentation](https://muhammad-fiaz.github.io/logly/).

---

## Log Levels

| Level | Priority | Method | Use Case |
|-------|----------|--------|----------|
| TRACE | 5 | `logger.trace()` | Very detailed debugging |
| DEBUG | 10 | `logger.debug()` | Debugging information |
| INFO | 20 | `logger.info()` | General information |
| NOTICE | 25 | `logger.notice()` | Notice messages |
| SUCCESS | 30 | `logger.success()` | Successful operations |
| WARNING | 40 | `logger.warning()` | Warning messages |
| ERROR | 50 | `logger.error()` | Error conditions |
| FAIL | 55 | `logger.fail()` | Operation failures |
| CRITICAL | 60 | `logger.critical()` | Critical system errors |
| FATAL | 70 | `logger.fatal()` | Fatal system errors |

---

## Architecture

Logly is built as a modular Rust workspace with a thin PyO3 binding:

| Crate | Purpose |
|-------|---------|
| `error` | Error types and conversions |
| `config` | Configuration data structures |
| `levels` | Log level definitions and registry |
| `record` | Log record builder |
| `color` | ANSI color engine and themes |
| `format` | Template, JSON, and custom formatters |
| `filter` | Level, prefix, extra, and chain filters |
| `rotate` | File rotation policies and execution |
| `compress` | Compression codecs (gzip, zip, bz2, xz, zstd, tar) |
| `concurrency` | Background workers and thread pool |
| `schedule` | Scheduled tasks and scheduler |
| `context` | Bound context, scoped context, patchers |
| `sink` | Sink trait and built-in implementations |
| `core` | Logger engine dispatch |
| `network` | HTTP, TCP, UDP, Syslog sinks |
| `source` | Caller frame inspection |

---

## Building from Source

| Tool | Version | Purpose |
|------|---------|---------|
| **Rust** | Latest stable | Compile the native engine |
| **Python** | 3.10+ | Runtime and build scripts |
| **uv** | Latest | Package manager (recommended) |
| **Maturin** | 1.x | Build backend for PyO3 wheels |

```bash
# Install uv (if not already installed)
pip install uv

# Build the extension in development mode
uv run maturin develop

# Run Python tests
uv run pytest

# Run Rust tests
cargo test --workspace

# Lint
uv run ruff check .
cargo clippy --workspace --all-targets -- -D warnings
```

---

## Documentation

Full documentation is available at: https://muhammad-fiaz.github.io/logly

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## Acknowledgements

Logly's Python API syntax and ergonomics are inspired by [Loguru](https://github.com/Delgan/loguru). The underlying engine is an independent, from-scratch Rust implementation.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Links

- **Documentation**: https://muhammad-fiaz.github.io/logly
- **PyPI**: https://pypi.org/project/logly/
- **Repository**: https://github.com/muhammad-fiaz/logly
- **Issues**: https://github.com/muhammad-fiaz/logly/issues
