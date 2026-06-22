---
title: Django Integration
description: Route Django logging through Logly with a custom handler and middleware.
---

# Django Integration

Logly provides a Django handler and middleware to capture request context and route all application logs through Logly.

## Example

```python
--8<-- "examples/django_integration.py"
```

## How It Works

- Add `LoglyHandler` to your `LOGGING` dict in `settings.py` to forward Django log records to Logly.
- Add `LoglyMiddleware` to `MIDDLEWARE` to attach request context (method, path, status) to every log entry.
- Logly's structured output replaces Django's default `LOGGING` configuration with richer formatting and filtering.
