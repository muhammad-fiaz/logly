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
