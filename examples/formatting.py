"""Custom formatters example - template strings and callable formatters."""

from typing import Any

from logly import logger

# Template format
sink_id = logger.add(
    "formatted.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name}:{function}:{line} - {message}",
)
logger.info("Formatted with template")
logger.remove(sink_id)


# Callable formatter
def my_formatter(record: dict[str, Any]) -> str:
    level = record.get("level", "UNKNOWN")
    message = record.get("message", "")
    return f"[{level}] {message}"


sink_id = logger.add("custom.log", format=my_formatter)
logger.info("Formatted with callable")
logger.remove(sink_id)

# JSON format
sink_id = logger.add("json.log", serialize=True)
logger.info("JSON formatted output")
logger.remove(sink_id)

# Format with extra fields
sink_id = logger.add(
    "extra_fields.log",
    format="{time} | {level} | {message} | user={extra[user_id]}",
)
logger.bind(user_id="12345").info("Log with extra fields")
logger.remove(sink_id)
