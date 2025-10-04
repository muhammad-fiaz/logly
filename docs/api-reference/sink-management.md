---
title: Sink Management API - Logly Python Logging
description: Complete professional guide to managing logging sinks in Logly with comprehensive parameters, examples, and best practices.
keywords: python, logging, sink management, api, destinations, configuration, rotation, filtering, logly
---

# Sink Management API Reference

Complete professional guide to managing logging sinks in Logly with comprehensive parameters, examples, and best practices.

---

## Overview

**Sinks** are output destinations for your logs. Logly supports multiple sinks simultaneously, each with independent configuration for rotation, filtering, formatting, and async writing. This allows you to route different log levels to different files, apply custom formats, and optimize performance.

---

## Core Methods

### logger.add()

Add a logging sink (output destination) with optional rotation, filtering, and async writing.

#### Signature

```python
logger.add(
    sink: str | None = None,
    rotation: str | None = None,
    size_limit: str | None = None,
    retention: int | None = None,
    filter_min_level: str | None = None,
    filter_module: str | None = None,
    filter_function: str | None = None,
    async_write: bool = True,
    buffer_size: int = 8192,
    flush_interval: int = 100,
    max_buffered_lines: int = 1000,
    date_style: str | None = None,
    date_enabled: bool = False,
    format: str | None = None,
    json: bool = False
) -> int
```

