"""Tests for Logly exception class hierarchy."""

from logly.exceptions import (
    CompressionError,
    ConfigError,
    FilterError,
    FormatterError,
    LoglyError,
    RotationError,
    SinkError,
)


class TestExceptionHierarchy:
    def test_logly_error_inherits_from_exception(self) -> None:
        assert issubclass(LoglyError, Exception)

    def test_sink_error_inherits_from_logly_error(self) -> None:
        assert issubclass(SinkError, LoglyError)

    def test_rotation_error_inherits_from_sink_error(self) -> None:
        assert issubclass(RotationError, SinkError)

    def test_compression_error_inherits_from_sink_error(self) -> None:
        assert issubclass(CompressionError, SinkError)

    def test_formatter_error_inherits_from_logly_error(self) -> None:
        assert issubclass(FormatterError, LoglyError)

    def test_filter_error_inherits_from_logly_error(self) -> None:
        assert issubclass(FilterError, LoglyError)

    def test_config_error_inherits_from_logly_error(self) -> None:
        assert issubclass(ConfigError, LoglyError)

    def test_all_exceptions_catchable_by_logly_error(self) -> None:
        for exc_cls in (
            SinkError,
            RotationError,
            CompressionError,
            FormatterError,
            FilterError,
            ConfigError,
        ):
            try:
                raise exc_cls("test")
            except LoglyError:
                pass

    def test_rotation_error_not_catchable_by_formatter_error(self) -> None:
        try:
            raise RotationError("test")
            raise AssertionError("Should have raised")  # noqa: E501
        except FormatterError:
            raise AssertionError("Should not be caught by FormatterError") from None
        except SinkError:
            pass

    def test_exceptions_have_message(self) -> None:
        for exc_cls in (
            LoglyError,
            SinkError,
            FormatterError,
            FilterError,
            ConfigError,
            RotationError,
            CompressionError,
        ):
            exc = exc_cls("test message")
            assert str(exc) == "test message"

    def test_exceptions_can_be_raised_and_caught(self) -> None:
        with raises_contextmanager(LoglyError):
            raise LoglyError()
        with raises_contextmanager(SinkError):
            raise SinkError()
        with raises_contextmanager(RotationError):
            raise RotationError()
        with raises_contextmanager(CompressionError):
            raise CompressionError()
        with raises_contextmanager(FormatterError):
            raise FormatterError()
        with raises_contextmanager(FilterError):
            raise FilterError()
        with raises_contextmanager(ConfigError):
            raise ConfigError()


class raises_contextmanager:
    """Minimal context manager for testing exceptions without pytest.raises."""

    def __init__(self, exc_type):
        self._exc_type = exc_type

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            raise AssertionError(f"Expected {self._exc_type.__name__} to be raised")
        return issubclass(exc_type, self._exc_type)
