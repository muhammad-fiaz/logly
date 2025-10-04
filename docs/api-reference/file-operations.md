# File Operations

Complete guide to file operations in Logly.

## Overview

Logly provides comprehensive file operation methods to manage, read, and analyze log files programmatically.

## Reading Log Files

### read()

Read entire log file content from a sink.

```python
from logly import logger

id = logger.add("app.log")
logger.info("Message 1")
logger.info("Message 2")

content = logger.read(id)
print(content)
```

**Returns:** String content or None if file doesn't exist

### read_all()

Read content from all active sinks.

```python
from logly import logger

id1 = logger.add("app.log")
id2 = logger.add("error.log")
logger.info("Test message")

all_content = logger.read_all()
for sink_id, content in all_content.items():
    print(f"Sink {sink_id}:\n{content}")
```

**Returns:** Dictionary mapping sink IDs to file content

### read_lines()

Read specific line ranges from log files.

```python
from logly import logger

id = logger.add("app.log")
for i in range(100):
    logger.info(f"Message {i}")

# Read first 10 lines
first_lines = logger.read_lines(id, 1, 10)

# Read last 5 lines
last_lines = logger.read_lines(id, -5, -1)

# Read middle section
middle = logger.read_lines(id, 45, 55)
```

**Line Indexing:**

- Positive numbers: 1-indexed from start (1 = first line)
- Negative numbers: Count from end (-1 = last line, -5 = 5th from end)
- Inclusive range: Both start and end lines are included

### line_count()

Get total number of lines in a log file.

```python
from logly import logger

id = logger.add("app.log")
for i in range(50):
    logger.info(f"Line {i}")

count = logger.line_count(id)
print(f"Total lines: {count}")  # Output: Total lines: 50
```

**Use Cases:**

- Pagination through large log files
- Progress tracking
- File size estimation

## File Metadata

### file_size()

Get log file size in bytes.

```python
from logly import logger

id = logger.add("app.log")
logger.info("Hello world!")

size = logger.file_size(id)
print(f"File size: {size} bytes")

# Convert to human-readable
if size:
    kb = size / 1024
    mb = kb / 1024
    print(f"File size: {mb:.2f} MB")
```

**Returns:** Integer (bytes) or None

### file_metadata()

Get comprehensive file metadata.

```python
from logly import logger

id = logger.add("app.log")
logger.info("Test message")

metadata = logger.file_metadata(id)
print(f"Size: {metadata['size']} bytes")
print(f"Created: {metadata['created']}")
print(f"Modified: {metadata['modified']}")
print(f"Path: {metadata['path']}")
```

**Metadata Fields:**

- `size`: File size in bytes
- `created`: Creation timestamp (ISO 8601)
- `modified`: Last modification timestamp (ISO 8601)
- `path`: Absolute file path

## JSON Log Files

### read_json()

Read and parse JSON-formatted log files.

```python
from logly import logger

id = logger.add("data.log", json=True)
logger.info("User action", user="alice", action="login")
logger.info("User action", user="bob", action="logout")

# Compact JSON
json_compact = logger.read_json(id)
print(json_compact)

# Pretty-printed JSON
json_pretty = logger.read_json(id, pretty=True)
print(json_pretty)
```

**Output (compact):**

```json
[{"level":"INFO","message":"User action","user":"alice","action":"login"},{"level":"INFO","message":"User action","user":"bob","action":"logout"}]
```

**Output (pretty):**

```json
[
  {
    "level": "INFO",
    "message": "User action",
    "user": "alice",
    "action": "login"
  },
  {
    "level": "INFO",
    "message": "User action",
    "user": "bob",
    "action": "logout"
  }
]
```

**Supports:**

- JSON arrays
- Newline-delimited JSON (NDJSON)
- Automatic format detection

## File Deletion

### delete()

Delete log file for a specific sink (keeps sink configuration active).

```python
from logly import logger

id = logger.add("app.log")
logger.info("Old logs")

# Delete the file
success = logger.delete(id)
print(f"Deleted: {success}")

# Sink still active, creates new file
logger.info("New logs in fresh file")
```

**Behavior:**

- Deletes the log file from filesystem
- Sink configuration remains active
- Next log creates a new file
- Returns True on success, False if file doesn't exist

### delete_all()

Delete all log files from all sinks.

```python
from logly import logger

logger.add("app.log")
logger.add("error.log")
logger.add("debug.log")

logger.info("Old logs")

# Delete all files
count = logger.delete_all()
print(f"Deleted {count} files")

# All sinks still active
logger.info("Creates new files")
```