#### Parameters Table

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sink` | `str \| None` | `None` | Output destination: `"console"` for stdout or file path (e.g., `"app.log"`, `"logs/error.log"`). If `None`, defaults to console output. |
| `rotation` | `str \| None` | `None` | Time-based rotation policy: `"daily"` (rotate at midnight), `"hourly"` (rotate every hour), `"minutely"` (rotate every minute), or `"never"` (no time-based rotation). |
| `size_limit` | `str \| None` | `None` | Size-based rotation threshold. Supports units: `"B"` (bytes), `"KB"` (kilobytes), `"MB"` (megabytes), `"GB"` (gigabytes). Examples: `"500B"`, `"5KB"`, `"10MB"`, `"1GB"`. When file reaches this size, it rotates to a timestamped archive. |
| `retention` | `int \| None` | `None` | Number of rotated files to retain. Older files beyond this count are automatically deleted. Example: `retention=7` keeps last 7 rotated files. |
| `filter_min_level` | `str \| None` | `None` | Minimum log level for this sink. Only messages at or above this level are logged. Levels: `"TRACE"`, `"DEBUG"`, `"INFO"`, `"SUCCESS"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`. |
| `filter_module` | `str \| None` | `None` | Filter logs by module name. Only logs from the specified module are written to this sink. Example: `"app.auth"`, `"myapp.database"`. |
| `filter_function` | `str \| None` | `None` | Filter logs by function name. Only logs from the specified function are written to this sink. Example: `"request_handler"`, `"process_payment"`. |
| `async_write` | `bool` | `True` | Enable asynchronous (non-blocking) writing. When `True`, log writes happen in a background thread for better performance. When `False`, writes are synchronous (blocking). |
| `buffer_size` | `int` | `8192` | Buffer size in bytes for async writing. Larger buffers improve throughput but use more memory. Default: 8KB. Range: 1024-65536 bytes. |
| `flush_interval` | `int` | `100` | Flush interval in milliseconds for async writing. Buffered logs are written to disk at this interval. Lower values reduce latency, higher values improve throughput. Default: 100ms. |
| `max_buffered_lines` | `int` | `1000` | Maximum number of lines to buffer before forcing a flush. Prevents excessive memory usage during log bursts. Default: 1000 lines. |
| `date_style` | `str \| None` | `None` | Timestamp format style: `"rfc3339"` (ISO 8601), `"local"` (local timezone), `"utc"` (UTC timezone). If `None`, uses default format. |
| `date_enabled` | `bool` | `False` | Include timestamps in log output. When `True`, each log line includes a timestamp prefix. When `False`, no timestamp is added. |
| `format` | `str \| None` | `None` | Custom format string with placeholders. Available placeholders: `{time}`, `{level}`, `{message}`, `{module}`, `{function}`, `{filename}`, `{lineno}`, `{extra}`, or any custom field from kwargs. Example: `"{time} [{level}] {message}"`. |
| `json` | `bool` | `False` | Output logs in JSON format. When `True`, each log line is a JSON object with fields like `level`, `message`, and any extra fields. |

#### Returns

- **Type:** `int`
- **Description:** Handler ID (unique integer) for this sink. Used with `remove()`, `read()`, `delete()`, and other sink-specific methods.

#### Time-Based Rotation Examples

=== "Daily Rotation"

    ```python
    from logly import logger

    # Rotate at midnight, keep last 7 days
    id = logger.add("app.log", rotation="daily", retention=7)
    
    logger.info("Application started")
    logger.error("Database connection failed", retry=3)
    ```

    **Output Files:**
    ```
    app.log                 # Current day's logs
    app.2025-01-14.log      # Yesterday's logs
    app.2025-01-13.log      # 2 days ago
    ...
    app.2025-01-08.log      # 7 days ago (oldest kept)
    ```

=== "Hourly Rotation"

    ```python
    from logly import logger

    # Rotate every hour, keep last 24 hours
    id = logger.add("app.log", rotation="hourly", retention=24)
    
    logger.info("Hourly checkpoint")
    ```

    **Output Files:**
    ```
    app.log                   # Current hour
    app.2025-01-15-14.log     # 2 PM logs
    app.2025-01-15-13.log     # 1 PM logs
    app.2025-01-15-12.log     # 12 PM logs
    ...
    ```

=== "Minutely Rotation (Testing)"

    ```python
    from logly import logger

    # Rotate every minute, keep last 60 minutes
    id = logger.add("test.log", rotation="minutely", retention=60)
    
    logger.debug("Minutely test log")
    ```

    **Output Files:**
    ```
    test.log                      # Current minute
    test.2025-01-15-14-30.log     # 14:30 logs
    test.2025-01-15-14-29.log     # 14:29 logs
    ...
    ```

#### Size-Based Rotation Examples

=== "10MB Rotation"

    ```python
    from logly import logger

    # Rotate when file reaches 10MB, keep 5 archives
    id = logger.add("app.log", size_limit="10MB", retention=5)
    
    for i in range(100000):
        logger.info(f"Log entry {i}", data="x" * 100)
    ```

    **Output Files:**
    ```
    app.log                         # Current file (up to 10MB)
    app.2025-01-15-14-30-45.log     # Previous rotation
    app.2025-01-15-14-25-12.log     # Earlier rotation
    ...
    ```

    **Behavior:**
    - File grows until reaching 10MB
    - Automatically rotates with timestamp
    - Keeps only 5 most recent archives
    - Older archives auto-deleted

=== "Size Units Reference"

    ```python
    from logly import logger

    # Bytes
    logger.add("tiny.log", size_limit="500B", retention=10)

    # Kilobytes
    logger.add("small.log", size_limit="5KB", retention=20)

    # Megabytes (most common)
    logger.add("app.log", size_limit="50MB", retention=5)

    # Gigabytes (large applications)
    logger.add("bigdata.log", size_limit="2GB", retention=3)
    ```

    **Supported Units:**
    | Unit | Symbol | Bytes |
    |------|--------|-------|
    | Bytes | `B` | 1 |
    | Kilobytes | `KB` | 1,024 |
    | Megabytes | `MB` | 1,048,576 |
    | Gigabytes | `GB` | 1,073,741,824 |

=== "Combined Rotation"

    ```python
    from logly import logger

    # Both time AND size rotation
    # Rotates whichever condition is met first
    id = logger.add(
        "app.log",
        rotation="daily",       # Rotate at midnight
        size_limit="100MB",     # OR when file reaches 100MB
        retention=30            # Keep 30 most recent files
    )
    
    logger.info("Dual rotation strategy active")
    ```

    **Behavior:**
    - Rotates at midnight (time-based)
    - OR rotates when file reaches 100MB (size-based)
    - Whichever happens first triggers rotation
    - Keeps last 30 rotated files total

#### Filtering Examples

=== "Level Filtering"

    ```python
    from logly import logger

    # Error-only sink
    error_id = logger.add("errors.log", filter_min_level="ERROR")

    # Info and above
    app_id = logger.add("app.log", filter_min_level="INFO")

    # Everything (trace and above)
    debug_id = logger.add("debug.log", filter_min_level="TRACE")

    # Now log at different levels
    logger.trace("Trace message")      # Only to debug.log
    logger.debug("Debug message")      # Only to debug.log
    logger.info("Info message")        # To app.log and debug.log
    logger.error("Error message")      # To all three sinks
    ```

    **Log Level Hierarchy:**
    ```
    TRACE < DEBUG < INFO < SUCCESS < WARNING < ERROR < CRITICAL
    ```

    **Output in errors.log:**
    ```
    ERROR: Error message
    ```

    **Output in app.log:**
    ```
    INFO: Info message
    ERROR: Error message
    ```

    **Output in debug.log:**
    ```
    TRACE: Trace message
    DEBUG: Debug message
    INFO: Info message
    ERROR: Error message
    ```

=== "Module Filtering"

    ```python
    from logly import logger

    # Authentication module logs only
    auth_id = logger.add("auth.log", filter_module="app.auth")

    # Database module logs only
    db_id = logger.add("database.log", filter_module="app.database")

    # API module logs only
    api_id = logger.add("api.log", filter_module="app.api")

    # Module name is auto-detected from caller
    logger.info("User login successful", user="alice")  # Goes to auth.log if called from app.auth
    ```

    **Use Cases:**
    - Separate logs by application component
    - Debug specific modules without noise
    - Audit trails for sensitive modules
    - Performance monitoring per module

=== "Function Filtering"

    ```python
    from logly import logger

    # Only logs from payment processing
    payment_id = logger.add("payments.log", filter_function="process_payment")

    # Only logs from authentication handler
    auth_id = logger.add("auth_handler.log", filter_function="authenticate_user")

    # Function name is auto-detected
    def process_payment(amount, user):
        logger.info(f"Processing payment", amount=amount, user=user)
        # This goes to payments.log
    
    process_payment(100.50, "alice")
    ```

    **Output in payments.log:**
    ```
    INFO: Processing payment amount=100.5 user=alice
    ```

=== "Combined Filters"

    ```python
    from logly import logger

    # Error-level logs from auth module only
    id = logger.add(
        "auth_errors.log",
        filter_min_level="ERROR",
        filter_module="app.auth"
    )

    # Critical logs from specific function
    id2 = logger.add(
        "critical_payments.log",
        filter_min_level="CRITICAL",
        filter_function="process_payment"
    )
    ```

#### Async Writing Examples

=== "Default Async Configuration"

    ```python
    from logly import logger

    # Async enabled by default (recommended)
    id = logger.add("app.log", async_write=True)

    # High-throughput logging with zero blocking
    for i in range(10000):
        logger.info(f"Processing item {i}", status="active")
    
    # Main thread continues immediately
    # Background thread handles all file I/O
    ```

    **Benefits:**
    - ✅ Non-blocking: main thread never waits for disk I/O
    - ✅ Better throughput: batched writes to disk
    - ✅ Automatic buffering: intelligent buffer management
    - ✅ Zero performance impact on application code

=== "Custom Async Configuration"

    ```python
    from logly import logger

    # High-volume application with custom async settings
    id = logger.add(
        "high_volume.log",
        async_write=True,
        buffer_size=32768,          # 32KB buffer (4x default)
        flush_interval=500,         # Flush every 500ms (5x default)
        max_buffered_lines=5000     # 5000 lines max (5x default)
    )

    # Can handle massive log bursts
    for i in range(100000):
        logger.info(f"High-volume log {i}")
    ```

    **Configuration Guide:**

    | Scenario | buffer_size | flush_interval | max_buffered_lines |
    |----------|-------------|----------------|-------------------|
    | Low volume (< 100 logs/sec) | 8192 (8KB) | 100ms | 1000 |
    | Medium volume (< 1000 logs/sec) | 16384 (16KB) | 200ms | 2000 |
    | High volume (< 10000 logs/sec) | 32768 (32KB) | 500ms | 5000 |
    | Extreme volume (> 10000 logs/sec) | 65536 (64KB) | 1000ms | 10000 |

=== "Synchronous Writing (Blocking)"

    ```python
    from logly import logger

    # Synchronous writing for critical logs
    id = logger.add("critical.log", async_write=False)

    logger.critical("Payment processed", amount=1000000, user="alice")
    # Guaranteed written to disk before continuing
    ```

    **When to Use Synchronous:**
    - 💰 Financial transactions (immediate persistence)
    - 🔒 Security audit logs (no data loss)
    - 🚨 Critical errors (must be on disk)
    - 🧪 Testing (deterministic behavior)

    **When to Use Async (Default):**
    - 📊 Application logs (high volume)
    - 🐛 Debug logs (performance critical)
    - 📈 Metrics and analytics
    - 🌐 Web request logs

#### JSON Output Examples

=== "Basic JSON Logging"

    ```python
    from logly import logger

    # Enable JSON output
    id = logger.add("data.log", json=True)

    logger.info("User login", user="alice", ip="192.168.1.1", session="abc123")
    logger.error("Database error", code=500, query="SELECT * FROM users")
    ```

    **Output in data.log:**
    ```json
    {"level":"INFO","message":"User login","user":"alice","ip":"192.168.1.1","session":"abc123"}
    {"level":"ERROR","message":"Database error","code":500,"query":"SELECT * FROM users"}
    ```

    **Benefits:**
    - ✅ Machine-readable format
    - ✅ Easy parsing with `jq`, `grep`, or log aggregators
    - ✅ Structured data for analytics
    - ✅ Integration with ELK, Splunk, Datadog

=== "JSON with Timestamps"

    ```python
    from logly import logger

    id = logger.add(
        "events.log",
        json=True,
        date_enabled=True,
        date_style="rfc3339"
    )

    logger.info("Event occurred", event="user_signup", tier="premium")
    ```

    **Output:**
    ```json
    {"timestamp":"2025-01-15T14:30:45.123Z","level":"INFO","message":"Event occurred","event":"user_signup","tier":"premium"}
    ```

=== "NDJSON (Newline Delimited JSON)"

    ```python
    from logly import logger

    # Perfect for streaming and log aggregation
    id = logger.add("stream.log", json=True)

    for event in events:
        logger.info("Event", type=event.type, data=event.data)
    ```

    **Output Format (NDJSON):**
    ```json
    {"level":"INFO","message":"Event","type":"click","data":"button_1"}
    {"level":"INFO","message":"Event","type":"pageview","data":"/home"}
    {"level":"INFO","message":"Event","type":"purchase","data":"item_42"}
    ```

    **Processing with jq:**
    ```bash
    # Filter by event type
    cat stream.log | jq 'select(.type == "purchase")'

    # Extract specific fields
    cat stream.log | jq '{type: .type, data: .data}'
    ```

#### Custom Format Examples

=== "Basic Custom Format"

    ```python
    from logly import logger

    # Simple format with time, level, and message
    id = logger.add(
        "simple.log",
        format="{time} [{level}] {message}"
    )

    logger.info("Application started", version="1.0.0")
    logger.error("Connection failed", service="database")
    ```

    **Output:**
    ```
    2025-01-15T14:30:45Z [INFO] Application started version=1.0.0
    2025-01-15T14:30:46Z [ERROR] Connection failed service=database
    ```

=== "Detailed Format with Caller Info"

    ```python
    from logly import logger

    # Include module, function, filename, and line number
    id = logger.add(
        "debug.log",
        format="{time} [{level}] {message} - {module}:{function} ({filename}:{lineno})"
    )

    logger.debug("Processing request", request_id="abc123")
    ```

    **Output:**
    ```
    2025-01-15T14:30:45Z [DEBUG] Processing request request_id=abc123 - app.api:handle_request (api.py:42)
    ```

=== "Minimal Format"

    ```python
    from logly import logger

    # Just level and message
    id = logger.add("minimal.log", format="{level}: {message}")

    logger.info("User logged in", user="alice")
    logger.error("Payment failed", amount=100.50)
    ```

    **Output:**
    ```
    INFO: User logged in user=alice
    ERROR: Payment failed amount=100.5
    ```

=== "Custom Field Placeholders"

    ```python
    from logly import logger

    # Include specific extra fields in format
    id = logger.add(
        "requests.log",
        format="{time} | {level} | {message} | user={user} request_id={request_id}"
    )

    logger.info("API request", user="alice", request_id="xyz789", endpoint="/api/users")
    ```

    **Output:**
    ```
    2025-01-15T14:30:45Z | INFO | API request | user=alice request_id=xyz789 endpoint=/api/users
    ```

**Available Format Placeholders:**

| Placeholder | Description | Example Output |
|-------------|-------------|----------------|
| `{time}` | ISO 8601 timestamp | `2025-01-15T14:30:45.123Z` |
| `{level}` | Log level name | `INFO`, `ERROR`, `DEBUG` |
| `{message}` | Log message text | `User logged in` |
| `{module}` | Module name | `app.auth` |
| `{function}` | Function name | `authenticate_user` |
| `{filename}` | Source filename | `api.py` |
| `{lineno}` | Line number | `42` |
| `{extra}` | All extra fields as `key=value` | `user=alice session=abc123` |
| `{any_key}` | Specific extra field | `{user}` → `alice` |

---

### logger.remove()

Remove a logging sink by its handler ID.

#### Signature

```python
logger.remove(handler_id: int) -> bool
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `handler_id` | `int` | Handler ID returned by `add()`. Unique identifier for the sink to remove. |

