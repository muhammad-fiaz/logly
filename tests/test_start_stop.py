"""Tests for Logger.start() and Logger.stop() methods."""

from logly import Logger


class TestStart:
    def test_start_returns_none(self) -> None:
        lg = Logger()
        lg.start()

    def test_start_with_args(self) -> None:
        lg = Logger()
        lg.start("arg1", kwarg="value")


class TestStop:
    def test_stop_calls_complete(self) -> None:
        lg = Logger()
        lg.stop()

    def test_stop_does_not_raise(self) -> None:
        lg = Logger()
        lg.stop()
        lg.stop()


class TestFlush:
    def test_flush_delivers_and_is_idempotent(self) -> None:
        lg = Logger()
        messages: list[str] = []
        sink_id = lg.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        lg.info("hello")
        lg.flush()
        lg.flush()
        lg.remove(sink_id)
        assert len(messages) == 1
        assert "hello" in messages[0]

    def test_flush_drains_enqueue_sink(self) -> None:
        lg = Logger()
        messages: list[str] = []
        sink_id = lg.add(
            lambda m: messages.append(m), level="DEBUG", format="{message}", enqueue=True
        )
        lg.info("queued")
        lg.flush()
        lg.remove(sink_id)
        assert len(messages) == 1
