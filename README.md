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
<a href="https://github.com/muhammad-fiaz/logly/actions/workflows/docs.yml"><img src="https://github.com/muhammad-fiaz/logly/actions/workflows/docs.yml/badge.svg" alt="Deploy Documentation"></a>
<a href="https://github.com/muhammad-fiaz/logly/actions/workflows/python_publish.yaml"><img src="https://github.com/muhammad-fiaz/logly/actions/workflows/python_publish.yaml/badge.svg" alt="Publish Python distributions"></a>
<a href="https://github.com/muhammad-fiaz/logly/actions/workflows/testing.yml"><img src="https://github.com/muhammad-fiaz/logly/actions/workflows/testing.yml/badge.svg" alt="Testing"></a>
<a href="https://github.com/muhammad-fiaz/logly/actions/workflows/github-code-scanning/codeql"><img src="https://github.com/muhammad-fiaz/logly/actions/workflows/github-code-scanning/codeql/badge.svg" alt="CodeQL"></a>
<a href="https://github.com/muhammad-fiaz/logly/actions/workflows/dependabot/dependabot-updates"><img src="https://github.com/muhammad-fiaz/logly/actions/workflows/dependabot/dependabot-updates/badge.svg" alt="Dependabot Updates"></a>
<a href="https://github.com/muhammad-fiaz/logly/actions/workflows/python-package.yaml"><img src="https://github.com/muhammad-fiaz/logly/actions/workflows/python-package.yaml/badge.svg" alt="Run Tests"></a>

<p><em>Rust-powered, Loguru-like logging for Python.</em></p>

