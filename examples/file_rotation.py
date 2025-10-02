#!/usr/bin/env python3
"""
File Logging with Rotation Example

This example demonstrates file logging with automatic rotation based on size and time,
perfect for production applications that need log management.

Features demonstrated:
- Size-based rotation
- Time-based rotation
- Retention policies
- Multiple rotation strategies
- Async writing for performance
"""

import os
import time
from logly import logger


def demo_size_rotation():
    """Demonstrate size-based rotation."""
    print("=== Size-Based Rotation Demo ===")

    # Configure for file logging
    logger.configure(level="INFO", color=False, console=False)

    # Add file sink with size-based rotation
    size_sink = logger.add(
        "app.log",
        size_limit="500KB",  # Rotate when file reaches 500KB
        retention=3,  # Keep 3 rotated files
        async_write=True,  # Use async writing for performance
    )

    print(f"Added size-based sink with ID: {size_sink}")

    # Generate enough log messages to trigger rotation
    for i in range(2000):
        logger.info(f"Processing transaction {i:04d}", transaction_id=i, amount=100.50 + i)
        if i % 500 == 0:
            logger.warning(f"Checkpoint reached: {i + 1} transactions processed", checkpoint=i + 1)
        if i % 1000 == 0:
            logger.error(
                f"Simulated error at transaction {i}", error_code="TXN_FAIL", transaction=i
            )

        # Small delay to avoid overwhelming
        time.sleep(0.001)

    logger.info("Size-based rotation demo completed")

    # Clean up
    logger.remove(size_sink)


def demo_time_rotation():
    """Demonstrate time-based rotation."""
    print("\n=== Time-Based Rotation Demo ===")

    # Reset logger
    logger.reset()
    logger.configure(level="INFO", color=False, console=False)

    # Add sink with hourly rotation and date in filename
    time_sink = logger.add(
        "hourly.log",
        rotation="hourly",
        date_style="prefix",  # Put date before filename
        date_enabled=True,  # Include date in filename
        retention=5,
    )

    print(f"Added time-based sink with ID: {time_sink}")

    # Log messages over a short period
    for i in range(100):
        logger.info(f"Hourly log entry {i:03d}", sequence=i, timestamp=time.time())
        time.sleep(0.1)  # Small delay

    logger.info("Time-based rotation demo completed")
    logger.remove(time_sink)


def demo_combined_rotation():
    """Demonstrate combined size and time rotation."""
    print("\n=== Combined Rotation Demo ===")

    logger.reset()
    logger.configure(level="INFO", color=False, console=False)

    # Add sink with both size and time rotation
    combined_sink = logger.add(
        "combined.log",
        rotation="daily",  # Rotate daily
        size_limit="1MB",  # Or when reaching 1MB
        retention=7,  # Keep 7 files
        date_style="before_ext",  # Date before file extension
        date_enabled=True,
    )

    print(f"Added combined sink with ID: {combined_sink}")

    # Generate some log activity
    for i in range(500):
        logger.info(f"Combined rotation test {i}", counter=i, data={"value": i * 2})
        time.sleep(0.01)

    logger.info("Combined rotation demo completed")
    logger.remove(combined_sink)


def demo_different_sizes():
    """Demonstrate different size limits."""
    print("\n=== Different Size Limits Demo ===")

    logger.reset()
    logger.configure(level="INFO", color=False, console=False)

    # Small files
    small_sink = logger.add("small.log", size_limit="50KB", retention=3)
    # Medium files
    medium_sink = logger.add("medium.log", size_limit="500KB", retention=5)
    # Large files
    large_sink = logger.add("large.log", size_limit="5MB", retention=2)

    print("Added sinks with different size limits")

    # Generate varying amounts of logs for each
    for i in range(1000):
        # Log to all sinks
        logger.info(f"Multi-size log entry {i}", index=i)

        if i < 200:
            # Extra logs for small file rotation
            logger.debug(f"Debug info for small file {i}", detail=f"extra_{i}")
        elif i < 600:
            # Extra logs for medium file rotation
            logger.info(f"Info for medium file {i}", category="medium")
        # Large file will accumulate all logs

    logger.info("Different size limits demo completed")

    # Clean up
    logger.remove(small_sink)
    logger.remove(medium_sink)
    logger.remove(large_sink)


def main():
    """Run all rotation demos."""
    print("🚀 Logly File Rotation Examples")
    print("=" * 50)

    try:
        demo_size_rotation()
        demo_time_rotation()
        demo_combined_rotation()
        demo_different_sizes()

        print("\n" + "=" * 50)
        print("✅ All rotation demos completed!")
        print("\n📁 Generated log files:")

        # List generated files
        log_files = [f for f in os.listdir(".") if f.endswith(".log")]
        for log_file in sorted(log_files):
            if os.path.exists(log_file):
                size = os.path.getsize(log_file)
                print(f"  - {log_file} ({size:,} bytes)")

        print("\n💡 Note: Rotation may not occur immediately if size/time thresholds aren't met")
        print("   Run the script multiple times or increase log volume to see rotation in action")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        logger.exception("Demo failed", exc_info=e)


if __name__ == "__main__":
    main()
