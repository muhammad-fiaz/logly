"""Lazy evaluation example - deferred message and exception capturing."""

from logly import logger


def expensive_operation() -> str:
    return "computed value"


def get_username() -> str:
    return "alice"


def get_ip_address() -> str:
    return "10.0.0.1"


# Lazy message evaluation
logger.opt(lazy=True).debug("Result: {}", expensive_operation)
# expensive_operation() is only called if DEBUG level is enabled

# Lazy exception capture
try:
    risky_operation = 1 / 0
except ZeroDivisionError:
    logger.opt(exception=True).error("Division failed")

# Lazy with extra data
logger.opt(lazy=True).info(
    "User {} logged in from {}",
    get_username,
    get_ip_address,
)

logger.complete()
