---
title: File Operations Examples - Logly Python Logging
description: Practical examples demonstrating how to use Logly's file operation features for monitoring, analysis, and log management.
keywords: python, logging, examples, file operations, monitoring, analysis, management, logly
---

# File Operations Examples

Practical examples demonstrating how to use Logly's file operation features for monitoring, analysis, and log management.

---

## Log File Monitoring

Monitor log file growth and get real-time statistics.

```python
import logly
import time

logger = logly.Logger()
sink_id = logger.add("app.log")

# Initial state
initial_size = logger.file_size(sink_id)
print(f"Initial log size: {initial_size} bytes")

# Write some logs
for i in range(50):
    logger.info(f"Processing record {i}")
    time.sleep(0.1)

# Check growth
final_size = logger.file_size(sink_id)
growth = final_size - initial_size
print(f"Log grew by {growth} bytes ({final_size} total)")

# Get full metadata
metadata = logger.file_metadata(sink_id)
print(f"\nLog File Information:")
print(f"  Path: {metadata['path']}")
print(f"  Created: {metadata['created']}")
print(f"  Modified: {metadata['modified']}")
print(f"  Size: {metadata['size']} bytes")

# Count entries
count = logger.line_count(sink_id)
print(f"  Total entries: {count}")
```

**Output:**

```
Initial log size: 0 bytes
Log grew by 1250 bytes (1250 total)

Log File Information:
  Path: E:\Projects\myapp\app.log
  Created: 2024-01-15T10:00:00Z
  Modified: 2024-01-15T10:05:00Z
  Size: 1250 bytes
  Total entries: 50
```

---

## Log Pagination

Display logs page-by-page with navigation controls.

```python
import logly

logger = logly.Logger()
sink_id = logger.add("app.log")

# Generate sample logs
for i in range(1, 101):
    logger.info(f"Log entry {i}")

def display_page(sink_id, page_num, page_size=10):
    """Display a specific page of logs."""
    total_lines = logger.line_count(sink_id)
    total_pages = (total_lines + page_size - 1) // page_size
    
    if page_num < 1 or page_num > total_pages:
        print("Invalid page number")
        return
    
    start = (page_num - 1) * page_size + 1
    end = min(start + page_size - 1, total_lines)
    
    lines = logger.read_lines(sink_id, start, end)
    
    print(f"\n{'='*60}")
    print(f"Page {page_num}/{total_pages} (Lines {start}-{end} of {total_lines})")
    print(f"{'='*60}")
    print(lines)
    print(f"{'='*60}\n")

# Display different pages
display_page(sink_id, 1)   # First page
display_page(sink_id, 5)   # Middle page
display_page(sink_id, 10)  # Last page
```

**Output:**

```
============================================================
Page 1/10 (Lines 1-10 of 100)
============================================================
Log entry 1
Log entry 2
...
Log entry 10
============================================================

============================================================
Page 5/10 (Lines 41-50 of 100)
============================================================
Log entry 41
Log entry 42
...
Log entry 50
============================================================
```

---

## Recent Logs Display

Show the most recent log entries.

```python
import logly

logger = logly.Logger()
sink_id = logger.add("server.log")

# Simulate server activity
logger.info("Server started")
logger.info("Database connected")
logger.warn("High CPU usage detected")
logger.error("Failed to send email")
logger.info("Request processed successfully")

# Get last 3 log entries
recent = logger.read_lines(sink_id, -3, -1)
print("Most recent logs:")
print(recent)

# Get last log only
last_log = logger.read_lines(sink_id, -1, -1)
print(f"\nLast log entry: {last_log}")
```

**Output:**

```
Most recent logs:
[WARN] High CPU usage detected
[ERROR] Failed to send email
[INFO] Request processed successfully

Last log entry: [INFO] Request processed successfully
```

---

## JSON Log Analysis

Parse and analyze structured JSON logs.

```python
import logly
import json

logger = logly.Logger()
sink_id = logger.add("events.json", json=True)

# Log structured events
logger.info("User login", extra={
    "user_id": "alice123",
    "ip": "192.168.1.10",
    "success": True
})

logger.warn("Failed login attempt", extra={
    "user_id": "bob456",
    "ip": "192.168.1.20",
    "success": False,
    "reason": "invalid_password"
})

logger.info("User logout", extra={
    "user_id": "alice123",
    "duration": 3600
})

# Read and parse JSON logs
json_str = logger.read_json(sink_id, pretty=False)
events = json.loads(json_str)

print(f"Total events: {len(events)}")

# Analyze events
success_count = sum(1 for e in events if e.get("success") == True)
failed_count = sum(1 for e in events if e.get("success") == False)

print(f"Successful logins: {success_count}")
print(f"Failed logins: {failed_count}")

# Pretty print for debugging
print("\nPretty JSON:")
json_pretty = logger.read_json(sink_id, pretty=True)
print(json_pretty)
```

**Output:**

```
Total events: 3
Successful logins: 1
Failed logins: 1

Pretty JSON:
[
  {
    "level": "INFO",
    "message": "User login",
    "user_id": "alice123",
    "ip": "192.168.1.10",
    "success": true
  },
  {
    "level": "WARN",
    "message": "Failed login attempt",
    "user_id": "bob456",
    "ip": "192.168.1.20",
    "success": false,
    "reason": "invalid_password"
  },
  {
    "level": "INFO",
    "message": "User logout",
    "user_id": "alice123",
    "duration": 3600
  }
]
```

