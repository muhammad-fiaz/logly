---
title: FastAPI Integration
description: Attach Logly middleware to FastAPI for automatic request logging with context.
---

# FastAPI Integration

Use Logly's FastAPI middleware to automatically log every request with method, path, status code, and duration.

## Example

```python
--8<-- "examples/fastapi_integration.py"
```

## How It Works

- Add `LoglyMiddleware` to your `FastAPI` app to intercept all requests and responses.
- The middleware enriches each log entry with HTTP method, URL path, response status, and execution time.
- Use `logger.info()` inside your route handlers as usual - Logly merges handler and middleware logs seamlessly.
