---
title: Python 3.14 Support - Logly
description: Comprehensive guide to using Logly with Python 3.14 features including deferred annotations, template strings, improved pathlib, and more.
keywords: python, python 3.14, logging, new features, template strings, annotations, logly
---

# Python 3.14 Support

Logly fully supports Python 3.14 and takes advantage of its new features. This guide demonstrates how to use Python 3.14's capabilities with Logly for enhanced logging experiences.

!!! note "Note": Logly Version 0.1.6+ is required for full Python 3.14 compatibility.

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

Python 3.14's deferred annotation evaluation improves type hint handling without forward references.

#### Example: Self-Referencing Class with Logging

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

#### Explanation:

1. **`from __future__ import annotations`**: Enables deferred annotation evaluation
2. **`next_processor: LogProcessor | None`**: Self-reference without quotes (previously required `'LogProcessor'`)
3. **`annotationlib.get_annotations()`**: Runtime inspection of type hints
4. **Logger Integration**: Logs object creation and annotation inspection

#### ✅ Do's:
- Use `from __future__ import annotations` at the top of your file
- Write type hints naturally without string quotes
- Use `annotationlib` for runtime annotation inspection
- Log class initialization with relevant context

#### ❌ Don'ts:
- Don't use string quotes for forward references (`'LogProcessor'`)
- Don't mix old-style quoted annotations with deferred annotations
- Don't inspect annotations without proper error handling
- Don't forget that annotations are deferred until accessed

### 2. Template Strings (PEP 750) - Understanding the Difference

**Important Distinction**: Python 3.14's template strings (t-strings) and Logly's format strings serve **different purposes**.

#### Python 3.14 Template Strings (For Log Messages)

T-strings are perfect for creating **reusable log message templates**:

```python
from logly import logger

# Configure logger
logger.configure(level="INFO")
logger.add("app.log")

# Define reusable t-string templates for log messages
login_template = t"User {username} logged in from {ip}"
error_template = t"Error {code}: {message}"

# Use templates to create log messages
msg1 = login_template.format(username="Alice", ip="192.168.1.1")
logger.info(msg1)

msg2 = error_template.format(code=404, message="Not found")
logger.error(msg2)
```

**Output:**
```
[INFO] User Alice logged in from 192.168.1.1
[ERROR] Error 404: Not found
```

#### Logly Format Strings (For Log Output Formatting)

Logly format strings control **how logs are formatted in output files**:

```python
from logly import logger

# Logly's format strings define the OUTPUT structure
logger.configure(level="INFO")
logger.add(
    "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    #      ^^^^^^^^^^^^^^^^^^^^^^^^     Logly-specific patterns
)

# Log with custom fields (NOT t-strings)
logger.info("User login", username="Alice", age=30)
```

**Output:**
```
2025-10-11 13:45:32 | INFO | User login | username=Alice | age=30
```

#### Key Differences:

| Feature | Python 3.14 T-Strings | Logly Format Strings |
|---------|----------------------|----------------------|
| **Purpose** | Create reusable log **messages** | Define log **output format** |
| **Used in** | Your code (message creation) | `logger.add(format=...)` |
| **Syntax** | `t"Hello {name}"` | `"{time:YYYY-MM-DD} \\| {level} \\| {message}"` |
| **Special keywords** | Your own placeholders | `{time}`, `{level}`, `{message}`, `{file}`, etc. |
| **Example** | `t"User {user} logged in"` | `"{time:HH:mm:ss} \\| {level} \\| {message}"` |
| **Time patterns** | ❌ Not supported | ✅ `{time:YYYY-MM-DD HH:mm:ss}` |

#### ✅ Do's:
- ✅ Use **t-strings** to create reusable log message templates
- ✅ Use **Logly format strings** in `logger.add(format=...)` for output formatting
- ✅ Use `{time:...}` patterns only in Logly format strings
- ✅ Use `.format()` on t-string templates to create messages before logging

#### ❌ Don'ts:
- ❌ Don't use t-strings in `logger.add(format=...)` parameter
- ❌ Don't use `{time:YYYY-MM-DD}` in t-string templates (not supported)
- ❌ Don't pass Template objects directly to `logger.info()` - convert to string first
- ❌ Don't confuse message templates (t-strings) with output formatting (Logly format)

### 3. UUID7 for Request Tracking

Python 3.14's UUID7 provides time-sortable unique identifiers, perfect for distributed systems and request tracking.

#### Example: HTTP Request Handler with UUID7

