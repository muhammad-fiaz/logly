"""Tests for Django integration."""

from __future__ import annotations

from logly.integrations.django import LoglyHandler, LoglyMiddleware


class TestDjangoIntegration:
    """Tests for Django handler and middleware."""

    def test_handler_class_exists(self) -> None:
        """LoglyHandler should be importable."""
        assert LoglyHandler is not None

    def test_handler_is_subclass_of_logging_handler(self) -> None:
        """LoglyHandler should subclass logging.Handler."""
        import logging

        assert issubclass(LoglyHandler, logging.Handler)

    def test_middleware_class_exists(self) -> None:
        """LoglyMiddleware should be importable."""
        assert LoglyMiddleware is not None

    def test_handler_can_be_instantiated(self) -> None:
        """LoglyHandler should be instantiable."""
        handler = LoglyHandler()
        assert handler is not None
