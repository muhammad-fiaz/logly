"""Exception catching example - context manager and decorator."""

from logly import logger

# Context manager - suppresses exception
with logger.catch():
    result = 1 / 0

# Context manager - re-raises exception
try:
    with logger.catch(reraise=True):
        raise ValueError("Something went wrong")
except ValueError:
    pass

# Context manager with custom level
with logger.catch(level="CRITICAL"):
    raise ConnectionError("Cannot connect to database")


# Decorator - catches exceptions
@logger.catch()
def risky_function() -> None:
    raise TypeError("Decorated error")


risky_function()

# With reraise
with logger.catch(reraise=True):
    raise TimeoutError("Request timed out")

logger.complete()
