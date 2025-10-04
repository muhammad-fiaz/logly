# Automatic Version Checking

Logly includes an automatic version checking feature that notifies you when a new version is available on PyPI.

---

## Overview

The version checker:

- ✅ **Non-blocking**: Runs in a background thread
- ✅ **Fast**: 2-second timeout to avoid delays
- ✅ **Once per session**: Only checks once per Python process
- ✅ **Optional**: Can be disabled in configuration
- ✅ **No dependencies**: Uses built-in HTTP client

---

## How It Works

### Automatic Check

When you create a logger with `auto_update_check=True` (default), Logly:

1. Spawns a background thread
2. Makes an HTTP request to PyPI API
3. Compares semantic versions
4. Displays a warning if newer version exists

```python
from logly import PyLogger

# Automatic version check enabled (default)
logger.add("console")

# If an update is available, you'll see:
# ⚠ Warning: A new version of Logly is available!
#   Current version: 0.1.5
#   Latest version:  0.2.0
#   Upgrade with: pip install --upgrade logly
```

**Expected Output** (when update available):
```
⚠ Warning: A new version of Logly is available!
  Current version: 0.1.5
  Latest version:  0.2.0
  Upgrade with: pip install --upgrade logly
```

---

## Configuration

### Disable Version Checking

You can disable automatic version checking:

```python
from logly import PyLogger

# Disable version checking
logger = PyLogger(auto_update_check=False)
logger.add("console")

# No version check will be performed
```

**Use Cases for Disabling:**

- **Production environments**: Avoid network requests in production
- **Air-gapped systems**: No internet access
- **CI/CD pipelines**: Version checks not needed in automated builds
- **Strict security policies**: Minimize external HTTP requests

---

## Technical Details

### Version Comparison

Logly uses **semantic versioning** comparison:

```
Version Format: MAJOR.MINOR.PATCH

Examples:
  0.1.5 < 0.2.0  → Update available
  1.0.0 < 1.0.1  → Update available
  1.2.3 = 1.2.3  → No update
  2.0.0 > 1.9.9  → No update (current is newer)
```

**Comparison Algorithm:**

1. Split versions into parts: `"0.1.5"` → `[0, 1, 5]`
2. Compare each part left to right
3. First difference determines newer version
4. Missing parts treated as `0`

---

### Network Behavior

**HTTP Request:**

- **URL**: `https://pypi.org/pypi/logly/json`
- **Method**: `GET`
- **Timeout**: 2 seconds (2000ms)
- **Retries**: None (fails silently on error)

**Response Handling:**

```json
{
  "info": {
    "version": "0.2.0"
  }
}
```

Only the `info.version` field is extracted and compared.

---

### Performance Impact

The version check is designed to have **minimal performance impact**:

| Aspect | Impact | Details |
|--------|--------|---------|
| **Execution Time** | ~0ms | Background thread, non-blocking |
| **Network Request** | 2s timeout | Fast-fail on network issues |
| **Memory Usage** | ~10 KB | Small HTTP client and JSON parser |
| **CPU Usage** | Negligible | Simple string comparison |
| **Frequency** | Once per process | Atomic flag prevents duplicate checks |

**Benchmark:**

```python
import time
from logly import PyLogger

start = time.time()
logger = PyLogger(auto_update_check=True)
logger.add("console")
end = time.time()

print(f"Logger initialization: {(end - start) * 1000:.2f}ms")
# Output: Logger initialization: 0.15ms
# (Version check runs in background, doesn't block)
```

**Expected Output:**
```
Logger initialization: 0.15ms
```

The version check happens **after** logger initialization completes.

---

## Error Handling

The version checker **fails silently** to avoid disrupting your application:

### Network Errors

```python
# No internet connection
logger = PyLogger(auto_update_check=True)
# No error thrown, no warning displayed
```

### Timeout Errors

```python
# Slow connection (>2 seconds)
logger = PyLogger(auto_update_check=True)
# Request times out, no error thrown
```

### Invalid Responses

```python
# PyPI returns malformed JSON
logger = PyLogger(auto_update_check=True)
# JSON parsing fails, no error thrown
```

**Design Philosophy:**

Version checking is a **convenience feature**, not a critical component. It should never cause application failures or delays.

---

## Best Practices

### Development Environment

**Recommended**: Keep version checking **enabled**

```python
# Development - stay informed about updates
logger = PyLogger(auto_update_check=True)
```

**Benefits:**

- Stay up-to-date with latest features
- Get bug fixes and performance improvements
- Receive security updates

---

### Production Environment

**Recommended**: **Disable** version checking

```python
# Production - no version checks
logger = PyLogger(auto_update_check=False)
```

**Reasons:**

