---
title: Troubleshooting Guide - Logly
description: Comprehensive troubleshooting guide for common Logly issues including file access, permissions, network errors, and configuration problems.
keywords: troubleshooting, errors, problems, solutions, file access, permissions, network, logly
---

# Troubleshooting Guide

This guide covers common issues you may encounter when using Logly and provides solutions to resolve them.

---

## Quick Diagnosis

Use this checklist to quickly identify the type of issue you're experiencing:

- **Installation Issues**: Can't install or import Logly → [Installation Problems](#installation-problems)
- **File Access Errors**: Logs not writing to files → [File Access Issues](#file-access-issues)
- **Permission Denied**: Access denied errors → [Permission Issues](#permission-issues)
- **Network Errors**: Version check failures → [Network Issues](#network-issues)
- **Configuration Errors**: Invalid settings → [Configuration Problems](#configuration-problems)
- **Performance Issues**: Slow logging or high memory → [Performance Problems](#performance-problems)
- **Import Errors**: Can't import Logly → [Import and Compatibility Issues](#import-and-compatibility-issues)
- **Rotation Not Working**: Files not rotating → [File Rotation Issues](#file-rotation-issues)
- **Missing Logs**: Logs disappearing → [Missing or Lost Logs](#missing-or-lost-logs)
- **Callback Errors**: Callback failures → [Callback Issues](#callback-issues)

---

## Installation Problems

### Issue: `pip install logly` fails

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement logly
ERROR: Failed building wheel for logly
```

**Solutions:**

1. **Upgrade pip, setuptools, and wheel:**
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

2. **Check Python version (requires Python 3.10+):**
   ```bash
   python --version
   ```
   If below 3.10, upgrade Python or use a virtual environment with Python 3.10+.

3. **Install from PyPI with verbose output:**
   ```bash
   pip install logly -v
   ```

4. **Try installing with no cache:**
   ```bash
   pip install --no-cache-dir logly
   ```

5. **Install specific version:**
   ```bash
   pip install logly==0.1.5
   ```

### Issue: Import error after installation

**Symptoms:**
```python
ImportError: No module named 'logly'
ModuleNotFoundError: No module named 'logly'
```

**Solutions:**

1. **Verify installation:**
   ```bash
   pip show logly
   pip list | grep logly
   ```

2. **Check you're using the correct Python/pip:**
   ```bash
   python -m pip install logly
   ```

3. **Verify virtual environment is activated:**
   ```bash
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

4. **Reinstall Logly:**
   ```bash
   pip uninstall logly
   pip install logly
   ```

---

## File Access Issues

### Issue: Logs not writing to file

**Symptoms:**
- No log file created
- Log file is empty
- File exists but logs are missing

**Solutions:**

1. **Verify sink is added:**
   ```python
   from logly import logger
   
   # Make sure you add a file sink
   logger.add("logs/app.log")
   logger.info("Test message")
   logger.complete()  # ← Don't forget this!
   ```

2. **Check directory exists:**
   ```python
   import os
   
   # Create directory if it doesn't exist
   os.makedirs("logs", exist_ok=True)
   logger.add("logs/app.log")
   ```

3. **Use absolute paths to avoid ambiguity:**
   ```python
   import os
   
   log_path = os.path.abspath("logs/app.log")
   print(f"Logging to: {log_path}")
   logger.add(log_path)
   ```

4. **Verify `logger.complete()` is called:**
   ```python
   # At the end of your script or in cleanup
   logger.complete()  # Flushes all buffered logs
   ```

5. **Check async writing isn't buffering:**
   ```python
   # Force synchronous writing for immediate output
   logger.add("logs/app.log", async_write=False)
   ```

### Issue: File locked or in use

**Symptoms:**
```
IOError: [Errno 13] Permission denied: 'app.log'
PermissionError: [WinError 32] The process cannot access the file
```

**Solutions:**

1. **Remove all handlers before rotation:**
   ```python
   # Remove all existing sinks
   logger.remove_all()
   # Add fresh sinks
   logger.add("logs/app.log")
   ```

2. **Check if file is open in another program:**
   - Close text editors, log viewers, or other programs using the file
   - On Windows, check Task Manager for processes locking the file

3. **Use different log file:**
   ```python
   import time
   
   # Add timestamp to filename
   log_file = f"logs/app_{int(time.time())}.log"
   logger.add(log_file)
   ```

4. **Enable date-based naming to avoid conflicts:**
   ```python
   logger.add("logs/app.log", date_enabled=True)
   # Creates: app_2025-10-04.log
   ```

---

## Permission Issues

### Issue: Permission denied writing logs

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: '/var/log/app.log'
IOError: [Errno 13] Permission denied
```

**Solutions:**

1. **Use writable directory:**
   ```python
   # Instead of /var/log (requires root), use user directory
   import os
   
   log_dir = os.path.join(os.path.expanduser("~"), "logs")
   os.makedirs(log_dir, exist_ok=True)
   logger.add(f"{log_dir}/app.log")
   ```

2. **Check directory permissions (Linux/Mac):**
   ```bash
   ls -la /path/to/logs
   chmod 755 /path/to/logs  # Make directory writable
   ```

3. **Run with appropriate permissions:**
   ```bash
   # Linux/Mac (if necessary)
   sudo python app.py
   
   # Or fix ownership
   sudo chown $USER:$USER /path/to/logs
   ```

4. **Use current working directory:**
   ```python
   logger.add("app.log")  # Writes to current directory
   ```

### Issue: Cannot create directory

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: 'logs'
FileNotFoundError: [Errno 2] No such file or directory
```

**Solutions:**

1. **Create directory with proper error handling:**
   ```python
   import os
   
   try:
       os.makedirs("logs", exist_ok=True)
       logger.add("logs/app.log")
   except PermissionError:
       # Fallback to temp directory
       import tempfile
       temp_dir = tempfile.gettempdir()
       logger.add(f"{temp_dir}/app.log")
       logger.warning(f"Using temp directory for logs: {temp_dir}")
   ```

2. **Use environment-appropriate paths:**
   ```python
   import os
   import sys
   
   if sys.platform == "win32":
       log_dir = os.path.join(os.getenv("APPDATA"), "MyApp", "logs")
   else:
       log_dir = os.path.join(os.path.expanduser("~"), ".myapp", "logs")
   
   os.makedirs(log_dir, exist_ok=True)
   logger.add(f"{log_dir}/app.log")
   ```

---

## Network Issues

### Issue: Version check failing

**Symptoms:**
```
Warning: Failed to check for updates
Connection timeout when checking PyPI
```

**Solutions:**

1. **Disable version checking if behind firewall:**
   ```python
   # Version check is non-blocking and won't affect logging
   # But you can disable it by configuring proxy or ignoring warnings
   ```

2. **Configure proxy settings (if needed):**
   ```bash
   # Set environment variables before running
   export HTTP_PROXY=http://proxy.example.com:8080
   export HTTPS_PROXY=http://proxy.example.com:8080
   
   python app.py
   ```

3. **Check network connectivity:**
   ```bash
   ping pypi.org
   curl https://pypi.org/pypi/logly/json
   ```

4. **Version check is async and non-blocking:**
   - The version check runs in background and won't affect logging
   - If it fails, logging continues normally
   - Safe to ignore if not critical

---

## Configuration Problems

### Issue: Invalid log level error

**Symptoms:**
```
ValueError: Invalid log level: 'INVALID_LEVEL'. 
Valid levels are: TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
```

**Solutions:**

1. **Use valid log levels:**
   ```python
   # ✓ Correct (case-insensitive)
   logger.configure(level="INFO")
   logger.configure(level="debug")
   logger.configure(level="Error")
   
   # ✗ Invalid
   logger.configure(level="VERBOSE")  # Not a valid level
   ```

2. **Valid levels are:**
   - `TRACE` - Most verbose
   - `DEBUG` - Development debugging
   - `INFO` - General information
   - `SUCCESS` - Successful operations
   - `WARNING` - Warning messages
   - `ERROR` - Error conditions
   - `CRITICAL` - Critical failures

### Issue: Invalid rotation policy

**Symptoms:**
```
ValueError: Invalid rotation policy: 'weekly'. 
Valid policies are: daily, hourly, minutely, or size-based (e.g., '10MB')
```

**Solutions:**

1. **Use valid rotation policies:**
   ```python
   # Time-based rotation
   logger.add("app.log", rotation="daily")    # ✓
   logger.add("app.log", rotation="hourly")   # ✓
   logger.add("app.log", rotation="minutely") # ✓
   
   # Size-based rotation
   logger.add("app.log", rotation="10MB")     # ✓
   logger.add("app.log", rotation="1GB")      # ✓
   
   # Invalid
   logger.add("app.log", rotation="weekly")   # ✗ Not supported
   ```

2. **Size format examples:**
   ```python
   logger.add("app.log", rotation="500B")   # 500 bytes
   logger.add("app.log", rotation="5KB")    # 5 kilobytes
   logger.add("app.log", rotation="10MB")   # 10 megabytes
   logger.add("app.log", rotation="1GB")    # 1 gigabyte
   ```

### Issue: Invalid format string

**Symptoms:**
```
ValueError: Invalid format template: ...
```

**Solutions:**

1. **Use valid format placeholders:**
   ```python
   # Valid placeholders
   logger.add("app.log", format="{time} [{level}] {message}")
   logger.add("app.log", format="{time} | {level:8} | {module}:{function} | {message}")
   
   # Available placeholders:
   # {time}     - Timestamp
   # {level}    - Log level
   # {message}  - Log message
   # {module}   - Module name
   # {function} - Function name
   # {extra}    - Extra fields
   ```

2. **Check for syntax errors:**
   ```python
   # ✗ Missing closing brace
   logger.add("app.log", format="{time [{level}] {message}")
   
   # ✓ Correct
   logger.add("app.log", format="{time} [{level}] {message}")
   ```

---

## Performance Problems

### Issue: Logging is slow

**Symptoms:**
- Application hangs during logging
- High latency when logging
- Logs take seconds to write

**Solutions:**

1. **Enable async writing (default):**
   ```python
   logger.add("app.log", async_write=True)  # Non-blocking
   ```

2. **Increase buffer size for high-throughput:**
   ```python
   logger.add(
       "app.log",
       buffer_size=16384,        # 16 KB buffer
       max_buffered_lines=5000   # Buffer more lines
   )
   ```

3. **Reduce flush frequency:**
   ```python
   logger.add(
       "app.log",
       flush_interval=5000  # Flush every 5 seconds (default: 1 second)
   )
   ```

4. **Disable features you don't need:**
   ```python
   logger.configure(
       color=False,      # Disable color processing
       show_time=False   # Disable timestamp formatting
   )
   ```

5. **Use storage_levels to filter:**
   ```python
   # Don't write DEBUG/TRACE to files
   logger.configure(
       storage_levels={"TRACE": False, "DEBUG": False}
   )
   ```

### Issue: High memory usage

**Symptoms:**
- Memory usage grows over time
- Out of memory errors
- Process using too much RAM

**Solutions:**

1. **Reduce buffer sizes:**
   ```python
   logger.add(
       "app.log",
       buffer_size=4096,         # Smaller buffer
       max_buffered_lines=500    # Buffer fewer lines
   )
   ```

2. **Flush more frequently:**
   ```python
   logger.add("app.log", flush_interval=100)  # Flush every 100ms
   ```

3. **Enable rotation to limit file size:**
   ```python
   logger.add(
       "app.log",
       rotation="10MB",   # Rotate at 10MB
       retention=5        # Keep only 5 rotated files
   )
   ```

4. **Remove unnecessary sinks:**
   ```python
   # To remove a specific sink, save handler ID when adding
   handler_id = logger.add("app.log")
   # Later, remove it
   logger.remove(handler_id)
   
   # Or reset all configuration and start fresh
   logger.reset()
   logger.add("app.log")  # Add only what you need
   ```

5. **Disable callbacks if not needed:**
   ```python
   # Remove callbacks when done
   logger.remove_callback(callback_id)
   ```

---

## Import and Compatibility Issues

### Issue: `_logly.pyd` not found (Windows)

**Symptoms:**
```
ImportError: DLL load failed: The specified module could not be found.
```

**Solutions:**

1. **Install Visual C++ Redistributable:**
   - Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Install and restart

2. **Check Python architecture matches:**
   ```bash
   python -c "import struct; print(struct.calcsize('P') * 8)"
   # Should output 64 for 64-bit Python
   ```

3. **Reinstall Logly:**
   ```bash
   pip uninstall logly
   pip install --no-cache-dir logly
   ```

### Issue: Module compiled with wrong Python version

**Symptoms:**
```
ImportError: Module use of python312.dll conflicts with this version of Python.
```

**Solutions:**

1. **Ensure Python version matches:**
   ```bash
   python --version  # Check your Python version
   pip show logly    # Check Logly's required Python version
   ```

2. **Use correct Python interpreter:**
   ```bash
   python3.10 -m pip install logly
   python3.10 app.py
   ```

3. **Rebuild from source (if needed):**
   ```bash
   pip install maturin
   git clone https://github.com/muhammad-fiaz/logly.git
   cd logly
   maturin develop
   ```

---

## File Rotation Issues

### Issue: Files not rotating

**Symptoms:**
- Single log file grows indefinitely
- No rotated files created
- Rotation policy ignored

**Solutions:**

1. **Verify rotation is configured:**
   ```python
   # ✓ Rotation enabled
   logger.add("app.log", rotation="daily")
   
   # ✗ No rotation
   logger.add("app.log")  # rotation=None by default
   ```

2. **Check rotation thresholds:**
   ```python
   # Size-based: file must exceed size
   logger.add("app.log", rotation="10MB")  # Rotates when > 10MB
   
   # Time-based: must cross boundary
   logger.add("app.log", rotation="daily")  # Rotates at midnight
   ```

3. **Ensure `logger.complete()` is called:**
   ```python
   # Rotation happens during file close
   logger.complete()  # Triggers rotation if needed
   ```

4. **Check file permissions for renaming:**
   ```bash
   # Linux/Mac
   ls -la logs/
   chmod 755 logs/
   ```

### Issue: Too many rotated files

**Symptoms:**
- Disk filling up with old logs
- Hundreds of `.log.1`, `.log.2` files

**Solutions:**

1. **Set retention policy:**
   ```python
   logger.add(
       "app.log",
       rotation="daily",
       retention=7  # Keep only last 7 days
   )
   ```

2. **Enable compression:**
   ```python
   logger.add(
       "app.log",
       rotation="daily",
       compression="gzip"  # or "zstd"
   )
   ```

3. **Manually clean old files:**
   ```python
   import os
   import time
   
   log_dir = "logs"
   max_age_days = 7
   
   now = time.time()
   for filename in os.listdir(log_dir):
       filepath = os.path.join(log_dir, filename)
       if os.path.isfile(filepath):
           age_days = (now - os.path.getmtime(filepath)) / 86400
           if age_days > max_age_days:
               os.remove(filepath)
   ```

---

## Missing or Lost Logs

### Issue: Logs disappearing

**Symptoms:**
- Logs written but file is empty later
- Some log messages missing
- Intermittent log loss

**Solutions:**

1. **Always call `logger.complete()`:**
   ```python
   import atexit
   
   # Ensure logs are flushed on exit
   atexit.register(logger.complete)
   
   # Or use try/finally
   try:
       logger.info("Processing...")
   finally:
       logger.complete()
   ```

2. **Use synchronous writing for critical logs:**
   ```python
   # Critical logs should be written immediately
   logger.add("critical.log", async_write=False)
   logger.error("Critical error occurred")
   ```

3. **Check log level filtering:**
   ```python
   # If level=INFO, DEBUG logs won't appear
   logger.configure(level="TRACE")  # Show all logs
   ```

4. **Verify storage_levels configuration:**
   ```python
   # Make sure storage isn't disabled for certain levels
   logger.configure(
       storage_levels={"DEBUG": True, "INFO": True}
   )
   ```

5. **Check disk space:**
   ```bash
   df -h  # Linux/Mac
   # Windows: Check drive properties
   ```

### Issue: Console logs missing

**Symptoms:**
- Logs appear in files but not console
- Console output incomplete

**Solutions:**

1. **Add console sink explicitly:**
   ```python
   logger.add("console")  # Explicitly add console output
   ```

2. **Check console_levels configuration:**
   ```python
   logger.configure(
       console_levels={"INFO": True, "DEBUG": True}
   )
   ```

3. **Verify stderr/stdout redirection:**
   ```python
   import sys
   
   # Check if stdout is redirected
   print(f"stdout: {sys.stdout}")
   print(f"stderr: {sys.stderr}")
   ```

---

## Callback Issues

### Issue: Callbacks not executing

**Symptoms:**
- Callback function not called
- No callback output

**Solutions:**

1. **Verify callback is added:**
   ```python
   def my_callback(record):
       print(f"Callback received: {record['message']}")
   
   callback_id = logger.add_callback(my_callback)
   print(f"Callback ID: {callback_id}")  # Should return integer
   ```

2. **Check callback function signature:**
   ```python
   # ✓ Correct signature
   def my_callback(record: dict) -> None:
       level = record["level"]
       message = record["message"]
   
   # ✗ Wrong signature
   def my_callback():  # Missing record parameter
       pass
   ```

3. **Handle callback exceptions:**
   ```python
   def safe_callback(record):
       try:
           # Your callback logic
           send_alert(record["message"])
       except Exception as e:
           # Callback errors are caught but logged
           print(f"Callback error: {e}")
   
   logger.add_callback(safe_callback)
   ```

### Issue: Callback causing errors

**Symptoms:**
```
RuntimeError: Callback execution error: ...
```

**Solutions:**

1. **Add error handling in callback:**
   ```python
   def robust_callback(record):
       try:
           if record["level"] == "ERROR":
               send_alert(record)
       except ConnectionError:
           # Handle network errors gracefully
           print("Alert service unavailable")
       except Exception as e:
           print(f"Callback failed: {e}")
   
   logger.add_callback(robust_callback)
   ```

2. **Test callback independently:**
   ```python
   # Test callback with sample data
   sample_record = {
       "level": "ERROR",
       "message": "Test error",
       "timestamp": "2025-10-04T10:30:00"
   }
   
   my_callback(sample_record)  # Test before adding to logger
   ```

3. **Remove problematic callback:**
   ```python
   logger.remove_callback(callback_id)
   ```

---

## Platform-Specific Issues

### Windows-Specific

**Issue: Path separators causing errors**
```python
# ✗ Problematic on Windows
logger.add("logs/app.log")

# ✓ Cross-platform compatible
import os
logger.add(os.path.join("logs", "app.log"))

# ✓ Or use forward slashes (works on Windows too)
logger.add("logs/app.log")
```

**Issue: File locks preventing rotation**
```python
# Windows locks files more aggressively
# Use date_enabled to create new files instead
logger.add("app.log", rotation="daily", date_enabled=True)
```

### Linux/Mac-Specific

**Issue: Permission denied in /var/log**
```bash
# Solution 1: Use user directory
logger.add("~/logs/app.log")

# Solution 2: Create with proper permissions
sudo mkdir /var/log/myapp
sudo chown $USER:$USER /var/log/myapp
logger.add("/var/log/myapp/app.log")
```

**Issue: Signal handling with async writing**
```python
import signal
import sys

def signal_handler(sig, frame):
    logger.complete()  # Flush logs before exit
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

---

## Debugging Tips

### Enable verbose error messages

```python
import logging
import sys

# Enable Python's logging to see internal errors
logging.basicConfig(level=logging.DEBUG)

# Add traceback for exceptions
import traceback

try:
    logger.add("problematic.log")
except Exception as e:
    traceback.print_exc()
```

### Test minimal configuration

```python
# Start with absolute minimum
from logly import logger

logger.add("console")
logger.info("Test message")
logger.complete()

# If this works, add features incrementally
```

### Check file accessibility

```python
import os

log_path = "logs/app.log"

# Check if path is writable
try:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'a') as f:
        f.write("test\n")
    print(f"✓ Path is writable: {log_path}")
except Exception as e:
    print(f"✗ Path error: {e}")
```

### Verify Logly version

```python
import importlib.metadata

version = importlib.metadata.version('logly')
print(f"Logly version: {version}")

# Check if it's the latest
# Latest version: 0.1.5
```

---

## Getting Help

### Before Reporting Issues

1. **Check this troubleshooting guide**
2. **Search existing issues**: https://github.com/muhammad-fiaz/logly/issues
3. **Update to latest version**: `pip install --upgrade logly`
4. **Test with minimal example**

### Reporting Bugs

When reporting issues, include:

1. **Logly version**: `pip show logly`
2. **Python version**: `python --version`
3. **Operating system**: Windows/Linux/Mac + version
4. **Minimal code example** that reproduces the issue
5. **Full error message and traceback**
6. **Expected vs actual behavior**

**Report issues at**: https://github.com/muhammad-fiaz/logly/issues

### Example Bug Report

```
**Logly Version**: 0.1.5
**Python Version**: 3.10.12
**OS**: Windows 11

**Issue**: Logs not writing to file

**Code**:
```python
from logly import logger
logger.add("app.log")
logger.info("Test")
logger.complete()
```

**Expected**: Log file created with message
**Actual**: No file created

**Error Message**: None
```

---

## Common Error Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `ValueError: Invalid log level` | Invalid level string | Use TRACE/DEBUG/INFO/SUCCESS/WARNING/ERROR/CRITICAL |
| `ValueError: Invalid rotation policy` | Invalid rotation format | Use daily/hourly/minutely or size (e.g., "10MB") |
| `PermissionError` | No write access | Use writable directory or fix permissions |
| `FileNotFoundError` | Directory doesn't exist | Create directory with `os.makedirs()` |
| `ImportError: No module named 'logly'` | Logly not installed | Run `pip install logly` |
| `ImportError: DLL load failed` | Missing C++ runtime | Install Visual C++ Redistributable |
| `IOError: File is locked` | File in use | Close other programs or use different filename |
| `RuntimeError: Callback execution error` | Callback exception | Add error handling in callback function |

---

## Performance Tuning Checklist

- [ ] Enable async writing: `async_write=True`
- [ ] Increase buffer size: `buffer_size=16384`
- [ ] Reduce flush frequency: `flush_interval=5000`
- [ ] Filter unnecessary levels: `storage_levels={"DEBUG": False}`
- [ ] Disable colors if not needed: `color=False`
- [ ] Use size-based rotation: `rotation="10MB"`
- [ ] Enable compression: `compression="gzip"`
- [ ] Set retention policy: `retention=7`
- [ ] Remove unused sinks: Use `logger.remove(handler_id)` or `logger.reset()`
- [ ] Minimize callback overhead

---

## Sink Management Issues

### Issue: Cannot remove sink

**Symptoms:**
- `remove()` doesn't work
- Sink ID not found
- Sink still logging after removal

**Solutions:**

1. **Save sink ID when adding:**
   ```python
   from logly import logger
   
   # Save the ID returned by add()
   sink_id = logger.add("app.log")
   
   # Later, remove using that ID
   logger.remove(sink_id)
   ```

2. **List all sinks to find ID:**
   ```python
   # Get list of all sink IDs
   sink_ids = logger.list_sinks()
   print(f"Active sinks: {sink_ids}")
   
   # Remove specific sink
   logger.remove(sink_ids[0])
   ```

3. **Remove all sinks at once:**
   ```python
   # Remove all configured sinks
   logger.remove_all()
   ```

4. **Check sink count:**
   ```python
   count = logger.sink_count()
   print(f"Active sinks: {count}")
   ```

### Issue: Sink information retrieval fails

**Symptoms:**
- `sink_info()` returns empty
- Cannot get sink details
- Sink ID doesn't exist

**Solutions:**

1. **Verify sink exists:**
   ```python
   sink_ids = logger.list_sinks()
   if sink_id in sink_ids:
       info = logger.sink_info(sink_id)
       print(info)
   else:
       print(f"Sink {sink_id} not found")
   ```

2. **Get all sinks information:**
   ```python
   all_info = logger.all_sinks_info()
   for sink_id, details in all_info.items():
       print(f"Sink {sink_id}: {details}")
   ```

3. **Check sink configuration:**
   ```python
   info = logger.sink_info(sink_id)
   if info:
       print(f"Path: {info['path']}")
       print(f"Rotation: {info['rotation']}")
       print(f"Async: {info['async_write']}")
   ```

---

## File Operations Issues

### Issue: Cannot read log file

**Symptoms:**
- `read()` returns empty
- `read_all()` fails
- File exists but cannot be read

**Solutions:**

1. **Flush logs before reading:**
   ```python
   from logly import logger
   
   logger.add("app.log")
   logger.info("Test message")
   logger.complete()  # Flush all logs
   
   # Now read
   content = logger.read("app.log")
   print(content)
   ```

2. **Use absolute path:**
   ```python
   import os
   
   log_path = os.path.abspath("logs/app.log")
   content = logger.read(log_path)
   ```

3. **Check file exists:**
   ```python
   import os
   
   if os.path.exists("app.log"):
       content = logger.read("app.log")
   else:
       print("Log file not found")
   ```

4. **Read all log files:**
   ```python
   # Read all .log files in directory
   all_logs = logger.read_all("logs/*.log")
   for filepath, content in all_logs.items():
       print(f"\n=== {filepath} ===")
       print(content)
   ```

### Issue: Cannot get file metadata

**Symptoms:**
- `file_metadata()` fails
- `file_size()` returns 0
- Metadata incomplete

**Solutions:**

1. **Ensure file exists and is flushed:**
   ```python
   logger.complete()  # Flush first
   
   metadata = logger.file_metadata("app.log")
   print(f"Size: {metadata['size']} bytes")
   print(f"Created: {metadata['created']}")
   print(f"Modified: {metadata['modified']}")
   ```

2. **Check file size:**
   ```python
   size = logger.file_size("app.log")
   print(f"File size: {size} bytes")
   ```

3. **Get line count:**
   ```python
   count = logger.line_count("app.log")
   print(f"Total lines: {count}")
   ```

### Issue: Cannot delete log files

**Symptoms:**
- `delete()` fails
- Files not removed
- Permission denied when deleting

**Solutions:**

1. **Remove sinks before deleting:**
   ```python
   # Remove all sinks first
   logger.remove_all()
   
   # Then delete file
   logger.delete("app.log")
   ```

2. **Delete all log files:**
   ```python
   # Delete all .log files in directory
   deleted = logger.delete_all("logs/*.log")
   print(f"Deleted {len(deleted)} files")
   ```

3. **Handle deletion errors:**
   ```python
   import os
   
   try:
       logger.delete("app.log")
   except PermissionError:
       # File may be locked
       logger.remove_all()  # Remove sinks
       logger.delete("app.log")  # Try again
   ```

---

## Context Binding Issues

### Issue: Context not appearing in logs

**Symptoms:**
- `bind()` doesn't add context
- Extra fields missing
- Context not persisted

**Solutions:**

1. **Verify bind usage:**
   ```python
   from logly import logger
   
   # Bind context permanently
   logger.bind(request_id="abc123", user="john")
   logger.info("User action")
   # Output: ... request_id=abc123 user=john
   ```

2. **Use contextualize() for temporary context:**
   ```python
   with logger.contextualize(session_id="xyz"):
       logger.info("Session started")
       # session_id only in this block
   ```

3. **Check JSON format for extra fields:**
   ```python
   logger.configure(json=True)
   logger.bind(app="myapp", version="1.0")
   logger.info("Message")
   # Extra fields visible in JSON output
   ```

4. **Clear bound context:**
   ```python
   # Reset configuration to clear bindings
   logger.reset()
   ```

---

## JSON Logging Issues

### Issue: JSON format malformed

**Symptoms:**
- Invalid JSON output
- Cannot parse log files
- Missing fields in JSON

**Solutions:**

1. **Enable proper JSON formatting:**
   ```python
   from logly import logger
   
   logger.configure(json=True, pretty_json=True)
   logger.info("Test message", extra_field="value")
   ```

2. **Read JSON logs properly:**
   ```python
   import json
   
   # Read and parse JSON logs
   logs = logger.read_json("app.log", pretty=False)
   for log in logs:
       print(json.dumps(log, indent=2))
   ```

3. **Check for NDJSON format:**
   ```python
   # Logly outputs NDJSON (one JSON per line)
   content = logger.read("app.log")
   for line in content.strip().split('\n'):
       log_entry = json.loads(line)
       print(log_entry)
   ```

---

## Advanced Features Troubleshooting

### Issue: Custom format not applied

**Symptoms:**
- Format string ignored
- Wrong log structure
- Placeholders not replaced

**Solutions:**

1. **Use correct format syntax:**
   ```python
   logger.add(
       "app.log",
       format="{time} | {level:8} | {module}:{function} | {message}"
   )
   ```

2. **Available placeholders:**
   ```python
   # Valid format placeholders:
   # {time}     - Timestamp
   # {level}    - Log level (e.g., INFO)
   # {message}  - Log message
   # {module}   - Module name
   # {function} - Function name
   # {extra}    - Extra context fields
   ```

3. **Verify format is set per-sink:**
   ```python
   # Each sink can have different format
   logger.add("console", format="{time} {level} {message}")
   logger.add("file.log", format="{time} | {level:8} | {message}")
   ```

### Issue: Rotation not working as expected

**Symptoms:**
- Files rotate too early/late
- Wrong rotation schedule
- Size limits not respected

**Solutions:**

1. **Check rotation configuration:**
   ```python
   # Time-based rotation
   logger.add("app.log", rotation="daily")   # Rotates at midnight
   logger.add("app.log", rotation="hourly")  # Every hour
   
   # Size-based rotation
   logger.add("app.log", rotation="10MB")    # At 10MB
   logger.add("app.log", rotation="1GB")     # At 1GB
   ```

2. **Combine with retention:**
   ```python
   logger.add(
       "app.log",
       rotation="daily",
       retention=7  # Keep 7 days
   )
   ```

3. **Enable date in filename:**
   ```python
   logger.add(
       "app.log",
       rotation="daily",
       date_enabled=True  # Creates app_2025-10-04.log
   )
   ```

### Issue: Async write delays logs

**Symptoms:**
- Logs appear delayed
- Real-time logs not visible
- Buffer not flushing

**Solutions:**

1. **Reduce flush interval:**
   ```python
   logger.add(
       "app.log",
       async_write=True,
       flush_interval=100  # Flush every 100ms
   )
   ```

2. **Force immediate write:**
   ```python
   # For critical logs, use sync writing
   logger.add("critical.log", async_write=False)
   ```

3. **Manual flush:**
   ```python
   logger.info("Important message")
   logger.complete()  # Force flush immediately
   ```

4. **Reduce buffer size:**
   ```python
   logger.add(
       "app.log",
       buffer_size=1024,        # Small buffer (1KB)
       max_buffered_lines=100   # Few lines
   )
   ```

### Issue: Callbacks not receiving all logs

**Symptoms:**
- Some logs skip callback
- Callback executed partially
- Missing log levels in callback

**Solutions:**

1. **Check callback level filtering:**
   ```python
   def my_callback(record):
       # Check what level is received
       print(f"Level: {record['level']}")
       print(f"Message: {record['message']}")
   
   logger.add_callback(my_callback)
   ```

2. **Verify callback registration:**
   ```python
   callback_id = logger.add_callback(my_callback)
   print(f"Callback registered: {callback_id}")
   ```

3. **Handle all log levels:**
   ```python
   def universal_callback(record):
       level = record["level"]
       message = record["message"]
       timestamp = record.get("timestamp", "")
       
       # Process all levels
       if level in ["ERROR", "CRITICAL"]:
           send_alert(message)
       elif level == "INFO":
           log_to_db(message)
   
   logger.add_callback(universal_callback)
   ```

4. **Remove and re-add callback:**
   ```python
   logger.remove_callback(callback_id)
   new_id = logger.add_callback(my_callback)
   ```

---

## Still Having Issues?

If you've tried the solutions above and still experiencing problems:

1. **Update Logly**: `pip install --upgrade logly`
2. **Check GitHub issues**: https://github.com/muhammad-fiaz/logly/issues
3. **Ask for help**: Open a new issue with details
4. **Contact maintainer**: https://github.com/muhammad-fiaz

**Documentation**: https://muhammad-fiaz.github.io/logly/  
**GitHub**: https://github.com/muhammad-fiaz/logly  
**PyPI**: https://pypi.org/project/logly/

---

*Last Updated: October 4, 2025 - Logly v0.1.5*
