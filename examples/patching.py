"""Patching example - modify log records before they reach sinks."""

from typing import Any

from logly import logger


# Global patcher - adds version to all records
def add_version(record: dict[str, Any]) -> None:
    record.setdefault("extra", {})["version"] = "1.0.0"


sink_id = logger.add("patched.log", patch=add_version)
logger.info("With version")
logger.remove(sink_id)


# Patch with multiple fields
def enrich_record(record: dict[str, Any]) -> None:
    extra = record.setdefault("extra", {})
    extra["env"] = "production"
    extra["region"] = "us-east-1"


sink_id = logger.add("enriched.log", patch=enrich_record)
logger.info("Enriched log entry")
logger.remove(sink_id)

# Scoped patcher
with logger.contextualize(service="api", version="2.0"):
    logger.info("Scoped context applies to all logs in this block")

logger.complete()
