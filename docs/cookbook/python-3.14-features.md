---
title: Python 3.14 Features Cookbook - Logly
description: Complete cookbook demonstrating all Python 3.14 features with Logly logging including deferred annotations, UUID7, pathlib improvements, and parallel processing.
keywords: python 3.14, cookbook, examples, new features, uuid7, annotations, pathlib, parallelism, logly
---

# Python 3.14 Features Cookbook

This cookbook demonstrates how to use all major Python 3.14 features together with Logly for enhanced logging experiences. Each example is production-ready and demonstrates best practices.

## Prerequisites

```bash
# Ensure you have Python 3.14
python --version  # Should show Python 3.14.x

# Install Logly
pip install logly
```

## Feature Overview

Python 3.14 introduces:

1. **PEP 649**: Deferred evaluation of annotations
2. **PEP 750**: Template strings (t-strings) - *Note: Different from Logly format strings*
3. **UUID7**: Time-sortable UUIDs
4. **Improved pathlib**: `copy()`, `move()`, `info` property
5. **InterpreterPoolExecutor**: True parallelism
6. **Simplified exception syntax**: `except ValueError, TypeError`
7. **Performance improvements**: Faster execution, lower memory

---

## Recipe 1: Deferred Annotations with Logging

**Use Case**: Type-safe logging classes without forward reference complexity.

```python
#!/usr/bin/env python3.14
"""Deferred annotations example with Logly."""

from __future__ import annotations
from logly import logger
import annotationlib
from typing import TYPE_CHECKING

class LoggingNode:
    """A linked list node with comprehensive logging."""
    
    # Python 3.14: No quotes needed for forward references!
    next: LoggingNode | None = None
    prev: LoggingNode | None = None
    
    def __init__(self, value: int, node_id: str):
        self.value = value
        self.node_id = node_id
        
        # Bind context for this node
        self.logger = logger.bind(node_id=node_id, value=value)
        self.logger.info("Node created")
    
    def link_next(self, node: LoggingNode) -> None:
        """Link to next node with logging."""
        self.next = node
        node.prev = self
        
        self.logger.info("Linked to next node", 
                        next_node_id=node.node_id)
    
    def traverse(self) -> list[int]:
        """Traverse and log all nodes."""
        result = [self.value]
        current = self.next
        
        self.logger.debug("Starting traversal")
        
        while current:
            result.append(current.value)
            current.logger.debug("Visited during traversal")
            current = current.next
        
        self.logger.info("Traversal complete", 
                        nodes_visited=len(result))
        return result

def inspect_node_annotations():
    """Inspect annotations using Python 3.14 annotationlib."""
    # Get annotations in different formats
    forward_refs = annotationlib.get_annotations(
        LoggingNode, 
        format=annotationlib.Format.FORWARDREF
    )
    
    values = annotationlib.get_annotations(
        LoggingNode,
        format=annotationlib.Format.VALUE
    )
    
    logger.info("Node annotations",
               forward_refs=str(forward_refs),
               values=str(values))

# Example usage
if __name__ == "__main__":
    logger.configure(level="DEBUG")
    logger.add("nodes.log", 
              format="{time:HH:mm:ss.SSS} | {node_id} | {level} | {message}")
    
    # Create linked list
    node1 = LoggingNode(10, "node-1")
    node2 = LoggingNode(20, "node-2")
    node3 = LoggingNode(30, "node-3")
    
    node1.link_next(node2)
    node2.link_next(node3)
    
    # Traverse
    values = node1.traverse()
    logger.info("Traversal result", values=values)
    
    # Inspect annotations
    inspect_node_annotations()
    
    logger.complete()
```

**Output:**
```
[INFO] Node created | node_id=node-1 | value=10
[INFO] Node created | node_id=node-2 | value=20
[INFO] Node created | node_id=node-3 | value=30
[INFO] Linked to next node | node_id=node-1 | next_node_id=node-2
[INFO] Linked to next node | node_id=node-2 | next_node_id=node-3
[DEBUG] Starting traversal | node_id=node-1
[DEBUG] Visited during traversal | node_id=node-2
[DEBUG] Visited during traversal | node_id=node-3
[INFO] Traversal complete | node_id=node-1 | nodes_visited=3
```

