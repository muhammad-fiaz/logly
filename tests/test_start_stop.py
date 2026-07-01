"""Tests for Logger.start() and Logger.stop() methods."""

from logly import Logger


class TestStart:
    def test_start_returns_none(self) -> None:
        lg = Logger()
        result = lg.start()
        assert result is None

    def test_start_with_args(self) -> None:
        lg = Logger()
        result = lg.start("arg1", kwarg="value")
        assert result is None


class TestStop:
    def test_stop_calls_complete(self) -> None:
        lg = Logger()
        lg.stop()

    def test_stop_does_not_raise(self) -> None:
        lg = Logger()
        lg.stop()
        lg.stop()
