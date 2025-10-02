---
title: Context Management API - Logly Python Logging
description: Logly context management API reference. Learn how to bind persistent context and use contextualize for temporary context in log messages.
keywords: python, logging, context, management, api, binding, persistent, temporary, logly
---

# Context Management

Methods for adding contextual information to log messages.

---

## Overview

Logly supports two context management approaches:

| Method | Scope | Use Case |
|--------|-------|----------|
| `bind()` | **Global** | Add fields to all subsequent logs |
| `contextualize()` | **Scoped** | Add fields within context manager |

All context fields:
- ✅ Automatically included in log output
- ✅ Support JSON mode (nested under `fields`)
- ✅ Can be overridden by method kwargs
- ✅ Persist across async boundaries

---

## logger.bind()

Add fields globally that persist across all log calls.

### Signature

```python
logger.bind(**kwargs) -> PyLogger
```

### Parameters
- `**kwargs`: Key-value pairs to bind

### Returns
- `PyLogger`: New logger instance with bound context

### Examples

=== "Request Context"
    ```python
    from logly import logger
    
    # Bind request context
    request_logger = logger.bind(
        request_id="abc-123",
        user_id="user-456",
        ip="192.168.1.1"
    )
    
    # All logs include context
    request_logger.info("Processing request")
    # Output: ... | Processing request request_id=abc-123 user_id=user-456 ip=192.168.1.1
    
    request_logger.error("Request failed", status_code=500)
    # Output: ... | Request failed request_id=abc-123 user_id=user-456 ip=192.168.1.1 status_code=500
    ```

=== "User Session"
    ```python
    # Bind user session
    user_logger = logger.bind(
        user_id="alice",
        session_id="sess-789",
        role="admin"
    )
    
    user_logger.info("User logged in")
    user_logger.debug("Accessed dashboard")
    user_logger.info("User logged out")
    # All logs include user_id, session_id, role
    ```

=== "Microservice Context"
    ```python
    # Bind service context
    service_logger = logger.bind(
        service="auth-api",
        version="1.2.3",
        environment="production",
        pod_id="pod-abc-123"
    )
    
    service_logger.info("Service started")
    service_logger.error("Database connection failed")
    # All logs include service metadata
    ```

=== "Chain Binding"
    ```python
    # Chain multiple bind() calls
    logger_with_context = (
        logger
        .bind(service="api")
        .bind(version="1.0.0")
        .bind(environment="prod")
    )
    
    logger_with_context.info("Initialized")
    # Output: ... | Initialized service=api version=1.0.0 environment=prod
    ```

### Notes

!!! tip "When to Use bind()"
    - **Web Requests**: Bind request_id, user_id at start of request
    - **Background Jobs**: Bind job_id, worker_id
    - **Microservices**: Bind service name, version, environment
    - **Multi-tenancy**: Bind tenant_id, organization_id

!!! warning "Immutability"
    `bind()` returns a **new** logger instance. The original logger is unchanged:
    ```python
    original = logger
    bound = logger.bind(x=1)
    
    original.info("Test")  # Does NOT include x=1
    bound.info("Test")     # Includes x=1
    ```

!!! info "Memory Efficiency"
    Bound loggers share the same underlying backend. Creating many bound loggers is efficient.

---

## logger.contextualize()

Add fields within a scoped context manager. Fields are automatically removed when exiting the context.

### Signature

```python
logger.contextualize(**kwargs) -> ContextManager
```

### Parameters
- `**kwargs`: Key-value pairs to add within context

### Returns
- `ContextManager`: Context manager that adds/removes fields

### Examples

=== "Function Scope"
    ```python
    from logly import logger
    
    def process_order(order_id: int):
        with logger.contextualize(order_id=order_id, stage="processing"):
            logger.info("Starting order processing")
            # ... processing logic ...
            logger.info("Order validated")
            logger.info("Payment processed")
        
        # Context removed after exiting
        logger.info("Order complete")
    ```

