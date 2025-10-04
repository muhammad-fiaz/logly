# Managing Multiple Sinks

Learn how to add, remove, and manage multiple logging sinks efficiently.

## Overview

Logly allows you to send log messages to multiple destinations (sinks) simultaneously. This guide demonstrates how to manage these sinks dynamically at runtime.

## Basic Sink Management

### Adding Multiple Sinks

```python
from logly import logger

# Configure logger
logger.configure(level="INFO", console=False)

# Add multiple file sinks
app_log = logger.add("logs/app.log")
error_log = logger.add("logs/errors.log", filter_min_level="ERROR")
debug_log = logger.add("logs/debug.log", filter_min_level="DEBUG")

# Log to all sinks
logger.info("Application started")
logger.error("Something went wrong")
logger.debug("Debug information")

# Ensure all logs are written
logger.complete()
```

### Removing Specific Sinks

```python
from logly import logger

# Add sinks and store their IDs
app_handler = logger.add("logs/app.log")
error_handler = logger.add("logs/errors.log")

logger.info("Logged to both files")

# Remove one specific sink
logger.remove(error_handler)

# This only goes to app.log now
logger.error("Only in app.log")

logger.complete()
```

### Removing All Sinks

The `remove_all()` method provides a quick way to clear all logging outputs:

```python
from logly import logger

# Set up multiple sinks
logger.add("logs/app.log")
logger.add("logs/errors.log")
logger.add("logs/debug.log")

logger.info("Message to all three files")

# Remove all sinks at once
count = logger.remove_all()
print(f"Removed {count} sinks")  # Output: Removed 3 sinks

# No output anywhere now
logger.info("This goes nowhere")

logger.complete()
```

## Real-World Examples

### Environment-Based Configuration

Switch logging configuration based on environment:

```python
from logly import logger
import os

def setup_logging():
    """Configure logging based on environment."""
    # Clear any existing configuration
    logger.remove_all()
    
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        # Production: JSON logs, daily rotation
        logger.configure(level="WARNING", console=False, json=True)
        logger.add(
            "logs/production.log",
            rotation="daily",
            retention=30,
            async_write=True
        )
        logger.add(
            "logs/errors.log",
            filter_min_level="ERROR",
            rotation="daily",
            retention=90
        )
    
    elif environment == "staging":
        # Staging: Structured logs for testing
        logger.configure(level="INFO", console=True, json=True)
        logger.add(
            "logs/staging.log",
            rotation="daily",
            retention=14
        )
    
    else:
        # Development: Console + file with debug info
        logger.configure(level="DEBUG", console=True, color=True)
        logger.add("logs/dev.log", async_write=True)

# Initialize logging
setup_logging()

# Your application code
logger.info("Application running in %s mode", os.getenv("ENVIRONMENT", "development"))
```

### Dynamic Log File Rotation

Rotate log files programmatically based on custom events:

```python
from logly import logger
from datetime import datetime
import atexit

class LogFileManager:
    """Manages log file rotation and cleanup."""
    
    def __init__(self, base_path="logs"):
        self.base_path = base_path
        self.current_handler = None
        self.rotate_log_file()
        
        # Ensure cleanup on exit
        atexit.register(self.cleanup)
    
    def rotate_log_file(self):
        """Create a new timestamped log file."""
        # Remove current log file sink
        if self.current_handler is not None:
            logger.remove(self.current_handler)
        
        # Create new timestamped file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{self.base_path}/app_{timestamp}.log"
        
        self.current_handler = logger.add(
            log_file,
            async_write=True,
            buffer_size=16384
        )
        
        logger.info(f"Rotated to new log file: {log_file}")
    
    def cleanup(self):
        """Clean up logging on exit."""
        logger.remove_all()
        logger.complete()

# Usage
log_manager = LogFileManager()

# Do some work
logger.info("Processing request 1")
logger.info("Processing request 2")

# Manually rotate when needed (e.g., after 1000 requests)
log_manager.rotate_log_file()

logger.info("Processing request 3")  # Goes to new file
```

### Feature Flag Logging

Enable/disable logging for specific features:

```python
from logly import logger

class FeatureLogger:
    """Manage feature-specific logging outputs."""
    
    def __init__(self):
        self.feature_handlers = {}
    
    def enable_feature(self, feature_name, log_level="DEBUG"):
        """Enable detailed logging for a specific feature."""
        if feature_name not in self.feature_handlers:
            handler = logger.add(
                f"logs/features/{feature_name}.log",
                filter_min_level=log_level,
                async_write=True
            )
            self.feature_handlers[feature_name] = handler
            logger.info(f"Enabled logging for feature: {feature_name}")
    
    def disable_feature(self, feature_name):
        """Disable logging for a specific feature."""
        if feature_name in self.feature_handlers:
            handler = self.feature_handlers.pop(feature_name)
            logger.remove(handler)
            logger.info(f"Disabled logging for feature: {feature_name}")
    
    def disable_all_features(self):
        """Disable all feature-specific logging."""
        for handler in self.feature_handlers.values():
            logger.remove(handler)
        self.feature_handlers.clear()
        logger.info("Disabled all feature logging")

# Usage
feature_logger = FeatureLogger()

# Enable logging for specific features during debugging
feature_logger.enable_feature("authentication")
feature_logger.enable_feature("payment_processing")

# Log with feature context
logger.debug("User login attempt", feature="authentication")
logger.debug("Processing payment", feature="payment_processing")

# Disable when done
feature_logger.disable_feature("authentication")
feature_logger.disable_all_features()
```

### Temporary Debug Logging