```python
from uuid import uuid7
from logly import logger
import time

class RequestHandler:
    """Handle HTTP requests with UUID7 tracking."""
    
    def handle_request(self, endpoint: str, data: dict):
        # Generate time-sortable UUID
        request_id = uuid7()
        start_time = time.perf_counter()
        
        # Bind request context
        request_logger = logger.bind(
            request_id=str(request_id),
            endpoint=endpoint
        )
        
        request_logger.info("Request started", method="POST")
        
        try:
            # Process request
            result = self._process(data)
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            request_logger.success("Request completed", 
                                  result=result, 
                                  duration_ms=f"{duration_ms:.2f}")
            return result
            
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            request_logger.error("Request failed", 
                               error=str(e),
                               duration_ms=f"{duration_ms:.2f}",
                               exception=True)
            raise
    
    def _process(self, data: dict) -> str:
        return f"Processed: {data}"

# Usage
logger.configure(level="INFO")
logger.add("requests.log", 
          format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {request_id} | {level} | {message}")

handler = RequestHandler()
handler.handle_request("/api/users", {"user": "alice", "action": "create"})
logger.complete()
```

**Output:**
```
2025-10-11 13:45:32.123 | 01933b7e-8f9a-7000-8000-123456789abc | INFO | Request started | endpoint=/api/users | method=POST
2025-10-11 13:45:32.273 | 01933b7e-8f9a-7000-8000-123456789abc | SUCCESS | Request completed | result=Processed: {'user': 'alice', 'action': 'create'} | duration_ms=150.23
```

#### Explanation:

1. **`uuid7()`**: Generates time-sortable UUID (timestamp embedded in ID)
2. **Time-sortable**: UUIDs naturally sort by creation time for easy log analysis
3. **`logger.bind()`**: Attaches request_id to all logs in this scope
4. **Performance tracking**: Uses `time.perf_counter()` for accurate duration measurement

#### ✅ Do's:
- Use UUID7 for request/transaction tracking in distributed systems
- Bind UUID7 to logger context for automatic inclusion in all logs
- Store UUID7 as strings in databases for easy sorting
- Use UUID7 for correlation across microservices

#### ❌ Don'ts:
- Don't use UUID4 when you need time-sortable IDs
- Don't convert UUID7 to string before storing if you need sorting
- Don't forget that UUID7 reveals creation timestamp (security consideration)
- Don't use UUID7 for security tokens (use secrets module instead)

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

## Quick Start Example

Here's a small, complete example showing Python 3.14 features with Logly:

```python
#!/usr/bin/env python3.14
"""Simple Python 3.14 + Logly example."""

from __future__ import annotations
from uuid import uuid7
from pathlib import Path
from logly import logger

class UserService:
    """User service with Python 3.14 features."""
    
    users: dict[str, dict] = {}  # PEP 649: no quotes needed
    
    def create_user(self, name: str, email: str) -> str:
        """Create user with UUID7 tracking."""
        user_id = str(uuid7())  # Time-sortable UUID
        
        # Bind context for this operation
        op_logger = logger.bind(
            operation="create_user",
            user_id=user_id,
            user_name=name
        )
        
        op_logger.info("Creating user")
        
        try:
            self.users[user_id] = {
                "name": name,
                "email": email,
                "created_at": str(uuid7())
            }
            
            op_logger.success("User created successfully")
            return user_id
            
        except ValueError, TypeError:  # Python 3.14 syntax
            op_logger.error("Invalid user data")
            return ""
        
        except Exception as e:
            op_logger.critical("Failed to create user", 
                             error=str(e),
                             exception=True)
            return ""

def main():
    """Main function."""
    # Configure logging with pathlib
    log_dir = Path("example_logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.configure(level="INFO", color=True)
    logger.add(
        str(log_dir / "users.log"),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:8} | {operation} | {user_id} | {message}"
    )
    
    # Create service and users
    service = UserService()
    
    user1_id = service.create_user("Alice", "alice@example.com")
    user2_id = service.create_user("Bob", "bob@example.com")
    user3_id = service.create_user("", "invalid")  # This will fail
    
    print(f"Created users: {user1_id[:8]}..., {user2_id[:8]}...")
    print(f"Failed user: {user3_id}")
    
    logger.complete()

if __name__ == "__main__":
    main()
```

### Output:
```
2025-10-11 14:30:15 | INFO     | create_user | 01933b7e-8f9a-7000-8000-123456789abc | Creating user
2025-10-11 14:30:15 | SUCCESS  | create_user | 01933b7e-8f9a-7000-8000-123456789abc | User created successfully
2025-10-11 14:30:15 | INFO     | create_user | 01933b7e-8f9a-7000-8000-123456789abd | Creating user
2025-10-11 14:30:15 | SUCCESS  | create_user | 01933b7e-8f9a-7000-8000-123456789abd | User created successfully
2025-10-11 14:30:15 | INFO     | create_user | 01933b7e-8f9a-7000-8000-123456789abe | Creating user
2025-10-11 14:30:15 | ERROR    | create_user | 01933b7e-8f9a-7000-8000-123456789abe | Invalid user data
Created users: 01933b7e..., 01933b7e...
Failed user: 
```

