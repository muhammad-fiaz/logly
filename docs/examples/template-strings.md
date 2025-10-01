---
title: Template Strings - Logly Examples
description: Template strings example showing how to use variable interpolation and formatting in log messages with Logly.
keywords: python, logging, example, template, strings, interpolation, formatting, variables, logly
---

# Template Strings

This example demonstrates Logly's template string functionality, which allows you to embed variables directly in log messages using `{variable}` syntax.

## Code Example

```python
from logly import logger

# Configure logging
logger.configure(level="INFO", color=True)
logger.add("console")

# Basic template strings
user_id = 12345
action = "login"
logger.info("User {user_id} performed {action}", user_id=user_id, action=action)

# Multiple variables
product_name = "Widget Pro"
price = 99.99
quantity = 5
logger.info("Sold {quantity} units of {product_name} at ${price} each",
           product_name=product_name, price=price, quantity=quantity)

# With context binding
logger.bind(session_id="sess-abc123", user_agent="Mozilla/5.0")

logger.info("Request from {user_agent} in session {session_id}")

# Complex data structures
user = {"id": 123, "name": "Alice", "role": "admin"}
permissions = ["read", "write", "delete"]
logger.info("User {user[name]} (ID: {user[id]}) has permissions: {permissions}",
           user=user, permissions=permissions)

# Template strings with different log levels
logger.warning("Low disk space: {available_gb}GB remaining on {mount_point}",
              available_gb=2.1, mount_point="/var")

logger.error("Database connection failed after {retry_count} attempts to {host}:{port}",
            retry_count=3, host="db.example.com", port=5432)

# Using f-strings with templates (advanced)
def process_order(order_id, customer_name, total_amount):
    logger.info("Processing order {order_id} for {customer_name}",
               order_id=order_id, customer_name=customer_name)
    
    # Simulate processing
    logger.debug("Validating payment of ${total_amount}", total_amount=total_amount)
    logger.info("Order {order_id} completed successfully")
    
    return f"Order {order_id} processed"

# Usage
result = process_order("ORD-12345", "John Doe", 149.99)
```

## Output

```
2025-01-15 10:30:45 | INFO  | User 12345 performed login
2025-01-15 10:30:45 | INFO  | Sold 5 units of Widget Pro at $99.99 each
2025-01-15 10:30:45 | INFO  | Request from Mozilla/5.0 in session sess-abc123
2025-01-15 10:30:45 | INFO  | User Alice (ID: 123) has permissions: ['read', 'write', 'delete']
2025-01-15 10:30:45 | WARN  | Low disk space: 2.1GB remaining on /var
2025-01-15 10:30:45 | ERROR | Database connection failed after 3 attempts to db.example.com:5432
2025-01-15 10:30:45 | INFO  | Processing order ORD-12345 for John Doe
2025-01-15 10:30:45 | DEBUG | Validating payment of $149.99
2025-01-15 10:30:45 | INFO  | Order ORD-12345 completed successfully
```

## Advanced Template Features

### Nested Object Access

```python
from logly import logger

# Complex nested data
request = {
    "user": {
        "id": 123,
        "profile": {
            "name": "Alice",
            "email": "alice@example.com"
        }
    },
    "action": "update_profile",
    "changes": ["name", "email"]
}

logger.info("User {request[user][profile][name]} ({request[user][id]}) {request[action]}: {request[changes]}",
           request=request)
```

**Output:**
```
2025-01-15 10:30:45 | INFO | User Alice (123) update_profile: ['name', 'email']
```

### List and Dict Formatting

```python
from logly import logger

# Lists
tags = ["urgent", "security", "audit"]
logger.warning("Security alert with tags: {tags}", tags=tags)

# Dictionaries
metadata = {"version": "1.2.3", "environment": "production", "region": "us-west-2"}
logger.info("Deployment completed in {metadata[environment]} {metadata[region]} (v{metadata[version]})",
           metadata=metadata)
```

**Output:**
```
2025-01-15 10:30:45 | WARN | Security alert with tags: ['urgent', 'security', 'audit']
2025-01-15 10:30:45 | INFO | Deployment completed in production us-west-2 (v1.2.3)
```

### Template String Best Practices

### ✅ DO

```python
# Use descriptive variable names
logger.info("User {user_id} purchased {product_name} for ${price}",
           user_id=user.id, product_name=product.name, price=product.price)

# Include units and context
logger.warning("Disk usage at {percentage}% on {mount_point}",
              percentage=85.5, mount_point="/var/log")

# Use consistent formatting
logger.error("Connection timeout after {timeout_seconds}s to {host}:{port}",
            timeout_seconds=30, host="api.example.com", port=443)
```

### ❌ DON'T

```python
# Don't use string concatenation
logger.info("User " + str(user_id) + " logged in")  # ❌

# Don't mix f-strings and templates unnecessarily
logger.info(f"User {user_id} logged in", user_id=user_id)  # ❌ Redundant

# Don't put complex logic in templates
logger.info("Result: {calculate_complex_value()}", calculate_complex_value=expensive_function)  # ❌
```

### Performance Note

Template variables are only evaluated if the log level passes filtering:

```python
logger.configure(level="INFO")

# This function call is SKIPPED when level="INFO"
logger.debug("Expensive debug: {expensive_operation()}", expensive_operation=my_slow_function)

# This function call IS executed
logger.info("Info message: {expensive_operation()}", expensive_operation=my_slow_function)
```

## Key Features Demonstrated

- **Template syntax**: Use `{variable}` for clean, readable messages
- **Type safety**: Variables are properly formatted regardless of type
- **Performance**: Lazy evaluation prevents unnecessary computation
- **Nested access**: Access properties of objects and dictionaries
- **Context integration**: Templates work seamlessly with bound context