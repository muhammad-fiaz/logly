---
title: Exception Handling API - Logly Python Logging
description: Logly exception handling API reference. Learn how to use catch decorators and exception logging methods for robust error handling.
keywords: python, logging, exceptions, api, error, handling, decorators, catch, logly
---

# Exception Handling

Methods for catching and logging exceptions.

---

## Overview

Logly provides two approaches for exception handling:

| Method | Type | Use Case |
|--------|------|----------|
| `catch()` | **Decorator** | Wrap functions to catch exceptions |
| `exception()` | **Method** | Log exceptions manually |

Both methods:
- ✅ **Capture full traceback** (file, line, function)
- ✅ **Support custom error handlers** (callbacks on error)
- ✅ **Work with sync and async functions**
- ✅ **Include exception details** in log output
- ✅ **Allow re-raising** exceptions

---

## logger.catch()

Decorator that catches exceptions in functions and logs them automatically.

### Signature

```python
logger.catch(
    exception: type[BaseException] | tuple[type[BaseException], ...] = Exception,
    *,
    level: str = "ERROR",
    reraise: bool = False,
    message: str = "An error occurred",
    onerror: Callable | None = None
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `exception` | `type \| tuple` | `Exception` | Exception type(s) to catch |
| `level` | `str` | `"ERROR"` | Log level for caught exceptions |
| `reraise` | `bool` | `False` | Re-raise exception after logging |
| `message` | `str` | `"An error occurred"` | Custom error message |
| `onerror` | `Callable \| None` | `None` | Callback function on error |

### Returns
- Decorator function

### Examples

=== "Basic Usage"
    ```python
    from logly import logger
    
    logger.configure(level="DEBUG")
    logger.add("console")
    
    @logger.catch()
    def divide(a: int, b: int) -> float:
        return a / b
    
    # Normal execution
    result = divide(10, 2)  # Returns 5.0
    
    # Exception caught and logged
    result = divide(10, 0)  # Returns None, logs ZeroDivisionError
    ```

    **Output:**
    ```
    2025-01-15 10:30:45 | ERROR | An error occurred
    Traceback (most recent call last):
      File "app.py", line 8, in divide
        return a / b
    ZeroDivisionError: division by zero
    ```

=== "Custom Message"
    ```python
    @logger.catch(message="Division operation failed")
    def divide(a: int, b: int) -> float:
        return a / b
    
    divide(10, 0)
    # Output: ... | ERROR | Division operation failed
    ```

=== "Specific Exceptions"
    ```python
    @logger.catch(exception=(ValueError, TypeError))
    def process_data(data: str) -> int:
        return int(data)
    
    process_data("invalid")  # Catches ValueError
    process_data(None)       # Catches TypeError
    ```

=== "Reraise Exception"
    ```python
    @logger.catch(reraise=True)
    def critical_operation():
        risky_code()
    
    try:
        critical_operation()  # Logs AND raises exception
    except Exception as e:
        print(f"Caught: {e}")
    ```

=== "Custom Log Level"
    ```python
    @logger.catch(level="CRITICAL")
    def system_critical_task():
        perform_critical_operation()
    
    system_critical_task()  # Logs at CRITICAL level
    ```

=== "Error Callback"
    ```python
    def on_error(exception: Exception):
        print(f"Error handler: {type(exception).__name__}")
        # Send alert, increment counter, etc.
    
    @logger.catch(onerror=on_error)
    def monitored_function():
        raise ValueError("Something went wrong")
    
    monitored_function()
    # Logs error AND calls on_error()
    ```

=== "Async Functions"
    ```python
    import asyncio
    
    @logger.catch()
    async def async_task():
        await asyncio.sleep(1)
        raise RuntimeError("Async error")
    
    asyncio.run(async_task())  # Logs exception
    ```

=== "Class Methods"
    ```python
    class DataProcessor:
        @logger.catch(message="Processing failed")
        def process(self, data):
            # ... processing logic ...
            raise ValueError("Invalid data")
    
    processor = DataProcessor()
    processor.process(data)  # Logs exception
    ```

### Notes

!!! tip "When to Use catch()"
    - **Function-Level**: Wrap entire functions for automatic error handling
    - **API Endpoints**: Catch exceptions in web handlers
    - **Background Tasks**: Monitor long-running tasks
    - **Data Processing**: Catch errors in data pipelines
    - **Integration Points**: Log errors at system boundaries

!!! warning "Return Value"
    When an exception is caught (and not re-raised), the function returns `None`:
    ```python
    @logger.catch()
    def get_user(user_id: int) -> User:
        return database.get(user_id)  # Raises exception
    
    user = get_user(123)  # user = None (not User)
    ```

!!! info "Multiple Exceptions"
    Catch multiple exception types:
    ```python
    @logger.catch(exception=(ValueError, KeyError, IndexError))
    def process_data(data):
        # ... processing ...
        pass
    ```

!!! warning "Exception Propagation"
    Without `reraise=True`, exceptions are **not** propagated:
    ```python
    @logger.catch()  # reraise=False (default)
    def task():
        raise ValueError()
    
    try:
        task()  # No exception raised (caught and logged)
    except ValueError:
        print("This won't execute")  # Never reached
    ```

---

## logger.exception()

Manually log an exception with full traceback.

### Signature

```python
logger.exception(message: str, **kwargs) -> None
```

### Parameters
- `message` (str): Log message
- `**kwargs`: Additional context fields

### Returns
- `None`

### Examples

=== "Try/Except Block"
    ```python
    from logly import logger
    
    try:
        result = 10 / 0
    except ZeroDivisionError:
        logger.exception("Division error occurred")
    ```

    **Output:**
    ```
    2025-01-15 10:30:45 | ERROR | Division error occurred
    Traceback (most recent call last):
      File "app.py", line 4, in <module>
        result = 10 / 0
    ZeroDivisionError: division by zero
    ```

=== "With Context"
    ```python
    try:
        process_order(order_id=1234)
    except Exception:
        logger.exception(
            "Order processing failed",
            order_id=1234,
            user_id="alice",
            retry_count=3
        )
    ```

=== "Custom Handler"
    ```python
    def handle_request(request_id: str):
        try:
            process_request()
        except ValueError as e:
            logger.exception(
                "Invalid request data",
                request_id=request_id,
                error_type=type(e).__name__
            )
        except Exception:
            logger.exception(
                "Unexpected error",
                request_id=request_id
            )
    ```

=== "Async Context"
    ```python
    async def async_task():
        try:
            await risky_async_operation()
        except Exception:
            logger.exception("Async operation failed")
    ```

=== "Re-raise After Logging"
    ```python
    try:
        critical_operation()
    except Exception:
        logger.exception("Critical error")
        raise  # Re-raise after logging
    ```

### Notes

!!! tip "When to Use exception()"
    - **Try/Except Blocks**: Log exceptions in error handlers
    - **Custom Error Handling**: Add context before logging
    - **Debugging**: Capture full traceback for investigation
    - **Monitoring**: Track exception patterns

!!! info "Automatic Traceback"
    `exception()` automatically includes the full traceback from the current exception context:
    ```python
    try:
        raise ValueError("Error")
    except:
        logger.exception("Captured")  # Includes full traceback
    ```

!!! warning "Must Be In Exception Context"
    `exception()` should only be called within an exception handler (`except` block):
    ```python
    # ❌ WRONG: Not in exception context
    logger.exception("No exception")
    
    # ✅ CORRECT: In exception context
    try:
        raise ValueError()
    except:
        logger.exception("Exception captured")
    ```

---

## Comparison

### catch() vs exception()

| Feature | `catch()` | `exception()` |
|---------|-----------|---------------|
| **Type** | Decorator | Method |
| **Usage** | Wrap functions | Manual in try/except |
| **Automatic** | ✅ Yes | ❌ No |
| **Control** | Limited | Full |
| **Reraise** | Optional (`reraise=`) | Manual (`raise`) |
| **Callback** | Optional (`onerror=`) | N/A |

### When to Use Each

**Use `catch()` when:**
- ✅ You want automatic exception handling
- ✅ Function-level error handling is sufficient
- ✅ You need error callbacks (`onerror=`)
- ✅ Minimal boilerplate is preferred

**Use `exception()` when:**
- ✅ You need custom error handling logic
- ✅ Different exceptions require different handling
- ✅ You want fine-grained control
- ✅ You need to add context before logging

---

## Complete Example

```python
from logly import logger
import asyncio

