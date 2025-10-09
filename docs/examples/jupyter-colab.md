---
title: Jupyter & Colab Notebooks - Logly Examples
description: Using Logly in Jupyter Notebooks and Google Colab for interactive logging and data science workflows.
keywords: python, logging, jupyter, colab, notebook, interactive, data science
---

# Jupyter & Colab Notebooks

Logly works seamlessly in Jupyter Notebooks and Google Colab, displaying logs directly in notebook output cells.

!!! success "Fixed Issue #76 - Robust Output Display"
    Logly now uses a **multi-layered fallback mechanism** to ensure logs always appear:
    
    1. **Primary**: Python's `sys.stdout` (works in Jupyter/Colab notebook cells)
    2. **Fallback**: Rust's `println!` (always works, even if Python stdout fails)
    
    This dual approach ensures logs are **always visible** - whether you're in a notebook, terminal, or any other environment.
    Previously, logs weren't visible in notebooks because Rust's `println!` wrote to system stdout instead of notebook cells.
    See [Issue #76](https://github.com/muhammad-fiaz/logly/issues/76) for technical details.

---

## Quick Start in Notebooks

### Basic Logging

```python
# Install in notebook (if needed)
!pip install logly

# Import and start logging immediately
from logly import logger

logger.info("Starting data analysis")
logger.success("Data loaded successfully")
logger.warning("Missing values detected")
logger.error("Invalid data format")
```

**Output in notebook cell:**
```
[INFO] Starting data analysis | module=__main__ | function=<module>
[SUCCESS] Data loaded successfully | module=__main__ | function=<module>
[WARNING] Missing values detected | module=__main__ | function=<module>
[ERROR] Invalid data format | module=__main__ | function=<module>
```

---

## Data Science Workflows

### Logging Data Processing Steps

```python
from logly import logger
import pandas as pd

# Configure logging for data pipeline
logger.configure(level="INFO", show_time=False)

# Load data
logger.info("Loading dataset", source="data.csv")
df = pd.read_csv("data.csv")
logger.success("Loaded dataset", rows=len(df), columns=len(df.columns))

# Data cleaning
logger.info("Starting data cleaning")
df_clean = df.dropna()
logger.success("Removed missing values", 
               removed_rows=len(df) - len(df_clean),
               remaining=len(df_clean))

# Feature engineering
logger.info("Creating features")
df_clean['new_feature'] = df_clean['value'] * 2
logger.success("Created features", total_features=len(df_clean.columns))

# Model training
logger.info("Training model", algorithm="RandomForest")
# ... training code ...
logger.success("Model trained", accuracy=0.95, duration_sec=12.3)
```

---

## Machine Learning Pipelines

### Training Progress Logging

```python
from logly import logger
import time

logger.configure(level="INFO", color=True)

# Training loop with progress logging
epochs = 5
for epoch in range(1, epochs + 1):
    logger.info(f"Starting epoch {epoch}/{epochs}")
    
    # Simulate training
    time.sleep(1)
    train_loss = 0.5 - (epoch * 0.08)
    val_loss = 0.6 - (epoch * 0.07)
    
    logger.success(
        f"Epoch {epoch} completed",
        train_loss=f"{train_loss:.4f}",
        val_loss=f"{val_loss:.4f}"
    )

logger.success("Training completed!", final_loss=train_loss)
```

---

## Experiment Tracking

### Logging Hyperparameters and Results

```python
from logly import logger

# Log experiment configuration
logger.info("Starting experiment", 
            experiment_id="exp_001",
            model="XGBoost",
            learning_rate=0.1,
            max_depth=5)

# Log intermediate results
logger.info("Cross-validation results", 
            fold_1=0.89,
            fold_2=0.91,
            fold_3=0.88,
            mean=0.893)

# Log final metrics
logger.success("Experiment completed",
               accuracy=0.92,
               precision=0.89,
               recall=0.94,
               f1_score=0.915)
```

---

## Debugging in Notebooks

### Verbose Logging for Development

```python
from logly import logger

# Enable debug logging for development
logger.configure(level="DEBUG", show_time=True)

def process_data(data):
    logger.debug("Entering process_data", data_type=type(data).__name__)
    
    # Processing steps
    logger.debug("Step 1: Validation")
    if not isinstance(data, list):
        logger.error("Invalid data type", expected="list", got=type(data).__name__)
        return None
    
    logger.debug("Step 2: Transformation", items=len(data))
    result = [x * 2 for x in data]
    
    logger.success("Processing completed", output_size=len(result))
    return result

# Test the function
result = process_data([1, 2, 3, 4, 5])
```

---

## Google Colab Specific

### Installing and Using in Colab

```python
# Install Logly in Colab
!pip install -q logly

# Import and use
from logly import logger

logger.configure(level="INFO", color=True)
logger.info("Running in Google Colab", 
            runtime="Python 3",
            gpu_available=True)

# Works with Colab's output display
from IPython.display import display, HTML

logger.info("Processing data batch", batch_size=32, epoch=1)
# Your code here...
logger.success("Batch processed successfully")
```

---

## File Logging in Notebooks

### Combining Console and File Output

```python
from logly import logger

# Add file sink for persistent logging
logger.add("/content/experiment.log", 
           rotation="daily",
           retention=7)

# Logs go to both notebook output AND file
logger.info("Experiment started")
logger.success("Model saved", path="/content/model.pkl")

# Read back logs from file
logger.info("Reading logs from file...")
sink_ids = logger.list_sinks()
for sink_id in sink_ids:
    info = logger.sink_info(sink_id)
    if info and 'path' in info:
        logger.info(f"Log file: {info['path']}")
```

---

## Best Practices for Notebooks

### 1. **Keep Logs Concise**

```python
# ✅ Good - concise and informative
logger.info("Loading data", rows=1000)

# ❌ Avoid - too verbose for notebooks
logger.debug("Loading row 1...")
logger.debug("Loading row 2...")
# ... thousands of debug logs
```

### 2. **Use Structured Fields**

```python
# ✅ Good - structured data
logger.success("Analysis complete",
               mean=23.5,
               std=4.2,
               samples=1000)

# ❌ Avoid - unstructured strings
logger.success("Analysis complete: mean=23.5, std=4.2, samples=1000")
```

### 3. **Control Log Levels Per Cell**

```python
# Enable debug for specific sections
logger.configure(level="DEBUG")
# ... debugging code ...

# Return to normal level
logger.configure(level="INFO")
# ... regular code ...
```

### 4. **Clean Up Sinks**

```python
# At the end of your notebook
logger.remove_all()  # Remove all sinks
logger.complete()    # Flush pending logs
```

---

## Troubleshooting

### Logs Not Appearing?

If logs don't appear in your notebook:

1. **Check if logging is enabled:**
   ```python
   logger.configure(console=True)  # Ensure console output is enabled
   ```

2. **Verify log level:**
   ```python
   logger.configure(level="TRACE")  # Lower the threshold
   ```

3. **Check sink configuration:**
   ```python
   print(logger.list_sinks())  # Should show at least one sink
   print(logger.all_sinks_info())  # Check sink details
   ```

4. **Restart kernel and reimport:**
   ```python
   # Restart kernel, then:
   from logly import logger
   logger.info("Testing logs")
   ```

---

## Performance Considerations

### Async Logging in Notebooks

```python
# Async logging works great in notebooks
logger.add("/content/large_log.log", 
           async_write=True,
           buffer_size=8192,
           flush_interval=100)

# Log intensive operations without blocking
for i in range(10000):
    logger.debug(f"Processing item {i}", progress=i/10000)

# Ensure all logs are written before continuing
logger.complete()
```

---

## Integration with Notebook Tools

### Using with tqdm Progress Bars

```python
from logly import logger
from tqdm.notebook import tqdm
import time

logger.configure(level="INFO")

for i in tqdm(range(100), desc="Processing"):
    if i % 20 == 0:
        logger.info(f"Checkpoint at item {i}")
    time.sleep(0.05)

logger.success("Processing completed!")
```

### Using with IPython Display

```python
from logly import logger
from IPython.display import display, Markdown

logger.info("Generating report...")

# Combine logging with IPython display
display(Markdown("## Analysis Results"))
logger.success("Analysis completed", 
               total_samples=1000,
               accuracy=0.95)
```

---

## Next Steps

- Learn more about [Structured Logging](json-logging.md)
- Explore [File Operations](file-operations.md) for persistent logging
- Check out [Async Logging](async-logging.md) for performance optimization
- See [Per-Level Controls](per-level-controls.md) for fine-grained control

---

**Questions or Issues?**

If you encounter problems with Logly in notebooks, please:

1. Check the [Troubleshooting Guide](../guides/troubleshooting.md)
2. Search [existing issues](https://github.com/muhammad-fiaz/logly/issues)
3. [Open a new issue](https://github.com/muhammad-fiaz/logly/issues/new) if needed