---

## NDJSON Processing

Work with newline-delimited JSON logs.

```python
import logly
import json

logger = logly.Logger()
sink_id = logger.add("stream.ndjson", json=True)

# Log multiple events
for i in range(5):
    logger.info(f"Event {i}", extra={"event_id": i, "timestamp": f"2024-01-15T10:{i:02d}:00Z"})

# Read as NDJSON
ndjson_str = logger.read_json(sink_id, pretty=False)
events = json.loads(ndjson_str)

# Process each event
print("Event Summary:")
for event in events:
    event_id = event.get("event_id", "N/A")
    timestamp = event.get("timestamp", "N/A")
    message = event.get("message", "N/A")
    print(f"  [{event_id}] {timestamp} - {message}")
```

**Output:**

```
Event Summary:
  [0] 2024-01-15T10:00:00Z - Event 0
  [1] 2024-01-15T10:01:00Z - Event 1
  [2] 2024-01-15T10:02:00Z - Event 2
  [3] 2024-01-15T10:03:00Z - Event 3
  [4] 2024-01-15T10:04:00Z - Event 4
```

---

## Log File Cleanup Checker

Check if log files need rotation or cleanup based on size.

```python
import logly

logger = logly.Logger()
sink_id = logger.add("app.log")

# Simulate logging
for i in range(1000):
    logger.info(f"Operation {i} completed successfully")

# Check file size
size_bytes = logger.file_size(sink_id)
size_kb = size_bytes / 1024
size_mb = size_kb / 1024

print(f"Current log file size: {size_bytes} bytes ({size_mb:.2f} MB)")

# Determine if rotation needed
MAX_SIZE_MB = 5
if size_mb > MAX_SIZE_MB:
    print(f"⚠️  Warning: Log file exceeds {MAX_SIZE_MB} MB")
    print("Consider enabling log rotation or archiving old logs")
else:
    remaining = MAX_SIZE_MB - size_mb
    print(f"✓ Log file size OK ({remaining:.2f} MB remaining)")

# Show metadata
metadata = logger.file_metadata(sink_id)
print(f"\nFile details:")
print(f"  Created: {metadata['created']}")
print(f"  Modified: {metadata['modified']}")
print(f"  Path: {metadata['path']}")
```

**Output:**

```
Current log file size: 45000 bytes (0.04 MB)
✓ Log file size OK (4.96 MB remaining)

File details:
  Created: 2024-01-15T09:00:00Z
  Modified: 2024-01-15T10:30:00Z
  Path: E:\Projects\myapp\app.log
```

---

## Search Within Date Range

Find logs within a specific line range based on date.

```python
import logly
from datetime import datetime, timedelta

logger = logly.Logger()
sink_id = logger.add("app.log")

# Log with timestamps
base_time = datetime.now()
for i in range(24):
    log_time = base_time + timedelta(hours=i)
    logger.info(f"Event at hour {i}", extra={"timestamp": log_time.isoformat()})

# Get total count
total = logger.line_count(sink_id)
print(f"Total logs: {total}")

# Read first 5 hours
first_5_hours = logger.read_lines(sink_id, 1, 5)
print(f"\nFirst 5 hours:")
print(first_5_hours)

# Read last 3 hours
last_3_hours = logger.read_lines(sink_id, -3, -1)
print(f"\nLast 3 hours:")
print(last_3_hours)

# Read middle 4 hours (hours 10-13)
middle = logger.read_lines(sink_id, 10, 13)
print(f"\nHours 10-13:")
print(middle)
```

---

## Multi-File Monitoring

Monitor multiple log files simultaneously.

```python
import logly

logger = logly.Logger()

# Create multiple log files
app_sink = logger.add("app.log")
error_sink = logger.add("errors.log")
access_sink = logger.add("access.log")

# Write to different sinks
logger.info("Application started")  # Goes to app.log
logger.error("Database connection failed")  # Goes to errors.log

# Monitor all files
sinks = {
    "Application": app_sink,
    "Errors": error_sink,
    "Access": access_sink
}

print("Log File Status:")
print("=" * 70)
for name, sink_id in sinks.items():
    metadata = logger.file_metadata(sink_id)
    if metadata:
        size = int(metadata['size'])
        count = logger.line_count(sink_id)
        print(f"{name:12} | Size: {size:6} bytes | Lines: {count:4} | {metadata['path']}")
print("=" * 70)
```

**Output:**

```
Log File Status:
======================================================================
Application  | Size:    450 bytes | Lines:    1 | E:\Projects\app.log
Errors       | Size:    520 bytes | Lines:    1 | E:\Projects\errors.log
Access       | Size:      0 bytes | Lines:    0 | E:\Projects\access.log
======================================================================
```

---

## See Also

- [File Operations API](../api-reference/file-operations.md) - Complete method documentation
- [Configuration Guide](../guides/configuration.md) - File rotation and sink setup
- [JSON Logging Example](../examples/json-logging.md) - Working with structured logs
