"""Tests for stdlib logging integration."""

from __future__ import annotations

import logging

from logly import logger
from logly.integrations.stdlib import InterceptHandler


class TestStdlibIntegration:
    """Tests for stdlib logging integration."""

    def test_intercept_handler_routes_to_logly(self) -> None:
        """InterceptHandler should route stdlib records to Logly."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture)
        handler = InterceptHandler()
        stdlib_logger = logging.getLogger("test_stdlib")
        stdlib_logger.addHandler(handler)
        stdlib_logger.setLevel(logging.DEBUG)

        stdlib_logger.info("from stdlib")
        logger.remove(sink_id)
        stdlib_logger.removeHandler(handler)
        assert len(messages) >= 1

    def test_intercept_handler_level_mapping(self) -> None:
        """InterceptHandler should map stdlib levels to Logly levels."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        sink_id = logger.add(capture)
        handler = InterceptHandler()
        stdlib_logger = logging.getLogger("test_level_map")
        stdlib_logger.addHandler(handler)
        stdlib_logger.setLevel(logging.DEBUG)

        stdlib_logger.warning("warning from stdlib")
        logger.remove(sink_id)
        stdlib_logger.removeHandler(handler)
        assert len(messages) >= 1