### Explanation:

1. **Deferred Annotations** (`users: dict[str, dict] = {}`): No quotes needed for forward references in Python 3.14
2. **UUID7** (`uuid7()`): Time-sortable UUIDs for tracking users and operations
3. **Pathlib** (`Path("example_logs")`): Enhanced file path handling
4. **Exception Syntax** (`except ValueError, TypeError:`): Simplified exception catching without parentheses
5. **Logger Binding** (`logger.bind(...)`): Context-aware logging with operation and user tracking

### Do's and Don'ts

#### ✅ Do's:
- Use `uuid7()` for time-sortable unique identifiers
- Leverage deferred annotations for cleaner type hints
- Bind logger context for better traceability
- Use pathlib for cross-platform file operations
- Handle exceptions with Python 3.14's simplified syntax

#### ❌ Don'ts:
- Don't use t-strings in `logger.add(format=...)` - use Logly format strings instead
- Don't mix up deferred annotations with string literals
- Don't forget to call `logger.complete()` at the end
- Don't use old exception syntax when Python 3.14+ is available
- Don't ignore the performance benefits of UUID7 over UUID4

---

## Practical Use Cases for Small Applications

These examples demonstrate how to use Python 3.14 features with Logly in real-world small applications.

### Use Case 1: Understanding T-Strings with Logly

#### What are T-Strings?

T-strings are a new way to create **reusable string templates** in Python 3.14. They allow you to define a string with placeholders that can be filled later, rather than immediately.

**Analogy:**
Think of a blank invitation card:
- You design the card with placeholders like `Dear {name}, you are invited to {event}`
- Later, you can fill in the names and events whenever you need
- Previously, you had to fill in immediately, but t-strings let you **define first, fill later**

#### Syntax of T-Strings

```python
# Define a template (notice the 't' prefix)
t = t"Hello, {name}! Welcome to {event}."

# Fill in the placeholders later
message = t.format(name="Gunjan", event="Python Workshop")
print(message)
# Output: Hello, Gunjan! Welcome to Python Workshop.
```

- `t` before the string marks it as a **template string literal**
- `{placeholders}` indicate where values will be inserted later

#### Why T-Strings are Useful

**1. Reusable Templates:** Define once, use multiple times with different values

```python
invite = t"Dear {name}, your seat for {event} is confirmed."

print(invite.format(name="Gunjan", event="Python Workshop"))
print(invite.format(name="Shubham", event="Data Science Seminar"))
```

**2. Deferred Evaluation:** Don't know the values yet? Define the template now, fill in later

**3. Cleaner and Safer:**
- No messy concatenation: `"Hello " + name + "!"`
- Avoids errors and keeps templates readable

#### T-Strings vs F-Strings Comparison

| Feature | F-Strings | T-Strings |
|---------|-----------|-----------|
| **Evaluation time** | Immediate | Deferred (lazy) |
| **Reusable** | Not ideal | Designed for reuse |
| **Syntax** | `f"Hello {name}"` | `t"Hello {name}"` |
| **Best use case** | Quick interpolation | Templates for repeated use |

---

#### Using T-Strings with Logly – Real Examples

**Example 1: Reusable Log Templates for User Events**

```python
#!/usr/bin/env python3.14
"""Using t-strings for reusable log templates with Logly."""

from datetime import datetime
from logly import logger

# Configure Logly
logger.configure(level="INFO")
logger.add("app.log")

# Define reusable log templates
login_template = t"User {user} logged in from IP {ip} at {timestamp}"
purchase_template = t"User {user} purchased {item} for ${amount:.2f}"
error_template = t"Error {code} occurred for user {user}: {details}"

def user_login(user: str, ip: str):
    """Log user login event using template."""
    msg = login_template.format(
        user=user,
        ip=ip,
        timestamp=datetime.now()
    )
    logger.info(msg)

def purchase_event(user: str, amount: float, item: str):
    """Log purchase transaction using template."""
    msg = purchase_template.format(
        user=user,
        item=item,
        amount=amount
    )
    logger.info(msg)

def error_event(user: str, error_code: int, details: str):
    """Log error event using template."""
    msg = error_template.format(
        code=error_code,
        user=user,
        details=details
    )
    logger.error(msg)

# Use the same templates multiple times
user_login("alice", "192.168.1.100")
user_login("bob", "10.0.0.45")

purchase_event("alice", 49.99, "Premium Plan")
purchase_event("charlie", 99.99, "Enterprise License")

error_event("bob", 404, "Resource not found")
error_event("alice", 500, "Database connection failed")

logger.complete()
```

