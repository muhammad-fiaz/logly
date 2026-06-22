"""Rich console integration example."""

from logly import logger
from logly.integrations.rich import LoglyRichSink

# Add Rich sink
sink_id = logger.add(LoglyRichSink(), colorize=True)
logger.info("Rich-formatted output!")
logger.warning("Warning with Rich styling")
logger.error("Error with Rich styling")
logger.success("Success with Rich styling")
logger.complete()
logger.remove(sink_id)