Add temporary debug logging that automatically cleans up:

```python
from logly import logger
from contextlib import contextmanager

@contextmanager
def temporary_debug_log(filename):
    """Context manager for temporary debug logging."""
    # Add debug log file
    handler = logger.add(
        filename,
        filter_min_level="DEBUG",
        async_write=False  # Synchronous for immediate output
    )
    
    try:
        logger.debug(f"Started debug logging to {filename}")
        yield handler
    finally:
        # Remove debug log file
        logger.debug(f"Stopping debug logging to {filename}")
        logger.remove(handler)

# Usage
with temporary_debug_log("logs/debug_session.log"):
    logger.debug("Entering critical section")
    logger.debug("Processing data...")
    logger.debug("Validation complete")

# Debug file handler automatically removed
logger.debug("This won't go to debug_session.log")
```

### A/B Testing Logging

Separate logs for A/B test groups:

```python
from logly import logger
import random

class ABTestLogger:
    """Manage separate log files for A/B test variants."""
    
    def __init__(self):
        self.variant_handlers = {}
        logger.remove_all()
        logger.configure(level="INFO", console=False)
    
    def setup_variant(self, variant_name):
        """Set up logging for a test variant."""
        if variant_name not in self.variant_handlers:
            handler = logger.add(
                f"logs/ab_tests/{variant_name}.log",
                json=True,
                async_write=True
            )
            self.variant_handlers[variant_name] = handler
    
    def log_event(self, user_id, event_type, variant, **kwargs):
        """Log an event for a specific test variant."""
        logger.info(
            f"A/B Test Event: {event_type}",
            user_id=user_id,
            variant=variant,
            event=event_type,
            **kwargs
        )
    
    def cleanup(self):
        """Clean up all variant log files."""
        logger.remove_all()
        self.variant_handlers.clear()

# Usage
ab_logger = ABTestLogger()

# Set up variants
ab_logger.setup_variant("control")
ab_logger.setup_variant("variant_a")
ab_logger.setup_variant("variant_b")

# Simulate user sessions
for user_id in range(100):
    variant = random.choice(["control", "variant_a", "variant_b"])
    ab_logger.log_event(user_id, "page_view", variant, page="/landing")
    ab_logger.log_event(user_id, "button_click", variant, button_id="cta")

# Clean up when test is complete
ab_logger.cleanup()
logger.complete()
```

## Testing with remove_all()

### Reset Logging Between Tests

```python
import pytest
from logly import logger

@pytest.fixture(autouse=True)
def reset_logger():
    """Automatically reset logger before and after each test."""
    logger.remove_all()
    logger.reset()
    yield
    logger.remove_all()
    logger.reset()

def test_logging_feature_1(tmp_path):
    """Test with fresh logger state."""
    log_file = tmp_path / "test1.log"
    logger.add(str(log_file))
    logger.info("Test message 1")
    logger.complete()
    
    assert log_file.exists()
    assert "Test message 1" in log_file.read_text()

def test_logging_feature_2(tmp_path):
    """Another test with fresh logger state."""
    log_file = tmp_path / "test2.log"
    logger.add(str(log_file))
    logger.info("Test message 2")
    logger.complete()
    
    assert log_file.exists()
    assert "Test message 2" in log_file.read_text()
```

## Performance Considerations

### Efficient Sink Management

```python
from logly import logger
import time

# Adding many sinks
start = time.perf_counter()
for i in range(100):
    logger.add(f"logs/sink_{i}.log")
add_time = time.perf_counter() - start
print(f"Added 100 sinks in {add_time:.3f}s")

# Removing all sinks efficiently
start = time.perf_counter()
count = logger.remove_all()
remove_time = time.perf_counter() - start
print(f"Removed {count} sinks in {remove_time*1000:.2f}ms")
# Typical output: Removed 100 sinks in <1.00ms
```

### Thread-Safe Operations

All sink management operations are thread-safe:

```python
from logly import logger
import threading

def add_sinks():
    """Add sinks in background thread."""
    for i in range(10):
        logger.add(f"logs/thread_{threading.current_thread().name}_{i}.log")

def remove_all_sinks():
    """Remove all sinks in background thread."""
    count = logger.remove_all()
    print(f"Thread removed {count} sinks")

# Safe concurrent operations
threads = []
for i in range(5):
    t = threading.Thread(target=add_sinks, name=f"Worker-{i}")
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# Safe to call remove_all() from any thread
logger.remove_all()
```

## Best Practices

### 1. Always Store Handler IDs

```python
# Good: Can remove specific sinks
error_handler = logger.add("errors.log")
debug_handler = logger.add("debug.log")

logger.remove(debug_handler)  # Remove only debug log
```

### 2. Use remove_all() for Clean Slate

```python
# When reconfiguring, start fresh
logger.remove_all()
logger.configure(level="INFO")
logger.add("new_config.log")
```

### 3. Call complete() Before Exit

```python
import atexit

def cleanup():
    logger.complete()  # Flush all buffers
    logger.remove_all()  # Clean up sinks

atexit.register(cleanup)
```

### 4. Handle Errors Gracefully

```python
# Logly uses silent failure for robustness
handler = logger.add("app.log")
logger.remove(handler)

# Safe to log even after removal - no errors thrown
logger.info("This is silently ignored")
```

## See Also

- [Sink Management API](../api-reference/sink-management.md) - Complete API reference
- [Configuration Guide](../guides/configuration.md) - Logger configuration
- [Production Deployment](../guides/production-deployment.md) - Production best practices
- [File Rotation Example](file-rotation.md) - Log file rotation strategies