- Avoid unnecessary network requests
- Reduce attack surface
- Comply with security policies
- Faster startup (no background thread)

---

### CI/CD Pipelines

**Recommended**: **Disable** version checking

```python
# CI/CD - version controlled in requirements.txt
logger = PyLogger(auto_update_check=False)
```

**Reasons:**

- Dependencies managed via `requirements.txt` or `pyproject.toml`
- No need for runtime version checks
- Faster test execution

---

## Environment-Based Configuration

Use environment variables to control version checking:

```python
import os
from logly import PyLogger

# Enable in development, disable in production
is_dev = os.getenv("ENVIRONMENT") == "development"

logger = PyLogger(auto_update_check=is_dev)
logger.add("console")
```

**Example `.env` file:**

```bash
# Development
ENVIRONMENT=development

# Production
ENVIRONMENT=production
```

**Expected Behavior:**

```python
# Development environment
ENVIRONMENT=development
logger = PyLogger(auto_update_check=True)
# Version check runs

# Production environment
ENVIRONMENT=production
logger = PyLogger(auto_update_check=False)
# Version check skipped
```

---

## Troubleshooting

### No Warning Displayed

**Problem**: New version available but no warning shown

**Possible Causes:**

1. **Version check disabled**: Check `auto_update_check` parameter
2. **Network blocked**: Firewall blocking PyPI access
3. **Timeout**: Request took longer than 2 seconds
4. **Already checked**: Version check only runs once per process

**Solution:**

```python
# Ensure version checking is enabled
logger = PyLogger(auto_update_check=True)

# Check network access
import urllib.request
try:
    urllib.request.urlopen("https://pypi.org/pypi/logly/json", timeout=2)
    print("PyPI accessible")
except:
    print("PyPI not accessible")
```

---

### Slow Startup

**Problem**: Logger initialization takes several seconds

**Possible Cause**: Version check timing out (rare, should be background)

**Solution:**

```python
# Disable version checking
logger = PyLogger(auto_update_check=False)
```

---

## Security Considerations

### HTTPS Connection

All version checks use **HTTPS** to prevent man-in-the-middle attacks:

```
https://pypi.org/pypi/logly/json
```

Certificate validation is performed automatically.

---

### No Data Collection

The version check:

- ❌ Does **not** send usage data
- ❌ Does **not** track installations
- ❌ Does **not** send analytics
- ✅ Only fetches public version information

**Privacy**: Your usage of Logly is completely private.

---

### Air-Gapped Environments

For systems without internet access:

```python
# Disable version checking for air-gapped systems
logger = PyLogger(auto_update_check=False)
```

No errors will occur, and no network requests will be attempted.

---

## Manual Version Checking

To manually check your Logly version:

```python
import logly

print(logly.__version__)
# Output: 0.1.5
```

**Expected Output:**
```
0.1.5
```

To check the latest version on PyPI:

```bash
pip index versions logly
```

**Expected Output:**
```
logly (0.2.0)
Available versions: 0.2.0, 0.1.5, 0.1.4, 0.1.3
```

---

## Upgrading Logly

When a new version is available:

### Using pip

```bash
pip install --upgrade logly
```

**Expected Output:**
```
Collecting logly
  Downloading logly-0.2.0-cp312-cp312-win_amd64.whl (1.2 MB)
Successfully installed logly-0.2.0
```

### Using pip with version constraint

```bash
pip install "logly>=0.2.0"
```

### Verify upgrade

```python
import logly
print(logly.__version__)
```

**Expected Output:**
```
0.2.0
```

---

## FAQ

### How often does the version check run?

**Once per Python process**. The check uses an atomic flag to ensure it only runs on the first logger initialization.

### Does it slow down my application?

**No**. The check runs in a background thread and has a 2-second timeout. Your application continues immediately.

### Can I customize the timeout?

**Not currently**. The 2-second timeout is hard-coded to balance responsiveness and reliability.

### What happens if PyPI is down?

**Nothing**. The check fails silently, and your application continues normally.

### Is the version check secure?

**Yes**. It uses HTTPS to connect to PyPI and only reads public version information. No data is sent.

### Can I check for pre-release versions?

**No**. The version checker only compares stable releases from PyPI.

---

## Summary

| Feature | Default | Recommended (Dev) | Recommended (Prod) |
|---------|---------|-------------------|-------------------|
| **auto_update_check** | `True` | `True` | `False` |
| **Network Requests** | Yes | Yes | No |
| **Performance Impact** | Minimal | Acceptable | None (disabled) |
| **Security Risk** | Low | Low | None (disabled) |

**Key Takeaway**: Version checking is a helpful development feature that should be disabled in production environments for optimal performance and security.