---

## Recipe 2: UUID7 Request Tracking

**Use Case**: Time-sortable request IDs for distributed systems.

```python
#!/usr/bin/env python3.14
"""UUID7 request tracking with Logly."""

from uuid import uuid7
from logly import logger
from datetime import datetime, timezone
import time

class RequestTracker:
    """Track requests with UUID7 and comprehensive logging."""
    
    def __init__(self):
        logger.configure(level="INFO")
        logger.add("requests.log",
                  format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {request_id} | {level} | {message}")
    
    def handle_request(self, method: str, path: str, user_id: int) -> dict:
        """Handle a request with UUID7 tracking."""
        # Generate time-sortable UUID
        request_id = uuid7()
        start_time = time.perf_counter()
        
        # Extract timestamp from UUID7
        timestamp_ms = (request_id.int >> 80) & ((1 << 48) - 1)
        request_time = datetime.fromtimestamp(
            timestamp_ms / 1000.0, 
            tz=timezone.utc
        )
        
        # Create request-scoped logger
        req_logger = logger.bind(
            request_id=str(request_id),
            method=method,
            path=path,
            user_id=user_id
        )
        
        req_logger.info("Request started",
                       request_time=request_time.isoformat())
        
        try:
            # Simulate request processing
            req_logger.debug("Validating request")
            time.sleep(0.05)  # Simulate work
            
            req_logger.debug("Processing business logic")
            time.sleep(0.1)   # Simulate work
            
            result = {
                "request_id": str(request_id),
                "status": "success",
                "user_id": user_id
            }
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            req_logger.success("Request completed",
                             duration_ms=f"{duration_ms:.2f}",
                             status=200)
            
            return result
            
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            req_logger.error("Request failed",
                           error=str(e),
                           duration_ms=f"{duration_ms:.2f}",
                           exception=True)
            raise
    
    def generate_sorted_requests(self, count: int):
        """Generate multiple requests and show UUID7 sorting."""
        request_ids = []
        
        for i in range(count):
            request_id = uuid7()
            logger.info(f"Request {i+1} generated",
                       request_id=str(request_id))
            request_ids.append(request_id)
            time.sleep(0.01)  # Small delay to show sorting
        
        # UUIDs are naturally sorted by creation time
        sorted_ids = sorted(request_ids)
        logger.info("UUID7s are time-sorted",
                   naturally_sorted=request_ids == sorted_ids)

# Example usage
if __name__ == "__main__":
    tracker = RequestTracker()
    
    # Handle some requests
    tracker.handle_request("GET", "/api/users/123", user_id=123)
    tracker.handle_request("POST", "/api/orders", user_id=456)
    tracker.handle_request("DELETE", "/api/sessions/abc", user_id=123)
    
    # Demonstrate sorting
    tracker.generate_sorted_requests(5)
    
    logger.complete()
```

---

## Recipe 3: Enhanced Pathlib Log Management

**Use Case**: Manage log files with Python 3.14's improved pathlib.

