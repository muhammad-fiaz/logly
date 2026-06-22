"""Compression example - gzip, zip, bz2, xz."""

from logly import logger

# Gzip compression
sink_id = logger.add("app.gz.log", compression="gzip", rotation="daily")
logger.info("Compressed with gzip")
logger.complete()
logger.remove(sink_id)

# Zip compression
sink_id = logger.add("app.zip.log", compression="zip", rotation="daily")
logger.info("Compressed with zip")
logger.complete()
logger.remove(sink_id)

# Bz2 compression
sink_id = logger.add("app.bz2.log", compression="bz2", rotation="daily")
logger.info("Compressed with bz2")
logger.complete()
logger.remove(sink_id)

# Xz compression
sink_id = logger.add("app.xz.log", compression="xz", rotation="daily")
logger.info("Compressed with xz")
logger.complete()
logger.remove(sink_id)

# No compression
sink_id = logger.add("app.raw.log", compression=None)
logger.info("No compression")
logger.complete()
logger.remove(sink_id)