#### Returns

- **Type:** `bool`
- **Description:** `True` if sink was successfully removed, `False` if handler ID not found.

#### Examples

=== "Remove Single Sink"

    ```python
    from logly import logger

    # Add sink
    handler_id = logger.add("temp.log")
    logger.info("Temporary message")

    # Remove sink
    success = logger.remove(handler_id)
    print(f"Removed: {success}")  # Output: Removed: True

    # Subsequent logs don't go to temp.log
    logger.info("Not logged to temp.log")
    ```

=== "Remove Specific Sinks from List"

    ```python
    from logly import logger

    app_id = logger.add("app.log")
    error_id = logger.add("errors.log")
    debug_id = logger.add("debug.log")

    # Keep app.log, remove others
    logger.remove(error_id)
    logger.remove(debug_id)

    logger.info("Only in app.log")
    ```

=== "Error Handling"

    ```python
    from logly import logger

    # Try removing non-existent sink
    success = logger.remove(999)
    if not success:
        logger.warning("Sink not found")
    ```

#### Do's and Don'ts

✅ **DO:**
- Store handler IDs for later removal
- Check return value to confirm removal
- Remove temporary sinks when done

❌ **DON'T:**
- Remove sinks while async writes are pending (call `complete()` first)
- Remove sinks in loops without tracking IDs
- Assume removal succeeded without checking return value

