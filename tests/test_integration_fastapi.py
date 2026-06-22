"""Tests for FastAPI integration."""

from __future__ import annotations

from logly.integrations.fastapi import LoglyMiddleware


class TestFastAPIIntegration:
    """Tests for FastAPI middleware integration."""

    def test_middleware_importable(self) -> None:
        """LoglyMiddleware should be importable."""
        assert LoglyMiddleware is not None

    def test_middleware_class_is_defined(self) -> None:
        """LoglyMiddleware should be a class."""
        assert isinstance(LoglyMiddleware, type)
