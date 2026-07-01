---
title: tqdm
description: tqdm progress bar integration for Logly.
---

# tqdm

`TqdmSink` redirects log output through tqdm progress bars, preventing log messages from interfering with active progress bars.

## Installation

This integration requires the `tqdm` package.

::: code-group

```bash [uv]
uv add logly[tqdm]
```

```bash [pip]
pip install "logly[tqdm]"
```

```bash [uv (without extras)]
uv add tqdm
```

```bash [pip (without extras)]
pip install tqdm
```

:::

::: warning Missing Dependency
If `tqdm` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'tqdm'
```
:::

## Usage

```python
from logly import logger
from logly.integrations.tqdm import TqdmSink
from tqdm import tqdm

logger.remove()
logger.add(TqdmSink(), colorize=True)

for i in tqdm(range(100)):
    if i % 20 == 0:
        logger.info("Processing item {}", i)
```

## Full Example

```python
from logly import logger
from logly.integrations.tqdm import TqdmSink
from tqdm import tqdm
import time

logger.remove()
logger.add(TqdmSink(), colorize=True)

for i in tqdm(range(100)):
    if i % 20 == 0:
        logger.info("Processing item {}", i)
    time.sleep(0.05)

logger.success("Processing complete")
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tqdm_instance` | `Any` | `None` | Optional tqdm class or instance. Uses `tqdm.tqdm` if `None`. |

## Notes

- Uses `tqdm.write()` to safely output log messages without breaking progress bar display
- Integrates cleanly with tqdm progress bars without interfering with their display
- Supports `colorize=True` for colorized log output