---

### logger.remove_all()

Remove all logging sinks at once.

#### Signature

```python
logger.remove_all() -> int
```

#### Parameters

None

#### Returns

- **Type:** `int`
- **Description:** Number of sinks removed (count of active sinks before removal).

#### Examples

=== "Basic Cleanup"

    ```python
    from logly import logger

    logger.add("app.log")
    logger.add("error.log")
    logger.add("debug.log")

    logger.info("Some logs")

    # Remove all sinks
    count = logger.remove_all()
    print(f"Removed {count} sinks")  # Output: Removed 3 sinks
    ```

=== "Test Teardown"

    ```python
    import pytest
    from logly import logger

    @pytest.fixture(autouse=True)
    def cleanup_logs():
        yield
        # Clean up all sinks after each test
        logger.complete()       # Flush pending writes
        logger.delete_all()     # Delete files
        logger.remove_all()     # Remove sinks
    ```

=== "Dynamic Reconfiguration"

    ```python
    from logly import logger

    def reconfigure_logging(environment):
        # Remove all existing sinks
        logger.remove_all()
        
        # Add new configuration
        if environment == "production":
            logger.add("app.log", rotation="daily", retention=30)
            logger.add("errors.log", filter_min_level="ERROR")
        else:
            logger.add("console")
            logger.add("debug.log", filter_min_level="DEBUG")

    reconfigure_logging("production")
    ```

