"""Context binding and scoped context example."""

from logly import logger

# Bind persistent context fields
bound_logger = logger.bind(user_id="12345", request_id="abc-789")
bound_logger.info("User logged in")
bound_logger.info("Processing request")
# All logs from bound_logger include user_id and request_id

# Contextualize with context manager
with logger.contextualize(session_id="xyz-000"):
    logger.info("Inside session context")
    logger.info("Still in context")
    # All logs in this block include session_id
# Context restored after block

# Nested contexts
with logger.contextualize(service="api"):
    with logger.contextualize(endpoint="/users"):
        logger.info("Processing request")
        # Both service and endpoint are included

# Context with file sink
sink_id = logger.add("context.log", level="DEBUG")
bound = logger.bind(env="production", version="1.0.0")
bound.info("Production log with context")
logger.complete()
logger.remove(sink_id)
