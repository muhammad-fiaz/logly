---
title: Discord
description: Send log entries to Discord webhooks.
---

# Discord

`DiscordHandler` sends log entries to a Discord channel via webhook. Uses the Python standard library (`urllib.request`) - no extra dependencies required.

## Installation

This integration requires the `aiohttp` package.

::: code-group

```bash [uv]
uv add logly[discord]
```

```bash [pip]
pip install "logly[discord]"
```

```bash [uv (without extras)]
uv add aiohttp
```

```bash [pip (without extras)]
pip install aiohttp
```

:::

::: warning Missing Dependency
If `aiohttp` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'aiohttp'
```
:::

## Usage

```python
from logly import logger
from logly.integrations.discord import DiscordHandler

handler = DiscordHandler(
    "https://discord.com/api/webhooks/...",
    level="WARNING",
)
logger.add(handler, level="WARNING")
```

## Constructor Args

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `webhook_url` | `str` | `""` | Discord webhook URL |
| `timeout` | `float` | `10.0` | HTTP request timeout in seconds |
| `username` | `str \| None` | `None` | Override webhook username |
| `avatar_url` | `str \| None` | `None` | Override webhook avatar URL |

## Tips

- Use `level="WARNING"` or higher to avoid flooding your Discord channel.
- Create a dedicated webhook per environment (dev, staging, production).

## Full Example

```python
from logly import logger
from logly.integrations.discord import DiscordHandler

handler = DiscordHandler(
    webhook_url="https://discord.com/api/webhooks/123/abc...",
    timeout=15.0,
    username="Production Alerts",
)
logger.add(handler, level="ERROR")

logger.critical("Service is down", service="api-gateway")
```
