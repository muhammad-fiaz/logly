"""Tests for custom level features: Level class, icon support, level()."""

from __future__ import annotations

import io

from logly import Level, logger


class TestLevelClass:
    """Tests for the Level dataclass."""

    def test_level_is_frozen_dataclass(self) -> None:
        info = logger.level("INFO")
        assert isinstance(info, Level)
        # frozen dataclass
        try:
            info.name = "OTHER"  # type: ignore[misc]
        except AttributeError:
            pass  # expected

    def test_level_attributes(self) -> None:
        info = logger.level("INFO")
        assert info.name == "INFO"
        assert info.no == 20
        assert info.color is None
        assert info.icon is None

    def test_level_with_color(self) -> None:
        warning = logger.level("WARNING")
        assert warning.name == "WARNING"
        assert warning.no == 40
        assert warning.color == "yellow"

    def test_level_with_icon(self) -> None:
        logger.level("SUCCESS_PLUS", no=35, color="green", icon=">>")
        sp = logger.level("SUCCESS_PLUS")
        assert sp.name == "SUCCESS_PLUS"
        assert sp.no == 35
        assert sp.color == "green"
        assert sp.icon == ">>"

    def test_level_without_icon(self) -> None:
        logger.level("AUDIT", no=22, color="cyan")
        audit = logger.level("AUDIT")
        assert audit.name == "AUDIT"
        assert audit.no == 22
        assert audit.color == "cyan"
        assert audit.icon is None

    def test_level_repr(self) -> None:
        info = logger.level("INFO")
        assert "INFO" in repr(info)
        assert "20" in repr(info)


class TestLevelRegister:
    """Tests for level registration with icon."""

    def test_register_with_icon(self) -> None:
        logger.level("HTTP", no=21, color="blue", icon=">")
        http = logger.level("HTTP")
        assert http.name == "HTTP"
        assert http.no == 21
        assert http.color == "blue"
        assert http.icon == ">"

    def test_register_without_icon(self) -> None:
        logger.level("CUSTOM_NO_ICON", no=99, color="red")
        lvl = logger.level("CUSTOM_NO_ICON")
        assert lvl.name == "CUSTOM_NO_ICON"
        assert lvl.no == 99
        assert lvl.icon is None

    def test_register_updates_existing(self) -> None:
        logger.level("UPDATABLE", no=50, color="red")
        logger.level("UPDATABLE", no=55, color="magenta", icon="!")
        lvl = logger.level("UPDATABLE")
        assert lvl.no == 55
        assert lvl.color == "magenta"
        assert lvl.icon == "!"

    def test_register_empty_name_raises(self) -> None:
        import pytest

        with pytest.raises(ValueError):
            logger.level("", no=10)


class TestLevelLog:
    """Tests for logging with custom levels."""

    def test_log_with_custom_level(self) -> None:
        logger.level("METRIC", no=28, color="magenta", icon="#")
        buf = io.StringIO()
        sink_id = logger.add(
            buf,
            format="{level_icon} {level} {message}",
            level="TRACE",
        )
        try:
            logger.log("METRIC", "request latency 42ms")
            output = buf.getvalue()
            assert "METRIC" in output
            assert "request latency 42ms" in output
        finally:
            logger.remove(sink_id)

    def test_format_level_icon_token(self) -> None:
        logger.level("TEST_ICON", no=29, icon="*")
        buf = io.StringIO()
        sink_id = logger.add(buf, format="{level_icon} {message}", level="TRACE")
        try:
            logger.log("TEST_ICON", "hello")
            output = buf.getvalue()
            assert output.strip() == "* hello"
        finally:
            logger.remove(sink_id)

    def test_format_level_token(self) -> None:
        buf = io.StringIO()
        sink_id = logger.add(buf, format="{level} {message}", level="TRACE")
        try:
            logger.info("test msg")
            output = buf.getvalue()
            assert "INFO" in output
            assert "test msg" in output
        finally:
            logger.remove(sink_id)

    def test_format_level_no_token(self) -> None:
        buf = io.StringIO()
        sink_id = logger.add(buf, format="{level_no} {message}", level="TRACE")
        try:
            logger.info("test msg")
            output = buf.getvalue()
            assert "20" in output
        finally:
            logger.remove(sink_id)

    def test_icon_in_format_with_built_in_level(self) -> None:
        buf = io.StringIO()
        sink_id = logger.add(buf, format="{level_icon} {message}", level="TRACE")
        try:
            logger.info("built-in level has no icon")
            output = buf.getvalue()
            assert "built-in level has no icon" in output
        finally:
            logger.remove(sink_id)


class TestLevelList:
    """Tests for list_levels."""

    def test_list_levels(self) -> None:
        from logly import list_levels

        levels = list_levels()
        assert "INFO" in levels
        assert "DEBUG" in levels
        assert "WARNING" in levels
        assert "ERROR" in levels
        assert "CRITICAL" in levels
        assert "TRACE" in levels
        assert "SUCCESS" in levels

    def test_list_levels_includes_custom(self) -> None:
        from logly import list_levels

        logger.level("CUSTOM_LIST_TEST", no=88, color="blue", icon="~")
        levels = list_levels()
        assert "CUSTOM_LIST_TEST" in levels
