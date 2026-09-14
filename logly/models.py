"""Stdlib dataclass models for Logly configuration and validation.

This module provides validated configuration models for log sinks,
rotation policies, retention policies, and compression settings.
It uses only the Python standard library (``dataclasses``) with targeted
runtime validation, so ``pydantic`` is **not** required.

Optional pydantic interop (``uv add logly[pydantic]``):

- The dataclasses work with zero dependencies out of the box.
- If pydantic v2 is installed, each model exposes
  ``__get_pydantic_core_schema__``, so you can nest them directly inside
  your own ``pydantic.BaseModel`` or validate them with
  ``pydantic.TypeAdapter``.
- :func:`is_pydantic_available` lets you branch on availability.
- :meth:`model_validate` accepts plain dicts *and* pydantic model
  instances (via ``model_dump()``).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


class ValidationError(ValueError):
    """Raised when a configuration model fails validation.

    Subclasses :exc:`ValueError` for back-compat with code that previously
    caught ``pydantic.ValidationError`` (which itself subclasses
    :exc:`ValueError`). Import from here instead of ``pydantic``::

        from logly.models import ValidationError
    """


_ROTATION_KINDS: frozenset[str] = frozenset(
    {"never", "size", "interval", "clock", "weekday", "callable"}
)

_COMPRESSION_CODECS: frozenset[str] = frozenset(
    {
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
    }
)


def _dump(obj: Any) -> dict[str, Any]:
    return asdict(obj)


def is_pydantic_available() -> bool:
    """Return ``True`` if pydantic v2 is importable.

    Use it to gate optional pydantic-only code paths::

        from logly.models import is_pydantic_available

        if is_pydantic_available():
            adapter = TypeAdapter(SinkConfig)  # needs logly[pydantic]
    """
    try:
        import pydantic  # noqa: F401
    except ImportError:
        return False
    return True


def _unwrap_pydantic_model(data: Any) -> Any:
    """Unwrap a pydantic model instance to a plain dict, if applicable."""
    dump = getattr(data, "model_dump", None)
    if callable(dump):
        try:
            return dump()
        except Exception:
            return data
    return data


def _pydantic_core_schema(cls: type[Any], source_type: Any, handler: Any) -> Any:
    """Build a pydantic-core schema delegating validation to the dataclass.

    Lazy-imports ``pydantic_core`` so the core package stays dependency-free.
    """
    from pydantic_core import core_schema  # noqa: PLC0415

    def _validate(value: Any) -> Any:
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            return cls(**value)
        unwrapped = _unwrap_pydantic_model(value)
        if isinstance(unwrapped, dict):
            return cls(**unwrapped)
        raise ValueError(
            f"expected {cls.__name__}, dict, or pydantic model, "
            f"got {type(value).__name__}"
        )

    return core_schema.no_info_plain_validator_function(
        _validate,
        serialization=core_schema.plain_serializer_function_ser_schema(
            lambda v: asdict(v),
            return_schema=core_schema.dict_schema(),
        ),
    )


@dataclass
class RotationPolicy:
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
    value: Any = None

    def __post_init__(self) -> None:
        if self.kind not in _ROTATION_KINDS:
            raise ValidationError(
                f"kind must be one of {sorted(_ROTATION_KINDS)}, got {self.kind!r}"
            )
        if self.kind in ("size", "interval"):
            if isinstance(self.value, bool) or (
                isinstance(self.value, int) and self.value <= 0
            ):
                raise ValidationError(
                    "value must be positive for size or interval rotation"
                )

    def model_dump(self) -> dict[str, Any]:
        """Return a dict representation (pydantic-compat shim)."""
        return _dump(self)

    @classmethod
    def model_validate(cls, data: Any) -> RotationPolicy:
        """Build from a dict or pydantic model (pydantic-compat shim)."""
        if not isinstance(data, dict):
            data = _unwrap_pydantic_model(data)
        return cls(**data)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> Any:
        """Allow nesting inside user ``pydantic.BaseModel`` (needs ``logly[pydantic]``)."""
        return _pydantic_core_schema(cls, source_type, handler)


@dataclass
class RetentionPolicy:
    """Validated rotated-file retention configuration.

    Controls how many rotated log files are kept and for how long.

    Attributes:
        count: Maximum number of retained files. Must be >= 1 if set.
        seconds: Maximum retained age in seconds. Must be >= 1 if set.

    Example::

        RetentionPolicy(count=10)  # Keep last 10 files
        RetentionPolicy(seconds=86400 * 30)  # Keep 30 days
    """

    count: int | None = None
    seconds: int | None = None

    def __post_init__(self) -> None:
        for name in ("count", "seconds"):
            val = getattr(self, name)
            if val is None:
                continue
            if isinstance(val, bool) or not isinstance(val, int) or val < 1:
                raise ValidationError(f"{name} must be an int >= 1, got {val!r}")

    def model_dump(self) -> dict[str, Any]:
        """Return a dict representation (pydantic-compat shim)."""
        return _dump(self)

    @classmethod
    def model_validate(cls, data: Any) -> RetentionPolicy:
        """Build from a dict or pydantic model (pydantic-compat shim)."""
        if not isinstance(data, dict):
            data = _unwrap_pydantic_model(data)
        return cls(**data)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> Any:
        """Allow nesting inside user ``pydantic.BaseModel`` (needs ``logly[pydantic]``)."""
        return _pydantic_core_schema(cls, source_type, handler)


@dataclass
class CompressionPolicy:
    """Validated rotated-file compression configuration.

    Controls how rotated log files are compressed.

    Attributes:
        codec: Compression codec name. Supported codecs:

            - ``"none"``: No compression (default).
            - ``"gzip"`` / ``"gz"``: Gzip compression.
            - ``"zip"``: Zip archive.
            - ``"bz2"``: Bzip2 compression.
            - ``"xz"`` / ``"lzma"``: XZ compression.
            - ``"zstd"``: Zstandard compression.

            Aliases that resolve to their base codec:

            - ``"tar"`` → ``"gzip"``
            - ``"tar.gz"`` / ``"tgz"`` → ``"gzip"``
            - ``"tar.bz2"`` → ``"bz2"``
            - ``"tar.xz"`` → ``"xz"``

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

    def __post_init__(self) -> None:
        if self.codec not in _COMPRESSION_CODECS:
            raise ValidationError(
                f"codec must be one of {sorted(_COMPRESSION_CODECS)}, got {self.codec!r}"
            )

    def model_dump(self) -> dict[str, Any]:
        """Return a dict representation (pydantic-compat shim)."""
        return _dump(self)

    @classmethod
    def model_validate(cls, data: Any) -> CompressionPolicy:
        """Build from a dict or pydantic model (pydantic-compat shim)."""
        if not isinstance(data, dict):
            data = _unwrap_pydantic_model(data)
        return cls(**data)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> Any:
        """Allow nesting inside user ``pydantic.BaseModel`` (needs ``logly[pydantic]``)."""
        return _pydantic_core_schema(cls, source_type, handler)