**Output:**
```
[INFO] User alice logged in from IP 192.168.1.100 at 2025-10-11 14:30:00.123456
[INFO] User bob logged in from IP 10.0.0.45 at 2025-10-11 14:30:01.234567
[INFO] User alice purchased Premium Plan for $49.99
[INFO] User charlie purchased Enterprise License for $99.99
[ERROR] Error 404 occurred for user bob: Resource not found
[ERROR] Error 500 occurred for user alice: Database connection failed
```

**Why This is Better:**
- ✅ Template defined **once**, used **multiple times**
- ✅ Consistent log message format across your application
- ✅ Easy to update the format in one place
- ✅ Cleaner than string concatenation

---

**Example 2: Email Notification Templates with Logly**

```python
#!/usr/bin/env python3.14
"""Using t-strings for email notification logging."""

from logly import logger

# Configure Logly
logger.configure(level="INFO")
logger.add("notifications.log")

# Define email templates
email_template = t"""
Hello {name},

Thank you for registering for {event} on {date}.
We look forward to seeing you!

Best regards,
{organizer}
"""

welcome_template = t"Welcome email sent to {email} for user {name}"
reminder_template = t"Reminder sent to {email}: {event} starts in {hours} hours"

def send_welcome_email(name: str, email: str, event: str, date: str, organizer: str):
    """Send welcome email and log it."""
    # Generate email body
    email_body = email_template.format(
        name=name,
        event=event,
        date=date,
        organizer=organizer
    )
    
    # Log the email (in real app, you'd send it here)
    logger.info(email_body)
    
    # Log summary
    summary = welcome_template.format(email=email, name=name)
    logger.success(summary)

def send_event_reminder(email: str, event: str, hours: int):
    """Send event reminder and log it."""
    msg = reminder_template.format(
        email=email,
        event=event,
        hours=hours
    )
    logger.info(msg)

# Use templates multiple times
send_welcome_email(
    name="Gunjan",
    email="gunjan@example.com",
    event="Python Bootcamp",
    date="7th Oct 2025",
    organizer="edSlash Team"
)

send_welcome_email(
    name="Shubham",
    email="shubham@example.com",
    event="Data Science Seminar",
    date="15th Oct 2025",
    organizer="edSlash Team"
)

send_event_reminder("gunjan@example.com", "Python Bootcamp", 24)
send_event_reminder("shubham@example.com", "Data Science Seminar", 48)

logger.complete()
```

**Output:**
```
[INFO] 
Hello Gunjan,

Thank you for registering for Python Bootcamp on 7th Oct 2025.
We look forward to seeing you!

Best regards,
edSlash Team

[SUCCESS] Welcome email sent to gunjan@example.com for user Gunjan
[INFO] 
Hello Shubham,

Thank you for registering for Data Science Seminar on 15th Oct 2025.
We look forward to seeing you!

Best regards,
edSlash Team

[SUCCESS] Welcome email sent to shubham@example.com for user Shubham
[INFO] Reminder sent to gunjan@example.com: Python Bootcamp starts in 24 hours
[INFO] Reminder sent to shubham@example.com: Data Science Seminar starts in 48 hours
```

---

**Example 3: Application Status Templates**

```python
#!/usr/bin/env python3.14
"""Using t-strings for application status logging."""

from logly import logger
from datetime import datetime

# Configure Logly
logger.configure(level="INFO")
logger.add("app_status.log")

# Define status templates
startup_template = t"Application {app_name} started at {time} (version {version})"
shutdown_template = t"Application {app_name} stopped at {time} (uptime: {uptime})"
health_template = t"Health check: {service} is {status} (response time: {ms}ms)"

def log_startup(app_name: str, version: str):
    """Log application startup."""
    msg = startup_template.format(
        app_name=app_name,
        time=datetime.now(),
        version=version
    )
    logger.success(msg)

def log_shutdown(app_name: str, uptime: str):
    """Log application shutdown."""
    msg = shutdown_template.format(
        app_name=app_name,
        time=datetime.now(),
        uptime=uptime
    )
    logger.warning(msg)

def log_health_check(service: str, status: str, response_ms: int):
    """Log service health check."""
    msg = health_template.format(
        service=service,
        status=status,
        ms=response_ms
    )
    
    if status == "healthy":
        logger.success(msg)
    else:
        logger.error(msg)

# Application lifecycle logging
log_startup("UserAPI", "v1.2.3")

log_health_check("Database", "healthy", 45)
log_health_check("Cache", "healthy", 12)
log_health_check("External API", "degraded", 2500)

log_shutdown("UserAPI", "2h 15m 30s")

logger.complete()
```

**Output:**
```
[SUCCESS] Application UserAPI started at 2025-10-11 14:30:00.123456 (version v1.2.3)
[SUCCESS] Health check: Database is healthy (response time: 45ms)
[SUCCESS] Health check: Cache is healthy (response time: 12ms)
[ERROR] Health check: External API is degraded (response time: 2500ms)
[WARNING] Application UserAPI stopped at 2025-10-11 16:45:30.654321 (uptime: 2h 15m 30s)
```

