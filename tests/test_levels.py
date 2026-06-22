"""Tests for log levels: built-in levels, custom levels, and level operations."""

from __future__ import annotations

from logly import logger
from logly._logly import inspect_level, list_levels, register_custom_level


class TestBuiltinLevels:
    """Tests for the 10 built-in log levels."""

    def test_all_builtin_levels_exist(self) -> None:
        """All 10 built-in levels should be registered."""
        names = list_levels()
        expected = [
            "TRACE",
            "DEBUG",
            "INFO",
            "NOTICE",
            "SUCCESS",
            "WARNING",
            "ERROR",
            "FAIL",
            "CRITICAL",
            "FATAL",
        ]
        for name in expected:
            assert name in names

    def test_builtin_levels_are_ordered_by_priority(self) -> None:
        """Built-in levels should be ordered from lowest to highest severity."""
        names = list_levels()
        priorities = [inspect_level(n)[1] for n in names]
        assert priorities == sorted(priorities)

    def test_level_inspect_returns_tuple(self) -> None:
        """inspect_level should return (name, priority, color)."""
        name, priority, color = inspect_level("INFO")
        assert name == "INFO"
        assert priority == 20
        assert color is None or isinstance(color, str)

    def test_level_case_insensitive_lookup(self) -> None:
        """Level lookup should be case-insensitive."""
        name1, pri1, _ = inspect_level("info")
        name2, pri2, _ = inspect_level("INFO")
        assert name1 == name2
        assert pri1 == pri2

    def test_trace_level_priority(self) -> None:
        """TRACE should have the lowest priority."""
        _, priority, _ = inspect_level("TRACE")
        assert priority == 5

    def test_fatal_level_priority(self) -> None:
        """FATAL should have the highest priority."""
        _, priority, _ = inspect_level("FATAL")
        assert priority == 70

    def test_level_unknown_raises(self) -> None:
        """Unknown level should raise ValueError."""
        import pytest

        with pytest.raises(ValueError):
            inspect_level("NONexistent")


class TestCustomLevels:
    """Tests for custom level registration."""

    def test_register_custom_level(self) -> None:
        """Custom levels should be registerable."""
        name = register_custom_level("AUDIT", 35, "cyan")
        assert name == "AUDIT"
        result = inspect_level("AUDIT")
        assert result[0] == "AUDIT"
        assert result[1] == 35

    def test_custom_level_in_list(self) -> None:
        """Custom levels should appear in the level list."""
        register_custom_level("CUSTOM_TEST_1", 15, None)
        names = list_levels()
        assert "CUSTOM_TEST_1" in names

    def test_custom_level_ordering(self) -> None:
        """Custom level should be ordered correctly among built-in levels."""
        register_custom_level("CUSTOM_ORDER_TEST", 32, None)
        names = list_levels()
        success_idx = names.index("SUCCESS")
        warning_idx = names.index("WARNING")
        custom_idx = names.index("CUSTOM_ORDER_TEST")
        assert success_idx < custom_idx < warning_idx

    def test_register_empty_name_raises(self) -> None:
        """Registering an empty level name should raise."""
        import pytest

        with pytest.raises(ValueError):
            register_custom_level("", 100, None)

    def test_logger_log_at_custom_level(self) -> None:
        """Should be able to log at a custom level by name."""
        register_custom_level("CUSTOM_LOG_TEST", 22, None)
        sink = logger.add("stdout", level="TRACE")
        logger.log("CUSTOM_LOG_TEST", "custom message")
        logger.remove(sink)

    def test_logger_log_at_numeric_level(self) -> None:
        """Should be able to log at a numeric level."""
        sink = logger.add("stdout", level="TRACE")
        logger.log(20, "numeric level message")
        logger.remove(sink)
