from __future__ import annotations

import pytest

from logly.models import (
    CompressionPolicy,
    LoggerConfig,
    PrettyJsonConfig,
    RetentionPolicy,
    RotationPolicy,
    SinkConfig,
    ValidationError,
)


def test_sink_config_defaults() -> None:
    config = SinkConfig()

    assert config.level == "INFO"
    assert config.format == "{level} | {message}"
    assert config.append is True


def test_rotation_policy_validates_positive_value() -> None:
    with pytest.raises(ValidationError):
        RotationPolicy(kind="size", value=0)


def test_rotation_policy_valid_kind() -> None:
    policy = RotationPolicy(kind="size", value=1024)
    assert policy.kind == "size"
    assert policy.value == 1024


def test_rotation_policy_rejects_unknown_kind() -> None:
    with pytest.raises(ValidationError):
        RotationPolicy(kind="nope")  # type: ignore[arg-type]


def test_retention_policy_validates_positive() -> None:
    with pytest.raises(ValidationError):
        RetentionPolicy(count=-1)
    with pytest.raises(ValidationError):
        RetentionPolicy(seconds=0)


def test_compression_policy_rejects_invalid_codec() -> None:
    with pytest.raises(ValidationError):
        CompressionPolicy(codec="invalid")  # type: ignore[arg-type]


def test_logger_config_defaults() -> None:
    config = LoggerConfig()
    assert config.sinks == []
    assert config.disabled == set()


def test_logger_config_coerces_dicts() -> None:
    config = LoggerConfig(
        sinks=[{"level": "DEBUG"}],  # type: ignore[list-item]
        disabled=["myapp"],  # type: ignore[arg-type]
    )
    assert len(config.sinks) == 1
    assert config.sinks[0].level == "DEBUG"
    assert "myapp" in config.disabled


def test_pretty_json_config() -> None:
    config = PrettyJsonConfig(indent=2, sort_keys=True)
    assert config.indent == 2
    assert config.sort_keys is True


def test_to_dict_from_dict_roundtrip() -> None:
    config = SinkConfig(level="WARNING")
    dumped = config.to_dict()
    assert dumped["level"] == "WARNING"
    assert SinkConfig.from_dict(dumped).level == "WARNING"


def test_from_dict_rejects_non_mapping() -> None:
    with pytest.raises(ValidationError):
        SinkConfig.from_dict(["not", "a", "dict"])  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        RotationPolicy.from_dict("size")  # type: ignore[arg-type]


def test_from_dict_rejects_invalid_values() -> None:
    with pytest.raises(ValidationError):
        RotationPolicy.from_dict({"kind": "size", "value": 0})
    with pytest.raises(ValidationError):
        RetentionPolicy.from_dict({"count": -2})


def test_nested_from_dict_coercion() -> None:
    config = SinkConfig.from_dict(
        {
            "level": "DEBUG",
            "rotation": {"kind": "size", "value": 1024},
            "retention": {"count": 5},
            "compression": {"codec": "gzip"},
        }
    )
    assert isinstance(config.rotation, RotationPolicy)
    assert config.rotation.kind == "size"
    assert isinstance(config.retention, RetentionPolicy)
    assert config.retention.count == 5
    assert isinstance(config.compression, CompressionPolicy)
    assert config.compression.codec == "gzip"


def test_logger_config_from_dict() -> None:
    config = LoggerConfig.from_dict(
        {"sinks": [{"level": "ERROR", "serialize": True}], "disabled": ["noisy"]}
    )
    assert len(config.sinks) == 1
    assert config.sinks[0].level == "ERROR"
    assert config.disabled == {"noisy"}


def test_no_pydantic_dependency() -> None:
    """Logly configuration must not require, import, or detect Pydantic."""
    import subprocess
    import sys

    probe = (
        "import sys, logly, logly.models;"
        "assert 'pydantic' not in sys.modules, 'pydantic imported';"
        "assert 'pydantic_core' not in sys.modules, 'pydantic_core imported';"
        "assert not hasattr(logly.models, 'is_pydantic_available')"
    )
    subprocess.run([sys.executable, "-c", probe], check=True)

    import logly.models as models_module

    for name in (
        "RotationPolicy",
        "RetentionPolicy",
        "CompressionPolicy",
        "PrettyJsonConfig",
        "SinkConfig",
        "LoggerConfig",
    ):
        cls = getattr(models_module, name)
        assert not hasattr(cls, "__get_pydantic_core_schema__")
        assert not hasattr(cls, "model_validate")
        assert not hasattr(cls, "model_dump")
