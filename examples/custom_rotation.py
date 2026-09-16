"""Custom rotation conditions and level ordering."""

from logly import Logger, logger
from logly.models import RotationPolicy

logger.remove()

# Rotate with a custom condition: path and current size in bytes in,
# boolean out. Consulted after every write the other strategies skip.
logger.add("conditional.log", rotation=lambda path, size: size > 1_000_000)
logger.info("Rotates past one megabyte")

# Same rule expressed as a policy object.
logger.add(
    "policy.log",
    rotation=RotationPolicy(kind="callable", value=lambda path, size: size > 1_000_000),
)
logger.info("Policy-object condition")

# Levels compare by numeric severity.
low = logger.level("DEBUG")
high = logger.level("ERROR")
assert low < high

# Independent logger with its own sink set.
audit_log = Logger()
audit_log.level("AUDIT", no=35, color="green")
audit_log.add("audit.log", level="AUDIT")
audit_log.audit("Admin signed in")
audit_log.complete()

logger.complete()
