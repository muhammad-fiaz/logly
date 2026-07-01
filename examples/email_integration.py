"""Email integration example.

Sends log entries as emails via SMTP for critical alerts.
Uses stdlib smtplib - no extra dependencies needed.
"""

from logly import logger
from logly.integrations.email import EmailHandler

# Configure email handler for critical alerts only
# Replace with real SMTP credentials in production
handler = EmailHandler(
    smtp_host="smtp.example.com",
    smtp_port=587,
    from_addr="alerts@example.com",
    to_addrs=["ops@example.com"],
    username="alerts@example.com",
    password="app-password",
    use_tls=True,
    subject_prefix="[MyApp]",
)

# Add handler at CRITICAL level - only fires on severe errors
logger.add(handler, level="CRITICAL")

# These will NOT trigger an email
logger.info("Normal operation")
logger.warning("Disk usage at 80%")

# This WOULD trigger an email (but SMTP server must be reachable)
# logger.critical("Database connection pool exhausted")

logger.complete()