```python
#!/usr/bin/env python3.14
"""Enhanced pathlib log management with Python 3.14."""

from pathlib import Path
from logly import logger
from datetime import datetime
import shutil

class LogManager:
    """Manage log files using Python 3.14 pathlib features."""
    
    def __init__(self, base_dir: str = "logs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        logger.configure(level="INFO")
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging with organized directory structure."""
        # Create subdirectories
        self.current_dir = self.base_dir / "current"
        self.archive_dir = self.base_dir / "archive"
        
        self.current_dir.mkdir(exist_ok=True)
        self.archive_dir.mkdir(exist_ok=True)
        
        # Add log file
        self.log_file = self.current_dir / "app.log"
        logger.add(str(self.log_file),
                  format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
        
        logger.info("Log manager initialized",
                   log_dir=str(self.base_dir))
    
    def get_log_info(self, log_path: Path) -> dict:
        """Get log file information using Python 3.14 pathlib.info."""
        if not log_path.exists():
            return {"error": "File not found"}
        
        # Python 3.14: Use .info property instead of .stat()
        info = log_path.info
        
        file_info = {
            "path": str(log_path),
            "size_bytes": info.size,
            "size_kb": f"{info.size / 1024:.2f}",
            "is_file": info.is_file(),
            "is_dir": info.is_dir(),
            "created": datetime.fromtimestamp(info.ctime).isoformat(),
            "modified": datetime.fromtimestamp(info.mtime).isoformat(),
        }
        
        logger.info("Log file info retrieved", **file_info)
        return file_info
    
    def archive_log(self, source: Path) -> Path:
        """Archive log file using Python 3.14 pathlib.copy()."""
        if not source.exists():
            logger.warning("Source log not found", path=str(source))
            return None
        
        # Generate archive filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{source.stem}_{timestamp}{source.suffix}"
        archive_path = self.archive_dir / archive_name
        
        logger.info("Archiving log",
                   source=str(source),
                   destination=str(archive_path))
        
        # Python 3.14: Use new copy() method
        archived = source.copy(archive_path)
        
        logger.success("Log archived",
                      archive_path=str(archived),
                      size_kb=f"{archived.info.size / 1024:.2f}")
        
        return archived
    
    def rotate_logs(self, max_size_kb: int = 1024):
        """Rotate logs if they exceed max size."""
        for log_file in self.current_dir.glob("*.log"):
            info = log_file.info
            size_kb = info.size / 1024
            
            logger.debug("Checking log file",
                        file=log_file.name,
                        size_kb=f"{size_kb:.2f}")
            
            if size_kb > max_size_kb:
                logger.warning("Log file exceeds max size",
                             file=log_file.name,
                             size_kb=f"{size_kb:.2f}",
                             max_size_kb=max_size_kb)
                
                # Archive the large log
                self.archive_log(log_file)
                
                # Clear the original
                log_file.write_text("")
                logger.info("Log file rotated", file=log_file.name)
    
    def cleanup_old_archives(self, days: int = 30):
        """Clean up archives older than specified days."""
        import time
        cutoff_time = time.time() - (days * 86400)
        
        for archive in self.archive_dir.glob("*.log"):
            if archive.info.mtime < cutoff_time:
                age_days = (time.time() - archive.info.mtime) / 86400
                logger.info("Removing old archive",
                           file=archive.name,
                           age_days=f"{age_days:.1f}")
                archive.unlink()

# Example usage
if __name__ == "__main__":
    manager = LogManager()
    
    # Generate some logs
    for i in range(100):
        logger.info(f"Log entry {i+1}", iteration=i+1)
    
    # Get log info
    info = manager.get_log_info(manager.log_file)
    
    # Archive current log
    archived = manager.archive_log(manager.log_file)
    
    # Check rotation (adjust max_size_kb to force rotation)
    manager.rotate_logs(max_size_kb=1)
    
    # Cleanup old archives
    manager.cleanup_old_archives(days=30)
    
    logger.complete()
```

---

## Recipe 4: Parallel Processing with InterpreterPoolExecutor

**Use Case**: True parallel logging in CPU-bound tasks.

