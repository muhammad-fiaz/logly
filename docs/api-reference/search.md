---
title: Search API - Logly Python Logging
description: Logly search API reference. Learn how to search log files with advanced filtering, regex patterns, and performance-optimized Rust-powered search.
keywords: python, logging, search, api, regex, filtering, patterns, performance, logly
---

# Log Search Functionality

## Overview

Logly provides powerful log file search capabilities powered entirely by **Rust**, delivering high-performance searches with advanced filtering and pattern matching options.

## Features

- ✅ **Rust-powered** - All search operations in native Rust for maximum speed
- ✅ **Case-insensitive/sensitive** search modes
- ✅ **Regular expression** support for pattern matching
- ✅ **Find all or first** match modes
- ✅ **Line range filtering** (search specific line ranges)
- ✅ **Max results limiting** (stop after N matches)
- ✅ **Context lines** (show lines before/after matches)
- ✅ **Log level filtering** (search only ERROR/INFO/etc. lines)
- ✅ **Invert matching** (find lines that DON'T match, like `grep -v`)
- ✅ **Unicode support** for international characters
- ✅ **Zero Python overhead** - minimal wrapper, all logic in Rust

---

## API Reference

### `search_log(sink_id, pattern, **options)`

Search for a pattern in a sink's log file using Rust-powered search engine.

**Parameters:**

- `sink_id` (int): The handler ID of the sink whose log file to search
- `pattern` (str): The string or regex pattern to search for
- `case_sensitive` (bool, optional): Perform case-sensitive matching. Default: False
- `first_only` (bool, optional): Return only first match. Default: False
- `use_regex` (bool, optional): Treat pattern as regular expression. Default: False
- `start_line` (int, optional): Start searching from this line number (1-indexed)
- `end_line` (int, optional): Stop searching at this line number (inclusive)
- `max_results` (int, optional): Maximum number of results to return
- `context_before` (int, optional): Number of context lines before each match
- `context_after` (int, optional): Number of context lines after each match
- `level_filter` (str, optional): Only search lines containing this log level
- `invert_match` (bool, optional): Return lines that DON'T match. Default: False

**Returns:**

- `list[dict]`: List of dictionaries with:
  - `"line"` (int): Line number (1-indexed)
  - `"content"` (str): Full line content
  - `"match"` (str): The matched substring
  - `"context_before"` (list[str]): Lines before match (if requested)
  - `"context_after"` (list[str]): Lines after match (if requested)
- `None`: If sink not found or file doesn't exist
- `[]`: Empty list if no matches found

---

## Basic Usage

### Find All Matches

```python
from logly import logger

sink_id = logger.add("app.log")

logger.error("Connection error: Timeout")
logger.info("Processing data...")
logger.error("Database error: Connection refused")
logger.complete()

# Search for all error messages (case-insensitive by default)
results = logger.search_log(sink_id, "error")

print(f"Found {len(results)} matches:")
for result in results:
    print(f"  Line {result['line']}: {result['content']}")
```

### Find First Match Only

```python
# Find only the first occurrence (efficient for large files)
first_error = logger.search_log(sink_id, "error", first_only=True)

if first_error:
    result = first_error[0]
    print(f"First error at line {result['line']}: {result['content']}")
```

---

## Advanced Usage

### Regular Expression Search

```python
# Search for error codes (pattern: "error:" followed by digits)
error_codes = logger.search_log(
    sink_id,
    r"error:\s+\d+",
    use_regex=True
)

# Search for email addresses
emails = logger.search_log(
    sink_id,
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    use_regex=True
)

# Search for IP addresses
ips = logger.search_log(
    sink_id,
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    use_regex=True
)
```

### Case-Sensitive Search

```python
logger.info("ERROR: Critical failure")  # Uppercase
logger.info("error: Minor issue")       # Lowercase
logger.info("Error: Network problem")   # Title case
logger.complete()

# Case-insensitive (default) - finds all 3
all_errors = logger.search_log(sink_id, "error")
print(f"Found {len(all_errors)} matches")  # 3

# Case-sensitive - finds only exact matches
exact_errors = logger.search_log(sink_id, "error", case_sensitive=True)
print(f"Found {len(exact_errors)} matches")  # 1 (only lowercase)
```

### Line Range Filtering

```python
# Search only lines 100-200
results = logger.search_log(
    sink_id,
    "pattern",
    start_line=100,
    end_line=200
)

# Search from line 500 to end of file
results = logger.search_log(
    sink_id,
    "pattern",
    start_line=500
)
```

### Maximum Results Limit

```python
# Get at most 10 matches (useful for previews)
preview = logger.search_log(
    sink_id,
    "error",
    max_results=10
)
```

### Context Lines

```python
# Show 2 lines before and after each match
results = logger.search_log(
    sink_id,
    "crash",
    context_before=2,
    context_after=2
)

for result in results:
    print(f"Match at line {result['line']}:")
    print("Context before:")
    for line in result['context_before']:
        print(f"  {line}")
    print(f">>> {result['content']}")  # The match
    print("Context after:")
    for line in result['context_after']:
        print(f"  {line}")
```

### Log Level Filtering

```python
# Search for "timeout" only in ERROR-level logs
error_timeouts = logger.search_log(
    sink_id,
    "timeout",
    level_filter="ERROR"
)

# Search for specific pattern in INFO logs
info_results = logger.search_log(
    sink_id,
    "user login",
    level_filter="INFO"
)
```

### Invert Matching (grep -v)

```python
# Find all lines that DON'T contain "success"
failures = logger.search_log(
    sink_id,
    "success",
    invert_match=True
)

# Find non-INFO level logs
non_info = logger.search_log(
    sink_id,
    "INFO",
    invert_match=True,
    level_filter=None  # Search all lines
)
```

### Combined Filters

```python
# Complex search: ERROR logs with "database", lines 100-1000, max 5 results
critical_db_errors = logger.search_log(
    sink_id,
    "database",
    level_filter="ERROR",
    start_line=100,
    end_line=1000,
    max_results=5,
    context_before=1,
    context_after=1
)
```

---

## Use Cases

### 1. Error Detection and Analysis

```python
def analyze_errors(log_sink):
    """Find and categorize all errors in the log file."""
    errors = logger.search_log(log_sink, "error")
    
    # Categorize by error type using regex
    connection_errors = logger.search_log(
        log_sink,
        r"connection.*error",
        use_regex=True
    )
    
    timeout_errors = logger.search_log(
        log_sink,
        r"timeout",
        level_filter="ERROR"
    )
    
    print(f"Total errors: {len(errors)}")
    print(f"Connection errors: {len(connection_errors)}")
    print(f"Timeout errors: {len(timeout_errors)}")
```

### 2. User Activity Tracking

```python
def find_user_sessions(log_sink, username):
    """Find all log entries for a specific user."""
    # Find user login
    login = logger.search_log(
        log_sink,
        f"user={username}.*login",
        use_regex=True,
        first_only=True
    )
    
    # Find all user activities
    activities = logger.search_log(log_sink, username)
    
    print(f"User '{username}':")
    print(f"  First login: Line {login[0]['line']}")
    print(f"  Total activities: {len(activities)}")
```

### 3. Security Auditing

```python
def security_audit(log_sink):
    """Audit security-related events."""
    # Find failed login attempts
    failed_logins = logger.search_log(
        log_sink,
        r"authentication.*failed",
        use_regex=True
    )
    
    # Find access from suspicious IPs (not starting with 192.168)
    external_access = logger.search_log(
        log_sink,
        r"\b192\.168\.",
        use_regex=True,
        invert_match=True  # Find IPs that DON'T match
    )
    
    if len(failed_logins) > 5:
        print(f"⚠️  {len(failed_logins)} failed login attempts!")
    
    if external_access:
        print(f"🔒 {len(external_access)} external access attempts")
```

### 4. Performance Monitoring

```python
def find_slow_operations(log_sink):
    """Find operations that took too long."""
    # Search for duration > 1000ms using regex
    slow_queries = logger.search_log(
        log_sink,
        r"duration.*[1-9]\d{3,}ms",  # 1000+ ms
        use_regex=True,
        context_before=1,
        context_after=1
    )
    
    print(f"Found {len(slow_queries)} slow operations:")
    for result in slow_queries[:5]:  # Show first 5
        print(f"Line {result['line']}: {result['content']}")
```

---

## Best Practices

### 1. Use `first_only` for Existence Checks

```python
# ✅ Efficient - stops after first match
if logger.search_log(sink_id, "ERROR", first_only=True):
    print("Errors detected")

# ❌ Inefficient - reads entire file
if len(logger.search_log(sink_id, "ERROR")) > 0:
    print("Errors detected")
```

### 2. Use Regex for Complex Patterns

```python
# ✅ Precise regex matching
error_codes = logger.search_log(
    sink_id,
    r"error:\s+[A-Z]{3}\d{4}",  # e.g., "error: ERR1234"
    use_regex=True
)

# ❌ Imprecise string matching
error_codes = logger.search_log(sink_id, "error:")
```

### 3. Handle None vs Empty List

```python
results = logger.search_log(sink_id, "pattern")

if results is None:
    print("Error: Sink not found or file missing")
elif not results:
    print("No matches found")
else:
    print(f"{len(results)} matches found")
```

### 4. Always Flush Before Searching

```python
logger.info("Important message")
logger.complete()  # ✅ Flush before searching

results = logger.search_log(sink_id, "Important")
```

---

## Comparison with Other Tools

### vs. `grep` command

```bash
# Linux grep
grep -i "ERROR" app.log
grep -v "success" app.log
grep -A 2 -B 2 "crash" app.log
```

```python
# Logly equivalent (all Rust-powered)
logger.search_log(sink_id, "ERROR", case_sensitive=False)
logger.search_log(sink_id, "success", invert_match=True)
logger.search_log(sink_id, "crash", context_before=2, context_after=2)
```

**Advantages:**
- ✅ Programmatic access within Python
- ✅ Structured results with line numbers
- ✅ Cross-platform (Windows, Linux, macOS)
- ✅ No external dependencies
- ✅ Rust performance

### vs. Manual File Reading

```python
# ❌ Manual approach - all in Python
with open("app.log") as f:
    for line_num, line in enumerate(f, 1):
        if "ERROR" in line:
            print(f"Line {line_num}: {line}")

# ✅ Logly approach - Rust-powered
results = logger.search_log(sink_id, "ERROR")
for r in results:
    print(f"Line {r['line']}: {r['content']}")
```

---

## Troubleshooting

### No Results Found

1. **Flush pending writes:**
   ```python
   logger.complete()  # Ensure all logs are written
   results = logger.search_log(sink_id, "search_term")
   ```

2. **Check case sensitivity:**
   ```python
   # Try case-insensitive (default)
   results = logger.search_log(sink_id, "error")
   
   # If that fails, try exact match
   results = logger.search_log(sink_id, "ERROR", case_sensitive=True)
   ```

3. **Verify sink has a file:**
   ```python
   metadata = logger.file_metadata(sink_id)
   if metadata:
       print(f"Searching file: {metadata['path']}")
   else:
       print("Sink has no file (console sink?)")
   ```

### Returns None

**Cause:** Sink ID is invalid or sink has no file

**Solutions:**
```python
# Check sink exists
if logger.is_sink_enabled(sink_id) is None:
    print("Sink ID is invalid")

# Use file sinks, not console
file_sink = logger.add("app.log")  # ✅ Has file
console_sink = logger.add("console")  # ❌ No file
```

---

*All search operations powered by Rust for maximum performance*  
*Last updated: October 2025 | Logly v0.1.5*