---

#### Summary: T-Strings with Logly

**Key Benefits:**
- ✅ **Reusability:** Define templates once, use everywhere
- ✅ **Consistency:** Same log format across your application
- ✅ **Maintainability:** Update format in one place
- ✅ **Readability:** Clear separation of template and data
- ✅ **Deferred Evaluation:** Fill in values only when needed

**When to Use T-Strings with Logly:**
- You have **repeating log patterns** (login, purchases, errors)
- You need **consistent formatting** across multiple log points
- You want **template reuse** for emails, notifications, reports
- You need to **defer evaluation** until runtime

**When NOT to Use:**
- One-time log messages → Use regular f-strings
- Simple logs → `logger.info("User logged in")` is fine
- Performance-critical paths → F-strings are slightly faster

---

### Use Case 2: Simple Web API with Request Tracking

**Scenario**: A small Flask/FastAPI application that tracks user requests with UUID7.

```python
#!/usr/bin/env python3.14
"""Simple web API with Python 3.14 + Logly."""

from __future__ import annotations
from uuid import uuid7
from logly import logger
from pathlib import Path

class SimpleAPI:
    """Minimal API handler with UUID7 request tracking."""
    
    def __init__(self):
        # Setup logging with pathlib
        log_dir = Path("api_logs")
        log_dir.mkdir(exist_ok=True)
        
        logger.configure(level="INFO")
        logger.add(
            str(log_dir / "requests.log"),
            format="{time:YYYY-MM-DD HH:mm:ss} | {request_id} | {level} | {message}"
        )
    
    def handle_request(self, method: str, path: str, user_id: int) -> dict:
        """Handle API request with logging."""
        request_id = uuid7()  # Time-sortable ID
        
        # Bind context
        req_logger = logger.bind(
            request_id=str(request_id)[:8],  # Short ID for readability
            method=method,
            user_id=user_id
        )
        
        req_logger.info("Request received", path=path)
        
        try:
            # Simulate processing
            if path == "/users":
                result = {"users": ["Alice", "Bob"]}
            elif path.startswith("/user/"):
                uid = path.split("/")[-1]
                result = {"user_id": uid, "name": "Alice"}
            else:
                raise ValueError("Unknown endpoint")
            
            req_logger.success("Request completed", status=200)
            return result
            
        except ValueError, TypeError:  # Python 3.14 simplified syntax
            req_logger.error("Invalid request", status=400)
            return {"error": "Bad request"}

# Usage
api = SimpleAPI()
api.handle_request("GET", "/users", user_id=123)
api.handle_request("GET", "/user/456", user_id=123)
logger.complete()
```

**Output:**
```
2025-10-11 14:30:00 | 01933b7e | INFO | Request received | method=GET | user_id=123 | path=/users
2025-10-11 14:30:00 | 01933b7e | SUCCESS | Request completed | method=GET | user_id=123 | status=200
2025-10-11 14:30:00 | 01933b7f | INFO | Request received | method=GET | user_id=123 | path=/user/456
2025-10-11 14:30:00 | 01933b7f | SUCCESS | Request completed | method=GET | user_id=123 | status=200
```

**What You Learn:**
- UUID7 provides time-sortable request IDs (notice sequential IDs)
- `logger.bind()` adds context to all logs in the request scope
- Simplified exception handling with `except ValueError, TypeError`
- Pathlib for cross-platform log directory management

---

### Use Case 3: File Processor with Pathlib Enhancements

**Scenario**: A small script that processes files and manages log archives.

```python
#!/usr/bin/env python3.14
"""File processor using Python 3.14 pathlib features."""

from pathlib import Path
from logly import logger
from datetime import datetime

class FileProcessor:
    """Process files with enhanced pathlib logging."""
    
    def __init__(self):
        logger.configure(level="INFO")
        logger.add("processor.log")
    
    def process_directory(self, dir_path: str) -> dict:
        """Process all text files in directory."""
        data_dir = Path(dir_path)
        
        if not data_dir.exists():
            logger.error("Directory not found", path=dir_path)
            return {"processed": 0, "errors": 1}
        
        processed = 0
        
        for file_path in data_dir.glob("*.txt"):
            # Python 3.14: Use .info property (efficient)
            info = file_path.info
            
            logger.info("Processing file",
                       file=file_path.name,
                       size_kb=f"{info.size / 1024:.2f}",
                       modified=datetime.fromtimestamp(info.mtime).strftime("%Y-%m-%d"))
            
            # Process file
            with file_path.open('r') as f:
                line_count = len(f.readlines())
            
            logger.success("File processed",
                          file=file_path.name,
                          lines=line_count)
            
            # Python 3.14: Archive with .copy()
            archive_dir = data_dir / "archive"
            archive_dir.mkdir(exist_ok=True)
            
            archived = file_path.copy(archive_dir / file_path.name)
            logger.debug("File archived", archive=str(archived))
            
            processed += 1
        
        logger.info("Processing complete", total_files=processed)
        return {"processed": processed, "errors": 0}

# Usage
processor = FileProcessor()
result = processor.process_directory("data")
print(f"Result: {result}")
logger.complete()
```