# Configure
logger.configure(level="DEBUG", color=True)
logger.add("console")
logger.add("logs/errors.log", level="ERROR")

# Error callback
error_count = 0

def on_error(exception: Exception):
    global error_count
    error_count += 1
    print(f"🚨 Error #{error_count}: {type(exception).__name__}")

# Using catch() decorator
@logger.catch(
    message="Data processing failed",
    level="ERROR",
    onerror=on_error
)
def process_data(data: list[int]):
    return sum(data) / len(data)  # ZeroDivisionError if empty

# Using exception() method
def handle_request(request_id: str):
    try:
        if not request_id:
            raise ValueError("Missing request_id")
        
        result = process_data([])
        return result
    except ValueError as e:
        logger.exception(
            "Validation error",
            request_id=request_id,
            error_type="validation"
        )
    except Exception:
        logger.exception(
            "Unexpected error",
            request_id=request_id
        )

# Async example
@logger.catch(reraise=True)
async def async_task(task_id: int):
    await asyncio.sleep(0.1)
    if task_id < 0:
        raise ValueError(f"Invalid task_id: {task_id}")
    return task_id * 2

# Run examples
async def main():
    # Test catch() decorator
    result1 = process_data([1, 2, 3])  # OK: returns 2.0
    result2 = process_data([])          # ERROR: logged, returns None
    
    # Test exception() method
    handle_request("")     # ValueError logged
    handle_request("123")  # ZeroDivisionError logged
    
    # Test async catch()
    try:
        await async_task(-1)  # ValueError logged and raised
    except ValueError:
        print("Caught re-raised exception")
    
    print(f"Total errors: {error_count}")
    logger.complete()

