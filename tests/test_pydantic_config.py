"""Tests for Pydantic config models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from logly.models import (
    CompressionPolicy,
    LoggerConfig,
    RetentionPolicy,
    RotationPolicy,
    SinkConfig,
)


class TestPydanticConfig:
    """Tests for Pydantic configuration models."""

    def test_sink_config_defaults(self) -> None:
        """SinkConfig should have sensible defaults."""
        config = SinkConfig()
        assert config.level == "INFO"
        assert config.format == "{level} | {message}"
        assert config.serialize is False
        assert config.append is True
        assert config.enqueue is False

    def test_rotation_policy_validates_positive_value(self) -> None:
        """RotationPolicy should reject zero or negative values."""
        with pytest.raises(ValidationError):
            RotationPolicy(kind="size", value=0)

    def test_rotation_policy_valid_kind(self) -> None:
        """RotationPolicy should accept valid kinds."""
        policy = RotationPolicy(kind="size", value=1024)
        assert policy.kind == "size"
        assert policy.value == 1024

    def test_retention_policy_count(self) -> None:
        """RetentionPolicy should accept count."""
        policy = RetentionPolicy(count=5)
        assert policy.count == 5

    def test_retention_policy_seconds(self) -> None:
        """RetentionPolicy should accept seconds."""
        policy = RetentionPolicy(seconds=86400)
        assert policy.seconds == 86400

    def test_retention_policy_validates_positive(self) -> None:
        """RetentionPolicy should reject negative values."""
        with pytest.raises(ValidationError):
            RetentionPolicy(count=-1)

    def test_compression_policy_valid_codecs(self) -> None:
        """CompressionPolicy should accept valid codecs."""
        from typing import Literal

        codecs: list[
            Literal[
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
            ]
        ] = ["none", "gzip", "zip", "bz2", "xz", "lzma", "zstd"]
        for codec in codecs:
            policy = CompressionPolicy(codec=codec)
            assert policy.codec == codec

    def test_compression_policy_invalid_codec(self) -> None:
        """CompressionPolicy should reject invalid codecs."""
        from typing import Any, cast

        with pytest.raises(ValidationError):
            CompressionPolicy(codec=cast(Any, "invalid"))

    def test_logger_config_defaults(self) -> None:
        """LoggerConfig should have empty defaults."""
        config = LoggerConfig()
        assert config.sinks == []
        assert config.disabled == set()

    def test_logger_config_with_sinks(self) -> None:
        """LoggerConfig should accept sink configurations."""
        config = LoggerConfig(
            sinks=[SinkConfig(level="DEBUG")],
            disabled={"myapp"},
        )
        assert len(config.sinks) == 1
        assert config.sinks[0].level == "DEBUG"
        assert "myapp" in config.disabled