**Returns:** Number of files successfully deleted

## Console Operations

### clear()

Clear the console display.

```python
from logly import logger

logger.info("Message 1")
logger.info("Message 2")
logger.info("Message 3")

# Clear console
logger.clear()

# Console is now clear
logger.info("Fresh start")
```

**Platform Behavior:**

- **Windows**: Executes `cls` command
- **Unix/Linux/macOS**: Uses ANSI escape codes

**Note:** Only clears console display, does not affect log files

## Complete Example

```python
from logly import logger

# Setup sinks
app_id = logger.add("app.log", rotation="daily")
error_id = logger.add("error.log", filter_min_level="ERROR")
json_id = logger.add("data.log", json=True)

# Generate logs
for i in range(100):
    logger.info(f"Processing item {i}", item_id=i)
    if i % 10 == 0:
        logger.error(f"Error at item {i}", item_id=i)

# File inspection
print(f"App log size: {logger.file_size(app_id)} bytes")
print(f"Error log lines: {logger.line_count(error_id)}")

# Read specific sections
first_10 = logger.read_lines(app_id, 1, 10)
last_10 = logger.read_lines(app_id, -10, -1)
errors_around_50 = logger.read_lines(error_id, 45, 55)

# Get metadata
app_meta = logger.file_metadata(app_id)
print(f"App log created: {app_meta['created']}")
print(f"App log modified: {app_meta['modified']}")

# Read JSON data
json_data = logger.read_json(json_id, pretty=True)
print(json_data)

# Read all files
all_logs = logger.read_all()
for sink_id, content in all_logs.items():
    print(f"\n=== Sink {sink_id} ===")
    print(content[:200])  # First 200 chars

# Cleanup old files
logger.delete(error_id)  # Delete errors but keep sink
logger.delete_all()      # Delete all files
```

## Best Practices

### 1. Check Return Values

```python
from logly import logger

id = logger.add("app.log")

# Always check for None
content = logger.read(id)
if content:
    process_logs(content)

size = logger.file_size(id)
if size is not None:
    print(f"Size: {size} bytes")
```

### 2. Use Pagination for Large Files

```python
from logly import logger

id = logger.add("app.log")

total = logger.line_count(id)
page_size = 100

for page in range(0, total, page_size):
    start = page + 1
    end = min(page + page_size, total)
    lines = logger.read_lines(id, start, end)
    process_page(lines)
```

### 3. Monitor File Sizes

```python
from logly import logger

id = logger.add("app.log")

# Check size before reading
size = logger.file_size(id)
if size and size > 10 * 1024 * 1024:  # 10MB
    print("Warning: Large log file")
    # Use read_lines instead of read()
    recent = logger.read_lines(id, -100, -1)
else:
    content = logger.read(id)
```

### 4. Safe File Deletion

```python
from logly import logger

id = logger.add("app.log")

# Read before deleting
backup = logger.read(id)
if backup:
    save_to_archive(backup)

# Now safe to delete
logger.delete(id)
```

### 5. JSON Processing

```python
from logly import logger
import json

id = logger.add("events.log", json=True)
logger.info("Event", type="login", user="alice")
logger.info("Event", type="purchase", amount=99.99)

# Parse JSON logs
json_str = logger.read_json(id)
if json_str:
    events = json.loads(json_str)
    for event in events:
        if event.get("type") == "purchase":
            process_purchase(event)
```

## Error Handling

```python
from logly import logger

try:
    id = logger.add("app.log")
    
    # File operations may return None
    content = logger.read(id)
    if content is None:
        print("File not found or empty")
    
    # Line operations may fail
    lines = logger.read_lines(id, 1, 100)
    if lines is None:
        print("Could not read lines")
    
    # Size operations
    size = logger.file_size(id)
    if size is None:
        print("File doesn't exist yet")
    
    # Metadata
    meta = logger.file_metadata(id)
    if meta is None:
        print("Cannot get metadata")
    
except Exception as e:
    logger.exception("File operation failed")
```

## Performance Tips

1. **Use read_lines() for large files** instead of read()
2. **Check file_size()** before reading entire file
3. **Use line_count()** for pagination calculations
4. **Prefer JSON sinks** for structured log parsing
5. **Enable async_write** for better I/O performance

## See Also

- [Sink Management](sink-management.md)
- [Complete API Reference](complete-reference.md)
- [Configuration Guide](../guides/configuration.md)
