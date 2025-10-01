---
title: Exception Handling - Logly Examples
description: Exception handling example showing how to use Logly's catch decorator and exception logging methods for robust error handling.
keywords: python, logging, example, exception, handling, decorator, catch, error, logly
---

# Exception Handling

This example demonstrates how to use Logly's exception handling features, including the `@catch` decorator and exception logging methods for comprehensive error tracking.

## Code Example

```python
from logly import logger, catch
import requests

# Configure logging
logger.configure(
    level="INFO",
    format="{time} | {level} | {message}"
)

# Example 1: Basic exception logging
def risky_operation():
    """Function that might raise an exception"""
    raise ValueError("Something went wrong!")

try:
    risky_operation()
except Exception as e:
    logger.exception("Operation failed", error=e)

# Example 2: Using the catch decorator
@catch(level="ERROR", message="API call failed")
def api_call(url: str):
    """Make an API call with automatic exception logging"""
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()

@catch(level="WARNING", reraise=True)
def process_data(data: dict):
    """Process data with warning-level exception logging"""
    if "required_field" not in data:
        raise KeyError("Missing required field")
    return data["required_field"].upper()

# Example 3: Custom exception handling
@catch()
def custom_handler(exc: Exception):
    """Custom exception handler"""
    logger.error("Custom error occurred", error_type=type(exc).__name__, error_msg=str(exc))
    # Don't re-raise, handle it here

# Usage
if __name__ == "__main__":
    # This will log an error but not crash
    result1 = api_call("https://httpbin.org/status/404")

    # This will log a warning and re-raise
    try:
        result2 = process_data({})
    except KeyError:
        logger.info("Handled the re-raised exception")

    # This will use custom handler
    custom_handler(ValueError("Test error"))
```

## Output

```
2025-01-15 10:30:45 | ERROR | Operation failed
Traceback (most recent call last):
  File "example.py", line 15, in <main>
    ValueError: Something went wrong!

2025-01-15 10:30:45 | ERROR | API call failed
Traceback (most recent call last):
  File "example.py", line 22, in api_call
    requests.exceptions.HTTPError: 404 Client Error

2025-01-15 10:30:45 | WARN  | Data processing failed
Traceback (most recent call last):
  File "example.py", line 29, in process_data
    KeyError: Missing required field

2025-01-15 10:30:45 | INFO  | Handled the re-raised exception
2025-01-15 10:30:45 | ERROR | Custom error occurred
```

## Catch Decorator Options

### Basic Usage

```python
@catch()  # Default: level="ERROR", reraise=False
def my_function():
    pass
```

### Advanced Configuration

```python
@catch(
    level="WARNING",        # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    message="Custom error message",  # Custom message instead of function name
    reraise=True,           # Re-raise exception after logging (default: False)
    exclude=(ValueError,)   # Exception types to ignore
)
def my_function():
    pass
```

### Custom Handler

```python
@catch()
def my_error_handler(exc: Exception):
    """Custom exception handling logic"""
    if isinstance(exc, ConnectionError):
        logger.error("Network error - retrying", error=str(exc))
        # Implement retry logic
    else:
        logger.exception("Unexpected error", error=exc)
```

## Exception Logging Methods

### Log with Exception

```python
try:
    risky_code()
except Exception as e:
    logger.exception("Something failed", extra_data="value")
```

### Log Exception Object

```python
try:
    risky_code()
except Exception as e:
    logger.error("Operation failed", error=e, error_type=type(e).__name__)
```

## Real-World Examples

### Web Framework Error Handling

```python
from flask import Flask, request
from logly import logger, catch

app = Flask(__name__)

@app.errorhandler(500)
@catch(level="ERROR", message="Unhandled server error")
def handle_500(error):
    logger.exception("Internal server error", url=request.url, method=request.method)
    return "Internal Server Error", 500

@app.route('/api/data')
@catch(level="WARNING", reraise=True)
def get_data():
    # This will log warnings but still return errors to client
    if not request.args.get('id'):
        raise ValueError("Missing required parameter: id")

    data = fetch_data(request.args['id'])
    return data
```

### Database Operations

```python
import sqlite3
from logly import logger, catch

@catch(level="ERROR", message="Database operation failed")
def execute_query(query: str, params: tuple = ()):
    """Execute database query with error handling"""
    conn = sqlite3.connect('app.db')
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.commit()
        return result
    except sqlite3.Error as e:
        logger.exception("Database error", query=query, params=params)
        raise
    finally:
        conn.close()

# Usage
try:
    result = execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
except Exception:
    # Error already logged by decorator
    return {"error": "Database error"}
```

## Key Features Demonstrated

- **Automatic exception logging**: `@catch` decorator handles exceptions
- **Configurable behavior**: Control log level, messages, and re-raising
- **Custom handlers**: Implement your own exception handling logic
- **Traceback inclusion**: Full stack traces in logs
- **Context preservation**: Exception logs include current context