"""Test script to verify internal debug mode functionality."""

import os
from logly import logger

# Clean up any existing debug log
if os.path.exists("test_debug.log"):
    os.remove("test_debug.log")

print("Creating logger with internal debug mode enabled...")
debug_logger = logger(
    auto_update_check=False,  # Disable version check for faster testing
    internal_debug=True,
    debug_log_path="test_debug.log",
)

print("Performing various operations...")
debug_logger.configure(level="DEBUG", color=True)
debug_logger.add("test_app.log", rotation="daily")
debug_logger.info("Test message 1", user="alice")
debug_logger.debug("Test debug message")
debug_logger.warning("Test warning")

print("\n" + "=" * 60)
print("DEBUG LOG CONTENTS:")
print("=" * 60)

if os.path.exists("test_debug.log"):
    with open("test_debug.log", "r") as f:
        print(f.read())
else:
    print("❌ Debug log file was not created!")

# Cleanup
debug_logger.complete()
if os.path.exists("test_debug.log"):
    os.remove("test_debug.log")
if os.path.exists("test_app.log"):
    os.remove("test_app.log")

print("\n✅ Test completed!")
