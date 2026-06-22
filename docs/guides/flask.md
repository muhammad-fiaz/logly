---
title: Flask Integration
description: Integrating Logly with Flask applications
---

# Flask Integration

## Basic Setup

```python
from flask import Flask, g, request
from logly import logger
from logly.integrations.flask import LoglyMiddleware

app = Flask(__name__)
LoglyMiddleware(app)
```

::: tip
The `LoglyMiddleware` adds request context (request_id, method, path) to all log messages during request handling.
:::

## Manual Setup

```python
import time
import uuid
from flask import Flask, g, request
from logly import logger

app = Flask(__name__)

@app.before_request
def logly_before_request():
    g.logly_request_id = str(uuid.uuid4())
    g.logly_start = time.perf_counter()
    logger.contextualize(
        request_id=g.logly_request_id,
        method=request.method,
        path=request.path,
    )

@app.after_request
def logly_after_request(response):
    elapsed_ms = (time.perf_counter() - g.logly_start) * 1000
    logger.info(
        "{} {} {} {:.1f}ms",
        request.method,
        request.path,
        response.status_code,
        elapsed_ms,
    )
    return response
```

## Request Context

```python
@app.route("/users/<int:user_id>")
def get_user(user_id):
    logger.info("Fetching user {}", user_id)
    # Logs include: request_id, method, path from context
    return {"user_id": user_id}
```
