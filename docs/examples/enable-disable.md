---
title: Enable/Disable Logging
description: Conditionally enable or disable logging for specific names.
---

# Enable/Disable Logging

Logly lets you enable or disable logging for specific module names.

## Example

```python
--8<-- "examples/enable_disable.py"
```

## How It Works

- `logger.disable("name")` suppresses all log messages from sources matching that name.
- `logger.enable("name")` re-enables logging for that source.
- These calls are **additive** — disabling one name does not affect other names.