#### Use Cases

- 🧹 **Cleanup:** Remove all sinks before shutdown
- 🧪 **Testing:** Reset logging state between tests
- 🔄 **Reconfiguration:** Clear and re-add sinks with new settings
- 🔧 **Dynamic Management:** Switch logging strategies at runtime

#### Do's and Don'ts

✅ **DO:**
- Call `complete()` before removing to flush async writes
- Use in test cleanup/teardown
- Combine with `delete_all()` for full cleanup

❌ **DON'T:**
- Call in production without reconfiguring sinks
- Remove all sinks without adding replacements
- Use during active logging without flushing

---

### logger.sink_count()

Get the number of active logging sinks.

#### Signature

```python
logger.sink_count() -> int
```

#### Parameters

None

#### Returns

- **Type:** `int`
- **Description:** Total number of currently active sinks (including console and file sinks).

#### Examples

=== "Check Sink Count"

    ```python
    from logly import logger

    logger.add("app.log")
    logger.add("error.log")

    count = logger.sink_count()
    print(f"Active sinks: {count}")  # Output: Active sinks: 2
    ```

=== "Conditional Sink Addition"

    ```python
    from logly import logger

    # Ensure at least one sink is configured
    if logger.sink_count() == 0:
        logger.add("console")
        logger.warning("No sinks found, added console sink")
    ```

=== "Monitor Sink Health"

    ```python
    from logly import logger

    def check_logging_health():
        count = logger.sink_count()
        if count == 0:
            logger.add("fallback.log")
            print("WARNING: No sinks configured, added fallback")
        elif count > 10:
            print(f"WARNING: Too many sinks ({count}), may impact performance")
        else:
            print(f"✓ Logging healthy: {count} sinks active")

    check_logging_health()
    ```

#### Use Cases

- ✅ **Health Checks:** Verify logging is configured
- ✅ **Debugging:** Troubleshoot missing log output
- ✅ **Monitoring:** Track sink configuration
- ✅ **Validation:** Ensure expected sinks are active

---

### logger.list_sinks()

List all active sink handler IDs.

#### Signature

```python
logger.list_sinks() -> list[int]
```

#### Parameters

None

#### Returns

- **Type:** `list[int]`
- **Description:** List of handler IDs for all active sinks. Returns empty list if no sinks configured.

#### Examples

=== "List All Sinks"

    ```python
    from logly import logger

    id1 = logger.add("app.log")
    id2 = logger.add("error.log")
    id3 = logger.add("debug.log")

    ids = logger.list_sinks()
    print(f"Sink IDs: {ids}")  # Output: Sink IDs: [1, 2, 3]
    ```

=== "Iterate and Process Sinks"

    ```python
    from logly import logger

    logger.add("app.log", rotation="daily")
    logger.add("error.log", filter_min_level="ERROR")
    logger.add("debug.log", filter_min_level="DEBUG")

    # Process each sink
    for sink_id in logger.list_sinks():
        info = logger.sink_info(sink_id)
        print(f"Sink {sink_id}: {info['path']}")
    ```

    **Output:**
    ```
    Sink 1: app.log
    Sink 2: error.log
    Sink 3: debug.log
    ```

