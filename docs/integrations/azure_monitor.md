---
title: Azure Monitor
description: Send log records to Azure Monitor/Application Insights.
---

# Azure Monitor

`AzureMonitorSink` sends log records to Azure Monitor or Application Insights. Supports connection string configuration and severity mapping.

## Installation

This integration requires the `azure-monitor-opentelemetry-exporter` package.

::: code-group

```bash [uv]
uv add logly[azure]
```

```bash [pip]
pip install "logly[azure]"
```

```bash [uv (without extras)]
uv add azure-monitor-opentelemetry-exporter
```

```bash [pip (without extras)]
pip install azure-monitor-opentelemetry-exporter
```

:::

::: warning Missing Dependency
If `azure.monitor.opentelemetry.exporter` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'azure.monitor'
```
:::

## Usage

```python
from logly import logger
from logly.integrations.azure_monitor import AzureMonitorSink

logger.add(
    AzureMonitorSink(connection_string="InstrumentationKey=...")
)
```

## Full Example

```python
from logly import logger
from logly.integrations.azure_monitor import AzureMonitorSink

logger.add(
    AzureMonitorSink(
        connection_string="InstrumentationKey=abc123;IngestionEndpoint=https://.../",
        service_name="my-api",
        cloud_role="production",
    ),
    level="INFO",
)

logger.info("Request processed")
logger.error("Downstream service unavailable", service="payments")
```
