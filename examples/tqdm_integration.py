"""tqdm integration example - log output through progress bars.

Demonstrates how TqdmSink redirects log messages through tqdm.write()
so progress bars are not corrupted by log output.

Requires: pip install tqdm
"""

from tqdm import tqdm

from logly import logger
from logly.integrations.tqdm import TqdmSink

# Remove default stderr sink and add tqdm sink
logger.remove()
logger.add(TqdmSink(), colorize=True)

# Simulate a long-running task with a progress bar
for i in tqdm(range(20), desc="Processing"):
    if i % 5 == 0:
        logger.info("Reached item {}", i)
    if i == 15:
        logger.warning("Item {} is slow", i)

logger.success("All items processed")
logger.complete()
