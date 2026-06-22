from __future__ import annotations

import pytest
from pydantic import ValidationError

from logly.models import RotationPolicy, SinkConfig


def test_sink_config_defaults() -> None:
    config = SinkConfig()

    assert config.level == "INFO"
    assert config.format == "{level} | {message}"
    assert config.append is True


def test_rotation_policy_validates_positive_value() -> None:
    with pytest.raises(ValidationError):
        RotationPolicy(kind="size", value=0)
