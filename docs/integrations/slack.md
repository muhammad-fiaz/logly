---
title: Slack
description: Send log entries to Slack webhooks.
---

# Slack

`SlackHandler` sends log entries to a Slack channel via incoming webhook. No extra dependencies required.

## Installation

This integration uses Python's standard library (`urllib.request`). No additional packages needed.

::: code-group

```bash [uv]
uv add logly
```

```bash [pip]
pip install logly
```

:::

::: warning Missing Dependency
If `slack-sdk` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'slack_sdk'
```
:::

## Usage

```python
from logly import logger
from logly.integrations.slack import SlackHandler

handler = SlackHandler(
    "https://hooks.slack.com/services/...",
    channel="#logs",
    username="Logly Bot",
)
logger.add(handler, level="WARNING")
```

## Constructor Args

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `webhook_url` | `str` | `""` | Slack incoming webhook URL |
| `channel` | `str \| None` | `None` | Channel override for the webhook |
| `username` | `str \| None` | `None` | Username override for the webhook |
| `icon_emoji` | `str \| None` | `None` | Emoji override for the webhook icon |
| `timeout` | `float` | `10.0` | HTTP request timeout in seconds |

## Tips

- Use a dedicated Slack channel for production alerts to keep them separate from development noise.
- Set `icon_emoji` to `":rotating_light:"` for critical alerts.

## Full Example

```python
from logly import logger
from logly.integrations.slack import SlackHandler

handler = SlackHandler(
    webhook_url="https://hooks.slack.com/services/T00/B00/xxx",
    channel="#ops-alerts",
    username="Logly Alerts",
    icon_emoji=":warning:",
)
logger.add(handler, level="WARNING")

logger.warning("High memory usage detected", usage="87%")
logger.error("Database connection pool exhausted")
```