**📚 [Documentation](https://muhammad-fiaz.github.io/logly/) | [API Reference](https://muhammad-fiaz.github.io/logly/api-reference/) | [Quick Start](https://muhammad-fiaz.github.io/logly/quickstart/)**

</div>

---

## Overview

**Logly** is a high-performance logging library for Python, powered by Rust. It combines the familiar Loguru-like API with the performance and safety guarantees of Rust.

Built with a modular Rust backend using PyO3/Maturin, Logly provides fast logging while maintaining memory safety and thread safety through Rust's ownership system.

> ⚠️ **Active Development**: Logly is actively developed. Performance continues to improve with each release. 

### 🎯 Why Logly?

Logly combines the simplicity of Python with the performance and safety of Rust, providing:

- **High Performance**: Rust-powered backend with optimized data structures
- **Memory Safety**: No data races, guaranteed thread safety
- **Comprehensive Solution**: Full-featured logging with async, rotation, filtering, and callbacks
- **Developer Friendly**: Intuitive API inspired by Loguru

### ✨ Key Features

- 🚀 **Rust-Powered Backend**: High-performance logging with async buffering
- 📦 **Modular Architecture**: Clean separation (backend, config, format, utils)
- 🔄 **Async Logging**: Background thread writing with configurable buffering
- 📋 **Structured JSON**: Native JSON support with custom fields and pretty printing
- 🎛️ **Per-Level Controls**: Fine-grained control over console output, timestamps, colors, and storage
- 🔧 **Smart Rotation**: Time-based (daily/hourly/minutely) and size-based rotation
- 🗜️ **Compression**: Built-in gzip and zstd compression for rotated files
- 🎯 **Multi-Sink**: Multiple outputs with independent filtering and formatting
- 🔍 **Rich Filtering**: Filter by level, module, or function name
- 📞 **Callbacks**: Custom log processing with async execution and color styling
- 🛡️ **Memory Safe**: Rust's ownership system prevents data races
- 🧵 **Thread Safe**: Lock-free operations with optimized synchronization

---

## Installation

### From PyPI (Recommended)

```bash
pip install logly
```

### From Source (Development)

Requires: Python 3.10+, Rust 1.70+, Maturin

```bash
git clone https://github.com/muhammad-fiaz/logly.git
cd logly
pip install maturin
maturin develop  # Development build
```

For detailed installation instructions, see the [Installation Guide](https://muhammad-fiaz.github.io/logly/installation/).

---

## Quick Start

```python
from logly import logger

# Add console output
logger.add("console")

# Add file output with rotation
logger.add(
    "logs/app.log",
    rotation="daily",        # Rotate daily
    retention=7,             # Keep 7 days
    date_enabled=True,       # Add date to filename
    async_write=True         # Async writing for performance
)

# Configure global settings
logger.configure(
    level="INFO",
    color=True,
    show_time=True,
    json=False
)

# Basic logging
logger.info("Application started", version="1.0.0")
logger.success("Deployment successful 🚀", region="us-west")
logger.warning("High memory usage", usage_percent=85)
logger.error("Database connection failed", retry_count=3)

# Structured logging with context
request_logger = logger.bind(request_id="r-123", user="alice")
request_logger.info("Processing request")

# Context manager for temporary context
with logger.contextualize(step=1):
    logger.debug("Processing step 1")

# Exception logging
@logger.catch(reraise=False)
def may_fail():
    return 1 / 0

# Async callbacks for real-time processing
def alert_on_error(record):
    if record["level"] == "ERROR":
        send_alert(record["message"])

callback_id = logger.add_callback(alert_on_error)

# Ensure all logs are written before exit
logger.complete()
```



---

## Advanced Features

### 1. File Rotation & Retention

```python
# Time-based rotation
logger.add("logs/app.log", rotation="daily", retention=30)  # Keep 30 days
logger.add("logs/app.log", rotation="hourly", retention=24)  # Keep 24 hours

# Size-based rotation
logger.add("logs/app.log", size_limit="10MB", retention=5)  # Keep 5 files
logger.add("logs/app.log", size_limit="100MB", retention=10)

# Combined rotation
logger.add("logs/app.log", rotation="daily", size_limit="50MB", retention=7)
```

### 2. Per-Sink Filtering

```python
# Level-based filtering
logger.add("logs/debug.log", filter_min_level="DEBUG")
logger.add("logs/errors.log", filter_min_level="ERROR")

# Module-based filtering
logger.add("logs/database.log", filter_module="myapp.database")
logger.add("logs/api.log", filter_module="myapp.api")

# Function-based filtering
logger.add("logs/auth.log", filter_function="authenticate")
```

### 3. Structured JSON Logging

```python
# Enable JSON output
logger.configure(json=True)

# Pretty JSON for development
logger.configure(json=True, pretty_json=True)

# Log structured data
logger.info("User login", user_id=123, ip="192.168.1.1", success=True)
# Output: {"timestamp":"2025-10-02T12:00:00Z","level":"INFO","message":"User login","fields":{"user_id":123,"ip":"192.168.1.1","success":true}}
```

### 4. Async Callbacks

```python
# Register callback for real-time processing
def send_to_monitoring(record):
    if record["level"] in ["ERROR", "CRITICAL"]:
        monitoring_service.send_alert(record)

callback_id = logger.add_callback(send_to_monitoring)

# Callbacks execute in background threads (zero blocking)
logger.error("Critical system failure", service="database")

# Remove callback when done
logger.remove_callback(callback_id)
```

### 5. Per-Level Control

```python
# Control console output per level
logger.configure(
    console_levels={"DEBUG": False, "INFO": True, "ERROR": True}
)

# Control timestamps per level
logger.configure(
    show_time=False,
    time_levels={"ERROR": True}  # Only show time for errors
)

# Control colors per level
logger.configure(
    color_levels={"INFO": False, "ERROR": True}
)

# Control file storage per level
logger.configure(
    storage_levels={"DEBUG": False}  # Don't write DEBUG to files
)
```

### 6. Custom Formatting

```python
# Simple format
logger.add("console", format="{time} [{level}] {message}")

# Detailed format
logger.add(
    "logs/detailed.log",
    format="{time} | {level:8} | {module}:{function} | {message} | {extra}"
)

# JSON-like format
logger.add(
    "logs/json-like.log",
    format='{{"timestamp": "{time}", "level": "{level}", "msg": "{message}"}}'
)
```

For complete feature documentation, see the [API Reference](https://muhammad-fiaz.github.io/logly/api-reference/).

---

## Testing & Quality

Logly maintains **96%+ code coverage** with comprehensive testing:

```bash
# Run tests
pytest

# With coverage
pytest --cov=logly --cov-report=term-missing

# Code quality (10.00/10 score)
pylint logly/
```

For development guidelines, see the [Development Guide](https://muhammad-fiaz.github.io/logly/guides/development/).

---

## Documentation

Complete documentation is available at [muhammad-fiaz.github.io/logly](https://muhammad-fiaz.github.io/logly/):

- 📖 [Getting Started Guide](https://muhammad-fiaz.github.io/logly/guides/getting-started/)
- 📚 [API Reference](https://muhammad-fiaz.github.io/logly/api-reference/)
- 🔧 [Configuration Guide](https://muhammad-fiaz.github.io/logly/guides/configuration/)
- 🚀 [Production Deployment](https://muhammad-fiaz.github.io/logly/guides/production-deployment/)
- 💡 [Examples](https://muhammad-fiaz.github.io/logly/examples/)

---

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).

### Want to contribute?

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

A big thank you to all contributors! 💖

[![Contributors](https://contrib.rocks/image?repo=muhammad-fiaz/logly&max=2000)](https://github.com/muhammad-fiaz/logly/graphs/contributors)

---

## Changelog

See the [GitHub Releases](https://github.com/muhammad-fiaz/logly/releases) page for detailed release notes.

---

## Acknowledgements

Special thanks to:

- **Loguru**: For inspiring the API design
- **tracing**: The Rust logging framework powering the backend
- **PyO3**: For seamless Python-Rust integration
- **Maturin**: For simplifying the build process
- **All contributors**: For valuable feedback and contributions

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=muhammad-fiaz/logly&type=Date&bg=transparent)](https://github.com/muhammad-fiaz/logly/)

**⭐ Star the repository if you find Logly useful!**

</div>
