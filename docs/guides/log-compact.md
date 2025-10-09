---
title: log_compact Parameter Guide - Logly
description: Complete guide to using log_compact for Jupyter Notebooks, Google Colab, and space-constrained environments.
keywords: python, logging, jupyter, colab, notebook, compact, log_compact, configuration
---

# Compact Log Format

The `log_compact` parameter enables a condensed output format optimized for space-constrained environments.

---

## Overview

The `log_compact` parameter is a boolean configuration option that reduces log verbosity while maintaining essential information. This format is particularly useful in environments with limited display width.

**Supported Environments:**

- Jupyter Notebooks
- Google Colab
- Terminal emulators with narrow widths
- Dashboard displays
- Split-screen coding environments

---

## Usage Guidelines

### Recommended Use Cases

Use `log_compact=True` in the following scenarios:

1. **Interactive Notebooks**
   - Jupyter/Colab environments where horizontal space is limited
   - Long log lines cause awkward wrapping
   - Cleaner output improves readability

2. **Narrow Terminal Windows**
   - Terminal width under 120 characters
   - Split-screen development setups
   - Remote SSH sessions with limited width

3. **Monitoring Dashboards**
   - Real-time log displays on compact screens
   - Embedded log viewers in web applications
   - Mobile device log viewing

4. **Multi-Panel IDEs**
   - VS Code with multiple panels
   - Vim/Emacs split windows
   - Any IDE with reduced panel width

### Not Recommended For

Avoid `log_compact=True` in these situations:

1. **Production Environments**
   - Standard terminal width (120+ characters)
   - Log files for grep/awk parsing
   - Log aggregation systems (ELK, Splunk)

2. **Detailed Debugging**
   - Complex error investigation
   - Production issue analysis
   - Cases requiring full context

3. **Automated Processing**
   - Log parsing scripts expecting standard format
   - CI/CD pipeline analysis
   - Structured log processing tools

---

## Configuration

---

## Configuration

### Basic Configuration

```python
from logly import logger

# Enable compact logging
logger.configure(log_compact=True)

logger.info("Starting data analysis")
logger.success("Loaded 1000 records from database")
logger.warning("Missing values detected in column 'age'")
logger.error("Failed to connect to API", retry_count=3)
```

### Output Comparison

**Standard Format (`log_compact=False`):**
```
2025-01-15T10:30:15.123456+00:00 [INFO] Starting data analysis | module=__main__ | function=<module>
2025-01-15T10:30:15.234567+00:00 [SUCCESS] Loaded 1000 records from database | module=data_loader | function=load_data
```

**Compact Format (`log_compact=True`):**
```
[INFO] Starting data analysis
[SUCCESS] Loaded 1000 records from database
```

### Parameter Details

```python
logger.configure(
    level: str = "INFO",
    color: bool = True,
    log_compact: bool = False  # Default: False
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `log_compact` | `bool` | `False` | Enable compact format. Reduces timestamp verbosity and optimizes spacing for narrow displays. |

### Format Changes in Compact Mode

Compact mode applies the following optimizations:

1. **Timestamps** - Removed or abbreviated
2. **Module Information** - Simplified or omitted
3. **Extra Fields** - Only essential fields included
4. **Spacing** - Minimal padding for compact display

---

## Examples

---

## Examples

### Jupyter Notebook Workflow

```python
from logly import logger
import pandas as pd

# Configure for notebook environment
logger.configure(
    level="INFO",
    log_compact=True,
    color=True,
    show_time=False
)

# Data processing pipeline
logger.info("Loading dataset")
df = pd.read_csv("sales_data.csv")
logger.success(f"Loaded {len(df)} rows")

logger.info("Cleaning data")
df_clean = df.dropna()
logger.success(f"Removed {len(df) - len(df_clean)} rows")

logger.info("Running analysis")
result = df_clean.groupby('category')['sales'].sum()
logger.success("Analysis complete", categories=len(result))
```

**Output:**
```
[INFO] Loading dataset
[SUCCESS] Loaded 1000 rows
[INFO] Cleaning data
[SUCCESS] Removed 50 rows
[INFO] Running analysis
[SUCCESS] Analysis complete (categories: 5)
```

### Machine Learning Training

```python
from logly import logger