=== "Selective Removal"

    ```python
    from logly import logger

    app_id = logger.add("app.log")
    error_id = logger.add("errors.log")
    debug_id = logger.add("debug.log")

    # Remove all except app.log
    for sink_id in logger.list_sinks():
        if sink_id != app_id:
            logger.remove(sink_id)

    print(f"Remaining sinks: {logger.list_sinks()}")  # [1]
    ```

#### Use Cases

- 🔍 **Inspection:** See what sinks are active
- 🔄 **Iteration:** Process all sinks programmatically
- 🎯 **Selective Operations:** Remove/modify specific sinks
- 📊 **Debugging:** Verify expected sinks exist

---

### logger.sink_info()

Get detailed information about a specific sink.

#### Signature

```python
logger.sink_info(handler_id: int) -> dict | None
```

#### Parameters Table

| Parameter | Type | Description |
|-----------|------|-------------|
| `handler_id` | `int` | Handler ID of the sink to query (returned by `add()`). |

#### Returns

- **Type:** `dict | None`
- **Description:** Dictionary with sink configuration details, or `None` if handler ID not found.

#### Response Fields Table

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Handler ID |
| `path` | `str` | File path or `"console"` |
| `rotation` | `str | None` | Rotation policy (`"daily"`, `"hourly"`, `"minutely"`, `None`) |
| `size_limit` | `str | None` | Size rotation limit (e.g., `"10MB"`, `None`) |
| `retention` | `int | None` | Number of files to retain |
| `filter_min_level` | `str | None` | Minimum log level filter |
| `filter_module` | `str | None` | Module name filter |
| `filter_function` | `str | None` | Function name filter |
| `async_write` | `bool` | Async writing enabled |
| `buffer_size` | `int` | Buffer size in bytes |
| `flush_interval` | `int` | Flush interval in milliseconds |
| `max_buffered_lines` | `int` | Maximum buffered lines |
| `format` | `str | None` | Custom format string |
| `json` | `bool` | JSON output enabled |
| `date_enabled` | `bool` | Timestamps enabled |
| `date_style` | `str | None` | Timestamp format style |

#### Examples

=== "Basic Sink Info"

    ```python
    from logly import logger

    id = logger.add("app.log", rotation="daily", retention=7)
    
    info = logger.sink_info(id)
    print(f"Path: {info['path']}")           # app.log
    print(f"Rotation: {info['rotation']}")   # daily
    print(f"Retention: {info['retention']}") # 7
    ```

=== "Inspect All Sink Properties"

    ```python
    from logly import logger

    id = logger.add(
        "app.log",
        rotation="daily",
        size_limit="10MB",
        retention=7,
        filter_min_level="INFO",
        async_write=True,
        buffer_size=16384,
        json=True
    )

    info = logger.sink_info(id)
    for key, value in info.items():
        print(f"{key}: {value}")
    ```

    **Output:**
    ```
    id: 1
    path: app.log
    rotation: daily
    size_limit: 10MB
    retention: 7
    filter_min_level: INFO
    filter_module: None
    filter_function: None
    async_write: True
    buffer_size: 16384
    flush_interval: 100
    max_buffered_lines: 1000
    format: None
    json: True
    date_enabled: False
    date_style: None
    ```

=== "Error Handling"

    ```python
    from logly import logger

    info = logger.sink_info(999)  # Non-existent ID
    if info is None:
        logger.error("Sink not found")
    else:
        logger.info(f"Found sink: {info['path']}")
    ```

#### Use Cases

- 📋 **Inspection:** View sink configuration
- 🐛 **Debugging:** Verify sink settings
- 📊 **Monitoring:** Track sink properties
- ✅ **Validation:** Confirm expected configuration

---

### logger.all_sinks_info()

Get detailed information about all active sinks.

#### Signature

```python
logger.all_sinks_info() -> list[dict]
```

#### Parameters

None

#### Returns

- **Type:** `list[dict]`
- **Description:** List of dictionaries, each containing sink configuration details (same format as `sink_info()`). Returns empty list if no sinks configured.

#### Examples

=== "View All Sinks"

    ```python
    from logly import logger

    logger.add("app.log", rotation="daily", retention=7)
    logger.add("errors.log", filter_min_level="ERROR", json=True)
    logger.add("debug.log", filter_min_level="DEBUG")

    all_sinks = logger.all_sinks_info()
    for sink in all_sinks:
        print(f"\nSink {sink['id']}:")
        print(f"  Path: {sink['path']}")
        print(f"  Rotation: {sink['rotation']}")
        print(f"  JSON: {sink['json']}")
    ```

    **Output:**
    ```
    Sink 1:
      Path: app.log
      Rotation: daily
      JSON: False

    Sink 2:
      Path: errors.log
      Rotation: None
      JSON: True

    Sink 3:
      Path: debug.log
      Rotation: None
      JSON: False
    ```