@dataclass
class PrettyJsonConfig:
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

    indent: int | None = 4
    sort_keys: bool = False
    ensure_ascii: bool = False
    separators: tuple[str, str] | None = None

    def __post_init__(self) -> None:
        if self.indent is not None and (
            isinstance(self.indent, bool)
            or not isinstance(self.indent, int)
            or self.indent < 0
        ):
            raise ValidationError(f"indent must be a non-negative int or None, got {self.indent!r}")
        if self.separators is not None:
            if (
                not isinstance(self.separators, (tuple, list))
                or len(self.separators) != 2
                or not all(isinstance(s, str) for s in self.separators)
            ):
                raise ValidationError(
                    "separators must be a (item_separator, key_separator) tuple of str"
                )
            self.separators = (str(self.separators[0]), str(self.separators[1]))

    def model_dump(self) -> dict[str, Any]:
        """Return a dict representation (pydantic-compat shim)."""
        return _dump(self)

    @classmethod
    def model_validate(cls, data: Any) -> PrettyJsonConfig:
        """Build from a dict or pydantic model (pydantic-compat shim)."""
        if not isinstance(data, dict):
            data = _unwrap_pydantic_model(data)
        return cls(**data)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> Any:
        """Allow nesting inside user ``pydantic.BaseModel`` (needs ``logly[pydantic]``)."""
        return _pydantic_core_schema(cls, source_type, handler)


def _coerce_rotation(value: RotationPolicy | dict[str, Any] | None) -> RotationPolicy | None:
    if value is None or isinstance(value, RotationPolicy):
        return value
    if isinstance(value, dict):
        return RotationPolicy(**value)
    raise ValidationError(f"rotation must be RotationPolicy, dict, or None, got {value!r}")


