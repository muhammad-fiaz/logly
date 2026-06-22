---
title: Rich Integration
description: Add a Rich sink for styled, colorized terminal output with Logly.
---

# Rich Integration

Logly can emit logs through Rich for beautifully styled and colorized console output.

## Example

```python
--8<-- "examples/rich_integration.py"
```

## How It Works

- Call `logger.add(LoglyRichSink(), colorize=True)` to register a Rich-based output sink.
- All log levels (INFO, WARNING, ERROR, SUCCESS) are rendered with Rich's styling and color formatting.
- Use `logger.remove(sink_id)` to unregister the sink when it's no longer needed.
