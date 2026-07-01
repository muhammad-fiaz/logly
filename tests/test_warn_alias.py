"""Tests for Logger.warn() alias of Logger.warning()."""

import io

from logly import Logger


class TestWarnAlias:
    def test_warn_produces_output(self) -> None:
        output = io.StringIO()
        lg = Logger()
        lg.add(output, level="WARNING", format="{message}")
        lg.warn("warning message")
        assert "warning message" in output.getvalue()

    def test_warn_uses_warning_level(self) -> None:
        output = io.StringIO()
        lg = Logger()
        lg.add(output, level="WARNING", format="{level}")
        lg.warn("test")
        assert "WARNING" in output.getvalue()

    def test_warn_same_as_warning(self) -> None:
        out1 = io.StringIO()
        out2 = io.StringIO()
        lg = Logger()
        lg.add(out1, level="WARNING", format="{message}")
        lg.add(out2, level="WARNING", format="{message}")
        lg.warn("msg")
        lg.warning("msg")
        assert out1.getvalue().strip() == out2.getvalue().strip()

    def test_warn_with_format_args(self) -> None:
        output = io.StringIO()
        lg = Logger()
        lg.add(output, level="WARNING", format="{message}")
        lg.warn("User {} logged in", "alice")
        assert "User alice logged in" in output.getvalue()

    def test_warn_with_format_kwargs(self) -> None:
        output = io.StringIO()
        lg = Logger()
        lg.add(output, level="WARNING", format="{message}")
        lg.warn("User {name} logged in", name="alice")
        assert "User alice logged in" in output.getvalue()

    def test_warn_is_callable(self) -> None:
        lg = Logger()
        assert callable(lg.warn)
