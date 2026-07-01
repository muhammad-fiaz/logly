"""Shared utilities for Logly integrations."""

from __future__ import annotations

import re

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from *text*.

    Args:
        text: String that may contain ANSI color/style codes.

    Returns:
        The string with all ANSI escape sequences removed.
    """
    return _ANSI_RE.sub("", text)