```python
#!/usr/bin/env python3.14
"""Parallel processing with isolated loggers using InterpreterPoolExecutor."""

from concurrent.futures import InterpreterPoolExecutor
from logly import logger
import time
import json

def cpu_intensive_task(task_id: int, data_size: int) -> dict:
    """CPU-intensive task with isolated logger."""
    # Each sub-interpreter gets its own logger instance
    from logly import logger
    from pathlib import Path
    import time
    
    # Setup logging for this worker
    log_dir = Path("logs/workers")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.configure(level="DEBUG")
    logger.add(
        str(log_dir / f"worker_{task_id}.log"),
        format="{time:HH:mm:ss.SSS} | {level} | {message}"
    )
    
    task_logger = logger.bind(task_id=task_id, worker=f"worker-{task_id}")
    
    task_logger.info("Task started", data_size=data_size)
    start_time = time.perf_counter()
    
    # Simulate CPU-intensive work
    result = 0
    for i in range(data_size):
        result += i ** 2
        
        if i % 10000 == 0:
            progress = (i / data_size) * 100
            task_logger.debug(f"Processing", 
                            progress=f"{progress:.1f}%",
                            current_value=i)
    
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    task_logger.success("Task completed",
                       result=result,
                       duration_ms=f"{duration_ms:.2f}")
    
    logger.complete()
    
    return {
        "task_id": task_id,
        "result": result,
        "duration_ms": duration_ms
    }

def main():
    """Main orchestrator with parallel task execution."""
    logger.configure(level="INFO")
    logger.add("logs/main.log",
              format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}")
    
    logger.info("Starting parallel processing")
    
    tasks = [
        (1, 50000),
        (2, 75000),
        (3, 100000),
        (4, 60000),
    ]
    
    # Use InterpreterPoolExecutor for true parallelism
    # Each worker runs in isolated sub-interpreter (no GIL contention!)
    with InterpreterPoolExecutor(max_workers=4) as executor:
        logger.info("Submitting tasks", task_count=len(tasks))
        
        futures = [
            executor.submit(cpu_intensive_task, task_id, size)
            for task_id, size in tasks
        ]
        
        # Collect results
        results = []
        for future in futures:
            result = future.result()
            results.append(result)
            logger.info("Task result received", **result)
    
    # Summary
    total_duration = sum(r["duration_ms"] for r in results)
    logger.success("All tasks completed",
                  tasks_completed=len(results),
                  total_duration_ms=f"{total_duration:.2f}",
                  avg_duration_ms=f"{total_duration/len(results):.2f}")
    
    logger.complete()

if __name__ == "__main__":
    main()
```

**Key Benefits:**
- Each sub-interpreter has isolated GIL
- True parallel execution on multi-core CPUs
- Independent logger configuration per worker
- No shared state between workers

---

## Recipe 5: Simplified Exception Handling

**Use Case**: Cleaner error handling with Python 3.14 syntax.

```python
#!/usr/bin/env python3.14
"""Simplified exception handling with Logly."""

from logly import logger

class DataValidator:
    """Validate data with comprehensive error logging."""
    
    def __init__(self):
        logger.configure(level="DEBUG")
        logger.add("validation.log",
                  format="{time:HH:mm:ss} | {level:8} | {message}")
    
    def validate_input(self, data: any) -> dict:
        """Validate input with Python 3.14 simplified exception syntax."""
        logger.info("Validation started", data_type=type(data).__name__)
        
        try:
            # Attempt to convert to integer
            value = int(data)
            
            if value < 0:
                raise ValueError("Negative values not allowed")
            
            logger.success("Validation passed", value=value)
            return {"valid": True, "value": value}
        
        # Python 3.14: Simplified syntax (no parentheses needed)
        except ValueError, TypeError:
            logger.error("Invalid data type",
                        input=str(data),
                        error_type="ValueError or TypeError")
            return {"valid": False, "error": "Invalid type"}
        
        # Traditional syntax still works
        except (ZeroDivisionError, OverflowError) as e:
            logger.error("Arithmetic error",
                        error=str(e),
                        exception=True)
            return {"valid": False, "error": "Arithmetic error"}
        
        except Exception as e:
            logger.critical("Unexpected error",
                          error=str(e),
                          exception=True)
            return {"valid": False, "error": "Unexpected"}
        
        finally:
            logger.debug("Validation complete")
    
    def batch_validate(self, items: list) -> dict:
        """Validate multiple items."""
        results = {"valid": [], "invalid": []}
        
        for i, item in enumerate(items):
            logger.debug(f"Validating item {i+1}/{len(items)}")
            result = self.validate_input(item)
            
            if result["valid"]:
                results["valid"].append(item)
            else:
                results["invalid"].append(item)
        
        logger.info("Batch validation complete",
                   total=len(items),
                   valid=len(results["valid"]),
                   invalid=len(results["invalid"]))
        
        return results

# Example usage
if __name__ == "__main__":
    validator = DataValidator()
    
    # Test various inputs
    test_data = [
        "123",      # Valid
        "abc",      # ValueError
        None,       # TypeError
        "456",      # Valid
        "-10",      # ValueError (negative)
        42,         # Valid
    ]
    
    results = validator.batch_validate(test_data)
    logger.info("Final results", **results)
    
    logger.complete()
```

