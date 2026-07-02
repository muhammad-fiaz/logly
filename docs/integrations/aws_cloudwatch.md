---
title: AWS CloudWatch
description: Send log records to AWS CloudWatch Logs.
---

# AWS CloudWatch

`CloudWatchSink` sends log records to AWS CloudWatch Logs with batching and background flushing. Automatically creates log groups and streams.

## Installation

This integration requires the `boto3` package.

::: code-group

```bash [uv]
uv add logly[aws]
```

```bash [pip]
pip install "logly[aws]"
```

```bash [uv (without extras)]
uv add boto3
```

```bash [pip (without extras)]
pip install boto3
```

:::

::: warning Missing Dependency
If `boto3` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'boto3'
```
:::

## Usage

```python
import logging
from logly.integrations.aws_cloudwatch import CloudWatchSink

logger = logging.getLogger("myapp")
logger.addHandler(CloudWatchSink(
    log_group="my-app",
    log_stream="main",
))
logger.setLevel(logging.INFO)
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `log_group` | (required) | CloudWatch log group name |
| `log_stream` | (required) | CloudWatch log stream name |
| `region` | `None` | AWS region (uses boto3 default if not set) |
| `batch_size` | `10000` | Max events per batch |
| `flush_interval` | `5` | Seconds between background flushes |
| `create_group` | `True` | Auto-create log group if missing |
| `create_stream` | `True` | Auto-create log stream if missing |

## Full Example

```python
import logging
from logly.integrations.aws_cloudwatch import CloudWatchSink

logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)

handler = CloudWatchSink(
    log_group="/aws/lambda/my-function",
    log_stream="2024-01-15",
    region="us-east-1",
    batch_size=5000,
    flush_interval=10,
)
logger.addHandler(handler)

logger.info("Lambda invoked")
logger.warning("Rate limit approaching")
logger.error("External API timeout")
```
