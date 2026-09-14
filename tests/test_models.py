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
    is_pydantic_available,
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


def test_model_dump_compat() -> None:
    config = SinkConfig(level="WARNING")
    dumped = config.model_dump()
    assert dumped["level"] == "WARNING"
    assert SinkConfig.model_validate(dumped).level == "WARNING"


def test_is_pydantic_available_returns_bool() -> None:
    assert isinstance(is_pydantic_available(), bool)


def test_pydantic_type_adapter() -> None:
    pydantic = pytest.importorskip("pydantic")
    adapter = pydantic.TypeAdapter(SinkConfig)
    assert adapter.validate_python({"level": "INFO"}).level == "INFO"
    with pytest.raises(ValueError):
        adapter.validate_python({"rotation": {"kind": "size", "value": 0}})


def test_pydantic_nested_model() -> None:
    pydantic = pytest.importorskip("pydantic")

    class AppConfig(pydantic.BaseModel):  # type: ignore[name-defined]
        sink: SinkConfig

    app = AppConfig.model_validate({"sink": {"level": "DEBUG"}})
    assert app.sink.level == "DEBUG"
    assert SinkConfig.model_validate(app.sink).level == "DEBUG"