---

## Complete Integration Example

Here's a comprehensive example using all Python 3.14 features:

```python
#!/usr/bin/env python3.14
"""Complete Python 3.14 + Logly integration example."""

from __future__ import annotations
from pathlib import Path
from uuid import uuid7
from datetime import datetime
from concurrent.futures import InterpreterPoolExecutor
from logly import logger
import annotationlib
import time

class Task:
    """Task with deferred annotations and UUID7 tracking."""
    
    next: Task | None = None  # PEP 649: no quotes needed!
    
    def __init__(self, name: str, work_size: int):
        self.task_id = uuid7()
        self.name = name
        self.work_size = work_size
        
        self.logger = logger.bind(
            task_id=str(self.task_id),
            task_name=name
        )
        
        self.logger.info("Task created")

def worker(task_name: str, work_size: int) -> dict:
    """Worker function running in isolated interpreter."""
    from logly import logger
    from uuid import uuid7
    import time
    
    # Each worker has isolated logger
    logger.configure(level="DEBUG")
    logger.add(f"worker_{task_name}.log")
    
    task_id = uuid7()
    logger.info("Worker started", 
               task_id=str(task_id),
               work_size=work_size)
    
    # Simulate work
    result = sum(i**2 for i in range(work_size))
    time.sleep(0.1)
    
    logger.success("Worker completed", result=result)
    logger.complete()
    
    return {"task": task_name, "result": result}

def main():
    """Main application."""
    # Setup logging with pathlib
    log_dir = Path("logs/complete_demo")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.configure(level="INFO")
    logger.add(
        str(log_dir / "main.log"),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}"
    )
    
    logger.info("Application started")
    
    # Create tasks with deferred annotations
    task1 = Task("data-processing", 10000)
    task2 = Task("report-generation", 15000)
    task3 = Task("cleanup", 5000)
    
    task1.next = task2
    task2.next = task3
    
    # Inspect annotations
    annotations = annotationlib.get_annotations(Task)
    logger.debug("Task annotations", annotations=str(annotations))
    
    # Parallel processing
    logger.info("Starting parallel execution")
    
    tasks_data = [
        ("task-1", 10000),
        ("task-2", 15000),
        ("task-3", 5000),
    ]
    
    with InterpreterPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(worker, name, size)
            for name, size in tasks_data
        ]
        
        results = [f.result() for f in futures]
    
    logger.success("All tasks completed", 
                  total_tasks=len(results))
    
    # Log file management with pathlib
    main_log = log_dir / "main.log"
    if main_log.exists():
        info = main_log.info  # Python 3.14 feature
        logger.info("Main log info",
                   size_kb=f"{info.size / 1024:.2f}",
                   modified=datetime.fromtimestamp(info.mtime).isoformat())
    
    logger.complete()

if __name__ == "__main__":
    main()
```

---

## Best Practices Summary

1. **Deferred Annotations**: Use `from __future__ import annotations` for clean type hints
2. **UUID7**: Perfect for time-sortable request/transaction tracking
3. **Pathlib `.info`**: More efficient than calling `.stat()` repeatedly
4. **InterpreterPoolExecutor**: Use for CPU-bound parallel tasks with isolated loggers
5. **Exception Handling**: Both old and new syntax work; use whichever is clearer
6. **Logly Format Strings**: Different from Python 3.14 t-strings; optimized for logging

## See Also

- [Python 3.14 Support Guide](../guides/python-3.14-support.md) - Comprehensive feature guide
- [Template String Formatting](../examples/template-strings.md) - Logly format strings
- [Performance Guide](../guides/performance.md) - Optimization techniques
- [Configuration Guide](../guides/configuration.md) - Advanced configuration
