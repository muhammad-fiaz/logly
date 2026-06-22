---
title: Django Integration
description: Custom logging handler and middleware for Django
---

# Django Integration

Logly provides `LoglyHandler` and `LoglyMiddleware` for Django applications.

## Handler Setup

```python
# settings.py
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "logly": {
            "class": "logly.integrations.django.LoglyHandler",
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["logly"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["logly"],
            "level": "INFO",
            "propagate": False,
        },
        "myapp": {
            "handlers": ["logly"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
```

## Middleware Setup

```python
# settings.py
MIDDLEWARE = [
    "logly.integrations.django.LoglyMiddleware",
    # ... other middleware
]
```

## What Middleware Captures

| Field | Description |
|-------|-------------|
| `request_id` | Unique request identifier |
| `method` | HTTP method |
| `path` | Request path |
| `client_ip` | Client IP address |
| Response timing | Logged automatically |

## Usage in Views

```python
from logly import logger

def my_view(request):
    logger.info("Processing request for {}", request.path)
    # Output includes request_id, method, path, client_ip

    try:
        result = process_data()
        logger.info("Request completed")
        return JsonResponse({"result": result})
    except Exception:
        logger.exception("Request failed")
        return JsonResponse({"error": "Internal server error"}, status=500)
```

## Custom Format

```python
# settings.py
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "logly": {
            "format": "{asctime} | {levelname} | {message}",
        },
    },
    "handlers": {
        "logly": {
            "class": "logly.integrations.django.LoglyHandler",
            "level": "DEBUG",
            "formatter": "logly",
        },
    },
    "root": {
        "handlers": ["logly"],
        "level": "INFO",
    },
}
```

## With Logly Configuration

```python
from logly import logger

# Configure Logly sinks in Django
logger.add(
    "logs/django.log",
    level="INFO",
    rotation="daily",
    retention="30 days",
    compression="gzip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {extra[request_id]} | {message}",
)

logger.add(
    "logs/django_errors.log",
    level="ERROR",
    rotation="daily",
    retention="90 days",
    serialize=True,
)
```

## ASGI Support

For Django ASGI applications, `LoglyMiddleware` works with both sync and async views:

```python
# settings.py (ASGI)
ASGI_APPLICATION = "myproject.asgi.application"

MIDDLEWARE = [
    "logly.integrations.django.LoglyMiddleware",
    # ... other middleware
]
```
