"""Type definitions for the Logly logging library.

Provides type aliases and protocols used throughout the Logly API
for type safety and IDE support.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Protocol, TextIO, TypeAlias

LevelType: TypeAlias = str | int
"""Type alias for log levels - either a string name (e.g. ``"INFO"``) or integer."""

SinkTarget: TypeAlias = str | Path | TextIO | Callable[[str], object]
"""Type alias for valid sink targets - file paths, file objects, or callables."""

FormatterCallable: TypeAlias = Callable[[dict[str, object]], str]
"""Type alias for custom formatter callables that accept a record dict and return a string."""

FilterCallable: TypeAlias = Callable[[dict[str, object]], bool]
"""Type alias for custom filter callables that accept a record dict and return a bool."""


class WriteSink(Protocol):
    """Protocol for custom write-style sinks.

    Any object implementing a ``write`` method matching this signature
    can be used as a Logly sink target.
    """

    def write(self, message: str) -> object:
        """Write a rendered log message.

        Args:
            message: The formatted log message string.

        Returns:
            Any return value (typically ignored by Logly).
        """