=== "Generate Sink Summary Report"

    ```python
    from logly import logger

    logger.add("app.log", rotation="daily", async_write=True)
    logger.add("errors.log", filter_min_level="ERROR", size_limit="50MB")
    logger.add("data.log", json=True, async_write=True)

    print("=== Logging Configuration ===")
    for sink in logger.all_sinks_info():
        print(f"\n📁 {sink['path']}")
        if sink['rotation']:
            print(f"   🔄 Rotation: {sink['rotation']}")
        if sink['size_limit']:
            print(f"   📏 Size limit: {sink['size_limit']}")
        if sink['filter_min_level']:
            print(f"   🎯 Min level: {sink['filter_min_level']}")
        if sink['json']:
            print(f"   📋 Format: JSON")
        if sink['async_write']:
            print(f"   ⚡ Async: enabled (buffer: {sink['buffer_size']} bytes)")
    ```

    **Output:**
    ```
    === Logging Configuration ===

    📁 app.log
       🔄 Rotation: daily
       ⚡ Async: enabled (buffer: 8192 bytes)

    📁 errors.log
       📏 Size limit: 50MB
       🎯 Min level: ERROR

    📁 data.log
       📋 Format: JSON
       ⚡ Async: enabled (buffer: 8192 bytes)
    ```

=== "Export Configuration to JSON"

    ```python
    from logly import logger
    import json

    logger.add("app.log", rotation="daily", retention=7)
    logger.add("errors.log", filter_min_level="ERROR")

    # Export configuration
    config = logger.all_sinks_info()
    with open("logging_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("Configuration exported to logging_config.json")
    ```

#### Use Cases

- 📊 **Monitoring:** Dashboard of all sinks
- 🔍 **Debugging:** Verify entire logging setup
- 💾 **Export:** Save configuration for documentation
- ✅ **Validation:** Ensure all expected sinks configured

---

## Multi-Sink Configuration

### Complete Production Example

```python
from logly import logger

# Configure global settings
logger.configure(level="INFO", color=True, show_time=True)

# 1. Console sink for development visibility
console_id = logger.add("console")

# 2. Main application log (daily rotation, 30-day retention)
app_id = logger.add(
    "logs/app.log",
    rotation="daily",
    retention=30,
    date_enabled=True,
    date_style="rfc3339",
    async_write=True
)

# 3. Error log (size-based rotation, higher retention)
error_id = logger.add(
    "logs/errors.log",
    filter_min_level="ERROR",
    size_limit="50MB",
    retention=90,
    date_enabled=True
)

# 4. Debug log (hourly rotation, short retention)
debug_id = logger.add(
    "logs/debug.log",
    filter_min_level="DEBUG",
    rotation="hourly",
    retention=24
)

# 5. JSON events log for analytics
events_id = logger.add(
    "logs/events.log",
    json=True,
    async_write=True,
    buffer_size=32768,
    rotation="daily",
    retention=365
)

# 6. Authentication audit log (module-filtered)
auth_id = logger.add(
    "logs/auth_audit.log",
    filter_module="app.auth",
    filter_min_level="INFO",
    date_enabled=True
)

# 7. Performance monitoring log (custom format)
perf_id = logger.add(
    "logs/performance.log",
    format="{time} | {level} | {message} | duration_ms={duration}",
    filter_min_level="INFO"
)

# Now log to appropriate sinks
logger.info("Application started", version="2.0.0", environment="production")
logger.error("Database connection failed", service="postgres", retry=3)
logger.debug("Cache hit", key="user:123", value="cached_data")

# Structured event logging
logger.info("User event", event_type="signup", user_id=42, tier="premium")

# Cleanup before shutdown
logger.complete()  # Flush all async writes
```

**Resulting File Structure:**
```
logs/
├── app.log              # All INFO+ logs, daily rotation
├── app.2025-01-14.log   # Previous day
├── errors.log           # ERROR+ only, size-based rotation
├── debug.log            # DEBUG+ logs, hourly rotation
├── debug.2025-01-15-14.log
├── events.log           # JSON format, annual retention
├── auth_audit.log       # Auth module only
└── performance.log      # Custom format with metrics
```

---

## Best Practices

### ✅ DO's

