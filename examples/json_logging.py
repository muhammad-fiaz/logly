#!/usr/bin/env python3
"""
JSON Logging Examples

This comprehensive guide shows you how to use Logly for structured JSON logging,
perfect for production applications that need machine-readable logs for monitoring,
analytics, and debugging.

JSON logging provides several key benefits:
- Structured data that's easy for machines to parse and analyze
- Consistent log format across different environments
- Rich context with key-value pairs
- Easy integration with log aggregation tools like ELK stack, Splunk, or Datadog
- Better searchability and filtering capabilities

Features demonstrated:
- Basic JSON logging with structured data
- Persistent context binding across log entries
- Level-based filtering and separate log files
- Pretty-printed JSON for development
- Custom fields and nested data structures
"""

import os

from logly import logger


def demo_json_logging():
    """Demonstrate JSON logging with structured data."""
    print("\n=== JSON Logging Demo ===")

    # Configure for JSON output (affects console output)
    logger.configure(level="INFO", json=True, console=False)

    # Add JSON sink with json=True parameter for automatic JSON formatting
    json_sink = logger.add(
        "app.jsonl",
        json=True,  # Enable JSON formatting for this file sink
        async_write=True,
    )

    print(f"Added JSON sink with ID: {json_sink}")

    # Log structured data
    logger.info("User login", user_id=12345, username="john_doe", ip="192.168.1.100")
    logger.warning("High memory usage", memory_percent=85.7, threshold=80.0, server="web-01")
    logger.error("Database connection failed", db_host="db.example.com", error_code="ECONNREFUSED")

    # Log with nested data
    user_data = {
        "profile": {
            "name": "Alice Smith",
            "email": "alice@example.com",
            "preferences": {"theme": "dark", "notifications": True, "device": "mobile"},
        }
    }

    logger.info("User profile updated", **user_data)

    # Log with arrays
    logger.info(
        "Batch processing completed",
        processed_items=[1, 2, 3, 4, 5],
        failed_items=[],
        duration_ms=1500,
    )

    logger.info("JSON logging demo completed")
    logger.remove(json_sink)


def demo_json_with_context():
    """Demonstrate JSON logging with persistent context."""
    print("\n=== JSON with Context Demo ===")

    logger.reset()
    logger.configure(level="INFO", console=False)

    # Add JSON sink
    json_sink = logger.add(
        "context.jsonl",
        json=True,  # Enable JSON formatting
    )

    # Bind persistent context
    logger.bind(request_id="req-123", user_agent="Mozilla/5.0", service="api")

    print(f"Added JSON sink with context binding: {json_sink}")

    # All logs will include the bound context
    logger.info("Request started", method="GET", path="/api/users")
    logger.debug("Database query executed", query="SELECT * FROM users", duration_ms=45)
    logger.info("Response sent", status_code=200, response_size=1024)

    # Temporary context override
    with logger.contextualize(session_id="sess-456", trace_id="trace-789"):
        logger.info("Processing payment", amount=99.99, currency="USD")
        logger.warning("Payment processing slow", latency_ms=2500)

    # Back to original context
    logger.info("Request completed", total_duration_ms=3000)

    logger.remove(json_sink)


def demo_json_with_levels():
    """Demonstrate JSON logging with different levels."""
    print("\n=== JSON with Different Levels Demo ===")

    logger.reset()
    logger.configure(level="TRACE", console=False)

    # Add separate JSON files for different levels
    all_sink = logger.add("all_levels.jsonl", json=True)
    error_sink = logger.add("errors_only.jsonl", json=True, filter_min_level="ERROR")

    print("Added JSON sinks for all levels and errors only")

    # Log at different levels
    logger.trace("Debugging information", step="init", value=42)
    logger.debug("Detailed debug info", component="auth", user_id=789)
    logger.info("General information", action="login", success=True)
    logger.warning("Warning message", warning_type="deprecated", feature="old_api")
    logger.error(
        "Error occurred", error_type="validation", field="email", error_message="Invalid format"
    )
    logger.critical("Critical system error", system="database", impact="high")

    logger.remove(all_sink)
    logger.remove(error_sink)


def demo_json_pretty_print():
    """Demonstrate pretty-printed JSON for development."""
    print("\n=== Pretty JSON Demo ===")

    logger.reset()
    logger.configure(level="INFO", console=False)

    # Add pretty JSON sink (for development/debugging)
    pretty_sink = logger.add("pretty.json", json=True)

    print(f"Added pretty JSON sink with ID: {pretty_sink}")

    # Log some data
    logger.info("Application started", version="1.2.3", environment="development")
    logger.info(
        "Configuration loaded",
        config={"database": {"host": "localhost", "port": 5432}, "cache": {"ttl": 3600}},
    )

    logger.remove(pretty_sink)


def demo_json_custom_fields():
    """Demonstrate adding custom fields to JSON logs."""
    print("\n=== Custom Fields Demo ===")

    logger.reset()
    logger.configure(level="INFO", console=False)

    # Add JSON sink with custom fields in format string
    custom_sink = logger.add("custom.jsonl", json=True)

    print(f"Added JSON sink with custom fields: {custom_sink}")

    # All logs will include the custom fields
    logger.info("User action", user_id=123, action="view_profile")
    logger.warning("Rate limit exceeded", user_id=456, endpoint="/api/data", limit=100)

    logger.remove(custom_sink)


def main():
    """Run all JSON logging demos."""
    print("🚀 Logly JSON Logging Examples")
    print("=" * 50)

    try:
        demo_json_logging()
        demo_json_with_context()
        demo_json_with_levels()
        demo_json_pretty_print()
        demo_json_custom_fields()

        print("\n" + "=" * 50)
        print("✅ All JSON demos completed!")
        print("\n📁 Generated JSON files:")

        # List generated files
        json_files = [f for f in os.listdir(".") if f.endswith((".json", ".jsonl"))]
        for json_file in sorted(json_files):
            if os.path.exists(json_file):
                size = os.path.getsize(json_file)
                print(f"  - {json_file} ({size:,} bytes)")

        print("\n💡 Tip: Use 'jq' command to pretty-print and query JSON logs:")
        print("   jq . app.jsonl")
        print("   jq 'select(.level == \"ERROR\")' errors_only.jsonl")

    except (OSError, ValueError, RuntimeError) as e:
        print(f"\n❌ Demo failed: {e}")
        logger.exception("Demo failed", exc_info=e)


if __name__ == "__main__":
    main()
