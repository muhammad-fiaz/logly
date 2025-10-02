#!/usr/bin/env python3
"""
Basic Console Logging Example

This example demonstrates the simplest way to get started with Logly for console logging
with beautiful colored output.

Features demonstrated:
- Basic logging at all levels
- Colored console output
- String formatting
- Extra context data
"""

from logly import logger


def main():
    # Configure for colored console output (console=True by default)
    logger.configure(level="TRACE", color=True, console=True)

    # Add console sink (required for console output)
    logger.add("console")

    # Log at all levels
    logger.trace("This is a TRACE message - most verbose")
    logger.debug("This is a DEBUG message - for development")
    logger.info("This is an INFO message - general information")
    logger.success("This is a SUCCESS message - operation completed")
    logger.warning("This is a WARNING message - potential issue")
    logger.error("This is an ERROR message - something went wrong")
    logger.critical("This is a CRITICAL message - system failure")

    # Log with string formatting
    logger.info("Processing user %s with ID %d", "alice", 12345)
    logger.warning("Rate limit exceeded for IP %s", "192.168.1.100")

    # Log with extra context data
    logger.info("User logged in", user_id=12345, ip="192.168.1.100", user_agent="Chrome/91.0")
    logger.error("Database connection failed", error_code="ECONNREFUSED", retry_count=3)

    # Simulate some work
    for i in range(5):
        logger.info("Processing item %d", i, progress=f"{i + 1}/5")

    logger.success("All tasks completed successfully!")


if __name__ == "__main__":
    main()
