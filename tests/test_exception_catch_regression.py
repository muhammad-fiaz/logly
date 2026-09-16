"""Regression tests for exception and catch handling.

logger.exception() must include the active exception traceback.
logger.catch() must log the caught exception before invoking onerror,
even when onerror exits (NoReturn) or raises.
"""

from __future__ import annotations

import sys

from logly import Logger


def _capture(logger: Logger, fmt: str = "{level}:{message}") -> tuple[list[str], int]:
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format=fmt)
    return messages, sink_id


def test_exception_includes_traceback() -> None:
    logger = Logger()
    messages, sink_id = _capture(logger)
    try:
        try:
            _ = 1 / 0
        except ZeroDivisionError:
            logger.exception("Something failed")
    finally:
        logger.remove(sink_id)
    assert len(messages) == 1
    assert "Something failed" in messages[0]
    assert "ZeroDivisionError" in messages[0]
    assert "Traceback" in messages[0]


def test_exception_default_format_includes_traceback() -> None:
    logger = Logger()
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG")
    try:
        try:
            _ = 1 / 0
        except ZeroDivisionError:
            logger.exception("Something failed")
    finally:
        logger.remove(sink_id)
    assert len(messages) == 1
    assert "ZeroDivisionError" in messages[0]
    assert "Traceback" in messages[0]


def test_opt_exception_true_captures_active_exception() -> None:
    logger = Logger()
    messages, sink_id = _capture(logger)
    try:
        try:
            _ = 1 / 0
        except ZeroDivisionError:
            logger.opt(exception=True).error("opt failed")
    finally:
        logger.remove(sink_id)
    assert len(messages) == 1
    assert "ZeroDivisionError" in messages[0]
    assert "Traceback" in messages[0]


def test_opt_exception_true_without_active_exception_logs_plain() -> None:
    logger = Logger()
    messages, sink_id = _capture(logger)
    try:
        logger.opt(exception=True).error("no active")
    finally:
        logger.remove(sink_id)
    assert len(messages) == 1
    assert "no active" in messages[0]
    assert "ZeroDivisionError" not in messages[0]
    assert "exception=True" not in messages[0]


def test_exception_exc_info_false_omits_traceback() -> None:
    logger = Logger()
    messages, sink_id = _capture(logger)
    try:
        try:
            _ = 1 / 0
        except ZeroDivisionError:
            logger.exception("oops", exc_info=False)
    finally:
        logger.remove(sink_id)
    assert len(messages) == 1
    assert "oops" in messages[0]
    assert "ZeroDivisionError" not in messages[0]


def test_catch_logs_before_onerror_exit() -> None:
    logger = Logger()
    messages, sink_id = _capture(logger)
    try:
        try:
            with logger.catch(onerror=lambda _: sys.exit(1)):
                _ = 1 / 0
        except SystemExit as exc:
            assert exc.code == 1
        else:
            raise AssertionError("SystemExit not raised")
    finally:
        logger.remove(sink_id)
    assert len(messages) == 1
    assert "ZeroDivisionError" in messages[0]
    assert "Traceback" in messages[0]


def test_catch_logs_before_onerror_raises() -> None:
    logger = Logger()
    messages, sink_id = _capture(logger)

    def _bad_onerror(exc: BaseException) -> None:
        raise RuntimeError("onerror failed")

    try:
        try:
            with logger.catch(onerror=_bad_onerror):
                _ = 1 / 0
        except RuntimeError as exc:
            assert str(exc) == "onerror failed"
        else:
            raise AssertionError("RuntimeError not raised")
    finally:
        logger.remove(sink_id)
    assert len(messages) == 1
    assert "ZeroDivisionError" in messages[0]
    assert "Traceback" in messages[0]


def test_catch_without_onerror_still_logs() -> None:
    logger = Logger()
    messages, sink_id = _capture(logger)
    try:
        with logger.catch():
            _ = 1 / 0
    finally:
        logger.remove(sink_id)
    assert len(messages) == 1
    assert "ZeroDivisionError" in messages[0]
