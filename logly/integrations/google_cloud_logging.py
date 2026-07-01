"""Google Cloud Logging integration for Logly.

Provides ``GoogleCloudLoggingSink`` that sends log entries to
Google Cloud Logging (formerly Stackdriver).

Requires ``google-cloud-logging``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[google-cloud-logging]

    # Option 2: pip
    pip install "logly[google-cloud-logging]"

    # Option 3: uv without extras
    uv add google-cloud-logging

    # Option 4: pip without extras
    pip install google-cloud-logging
"""

from __future__ import annotations

import importlib.util
from typing import Any

if importlib.util.find_spec("google.cloud.logging") is None:
    _has_google_cloud_logging: bool = False
else:
    _has_google_cloud_logging = True

_IMPORT_MSG = (
    "google-cloud-logging is required for Logly Google Cloud Logging integration.\n"
    "Install with one of:\n"
    "  uv add logly[google-cloud-logging]       # recommended\n"
    "  pip install logly[google-cloud-logging]\n"
    "  uv add google-cloud-logging\n"
    "  pip install google-cloud-logging"
)


class GoogleCloudLoggingSink:
    """Send log entries to Google Cloud Logging.

    Usage::

        from logly import logger
        from logly.integrations.google_cloud_logging import GoogleCloudLoggingSink

        logger.add(
            GoogleCloudLoggingSink(
                project_id="my-project",
                log_name="my-app",
            ),
            level="WARNING",
        )

    Args:
        project_id: Google Cloud project ID.
        log_name: Name of the log to write to.
        resource: Optional ``google.cloud.logging.Resource`` object.
            If ``None``, a generic global resource is used.
        credentials: Optional ``google.auth.credentials.Credentials`` object.
            If ``None``, uses Application Default Credentials.

    Raises:
        ImportError: If ``google-cloud-logging`` is not installed.
    """

    def __init__(
        self,
        project_id: str = "",
        *,
        log_name: str = "logly",
        resource: Any = None,
        credentials: Any = None,
    ) -> None:
        """Initialize the Google Cloud Logging sink.

        Args:
            project_id: Google Cloud project ID.
            log_name: Name of the log to write to.
            resource: Optional ``google.cloud.logging.Resource`` object.
            credentials: Optional ``google.auth.credentials.Credentials`` object.

        Raises:
            ImportError: If ``google-cloud-logging`` is not installed.
        """
        if not _has_google_cloud_logging:
            raise ImportError(_IMPORT_MSG)

        from google.cloud.logging import Client as _GCLClient

        client_kwargs: dict[str, Any] = {}
        if project_id:
            client_kwargs["project"] = project_id
        if credentials is not None:
            client_kwargs["credentials"] = credentials

        self._client = _GCLClient(**client_kwargs)
        self._log_name = log_name
        self._resource = resource
        self._gcl_logger = self._client.logger(log_name)

    def write(self, message: str) -> None:
        """Send one log entry to Google Cloud Logging.

        Args:
            message: The formatted log message to send.
        """
        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        msg = strip_ansi(message.rstrip("\n"))
        severity = self._detect_severity(msg)

        struct_data: dict[str, Any] = {
            "message": msg,
        }

        self._gcl_logger.log_struct(
            struct_data,
            severity=severity,
        )

    @staticmethod
    def _detect_severity(message: str) -> str:
        """Detect log severity from message content.

        Args:
            message: The log message string.

        Returns:
            Google Cloud Logging severity string.
        """
        upper = message.upper()
        if "FATAL" in upper or "CRITICAL" in upper:
            return "CRITICAL"
        if "ERROR" in upper or "FAIL" in upper:
            return "ERROR"
        if "WARNING" in upper or "WARN" in upper:
            return "WARNING"
        if "NOTICE" in upper:
            return "INFO"
        if "SUCCESS" in upper:
            return "INFO"
        if "DEBUG" in upper or "TRACE" in upper:
            return "DEBUG"
        return "INFO"

    def flush(self) -> None:
        """No-op for Google Cloud Logging sink."""

    def close(self) -> None:
        """Close the underlying client."""
        try:
            self._client.close()
        except Exception:
            pass
