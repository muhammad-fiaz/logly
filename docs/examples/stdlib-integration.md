---
title: Stdlib Integration
description: Route Python's standard library logging through Logly for unified output.
---

# Stdlib Integration

Use Logly's `InterceptHandler` to redirect all standard library `logging` calls through Logly, unifying output across frameworks.

## Example

```python
--8<-- "examples/stdlib_integration.py"
```

## How It Works

- Pass `InterceptHandler()` to `logging.basicConfig()` to capture all stdlib log records.
- Third-party libraries (uvicorn, Django, Flask) that use `logging` will automatically route through Logly.
- You can configure individual loggers with `logging.getLogger("name")` and their output flows through Logly's formatting and filtering.