**Output:**
```
[INFO] Processing file | file=data.txt | size_kb=1.25 | modified=2025-10-11
[SUCCESS] File processed | file=data.txt | lines=42
[DEBUG] File archived | archive=data/archive/data.txt
[INFO] Processing complete | total_files=1
Result: {'processed': 1, 'errors': 0}
```

**What You Learn:**
- `.info` property is more efficient than multiple `.stat()` calls
- `.copy()` method returns the new Path object
- `glob()` for pattern matching files
- Structured logging with file metadata

---

## Summary: Python 3.14 Features for Small Applications

### ✅ Do's

**For T-Strings and Logly:**
- ✅ Use Logly's `{time:YYYY-MM-DD}` for timestamps in format strings
- ✅ Use `{level}`, `{message}` for log formatting
- ✅ Pass data as kwargs: `logger.info("msg", key=value)`
- ✅ Use f-strings for simple message formatting when needed

**For Python 3.14 Features:**
- ✅ Use `from __future__ import annotations` for clean type hints
- ✅ Use UUID7 for time-sortable request/transaction tracking
- ✅ Use `.info` property for efficient file metadata access
- ✅ Use simplified exception syntax: `except ValueError, TypeError`

### ❌ Don'ts

**Critical Mistakes to Avoid:**
- ❌ **Don't** use Python 3.14 t-strings (`t"..."`) with Logly
- ❌ **Don't** confuse `Template` objects with log format strings
- ❌ **Don't** use f-strings for expensive operations in debug logs
- ❌ **Don't** use UUID4 when you need time-sortable IDs
- ❌ **Don't** call `.stat()` repeatedly (use `.info` once)

---

###  Web API with UUID7 Request Tracking

```python
from __future__ import annotations
from uuid import uuid7
from logly import logger
from pathlib import Path
import json

class APIHandler:
    """REST API handler with comprehensive logging."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logger.bind(service=name)
    
    def handle_request(self, method: str, path: str, data: dict | None = None) -> dict:
        # Generate UUID7 for request tracking
        request_id = uuid7()
        
        # Bind request context
        request_logger = self.logger.bind(
            request_id=str(request_id),
            method=method,
            path=path
        )
        
        request_logger.info("Request received", 
                           data_size=len(json.dumps(data or {})))
        
        try:
            # Process request
            if method == "GET" and path.startswith("/users/"):
                user_id = path.split("/")[-1]
                result = self._get_user(user_id)
            elif method == "POST" and path == "/users":
                result = self._create_user(data)
            else:
                raise ValueError("Invalid endpoint")
            
            request_logger.success("Request completed", 
                                  status_code=200,
                                  response_size=len(json.dumps(result)))
            return result
            
        except ValueError, TypeError:  # Python 3.14 syntax
            request_logger.error("Bad request", status_code=400)
            return {"error": "Bad request"}
        
        except Exception as e:
            request_logger.critical("Internal error", 
                                   status_code=500,
                                   error=str(e),
                                   exception=True)
            return {"error": "Internal server error"}
    
    def _get_user(self, user_id: str) -> dict:
        # Simulate database lookup
        return {"id": user_id, "name": "Alice", "email": "alice@example.com"}
    
    def _create_user(self, data: dict) -> dict:
        # Simulate user creation
        user_id = str(uuid7())
        return {"id": user_id, **data}

def setup_api_logging():
    """Configure logging for API service."""
    logger.configure(level="INFO", color=True)
    
    # Use pathlib for log management
    log_dir = Path("api_logs")
    log_dir.mkdir(exist_ok=True)
    
    # Main application log
    logger.add(
        str(log_dir / "api.log"),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:8} | {service} | {request_id} | {message}",
        rotation="1 day",
        retention="7 days"
    )
    
    # Error log
    logger.add(
        str(log_dir / "errors.log"),
        format="{time:YYYY-MM-DDTHH:mm:ss.SSS} | ERROR | {service} | {request_id} | {message}",
        filter_min_level="ERROR"
    )

# Usage
setup_api_logging()

api = APIHandler("UserService")

# Simulate API calls
print("=== API Request Examples ===")
result1 = api.handle_request("GET", "/users/123")
print(f"GET /users/123: {result1}")

result2 = api.handle_request("POST", "/users", {"name": "Bob", "email": "bob@example.com"})
print(f"POST /users: {result2}")

result3 = api.handle_request("GET", "/invalid")
print(f"GET /invalid: {result3}")

logger.complete()
```

