"""Email integration for Logly.

Provides ``EmailHandler`` that sends log entries as emails.

No extra dependencies required - uses ``smtplib`` from the
Python standard library.
"""

from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailHandler:
    """Send log entries as emails via SMTP.

    Usage::

        from logly import logger
        from logly.integrations.email import EmailHandler

        handler = EmailHandler(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            from_addr="alerts@example.com",
            to_addrs=["ops@example.com"],
            username="alerts@example.com",
            password="app-password",
        )
        logger.add(handler, level="ERROR")

    Args:
        smtp_host: SMTP server hostname.
        smtp_port: SMTP server port.
        from_addr: Sender email address.
        to_addrs: List of recipient email addresses.
        username: SMTP authentication username.
        password: SMTP authentication password.
        use_tls: Whether to use STARTTLS.
        use_ssl: Whether to use SSL/TLS from the start.
        timeout: SMTP connection timeout in seconds.
        subject_prefix: Prefix added to email subject lines.
    """

    def __init__(
        self,
        smtp_host: str = "localhost",
        smtp_port: int = 25,
        *,
        from_addr: str = "",
        to_addrs: list[str] | None = None,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool = True,
        use_ssl: bool = False,
        timeout: float = 30.0,
        subject_prefix: str = "[Logly]",
    ) -> None:
        """Initialize the Email handler.

        Args:
            smtp_host: SMTP server hostname.
            smtp_port: SMTP server port.
            from_addr: Sender email address.
            to_addrs: List of recipient email addresses.
            username: SMTP authentication username.
            password: SMTP authentication password.
            use_tls: Whether to use STARTTLS.
            use_ssl: Whether to use SSL/TLS from the start.
            timeout: SMTP connection timeout in seconds.
            subject_prefix: Prefix added to email subject lines.
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.from_addr = from_addr
        self.to_addrs = to_addrs or []
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.subject_prefix = subject_prefix

    def write(self, message: str) -> None:
        """Send one log message as an email."""
        if not self.from_addr or not self.to_addrs:
            return

        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        msg = MIMEMultipart()
        msg["From"] = self.from_addr
        msg["To"] = ", ".join(self.to_addrs)
        msg["Subject"] = f"{self.subject_prefix} Log Message"
        msg.attach(MIMEText(strip_ansi(message.rstrip("\n")), "plain"))

        try:
            server: smtplib.SMTP | smtplib.SMTP_SSL
            if self.use_ssl:
                server = smtplib.SMTP_SSL(  # pragma: no cover
                    self.smtp_host,
                    self.smtp_port,
                    timeout=self.timeout,
                )
            else:
                server = smtplib.SMTP(  # pragma: no cover
                    self.smtp_host,
                    self.smtp_port,
                    timeout=self.timeout,
                )

            try:
                if self.use_tls and not self.use_ssl:
                    server.starttls()  # pragma: no cover
                if self.username and self.password:
                    server.login(self.username, self.password)  # pragma: no cover
                server.sendmail(self.from_addr, self.to_addrs, msg.as_string())  # pragma: no cover
            finally:
                server.quit()
        except Exception:
            pass

    def flush(self) -> None:
        """No-op for Email handler."""

    def close(self) -> None:
        """No-op for Email handler."""
