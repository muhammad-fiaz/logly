---
title: Python 3.14 Support - Logly
description: Comprehensive guide to using Logly with Python 3.14 features including deferred annotations, template strings, improved pathlib, and more.
keywords: python, python 3.14, logging, new features, template strings, annotations, logly
---

# Python 3.14 Support

Logly fully supports Python 3.14 and takes advantage of its new features. This guide demonstrates how to use Python 3.14's capabilities with Logly for enhanced logging experiences.

## Overview

Python 3.14 introduces several major improvements:

- **PEP 649**: Deferred evaluation of annotations
- **PEP 750**: Template strings (t-strings)
- **Improved pathlib**: New `copy()`, `move()`, and `info` methods
- **InterpreterPoolExecutor**: True parallelism with sub-interpreters
- **UUID7**: Time-sortable UUIDs
- **Better exception syntax**: Simplified exception handling
- **Performance improvements**: Faster execution and reduced memory usage

## Installation

Logly supports Python 3.10 through 3.14:

```bash
# Using pip
pip install logly

# Using uv (recommended)
uv pip install logly

# Verify Python version
python --version  # Should show Python 3.14.x
```

## Python 3.14 Features with Logly

### 1. Deferred Annotations (PEP 649)

Python 3.14's deferred annotation evaluation improves type hint handling without forward references:

```python
from __future__ import annotations
from logly import logger
import annotationlib

class LogProcessor:
    """Example using deferred annotations with Logly."""
    
    next_processor: LogProcessor | None = None  # No quotes needed!
    
    def __init__(self, name: str):
        self.name = name
        logger.info("Processor created", processor_name=name)
    
    def process(self, message: str) -> LogProcessor | None:
        """Process a log message and return next processor."""
        logger.debug("Processing message", 
                    processor=self.name, 
                    message=message)
        return self.next_processor

# Inspect annotations at runtime
def inspect_processor_annotations():
    annotations = annotationlib.get_annotations(
        LogProcessor, 
        format=annotationlib.Format.VALUE
    )
    logger.info("Processor annotations", annotations=str(annotations))

# Usage
logger.configure(level="DEBUG")
processor = LogProcessor("MainProcessor")
inspect_processor_annotations()
logger.complete()
```

**Output:**
```
[INFO] Processor created | processor_name=MainProcessor
[INFO] Processor annotations | annotations={'next_processor': 'LogProcessor | None', ...}
```

### 2. Template Strings (PEP 750) - Not for Logly Format

**Important Note**: Python 3.14's new template strings (t-strings) are a language feature for creating `Template` objects, which is **different** from Logly's format strings.

**Python 3.14 Template Strings (t-strings):**
```python
from string.templatelib import Template

# This is Python 3.14's t-string feature (NOT used in Logly)
name = "Alice"
tmpl: Template = t"Hello {name}"  # Creates a Template object
print(tmpl.strings)  # ('Hello ', '')
print(tmpl.interpolations)  # (name,)
```

**Logly Format Strings (Custom Pattern):**
```python
from logly import logger

# Logly uses its own format string system (similar to Loguru)
logger.add(
    "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)
logger.info("User login", username="Alice")
# Output: 2025-10-11 13:45:32 | INFO | User login | username=Alice
```

While Python 3.14's t-strings are for general templating, **Logly's format strings** are specifically designed for log formatting with time patterns, level names, and custom fields.

### 3. UUID7 for Request Tracking

Python 3.14's UUID7 provides time-sortable unique identifiers, perfect for request/transaction tracking:

```python
from uuid import uuid7
from logly import logger

class RequestHandler:
    """Handle requests with UUID7 tracking."""
    
    def handle_request(self, endpoint: str, data: dict):
        # Generate time-sortable UUID
        request_id = uuid7()
        
        # Bind request context
        request_logger = logger.bind(
            request_id=str(request_id),
            endpoint=endpoint
        )
        
        request_logger.info("Request started")
        
        try:
            # Process request
            result = self._process(data)
            request_logger.success("Request completed", 
                                  result=result, 
                                  duration_ms=150)
        except Exception as e:
            request_logger.error("Request failed", 
                               error=str(e),
                               exception=True)
    
    def _process(self, data: dict) -> str:
        return "Success"

# Usage
logger.configure(level="INFO")
logger.add("requests.log", 
          format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {request_id} | {level} | {message}")

handler = RequestHandler()
handler.handle_request("/api/users", {"user": "alice"})
logger.complete()
```

**Output:**
```
2025-10-11 13:45:32.123 | 01933b7e-8f9a-7000-8000-123456789abc | INFO | Request started | endpoint=/api/users
2025-10-11 13:45:32.273 | 01933b7e-8f9a-7000-8000-123456789abc | SUCCESS | Request completed | result=Success | duration_ms=150
```

### 4. Improved Pathlib with Logly

Python 3.14 enhances `pathlib` with new methods. Use them for log file management:

```python
from pathlib import Path
from logly import logger
from datetime import datetime

def manage_log_files():
    """Demonstrate pathlib 3.14 features with log files."""
    logger.configure(level="INFO")
    
    # Create log directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Add log file
    log_file = log_dir / "app.log"
    sink_id = logger.add(str(log_file), rotation="daily")
    
    logger.info("Application started")
    logger.warning("Low disk space", available_mb=512)
    
    # Python 3.14: Check file info without separate stat() call
    if log_file.exists():
        info = log_file.info  # New in 3.14!
        logger.info("Log file info",
                   size=info.size,
                   is_file=info.is_file(),
                   modified=datetime.fromtimestamp(info.mtime).isoformat())
    
    # Python 3.14: Archive logs with new copy() method
    archive_dir = log_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    
    if log_file.exists():
        # New copy() method in Python 3.14
        archived = log_file.copy(archive_dir / f"app_{datetime.now():%Y%m%d}.log")
        logger.info("Log archived", archive_path=str(archived))
    
    logger.complete()
    
    # Cleanup: use new move() method
    # log_file.move(archive_dir / "final.log")  # New in 3.14

# Usage
manage_log_files()
```

### 5. InterpreterPoolExecutor for Parallel Logging

Python 3.14's `InterpreterPoolExecutor` enables true parallelism. Each worker can have its own logger instance:

```python
from concurrent.futures import InterpreterPoolExecutor
from logly import logger
import time

def worker_task(task_id: int) -> dict:
    """Worker function with isolated logging."""
    from logly import logger
    
    # Each interpreter has its own logger instance
    logger.configure(level="DEBUG")
    logger.add(f"worker_{task_id}.log")
    
    logger.info("Worker started", task_id=task_id)
    
    # Simulate work
    time.sleep(0.1)
    result = task_id ** 2
    
    logger.success("Worker completed", 
                  task_id=task_id, 
                  result=result)
    
    logger.complete()
    return {"task_id": task_id, "result": result}

def parallel_processing():
    """Demonstrate parallel processing with isolated loggers."""
    logger.configure(level="INFO")
    logger.add("main.log")
    
    logger.info("Starting parallel processing")
    
    # Use InterpreterPoolExecutor for true parallelism
    with InterpreterPoolExecutor(max_workers=4) as executor:
        tasks = range(5)
        futures = [executor.submit(worker_task, i) for i in tasks]
        
        for future in futures:
            result = future.result()
            logger.info("Task completed", **result)
    
    logger.info("All tasks completed")
    logger.complete()

# Usage
parallel_processing()
```

**Key Benefits:**
- Each sub-interpreter has **isolated global state**
- No GIL contention between interpreters
- True parallel execution for CPU-bound tasks
- Each worker can have independent logger configuration

### 6. Improved Exception Handling

Python 3.14 simplifies exception syntax (though parentheses still work):

```python
from logly import logger

def handle_user_input(data: str):
    """Demonstrate improved exception handling with logging."""
    logger.configure(level="DEBUG")
    
    try:
        # Attempt to process data
        result = int(data)
        logger.info("Input processed", value=result)
        
    except ValueError, TypeError:  # New simplified syntax in 3.14!
        # Both exceptions caught without parentheses
        logger.error("Invalid input", 
                    input=data,
                    error_type="ValueError or TypeError")
        
    except Exception as e:
        # Still works with 'as' clause
        logger.critical("Unexpected error", 
                       error=str(e),
                       exception=True)
    
    finally:
        logger.debug("Input processing complete")

# Usage
handle_user_input("123")    # Success
handle_user_input("abc")    # ValueError
handle_user_input(None)     # TypeError
logger.complete()
```

**Output:**
```
[INFO] Input processed | value=123
[DEBUG] Input processing complete
[ERROR] Invalid input | input=abc | error_type=ValueError or TypeError
[DEBUG] Input processing complete
```

### 7. Complete Python 3.14 + Logly Example

Here's a comprehensive example using multiple Python 3.14 features:

```python
#!/usr/bin/env python3.14
"""Complete demo: Python 3.14 features with Logly logging."""

from __future__ import annotations
from pathlib import Path
from uuid import uuid7
from datetime import datetime
from concurrent.futures import InterpreterPoolExecutor
from logly import logger
import annotationlib

class DataProcessor:
    """Process data with full Python 3.14 + Logly integration."""
    
    next: DataProcessor | None = None  # PEP 649: no quotes needed
    
    def __init__(self, name: str):
        self.name = name
        self.request_id = uuid7()  # UUID7 for tracking
        
        # Bind context
        self.logger = logger.bind(
            processor=name,
            request_id=str(self.request_id)
        )
        
        self.logger.info("Processor initialized")
    
    def process(self, data: list[int]) -> dict:
        """Process data with comprehensive logging."""
        self.logger.info("Processing started", items=len(data))
        
        try:
            # Simulate processing
            result = sum(data)
            self.logger.success("Processing completed", result=result)
            return {"sum": result, "count": len(data)}
            
        except ValueError, TypeError:  # Python 3.14 syntax
            self.logger.error("Invalid data type")
            return {"error": "Invalid data"}
        
        except Exception as e:
            self.logger.critical("Unexpected error", 
                               error=str(e),
                               exception=True)
            return {"error": str(e)}

def setup_logging():
    """Configure logging with Python 3.14 pathlib features."""
    logger.configure(level="DEBUG", color=True)
    
    # Use pathlib to manage log directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Add sinks with time format specs
    logger.add(
        str(log_dir / "app.log"),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:8} | {message}",
        rotation="daily"
    )
    
    logger.add(
        str(log_dir / "requests.log"),
        format="{time:YYYY-MM-DDTHH:mm:ss} | {request_id} | {processor} | {message}",
        filter_min_level="INFO"
    )
    
    logger.info("Logging configured", log_dir=str(log_dir))

def parallel_processing():
    """Demonstrate InterpreterPoolExecutor with isolated loggers."""
    logger.info("Starting parallel processing")
    
    def worker(data: list[int]) -> dict:
        from logly import logger
        processor = DataProcessor(f"Worker-{data[0]}")
        return processor.process(data)
    
    datasets = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    
    with InterpreterPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(worker, data) for data in datasets]
        results = [f.result() for f in futures]
    
    logger.info("Parallel processing completed", 
               total_results=len(results))
    return results

def inspect_annotations_demo():
    """Demonstrate PEP 649 annotation inspection."""
    annotations = annotationlib.get_annotations(
        DataProcessor,
        format=annotationlib.Format.VALUE
    )
    
    logger.debug("Class annotations inspected",
                annotations=str(annotations))

def main():
    """Main entry point."""
    print("=== Python 3.14 + Logly Demo ===\n")
    
    # Setup
    setup_logging()
    
    # Demo deferred annotations
    inspect_annotations_demo()
    
    # Demo single processor
    processor = DataProcessor("MainProcessor")
    result = processor.process([10, 20, 30])
    logger.info("Single processing result", **result)
    
    # Demo parallel processing
    results = parallel_processing()
    
    # Cleanup
    logger.complete()
    print("\nDemo complete! Check logs/ directory for output files.")

if __name__ == "__main__":
    main()
```

## Performance Considerations

Python 3.14 offers performance improvements that benefit Logly:

### 1. Faster Attribute Access
```python
# Python 3.14's optimized attribute access helps logger.bind() performance
request_logger = logger.bind(user_id=123, session_id="abc")
request_logger.info("Fast attribute access")  # Faster in 3.14
```

### 2. Improved Memory Usage
```python
# Python 3.14's reduced memory overhead for objects
for i in range(10000):
    logger.debug("Memory efficient logging", iteration=i)
    # Uses less memory per log call in 3.14
```

### 3. Optimized f-strings
```python
# Python 3.14 optimizes f-strings (but use lazy evaluation for logs)
value = 42

# ✗ Don't do this (evaluates even if level filtered)
logger.debug(f"Value is {expensive_function()}")

# ✓ Do this (lazy evaluation)
logger.debug("Value is {}", expensive_function())
```

## Migration Notes

If migrating from older Python versions to 3.14:

### Annotations
```python
# Old (Python < 3.14): Required quotes or __future__ import
class OldStyle:
    next: 'OldStyle' = None

# New (Python 3.14): No quotes needed
from __future__ import annotations
class NewStyle:
    next: NewStyle = None  # Works without quotes!
```

### Exception Handling
```python
# Old syntax (still works)
try:
    risky_operation()
except (ValueError, TypeError) as e:
    logger.error("Error occurred", error=str(e))

# New syntax (Python 3.14)
try:
    risky_operation()
except ValueError, TypeError as e:  # Simplified!
    logger.error("Error occurred", error=str(e))
```

## Best Practices

1. **Use UUID7 for Tracking**: Time-sortable UUIDs are perfect for request tracking
2. **Leverage Pathlib**: Use Python 3.14's enhanced pathlib for log management
3. **Isolated Loggers**: Use InterpreterPoolExecutor for truly parallel processing
4. **Deferred Annotations**: Clean type hints without forward reference strings
5. **Time Format Specs**: Use Logly's `{time:...}` format for readable timestamps

## Compatibility

Logly maintains compatibility across Python versions:

| Python Version | Status | Notes |
|---------------|--------|-------|
| 3.10 | ✅ Fully Supported | Stable, production-ready |
| 3.11 | ✅ Fully Supported | Performance improvements |
| 3.12 | ✅ Fully Supported | Enhanced error messages |
| 3.13 | ✅ Fully Supported | Experimental JIT, improved GIL |
| 3.14 | ✅ Fully Supported | Latest features, best performance |

## See Also

- [Template String Formatting](../examples/template-strings.md) - Logly's format string syntax
- [Configuration Guide](../guides/configuration.md) - Advanced configuration
- [Performance Guide](../guides/performance.md) - Optimization techniques
- [Python 3.14 Release Notes](https://docs.python.org/3.14/whatsnew/3.14.html) - Official Python docs