asyncio.run(main())
```

**Output:**
```
2025-01-15 10:30:45 | DEBUG | Processing data
2025-01-15 10:30:45 | ERROR | Data processing failed
Traceback...
ZeroDivisionError: division by zero
🚨 Error #1: ZeroDivisionError

2025-01-15 10:30:45 | ERROR | Validation error request_id= error_type=validation
Traceback...
ValueError: Missing request_id

2025-01-15 10:30:45 | ERROR | Data processing failed
Traceback...
ZeroDivisionError: division by zero
🚨 Error #2: ZeroDivisionError

2025-01-15 10:30:45 | ERROR | Unexpected error request_id=123
Traceback...
ZeroDivisionError: division by zero

2025-01-15 10:30:45 | ERROR | An error occurred
Traceback...
ValueError: Invalid task_id: -1
🚨 Error #3: ValueError

Caught re-raised exception
Total errors: 3
```

---

## Best Practices

### ✅ DO

```python
# 1. Use catch() for automatic handling
@logger.catch()
def api_endpoint():
    process_request()

# 2. Use exception() for custom handling
try:
    risky_operation()
except SpecificError:
    logger.exception("Known error", context="value")
except Exception:
    logger.exception("Unknown error")

# 3. Add context to exceptions
try:
    process_order(order_id)
except Exception:
    logger.exception("Order failed", order_id=order_id, user_id=user_id)

# 4. Use reraise for critical errors
@logger.catch(reraise=True)
def critical_operation():
    must_succeed()
```

### ❌ DON'T

```python
# 1. Don't catch all exceptions silently
@logger.catch()  # ❌ Hides all errors
def critical_operation():
    must_succeed()

# ✅ Use reraise for critical paths
@logger.catch(reraise=True)
def critical_operation():
    must_succeed()

# 2. Don't log exceptions twice
@logger.catch()  # Already logs exception
def process():
    try:
        risky_code()
    except Exception:
        logger.exception("Error")  # ❌ Duplicate logging

# 3. Don't use exception() outside try/except
logger.exception("No exception")  # ❌ No traceback available

# ✅ Use in exception context
try:
    raise ValueError()
except:
    logger.exception("Error captured")

# 4. Don't forget to add context
try:
    process_data(item)
except Exception:
    logger.exception("Error")  # ❌ Missing context

# ✅ Add relevant context
try:
    process_data(item)
except Exception:
    logger.exception("Error processing", item_id=item.id, step="validation")
```