def _coerce_retention(value: RetentionPolicy | dict[str, Any] | None) -> RetentionPolicy | None:
    if value is None or isinstance(value, RetentionPolicy):
        return value
    if isinstance(value, dict):
        return RetentionPolicy(**value)
    raise ValidationError(f"retention must be RetentionPolicy, dict, or None, got {value!r}")


def _coerce_compression(
    value: CompressionPolicy | dict[str, Any] | None,
) -> CompressionPolicy | None:
    if value is None or isinstance(value, CompressionPolicy):
        return value
    if isinstance(value, dict):
        return CompressionPolicy(**value)
    raise ValidationError(
        f"compression must be CompressionPolicy, dict, or None, got {value!r}"
    )


def _coerce_pretty_json(
    value: PrettyJsonConfig | dict[str, Any] | None,
) -> PrettyJsonConfig | None:
    if value is None or isinstance(value, PrettyJsonConfig):
        return value
    if isinstance(value, dict):
        return PrettyJsonConfig(**value)
    raise ValidationError(
        f"pretty_json must be PrettyJsonConfig, dict, or None, got {value!r}"
    )


@dataclass
class SinkConfig:
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
    rotation: RotationPolicy | dict[str, Any] | None = None
    retention: RetentionPolicy | dict[str, Any] | None = None
    compression: CompressionPolicy | dict[str, Any] | None = None
    enqueue: bool = False
    colorize: bool | None = None
    serialize: bool = False
    pretty_json: PrettyJsonConfig | dict[str, Any] | None = None
    append: bool = True
    mode: Literal["append", "overwrite"] = "append"

    def __post_init__(self) -> None:
        # Accept plain dicts like pydantic did, coercing to nested models.
        object.__setattr__(self, "rotation", _coerce_rotation(self.rotation))
        object.__setattr__(self, "retention", _coerce_retention(self.retention))
        object.__setattr__(self, "compression", _coerce_compression(self.compression))
        object.__setattr__(self, "pretty_json", _coerce_pretty_json(self.pretty_json))
        if self.mode not in ("append", "overwrite"):
            raise ValidationError(
                f"mode must be 'append' or 'overwrite', got {self.mode!r}"
            )

    def model_dump(self) -> dict[str, Any]:
        """Return a dict representation (pydantic-compat shim)."""
        return _dump(self)

    @classmethod
    def model_validate(cls, data: Any) -> SinkConfig:
        """Build from a dict or pydantic model (pydantic-compat shim)."""
        if not isinstance(data, dict):
            data = _unwrap_pydantic_model(data)
        return cls(**data)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> Any:
        """Allow nesting inside user ``pydantic.BaseModel`` (needs ``logly[pydantic]``)."""
        return _pydantic_core_schema(cls, source_type, handler)


@dataclass
class LoggerConfig:
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

    sinks: list[SinkConfig] = field(default_factory=list)
    disabled: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        coerced: list[SinkConfig] = []
        for item in self.sinks:
            if isinstance(item, SinkConfig):
                coerced.append(item)
            elif isinstance(item, dict):
                coerced.append(SinkConfig(**item))
            else:
                raise ValidationError(
                    "sinks must be a list of SinkConfig or dict, "
                    f"got {item!r}"
                )
        object.__setattr__(self, "sinks", coerced)
        if isinstance(self.disabled, (list, tuple)):
            object.__setattr__(self, "disabled", set(self.disabled))
        if not isinstance(self.disabled, set):
            raise ValidationError(
                f"disabled must be a set of str, got {self.disabled!r}"
            )

    def model_dump(self) -> dict[str, Any]:
        """Return a dict representation (pydantic-compat shim)."""
        return _dump(self)

    @classmethod
    def model_validate(cls, data: Any) -> LoggerConfig:
        """Build from a dict or pydantic model (pydantic-compat shim)."""
        if not isinstance(data, dict):
            data = _unwrap_pydantic_model(data)
        return cls(**data)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> Any:
        """Allow nesting inside user ``pydantic.BaseModel`` (needs ``logly[pydantic]``)."""
        return _pydantic_core_schema(cls, source_type, handler)


__all__ = [
    "CompressionPolicy",
    "LoggerConfig",
    "PrettyJsonConfig",
    "RetentionPolicy",
    "RotationPolicy",
    "SinkConfig",
    "ValidationError",
    "is_pydantic_available",
]
