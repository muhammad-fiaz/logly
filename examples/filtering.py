"""Filtering example - level, prefix, callable, and mapping filters."""

from typing import Any

from logly import logger

# Level filter (minimum level)
sink_id = logger.add("filtered.log", level="WARNING")
logger.info("This won't appear in filtered.log")
logger.warning("This will appear")
logger.error("This will also appear")
logger.remove(sink_id)


# Callable filter
def my_filter(record: dict[str, Any]) -> bool:
    return "important" in record.get("message", "")


sink_id = logger.add("important.log", filter=my_filter)
logger.info("not important")
logger.info("very important message")
logger.remove(sink_id)

# Prefix filter
sink_id = logger.add("myapp.log", filter={"name": "myapp."})
logger.info("myapp.module - this appears")
logger.remove(sink_id)

# Mapping filter with multiple conditions
sink_id = logger.add(
    "filtered.log",
    filter={"name": "myapp.", "extra.status": "active"},
)
logger.info("Filtered log entry")
logger.remove(sink_id)

# Combine level and filter
sink_id = logger.add(
    "combined.log",
    level="DEBUG",
    filter=my_filter,
)
logger.info("not important - skipped")
logger.info("important message - included at DEBUG")
logger.remove(sink_id)