=== "Request Handler"
    ```python
    def handle_request(request_id: str, user_id: str):
        with logger.contextualize(request_id=request_id, user_id=user_id):
            logger.info("Request received")
            
            try:
                result = process_request()
                logger.success("Request succeeded")
                return result
            except Exception as e:
                logger.error("Request failed", error=str(e))
                raise
        
        # request_id and user_id no longer in context
    ```

=== "Nested Contexts"
    ```python
    def outer_function():
        with logger.contextualize(level="outer"):
            logger.info("Outer scope")  # level=outer
            
            with logger.contextualize(level="inner"):
                logger.info("Inner scope")  # level=inner (overrides)
            
            logger.info("Back to outer")  # level=outer
    ```

=== "Async Context"
    ```python
    async def async_task(task_id: str):
        with logger.contextualize(task_id=task_id):
            logger.info("Task started")
            await process_async()
            logger.info("Task complete")
        # Context preserved across await boundaries
    ```

### Notes

!!! tip "When to Use contextualize()"
    - **Function Scope**: Add context for a specific function
    - **Request Handlers**: Add request-specific context
    - **Nested Operations**: Add context for sub-operations
    - **Try/Except Blocks**: Add context for error handling

!!! info "Automatic Cleanup"
    Context is automatically removed when exiting the `with` block, even if an exception occurs:
    ```python
    with logger.contextualize(x=1):
        logger.info("Inside")  # x=1
        raise ValueError()
    
    logger.info("Outside")  # x NOT included
    ```

!!! warning "Thread Safety"
    Context is **thread-local**. Each thread has its own context stack:
    ```python
    import threading
    
    def worker():
        with logger.contextualize(thread_id=threading.current_thread().name):
            logger.info("Worker log")  # Only this thread sees thread_id
    ```

---

## Context Priority

When the same field is defined in multiple places, the priority is:

**Highest to Lowest:**

1. **Method kwargs** (direct argument to log call)
2. **contextualize()** (innermost context)
3. **bind()** (bound context)
4. **Global configuration**

### Example

```python
logger.bind(x=1)  # Priority 3

with logger.contextualize(x=2):  # Priority 2
    logger.info("Test", x=3)  # Priority 1 (wins)
    # Output: ... | Test x=3
```

---

## Complete Example

```python
from logly import logger

# Configure
logger.configure(level="INFO", json=True)
logger.add("console")
logger.add("logs/app.log")

# Global context with bind()
service_logger = logger.bind(
    service="api",
    version="1.0.0",
    environment="production"
)

def handle_request(request_id: str, user_id: str):
    # Scoped context with contextualize()
    with service_logger.contextualize(request_id=request_id, user_id=user_id):
        service_logger.info("Request received")
        
        try:
            result = process_request()
            service_logger.success("Request succeeded", duration_ms=42)
            return result
        except Exception as e:
            # Include exception details
            service_logger.error("Request failed", error=str(e), error_type=type(e).__name__)
            raise

# Usage
handle_request("req-123", "alice")

# Cleanup
logger.complete()
```

---

## Best Practices

### ✅ DO

```python
# 1. Use bind() for long-lived context
request_logger = logger.bind(request_id=request_id)

# 2. Use contextualize() for scoped context
with logger.contextualize(stage="validation"):
    logger.info("Validating input")

# 3. Chain bind() for readability
logger.bind(service="api").bind(version="1.0").info("Started")

# 4. Include exception details in errors
try:
    risky_op()
except Exception as e:
    logger.error("Failed", error=str(e), error_type=type(e).__name__)
```

### ❌ DON'T

```python
# 1. Don't forget bind() returns new logger
logger.bind(x=1)  # ❌ Doesn't modify logger
logger.info("Test")  # ❌ x=1 NOT included

bound = logger.bind(x=1)  # ✅ Correct
bound.info("Test")  # ✅ x=1 included

# 2. Don't use contextualize() for global context
with logger.contextualize(service="api"):  # ❌ Too broad
    # ... entire application ...

logger_service = logger.bind(service="api")  # ✅ Use bind()

# 3. Don't nest too many contexts
with logger.contextualize(a=1):
    with logger.contextualize(b=2):
        with logger.contextualize(c=3):  # ❌ Hard to follow
            logger.info("Deep nesting")
```
