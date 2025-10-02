---
title: JSON Logging - Logly Examples
description: JSON logging example showing how to configure Logly for structured JSON output, perfect for log aggregation systems.
keywords: python, logging, example, json, structured, aggregation, elk, logly
---

# JSON Logging

This example demonstrates how to configure Logly for structured JSON output, ideal for log aggregation systems like ELK stack, Splunk, or CloudWatch.

## Code Example

```python
from logly import logger
import json

# Configure for JSON output
logger.configure(level="INFO", json=True)

# Add console sink without colors for JSON
logger.add("console", colorize=False)

# Log structured data
logger.info("User authentication successful", user_id=12345, ip="192.168.1.100")
logger.warning("Rate limit exceeded", user_id=12345, requests_per_minute=150)
logger.error("Database connection failed", error_code="ECONNREFUSED", retry_count=3)

# Log with complex nested data
user_data = {
    "id": 12345,
    "name": "John Doe",
    "preferences": {
        "theme": "dark",
        "notifications": True
    }
}
logger.info("User profile updated", user=user_data)
```

## Expected Output

The JSON logging produces structured, machine-readable log entries:

```json
{"timestamp": "2025-01-15T10:30:45.123456Z", "level": "INFO", "message": "User authentication successful", "user_id": 12345, "ip": "192.168.1.100"}
{"timestamp": "2025-01-15T10:30:46.234567Z", "level": "WARNING", "message": "Rate limit exceeded", "user_id": 12345, "requests_per_minute": 150}
{"timestamp": "2025-01-15T10:30:47.345678Z", "level": "ERROR", "message": "Database connection failed", "error_code": "ECONNREFUSED", "retry_count": 3}
{"timestamp": "2025-01-15T10:30:48.456789Z", "level": "INFO", "message": "User profile updated", "user": {"id": 12345, "name": "John Doe", "preferences": {"theme": "dark", "notifications": true}}}
```

**What happens:** Each log entry is serialized as a single JSON object, making it easy to parse and analyze with log aggregation tools.

## Per-Sink JSON Configuration

You can also enable JSON logging for individual sinks using the `json=True` parameter:

```python
from logly import logger

# Regular text console output
logger.add("console")

# JSON file output (structured logging)
logger.add("logs/app.jsonl", json=True)

# JSON console output for debugging
logger.add("console", json=True, filter_min_level="DEBUG")

# Log some events
logger.info("Application started", version="1.2.3", environment="production")
logger.debug("Database connection established", pool_size=10, timeout=30)
logger.warning("High memory usage detected", memory_mb=850, threshold_mb=800)
```

## Pretty JSON for Development

For development and debugging, you can enable pretty printing:

```python
logger.configure(level="INFO", json=True, pretty_json=True)
logger.add("console")

logger.info("Server started", port=8080, workers=4)
```

**Expected Output:**
```json
{
  "timestamp": "2025-01-15T10:30:45.123456Z",
  "level": "INFO",
  "message": "Server started",
  "port": 8080,
  "workers": 4
}
```

**What happens:** Pretty JSON formatting makes logs easier to read during development, with proper indentation and line breaks.

## Integration Examples

### ELK Stack (Elasticsearch, Logstash, Kibana)

```python
logger.configure(level="INFO", json=True)
logger.add("/var/log/app.jsonl")
```

### CloudWatch Logs

```python
logger.configure(level="INFO", json=True)
logger.add("console", colorize=False)
```

## Key Features Demonstrated

- **Structured logging**: Consistent JSON format for all logs
- **Extra fields**: Automatically include additional data in JSON
- **Machine readable**: Perfect for log aggregation and analysis
- **Flexible formatting**: Customize JSON structure as needed