# Configure for training environment
logger.configure(
    level="DEBUG",
    log_compact=True,
    color=True,
    show_module=False,
    show_function=False
)

# Training loop
epochs = 10
for epoch in range(1, epochs + 1):
    logger.info(f"Epoch {epoch}/{epochs}")
    
    train_loss = 0.5 / epoch
    val_loss = 0.6 / epoch
    
    logger.success(
        f"Epoch {epoch} complete",
        train_loss=round(train_loss, 4),
        val_loss=round(val_loss, 4)
    )
    
    if val_loss < 0.1:
        logger.success("Training complete - target loss reached")
        break
```

### Development Environment

```python
from logly import logger

# Configure for split-screen development
logger.configure(
    level="DEBUG",
    log_compact=True,
    color=True,
    show_time=True
)

def process_user_data(user_id: int):
    logger.debug(f"Processing user {user_id}")
    logger.info("Fetching user data")
    logger.success("User data retrieved", user_id=user_id)
    logger.info("Validating data")
    logger.success("Validation passed")
    return {"user_id": user_id, "status": "processed"}

result = process_user_data(123)
logger.success("Processing complete", result=result)
```

---

## Advanced Configurations

### Minimal Notebook Output

```python
# Extremely compact for notebooks
logger.configure(
    log_compact=True,
    show_time=False,
    show_module=False,
    show_function=False
)

logger.info("Minimal output")
logger.success("Perfect for notebooks")
```

**Output:**
```
[INFO] Minimal output
[SUCCESS] Perfect for notebooks
```

### Compact JSON Logging

```python
# Compact JSON format
logger.configure(
    log_compact=True,
    json=True,
    pretty_json=False
)

logger.info("User login", user_id=123, role="admin")
```

**Output:**
```json
{"level":"INFO","message":"User login","user_id":123,"role":"admin"}
```

---

## Performance Characteristics

### Resource Usage

| Aspect | Compact Mode | Standard Mode |
|--------|--------------|---------------|
| Memory | Lower (shorter strings) | Higher (full formatting) |
| Speed | Slightly faster | Slightly slower |
| File Size | 20-40% smaller | Standard size |

Performance differences are typically negligible (< 1% memory, < 0.1ms per entry).

### File Size Comparison

- **Standard Format:** 1000 lines ≈ 150KB
- **Compact Format:** 1000 lines ≈ 90KB

---

## Best Practices

### Recommended Patterns

**Interactive Development:**
```python
logger.configure(log_compact=True, show_time=False)
```

**Production Environments:**
```python
logger.configure(log_compact=False)  # Full details
```

**Color Enhancement:**
```python
logger.configure(log_compact=True, color=True)
```

### Common Mistakes

**Avoid in Production Logs:**
```python
# Not recommended - loses important context
logger.configure(log_compact=True)
logger.add("production.log")
```

**Conflicting Settings:**
```python
# Contradictory - pretty_json is already verbose
logger.configure(log_compact=True, pretty_json=True)
```

**Debugging Complex Issues:**
```python
# Not recommended - need full context
logger.configure(log_compact=True, level="DEBUG")
```

---

## Environment Detection

For automatic environment detection, use this pattern:

```python
import sys

# Detect notebook environment
IN_NOTEBOOK = 'ipykernel' in sys.modules

logger.configure(
    log_compact=IN_NOTEBOOK,
    show_time=not IN_NOTEBOOK
)
```

---

## Summary

| Aspect | Compact Mode | Standard Mode |
|--------|--------------|---------------|
| **Best For** | Notebooks, narrow terminals, dashboards | Production logs, debugging |
| **Output Length** | 20-40% shorter | Full details |
| **Readability** | Cleaner in constrained spaces | More context |
| **Performance** | Slightly faster (negligible) | Slightly slower (negligible) |
| **File Size** | Smaller | Larger |
| **Use Case** | Interactive development | Production systems |

---

## Related Documentation

- [Jupyter/Colab Examples](../examples/jupyter-colab.md)
- [Configuration Guide](configuration.md)
- [Quick Start](../quickstart.md)
