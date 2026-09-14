"""Regression tests from the production-readiness audit.

Covers: disabled structured logging, dispatch continuing past a failing
sink, model_validate input errors, chunked file parsing, unicode / large /
empty messages, failing Python sinks never raising, and disabled-logging
throughput smoke.
"""

from __future__ import annotations

import time

import pytest

from logly import Logger
from logly.models import SinkConfig, ValidationError


def _fresh_logger() -> Logger:
    return Logger()


def test_disabled_name_skips_structured_dispatch() -> None:
    logger = _fresh_logger()
    messages: list[str] = []
    logger.add(messages.append, level="DEBUG")
    logger.info("shown")
    logger.disable("logly")
    # Structured path (what Logger.log uses) must honor disable.
    logger.info("hidden")
    logger.enable("logly")
    logger.info("shown again")
    logger.complete()
    assert not any("hidden" in m for m in messages)
    assert sum("shown" in m for m in messages) == 2


def test_dispatch_continues_past_failing_sink() -> None:
    logger = _fresh_logger()
    received: list[str] = []

    def bad_sink(message: str) -> None:
        raise RuntimeError("boom")

    logger.add(bad_sink, level="DEBUG")
    logger.add(received.append, level="DEBUG")
    # Fail-fast dispatch would abort before the good sink; must not raise
    # (Python sink errors are reported on stderr, dispatch continues).
    logger.info("hello")
    logger.complete()
    assert any("hello" in m for m in received)


def test_failing_python_sink_never_raises() -> None:
    logger = _fresh_logger()

    def bad_sink(message: str) -> None:
        raise ValueError("sink failure")

    logger.add(bad_sink, level="DEBUG")
    logger.info("must not raise")
    logger.complete()


def test_model_validate_rejects_non_mapping() -> None:
    with pytest.raises(ValidationError):
        SinkConfig.model_validate(["not", "a", "dict"])  # type: ignore[arg-type]


def test_parse_honors_chunk_size(tmp_path) -> None:  # type: ignore[no-untyped-def]
    log_file = tmp_path / "app.log"
    log_file.write_text("INFO hello\nWARN world\n", encoding="utf-8")
    records = list(Logger.parse(str(log_file), chunk=2))
    assert [r["message"] for r in records] == ["INFO hello", "WARN world"]


def test_unicode_large_and_empty_messages() -> None:
    logger = _fresh_logger()
    messages: list[str] = []
    logger.add(messages.append, level="TRACE")
    logger.info("unicode: héllo wörld 🚀 中文")
    logger.info("x" * 200_000)
    logger.info("")
    logger.complete()
    assert len(messages) == 3
    assert "🚀" in messages[0]
    assert len(messages[1]) >= 200_000


def test_disabled_logging_is_quiet_and_fast() -> None:
    logger = _fresh_logger()
    messages: list[str] = []
    logger.add(messages.append, level="DEBUG")
    logger.disable("logly")
    start = time.perf_counter()
    for _ in range(200):
        logger.debug("dropped {}", 123)
    elapsed = time.perf_counter() - start
    logger.complete()
    assert messages == []
    assert elapsed < 5.0


def test_invalid_level_raises() -> None:
    logger = _fresh_logger()
    with pytest.raises(ValueError):
        logger.log("NO_SUCH_LEVEL", "x")
