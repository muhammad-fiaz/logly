---
title: Rich
description: Rich console output for formatted log display.
---

# Rich

`LoglyRichSink` provides beautiful console output using the Rich library. Implements the write-style sink interface.

## Installation

This integration requires the `rich` package.

::: code-group

```bash [uv]
uv add logly[rich]
```

```bash [pip]
pip install "logly[rich]"
```

```bash [uv (without extras)]
uv add rich
```

```bash [pip (without extras)]
pip install rich
```

:::

::: warning Missing Dependency
If `rich` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'rich'
```
:::

## Usage

```python
from logly import logger
from logly.integrations.rich import LoglyRichSink

logger.add(LoglyRichSink(), colorize=True)
```

## Full Example

```python
from logly import logger
from logly.integrations.rich import LoglyRichSink

# Add Rich sink with colorized output
logger.add(LoglyRichSink(), colorize=True, level="DEBUG")

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```