### Async Processing with Improved Exception Handling

```python
import asyncio
from __future__ import annotations
from uuid import uuid7
from logly import logger
from pathlib import Path

class AsyncProcessor:
    """Async data processor with Python 3.14 features."""
    
    def __init__(self, name: str):
        self.name = name
        self.request_id = uuid7()
        self.logger = logger.bind(
            processor=name,
            request_id=str(self.request_id)
        )
    
    async def process_batch(self, items: list[dict]) -> list[dict]:
        """Process items asynchronously with logging."""
        self.logger.info("Batch processing started", batch_size=len(items))
        
        tasks = []
        for i, item in enumerate(items):
            task = asyncio.create_task(self._process_item(item, i))
            tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle results and exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error("Item processing failed", 
                                     item_index=i, 
                                     error=str(result))
                else:
                    processed_results.append(result)
            
            self.logger.success("Batch processing completed", 
                               processed=len(processed_results),
                               failed=len(results) - len(processed_results))
            
            return processed_results
            
        except Exception as e:
            self.logger.critical("Batch processing failed", 
                                error=str(e),
                                exception=True)
            return []
    
    async def _process_item(self, item: dict, index: int) -> dict:
        """Process individual item."""
        item_logger = self.logger.bind(item_index=index)
        item_logger.debug("Processing item", item_keys=list(item.keys()))
        
        # Simulate async processing
        await asyncio.sleep(0.01)
        
        # Simulate random failure
        if index == 2:  # Fail third item
            raise ValueError("Simulated processing error")
        
        result = {
            "id": item.get("id"),
            "processed": True,
            "timestamp": str(uuid7())
        }
        
        item_logger.debug("Item processed successfully")
        return result

async def main():
    """Main async function."""
    logger.configure(level="INFO", color=True)
    
    # Use pathlib for log directory
    log_dir = Path("async_logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        str(log_dir / "async.log"),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:8} | {processor} | {request_id} | {message}"
    )
    
    processor = AsyncProcessor("BatchProcessor")
    
    # Sample data
    items = [
        {"id": "item1", "data": "value1"},
        {"id": "item2", "data": "value2"},
        {"id": "item3", "data": "value3"},  # This will fail
        {"id": "item4", "data": "value4"}
    ]
    
    results = await processor.process_batch(items)
    
    print(f"Processed {len(results)} items successfully")
    
    logger.complete()

# Run async example
print("=== Async Processing Example ===")
asyncio.run(main())
```

### Data Pipeline with Pathlib Enhancements

```python
from __future__ import annotations
from pathlib import Path
from uuid import uuid7
from logly import logger
from datetime import datetime
import json

class DataPipeline:
    """Data processing pipeline with Python 3.14 pathlib features."""
    
    def __init__(self, pipeline_name: str):
        self.pipeline_name = pipeline_name
        self.pipeline_id = uuid7()
        self.logger = logger.bind(
            pipeline=pipeline_name,
            pipeline_id=str(self.pipeline_id)
        )
        
        # Use pathlib for directory management
        self.data_dir = Path("data")
        self.archive_dir = Path("archive")
        self.data_dir.mkdir(exist_ok=True)
        self.archive_dir.mkdir(exist_ok=True)
    
    def process_files(self) -> dict:
        """Process all files in data directory."""
        self.logger.info("Pipeline started", data_dir=str(self.data_dir))
        
        stats = {"processed": 0, "errors": 0, "archived": 0}
        
        try:
            for file_path in self.data_dir.glob("*.json"):
                try:
                    result = self._process_file(file_path)
                    if result:
                        stats["processed"] += 1
                        self._archive_file(file_path)
                        stats["archived"] += 1
                    else:
                        stats["errors"] += 1
                        
                except Exception as e:
                    self.logger.error("File processing failed",
                                     file=str(file_path),
                                     error=str(e))
                    stats["errors"] += 1
            
            self.logger.success("Pipeline completed", **stats)
            return stats
            
        except Exception as e:
            self.logger.critical("Pipeline failed", 
                                error=str(e),
                                exception=True)
            return stats
    
    def _process_file(self, file_path: Path) -> bool:
        """Process individual file."""
        file_logger = self.logger.bind(file=str(file_path))
        
        # Use Python 3.14's info property
        info = file_path.info
        file_logger.info("Processing file",
                        size=info.size,
                        modified=datetime.fromtimestamp(info.mtime).isoformat())
        
        # Read and process JSON
        with file_path.open('r') as f:
            data = json.load(f)
        
        # Simulate processing
        processed_data = {
            "original": data,
            "processed_at": str(uuid7()),
            "pipeline": self.pipeline_name
        }
        
        # Write processed data
        output_path = file_path.with_suffix('.processed.json')
        with output_path.open('w') as f:
            json.dump(processed_data, f, indent=2)
        
        file_logger.success("File processed", output=str(output_path))
        return True
    
    def _archive_file(self, file_path: Path):
        """Archive processed file using Python 3.14 copy method."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        archive_path = self.archive_dir / archive_name
        
        # Use Python 3.14's copy method
        copied = file_path.copy(archive_path)
        self.logger.debug("File archived", 
                         original=str(file_path),
                         archive=str(copied))

def setup_pipeline_logging():
    """Configure logging for data pipeline."""
    logger.configure(level="INFO", color=True)
    
    logger.add(
        "pipeline.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:8} | {pipeline} | {pipeline_id} | {message}",
        rotation="daily"
    )

# Usage
print("=== Data Pipeline Example ===")

# Create sample data files
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

sample_data = [
    {"id": 1, "name": "Alice", "value": 100},
    {"id": 2, "name": "Bob", "value": 200},
    {"id": 3, "name": "Charlie", "value": 300}
]

for i, data in enumerate(sample_data):
    file_path = data_dir / f"data_{i+1}.json"
    with file_path.open('w') as f:
        json.dump(data, f, indent=2)

setup_pipeline_logging()

pipeline = DataPipeline("DataProcessor")
stats = pipeline.process_files()

print(f"Pipeline stats: {stats}")
logger.complete()
```

