---
title: Context Binding - Logly Examples
description: Context binding example showing how to add persistent and temporary context to log messages for better traceability.
keywords: python, logging, example, context, binding, persistent, temporary, traceability, logly
---

# Context Binding

This example demonstrates how to use Logly's context binding features to add persistent and temporary context to your log messages, making them more informative and traceable.

## Code Example

```python
from logly import logger

# Configure logging
logger.configure(level="INFO")
logger.add("console")

# Create a bound logger with persistent context
request_logger = logger.bind(user_id=12345, session_id="abc-123", service="auth")

# All logs from this logger include the bound context
request_logger.info("User authentication started")
request_logger.info("Validating credentials")
request_logger.info("Password verification successful")

# Nested context with contextualize
with logger.contextualize(request_id="req-456", endpoint="/login"):
    logger.info("Processing login request")
    
    # This log inherits the contextualize context
    logger.info("User lookup completed")
    
    # You can nest contextualize blocks
    with logger.contextualize(operation="password_check"):
        logger.info("Checking password hash")
        logger.info("Hash verification passed")
    
    logger.info("Login successful")

# Context from contextualize is cleared after the block
logger.info("Authentication flow completed")
```

## Expected Output

```
[INFO] User authentication started | user_id=12345 | session_id=abc-123 | service=auth
[INFO] Validating credentials | user_id=12345 | session_id=abc-123 | service=auth
[INFO] Password verification successful | user_id=12345 | session_id=abc-123 | service=auth
[INFO] Processing login request | request_id=req-456 | endpoint=/login
[INFO] User lookup completed | request_id=req-456 | endpoint=/login
[INFO] Checking password hash | request_id=req-456 | endpoint=/login | operation=password_check
[INFO] Hash verification passed | request_id=req-456 | endpoint=/login | operation=password_check
[INFO] Login successful | request_id=req-456 | endpoint=/login
[INFO] Authentication flow completed
```

**What happens:**
- **`logger.bind()`** creates a new logger instance with persistent context (user_id, session_id, service)
- **`logger.contextualize()`** adds temporary context for the duration of the `with` block
- Context can be nested - inner blocks inherit outer context
- After exiting a `contextualize` block, that context is removed
- The bound logger keeps its context throughout its lifetime

## Advanced Context Examples

### Web Application Context

```python
from flask import request, g
from logly import logger

def setup_request_logging():
    """Setup context for each web request"""
    logger.bind(
        request_id=request.headers.get('X-Request-ID', 'unknown'),
        user_agent=request.headers.get('User-Agent'),
        ip=request.remote_addr,
        method=request.method,
        path=request.path
    )

@app.before_request
def before_request():
    setup_request_logging()
    logger.info("Request started")

@app.after_request
def after_request(response):
    logger.info("Request completed", status=response.status_code, size=len(response.data))
    return response
```

### Database Transaction Context

```python
from logly import logger

def execute_transaction(user_id: int, operation: str):
    """Execute database transaction with context"""
    with logger.contextualize(user_id=user_id, operation=operation, transaction_id="tx-123"):
        logger.info("Starting transaction")

        try:
            # Database operations here
            logger.info("Executing SQL query", query="SELECT * FROM users")
            logger.info("Query completed", rows_affected=1)

            logger.info("Committing transaction")
            # commit logic

        except Exception as e:
            logger.error("Transaction failed", error=str(e))
            raise
```

### Multi-tenant Application

```python
from logly import logger

class TenantContext:
    def __init__(self, tenant_id: str, user_id: str):
        self.tenant_id = tenant_id
        self.user_id = user_id

    def __enter__(self):
        logger.bind(tenant_id=self.tenant_id, user_id=self.user_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.unbind("tenant_id", "user_id")

def process_tenant_request(tenant_id: str, user_id: str, data: dict):
    with TenantContext(tenant_id, user_id):
        logger.info("Processing tenant request", data_size=len(str(data)))

        # Process data
        logger.info("Validation completed")
        logger.info("Data processing completed")

        return {"status": "success"}
```

## Context Management Methods

### Persistent Context

```python
# Add persistent context
logger.bind(key="value", key2="value2")

# Remove specific keys
logger.unbind("key")

# Clear all context
logger.unbind_all()
```

### Temporary Context

```python
# Context for single log
logger.info("Message", extra={"temp_key": "temp_value"})

# Context for code block
with logger.contextualize(temp_key="temp_value"):
    logger.info("This log has temp context")
    logger.info("This one too")

# After block, context is gone
logger.info("Back to normal context")
```

## Key Features Demonstrated

- **Persistent context**: Context that applies to all subsequent logs
- **Temporary context**: Context for specific operations or code blocks
- **Nested context**: Hierarchical context inheritance
- **Automatic formatting**: Context automatically included in log format
- **Thread safety**: Context is isolated per thread