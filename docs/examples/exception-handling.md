---
title: Exception Handling - Logly Examples
description: Exception handling example showing how to use Logly's catch decorator and exception logging methods for robust error handling.
keywords: python, logging, example, exception, handling, decorator, catch, error, logly
---

# Exception Handling

This example demonstrates how to use Logly's exception handling features, including the `@catch` decorator and exception logging methods for comprehensive error tracking.

## Code Example

```python
from logly import logger

# Configure logging
logger.configure(level="INFO")
logger.add("console")

# Example 1: Using @logger.catch() decorator (prevents crashes)
@logger.catch(reraise=False)
def risky_operation():
    """Function that might raise an exception"""
    result = 1 / 0  # This will raise ZeroDivisionError
    return result

# Example 2: Catch and reraise (log but still raise)
@logger.catch(reraise=True)
def must_succeed():
    """Function where we want to log AND propagate the exception"""
    raise ValueError("Critical error that must be handled")

# Example 3: Manual exception logging
def manual_error_handling():
    """Manually log exceptions in try/except blocks"""
    try:
        data = {"key": "value"}
        result = data["missing_key"]  # KeyError
    except KeyError as e:
        logger.error("Key not found in data", key="missing_key", error=str(e))
        # Handle the error gracefully
        result = None
    return result

# Usage examples
if __name__ == "__main__":
    # This logs the error but doesn't crash (reraise=False)
    result1 = risky_operation()
    logger.info("Program continues after handled exception")
    
    # This logs the error and then crashes (reraise=True)
    try:
        result2 = must_succeed()
    except ValueError:
        logger.info("Caught the re-raised exception")
    
    # Manual exception handling with logging
    result3 = manual_error_handling()
    logger.info("Manual error handling complete", result=result3)
    
    logger.complete()
```

## Expected Output

```
[ERROR] An error occurred in function 'risky_operation'
Traceback (most recent call last):
  File "example.py", line 10, in risky_operation
    result = 1 / 0
ZeroDivisionError: division by zero

[INFO] Program continues after handled exception

[ERROR] An error occurred in function 'must_succeed'
Traceback (most recent call last):
  File "example.py", line 16, in must_succeed
    raise ValueError("Critical error that must be handled")
ValueError: Critical error that must be handled

[INFO] Caught the re-raised exception

[ERROR] Key not found in data | key=missing_key | error='missing_key'

[INFO] Manual error handling complete | result=None
```

**What happens:**
- **`@logger.catch(reraise=False)`**: Logs the full exception with traceback but doesn't crash the program
- **`@logger.catch(reraise=True)`**: Logs the exception AND re-raises it for you to handle
- **`logger.error()`**: Manual exception logging with custom messages and context
- Stack traces are automatically included for debugging
- The program continues execution after caught exceptions (when `reraise=False`)

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