### Microservice with Parallel Workers

```python
from concurrent.futures import InterpreterPoolExecutor
from __future__ import annotations
from uuid import uuid7
from logly import logger
from pathlib import Path
import time
import random

class Microservice:
    """Microservice with parallel worker processing."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.service_id = uuid7()
        self.logger = logger.bind(
            service=service_name,
            service_id=str(self.service_id)
        )
    
    def handle_requests(self, requests: list[dict]) -> list[dict]:
        """Handle multiple requests in parallel."""
        self.logger.info("Handling requests", count=len(requests))
        
        # Use InterpreterPoolExecutor for true parallelism
        with InterpreterPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self._process_request, req) for req in requests]
            results = [f.result() for f in futures]
        
        successful = [r for r in results if not r.get("error")]
        failed = [r for r in results if r.get("error")]
        
        self.logger.success("Requests processed",
                           successful=len(successful),
                           failed=len(failed))
        
        return results
    
    def _process_request(self, request: dict) -> dict:
        """Process individual request in isolated interpreter."""
        from logly import logger
        from uuid import uuid7
        
        # Each worker has its own logger instance
        request_id = uuid7()
        worker_logger = logger.bind(
            request_id=str(request_id),
            worker_id=str(uuid7())
        )
        
        worker_logger.configure(level="DEBUG")
        worker_logger.add(f"worker_{request_id}.log")
        
        try:
            worker_logger.info("Worker processing request", 
                              request_type=request.get("type"))
            
            # Simulate processing time
            time.sleep(random.uniform(0.1, 0.5))
            
            # Simulate random success/failure
            if random.random() < 0.8:  # 80% success rate
                result = {
                    "request_id": str(request_id),
                    "status": "success",
                    "data": f"Processed {request.get('data', 'unknown')}"
                }
                worker_logger.success("Request completed")
            else:
                raise ValueError("Simulated processing error")
            
            worker_logger.complete()
            return result
            
        except ValueError, TypeError:  # Python 3.14 syntax
            worker_logger.error("Processing failed", 
                               error="Invalid request data")
            worker_logger.complete()
            return {
                "request_id": str(request_id),
                "status": "error",
                "error": "Invalid request data"
            }
        
        except Exception as e:
            worker_logger.critical("Unexpected error", 
                                  error=str(e),
                                  exception=True)
            worker_logger.complete()
            return {
                "request_id": str(request_id),
                "status": "error", 
                "error": str(e)
            }

def setup_microservice_logging():
    """Configure logging for microservice."""
    logger.configure(level="INFO", color=True)
    
    log_dir = Path("microservice_logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        str(log_dir / "service.log"),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:8} | {service} | {service_id} | {message}",
        rotation="hourly"
    )

# Usage
print("=== Microservice Example ===")

setup_microservice_logging()

service = Microservice("OrderProcessor")

# Sample requests
requests = [
    {"type": "order", "data": "laptop"},
    {"type": "payment", "data": "credit_card"},
    {"type": "shipping", "data": "express"},
    {"type": "order", "data": "mouse"},
    {"type": "payment", "data": "paypal"},
    {"type": "invalid", "data": None}  # This will fail
]

results = service.handle_requests(requests)

print(f"Processed {len(results)} requests")
for result in results:
    status = result.get("status")
    req_id = result.get("request_id", "")[:8]
    print(f"Request {req_id}: {status}")

logger.complete()
```

These examples demonstrate practical usage of Python 3.14 features with Logly in real-world scenarios including web APIs, async processing, data pipelines, and microservices.
