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

## Output

```json
{"timestamp": "2025-01-15T10:30:45Z", "level": "INFO", "message": "User authentication successful", "module": "main", "function": "login", "line": 25, "user_id": 12345, "ip": "192.168.1.100"}
{"timestamp": "2025-01-15T10:30:46Z", "level": "WARN", "message": "Rate limit exceeded", "module": "main", "function": "api_handler", "line": 67, "user_id": 12345, "requests_per_minute": 150}
{"timestamp": "2025-01-15T10:30:47Z", "level": "ERROR", "message": "Database connection failed", "module": "main", "function": "db_connect", "line": 89, "error_code": "ECONNREFUSED", "retry_count": 3}
{"timestamp": "2025-01-15T10:30:48Z", "level": "INFO", "message": "User profile updated", "module": "main", "function": "update_profile", "line": 112, "user": {"id": 12345, "name": "John Doe", "preferences": {"theme": "dark", "notifications": true}}}
```

## Pretty JSON Option

For development and debugging, you can enable pretty printing:

```python
logger.configure(level="INFO", json=True, json_indent=2)
logger.add("console", colorize=False)
```

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