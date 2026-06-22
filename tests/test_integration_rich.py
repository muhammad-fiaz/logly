"""Tests for Rich console integration."""

from __future__ import annotations

import pytest


class TestRichIntegration:
    """Tests for Rich console sink integration."""

    def test_rich_sink_class_exists(self) -> None:
        """LoglyRichSink should be importable."""
        try:
            from logly.integrations.rich import LoglyRichSink

            assert LoglyRichSink is not None
        except ImportError:
            pytest.skip("rich is not installed")

    def test_rich_sink_has_write(self) -> None:
        """LoglyRichSink should have a write method."""
        try:
            from logly.integrations.rich import LoglyRichSink

            sink = LoglyRichSink()
            assert hasattr(sink, "write")
        except ImportError:
            pytest.skip("rich is not installed")
