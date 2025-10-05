"""Test script for auto-sink feature and new API"""

import warnings
import sys
import os

# Add current directory to path for local testing
sys.path.insert(0, os.path.dirname(__file__))

from logly import logger

print("=" * 70)
print("Testing Auto-Sink Feature & New API")
print("=" * 70)

# Test 1: Default behavior with auto sink
print("\n[Test 1] Default auto sink (should create console sink automatically)")
print("-" * 70)
logger.configure(level="INFO")
logger.info("✓ This message should appear in console (auto sink enabled)")
logger.debug("✗ This DEBUG message should NOT appear (level=INFO)")

# Test 2: Manual sink mode
print("\n[Test 2] Manual sink mode (auto_sink=False)")
print("-" * 70)
logger2 = logger(auto_update_check=False)
logger2.configure(level="INFO", auto_sink=False)
print("Configured with auto_sink=False - no automatic console sink")
logger2.info("✗ This should NOT appear (no sinks added yet)")
logger2.add("test_manual.log")
logger2.info("✓ This goes to test_manual.log only")
print("Logged to test_manual.log (not visible in console)")

# Test 3: Duplicate sink warning
print("\n[Test 3] Duplicate sink detection")
print("-" * 70)
logger3 = logger(auto_update_check=False)
logger3.configure(level="INFO")  # Auto-creates console sink
print("Auto sink created console sink")

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    logger3.add("console")

    if w and len(w) > 0:
        print(f"✓ Warning detected: {w[0].message}")
    else:
        print("✗ No warning detected (expected duplicate console sink warning)")

# Test 4: File duplicate detection
print("\n[Test 4] File duplicate detection")
print("-" * 70)
logger4 = logger(auto_update_check=False)
logger4.configure(level="INFO", auto_sink=False)
logger4.add("duplicate_test.log")
print("Added duplicate_test.log")

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    logger4.add("duplicate_test.log")

    if w and len(w) > 0:
        print(f"✓ Warning detected: {w[0].message}")
    else:
        print("✗ No warning detected (expected duplicate file sink warning)")

# Test 5: Custom logger instance
print("\n[Test 5] Custom logger instance with logger() callable")
print("-" * 70)
custom = logger(auto_update_check=False)
custom.configure(level="DEBUG")
print("Created custom logger with auto_update_check=False")
custom.info("✓ Custom logger works!")
custom.debug("✓ DEBUG level works (custom logger level=DEBUG)")

# Test 6: Multiple sinks
print("\n[Test 6] Multiple sinks (console + files)")
print("-" * 70)
logger5 = logger(auto_update_check=False)
logger5.configure(level="INFO")  # Auto console sink
logger5.add("multi_test.log")
logger5.add("multi_errors.log", filter_min_level="ERROR")
print("Added console (auto), multi_test.log, and multi_errors.log")
logger5.info("✓ This appears in console and multi_test.log")
logger5.error("✓ This appears in console, multi_test.log, and multi_errors.log")

# Clean up test files
import os

for f in ["test_manual.log", "duplicate_test.log", "multi_test.log", "multi_errors.log"]:
    if os.path.exists(f):
        os.remove(f)
        print(f"Cleaned up {f}")

print("\n" + "=" * 70)
print("All tests completed!")
print("=" * 70)
