---
title: Google Cloud Logging
description: Send log records to Google Cloud Logging (Stackdriver).
---

# Google Cloud Logging

`GoogleCloudLoggingHandler` sends log records to Google Cloud Logging (formerly Stackdriver). Supports structured logging, severity mapping, and resource configuration.

## Installation

This integration requires the `google-cloud-logging` package.

::: code-group

```bash [uv]
uv add logly[gcloud]
```

```bash [pip]
pip install "logly[gcloud]"
```

```bash [uv (without extras)]
uv add google-cloud-logging
```

```bash [pip (without extras)]
pip install google-cloud-logging
```

:::

::: warning Missing Dependency
If `google.cloud.logging` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'google.cloud.logging'
```
:::

## Usage

```python
from logly import logger
from logly.integrations.google_cloud_logging import GoogleCloudLoggingHandler

logger.add(GoogleCloudLoggingHandler(project_id="my-project"))
```

## Full Example

```python
from logly import logger
from logly.integrations.google_cloud_logging import GoogleCloudLoggingHandler

logger.add(
    GoogleCloudLoggingHandler(
        project_id="my-project",
        log_name="my-app-log",
        resource_type="gae_app",
        labels={"environment": "production"},
    ),
    level="INFO",
)

logger.info("Application started")
logger.error("Request failed", status_code=500)
```
