"""Pydantic models for Logly configuration and validation.

This module provides validated configuration models for log sinks,
rotation policies, retention policies, and compression settings.
All models use Pydantic for automatic validation and serialization.
"""

from __future__ import annotations

import sys
from typing import Literal

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from pydantic import BaseModel, Field, model_validator


class RotationPolicy(BaseModel):
    """Validated file rotation configuration.

    Controls how log files are rotated (split into new files).

    Attributes:
        kind: Rotation strategy name. Options:

            - ``"never"``: No rotation (default).
            - ``"size"``: Rotate when file reaches ``value`` bytes.
            - ``"interval"``: Rotate every ``value`` seconds.
            - ``"clock"``: Rotate at clock-based intervals.
            - ``"weekday"``: Rotate on specific weekdays.
            - ``"callable"``: Use a custom rotation function.

        value: Strategy-dependent value (byte count, interval seconds, etc.).

    Example::

        RotationPolicy(kind="size", value=10_000_000)  # 10 MB
        RotationPolicy(kind="interval", value=3600)  # 1 hour
    """

    kind: Literal["never", "size", "interval", "clock", "weekday", "callable"] = "never"
    value: int | str | None = None

    @model_validator(mode="after")
    def validate_value(self) -> Self:
        """Validate that value is positive for size/interval rotation."""
        if self.kind in ("size", "interval"):
            if isinstance(self.value, int) and self.value <= 0:
                raise ValueError("value must be positive for size or interval rotation")
        return self


class RetentionPolicy(BaseModel):
    """Validated rotated-file retention configuration.

    Controls how many rotated log files are kept and for how long.

    Attributes:
        count: Maximum number of retained files. Must be >= 1 if set.
        seconds: Maximum retained age in seconds. Must be >= 1 if set.

    Example::

        RetentionPolicy(count=10)  # Keep last 10 files
        RetentionPolicy(seconds=86400 * 30)  # Keep 30 days
    """

    count: int | None = Field(default=None, ge=1)
    seconds: int | None = Field(default=None, ge=1)


class CompressionPolicy(BaseModel):
    """Validated rotated-file compression configuration.

    Controls how rotated log files are compressed.

    Attributes:
        codec: Compression codec name. Supported codecs:

            - ``"none"``: No compression (default).
            - ``"gzip"`` / ``"gz"``: Gzip compression.
            - ``"zip"``: Zip archive.
            - ``"bz2"``: Bzip2 compression.
            - ``"xz"``: XZ compression.
            - ``"lzma"``: LZMA compression.
            - ``"zstd"``: Zstandard compression.
            - ``"tar"``: Tar archive.
            - ``"tar.gz"`` / ``"tgz"``: Tar + gzip.
            - ``"tar.bz2"``: Tar + bzip2.
            - ``"tar.xz"``: Tar + xz.

    Example::

        CompressionPolicy(codec="gzip")
    """

    codec: Literal[
        "none",
        "gzip",
        "zip",
        "bz2",
        "xz",
        "lzma",
        "zstd",
        "gz",
        "tar",
        "tar.gz",
        "tgz",
        "tar.bz2",
        "tar.xz",
    ] = "none"


class PrettyJsonConfig(BaseModel):
    """Configuration for pretty-printed JSON output.

    When enabled, log records are formatted as indented, human-readable
    JSON instead of compact JSON.

    Attributes:
        indent: Number of spaces for indentation (default: 4).
        sort_keys: Whether to sort dictionary keys alphabetically.
        ensure_ascii: Whether to escape non-ASCII characters.
        separators: Optional tuple of ``(item_separator, key_separator)``.

    Example::

        PrettyJsonConfig(indent=2, sort_keys=True)
    """

    indent: int = 4
    sort_keys: bool = False
    ensure_ascii: bool = False
    separators: tuple[str, str] | None = None


class SinkConfig(BaseModel):
    """Validated sink configuration.

    Defines the complete configuration for a log sink, including
    output format, rotation, retention, and compression settings.

    Attributes:
        level: Minimum level accepted by the sink (default: ``"INFO"``).
        format: Native template string for log formatting.
        rotation: Optional rotation policy.
        retention: Optional retention policy.
        compression: Optional compression policy.
        enqueue: Whether to dispatch through a background worker.
        colorize: Explicit ANSI colorization override.
        serialize: Whether to emit JSON records.
        pretty_json: Optional pretty JSON configuration.
        append: Whether file sinks append instead of truncating.
        mode: File open mode (``"append"`` or ``"overwrite"``).

    Example::

        SinkConfig(
            level="WARNING",
            rotation=RotationPolicy(kind="size", value=10_000_000),
            retention=RetentionPolicy(count=5),
        )
    """

    level: str = "INFO"
    format: str = "{level} | {message}"
    rotation: RotationPolicy | None = None
    retention: RetentionPolicy | None = None
    compression: CompressionPolicy | None = None
    enqueue: bool = False
    colorize: bool | None = None
    serialize: bool = False
    pretty_json: PrettyJsonConfig | None = None
    append: bool = True
    mode: Literal["append", "overwrite"] = "append"


class LoggerConfig(BaseModel):
    """Validated logger configuration.

    Represents a complete logger configuration with multiple sinks
    and disabled logger names.

    Attributes:
        sinks: List of sink configurations to install.
        disabled: Set of logger names disabled by default.

    Example::

        LoggerConfig(
            sinks=[
                SinkConfig(level="INFO"),
                SinkConfig(level="ERROR", serialize=True),
            ],
            disabled={"debug-only-logger"},
        )
    """

    sinks: list[SinkConfig] = Field(default_factory=list)
    disabled: set[str] = Field(default_factory=set)
