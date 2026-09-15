"""Shared utilities for Logly integrations."""

from __future__ import annotations

import re
from typing import Any

from logly import logger

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from *text*.

    Args:
        text: String that may contain ANSI color/style codes.

    Returns:
        The string with all ANSI escape sequences removed.
    """
    return _ANSI_RE.sub("", text)


def detect_canonical_level(message: str) -> str:
    """Infer a canonical level name from a formatted log message.

    Checks level tokens in severity-priority order so a message containing
    multiple tokens (e.g. ``"CRITICAL ... ERROR ..."``) resolves to the
    most severe one.

    Args:
        message: The formatted log message string.

    Returns:
        One of ``"CRITICAL"``, ``"ERROR"``, ``"WARNING"``, ``"NOTICE"``,
        ``"SUCCESS"``, ``"TRACE"``, ``"DEBUG"``, or ``"INFO"``.
    """
    upper = message.upper()
    if "FATAL" in upper or "CRITICAL" in upper:
        return "CRITICAL"
    if "ERROR" in upper or "FAIL" in upper:
        return "ERROR"
    if "WARNING" in upper or "WARN" in upper:
        return "WARNING"
    if "NOTICE" in upper:
        return "NOTICE"
    if "SUCCESS" in upper:
        return "SUCCESS"
    if "TRACE" in upper:
        return "TRACE"
    if "DEBUG" in upper:
        return "DEBUG"
    return "INFO"


def cli_echo(message: Any = None, *, err: bool = False) -> None:
    """Route CLI ``echo`` output through Logly (shared by click/typer).

    Args:
        message: Message to log. ``None`` is a no-op.
        err: If ``True``, log at ``WARNING``; otherwise ``INFO``.
    """
    if message is None:
        return
    level = "WARNING" if err else "INFO"
    try:
        logger.log(level, str(message))
    except Exception:
        pass
