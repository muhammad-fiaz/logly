"""Tests for logging.Handler as sink in logger.add()."""

from __future__ import annotations

import logging
from io import StringIO

from logly import Logger


def test_stream_handler_wrapped() -> None:
    logger = Logger()
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    sink_id = logger.add(handler, level="DEBUG", format="{message}")
    logger.info("handler test")
    logger.complete()
    logger.remove(sink_id)
    output = stream.getvalue()
    assert "handler test" in output


def test_stream_handler_receives_message() -> None:
    logger = Logger()
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    sink_id = logger.add(handler, level="DEBUG", format="{message}")
    logger.info("hello via handler")
    logger.complete()
    logger.remove(sink_id)
    assert "hello via handler" in stream.getvalue()


def test_stream_handler_error_level() -> None:
    logger = Logger()
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.ERROR)
    sink_id = logger.add(handler, level="DEBUG", format="{message}")
    logger.error("error message")
    logger.complete()
    logger.remove(sink_id)
    assert "error message" in stream.getvalue()


def test_stream_handler_filtering_by_sink_level() -> None:
    logger = Logger()
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.WARNING)
    sink_id = logger.add(handler, level="DEBUG", format="{message}")
    logger.info("should be filtered")
    logger.error("should pass")
    logger.complete()
    logger.remove(sink_id)
    output = stream.getvalue()
    assert "should be filtered" not in output
    assert "should pass" in output


def test_stream_handler_with_format() -> None:
    logger = Logger()
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    sink_id = logger.add(handler, level="DEBUG", format="{level}:{message}")
    logger.info("formatted")
    logger.complete()
    logger.remove(sink_id)
    output = stream.getvalue()
    assert "INFO" in output
    assert "formatted" in output


def test_file_handler(tmp_path) -> None:
    logger = Logger()
    log_file = tmp_path / "handler.log"
    handler = logging.FileHandler(str(log_file))
    sink_id = logger.add(handler, level="DEBUG", format="{message}")
    logger.info("file handler test")
    logger.complete()
    logger.remove(sink_id)
    content = log_file.read_text(encoding="utf-8")
    assert "file handler test" in content
