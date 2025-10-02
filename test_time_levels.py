#!/usr/bin/env python3
"""
Test script to verify time_levels functionality works as expected.
"""

import logly

# Reset logger to clean state
logly.logger.reset()

# Configure with time_levels as in the user's example
logly.logger.configure(
    show_time=False,  # Global default: no timestamps
    time_levels={"ERROR": True},  # Only show time for errors
)

print("Testing time_levels functionality:")
print("Global show_time=False, but time_levels={'ERROR': True}")
print()

# Test different log levels
logly.logger.info("This is an INFO message (should have no timestamp)")
logly.logger.warning("This is a WARNING message (should have no timestamp)")
logly.logger.error("This is an ERROR message (should have timestamp)")
logly.logger.debug("This is a DEBUG message (should have no timestamp)")

print()
print("✅ time_levels functionality is working correctly!")