| Practice | Example | Benefit |
|----------|---------|---------|
| **Use multiple sinks for different purposes** | App logs, error logs, audit logs, debug logs | Organized logging strategy |
| **Enable async writing for high-throughput** | `async_write=True, buffer_size=32768` | Better performance, non-blocking I/O |
| **Configure retention to manage disk space** | `retention=7` for debug, `retention=365` for audit | Automatic cleanup, compliance |
| **Use level filtering to reduce noise** | `filter_min_level="ERROR"` for production | Focus on important logs |
| **Rotate logs by time or size** | `rotation="daily"` or `size_limit="100MB"` | Manageable file sizes |
| **Use JSON for machine-readable logs** | `json=True` for analytics, monitoring | Easy parsing and analysis |
| **Store handler IDs for later removal** | `id = logger.add(...); logger.remove(id)` | Clean resource management |
| **Call `complete()` before shutdown** | `logger.complete()` before `sys.exit()` | Flush pending async writes |
| **Use module/function filters for debugging** | `filter_module="app.auth"` | Isolate specific components |
| **Monitor sink health with `sink_count()`** | Check count > 0 before critical logging | Ensure logging is active |

### ❌ DON'Ts

| Anti-Pattern | Why It's Bad | Better Approach |
|--------------|--------------|-----------------|
| **Too many sinks (> 20)** | Performance overhead, resource waste | Consolidate with filters |
| **Synchronous writing for high-volume** | Blocks application, poor performance | Use `async_write=True` |
| **No retention limits** | Disk fills up, manual cleanup needed | Set `retention` appropriately |
| **Logging everything to one file** | Hard to find specific logs | Use multiple filtered sinks |
| **Removing sinks without flushing** | Data loss from pending async writes | Call `complete()` first |
| **Hardcoded file paths** | Not portable, deployment issues | Use configuration files |
| **No rotation on production logs** | Massive files, performance degradation | Use `rotation` or `size_limit` |
| **Forgetting to remove test sinks** | Resource leaks in tests | Use `remove_all()` in teardown |
| **Using plain text for analytics** | Hard to parse, inefficient queries | Use `json=True` |
| **No error log separation** | Errors buried in noise | Dedicated `filter_min_level="ERROR"` sink |

---

## Common Patterns

### Pattern 1: Three-Tier Logging Strategy

```python
from logly import logger

# Tier 1: Console (development visibility)
logger.add("console")

# Tier 2: Application logs (operational monitoring)
logger.add("app.log", rotation="daily", retention=7, filter_min_level="INFO")

# Tier 3: Error logs (incident response)
logger.add("errors.log", filter_min_level="ERROR", retention=30)
```

**Use Case:** Standard production setup with clear separation of concerns.

---

### Pattern 2: Environment-Based Configuration

```python
import os
from logly import logger

def setup_logging():
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        # Production: file-only, errors emphasized
        logger.add("app.log", rotation="daily", retention=30, filter_min_level="INFO")
        logger.add("errors.log", filter_min_level="ERROR", retention=90)
        logger.add("audit.log", json=True, rotation="daily", retention=365)
    
    elif env == "staging":
        # Staging: console + files, more verbose
        logger.add("console")
        logger.add("staging.log", rotation="daily", retention=7, filter_min_level="DEBUG")
        logger.add("errors.log", filter_min_level="ERROR")
    
    else:  # development
        # Development: console only, max verbosity
        logger.add("console")
        logger.add("dev.log", filter_min_level="TRACE")

setup_logging()
```

**Use Case:** Different logging strategies per deployment environment.

---

### Pattern 3: Module-Specific Debugging

```python
from logly import logger

# General application logs
logger.add("app.log", filter_min_level="INFO")

# Deep debugging for specific module
logger.add(
    "auth_debug.log",
    filter_module="app.auth",
    filter_min_level="TRACE",
    rotation="hourly",
    retention=6
)

# Production: logs from app.auth go to both app.log (INFO+) and auth_debug.log (TRACE+)
```

**Use Case:** Debug production issues in specific modules without overwhelming logs.

---

### Pattern 4: High-Performance Async Logging

```python
from logly import logger

# High-volume application with optimized async settings
logger.add(
    "high_volume.log",
    async_write=True,
    buffer_size=65536,          # 64KB buffer
    flush_interval=1000,        # Flush every 1 second
    max_buffered_lines=10000,   # 10K line buffer
    rotation="daily",
    retention=7
)

# Can handle 10,000+ logs/sec without blocking
for i in range(100000):
    logger.info(f"Processing transaction {i}", amount=100.50)
```

**Use Case:** High-throughput applications (web servers, data pipelines, real-time systems).

---

## See Also

- **[File Operations API](file-operations.md)** - Read, delete, and manage log files
- **[Complete API Reference](complete-reference.md)** - Full method documentation
- **[Configuration Guide](../guides/configuration.md)** - Detailed configuration options
- **[Multi-Sink Example](../examples/multi-sink.md)** - Practical multi-sink setup
- **[Production Deployment](../guides/production-deployment.md)** - Production best practices
