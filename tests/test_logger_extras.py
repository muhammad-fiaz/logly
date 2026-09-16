"""Tests for Level ordering, elapsed records, template strings, and parity APIs."""

from __future__ import annotations

import datetime
import io
import os
import subprocess
import sys

import pytest

from logly import Logger
from logly._logly import _Logger


class TestLevelOrdering:
    def test_severity_order(self) -> None:
        logger = Logger()
        assert logger.level("DEBUG") < logger.level("ERROR")
        assert logger.level("ERROR") > logger.level("DEBUG")
        assert logger.level("INFO") <= logger.level("INFO")
        assert logger.level("INFO") >= logger.level("INFO")
        assert not logger.level("ERROR") < logger.level("DEBUG")

    def test_custom_level_ordering(self) -> None:
        logger = Logger()
        logger.level("ORDER_LOW", no=15, color="green")
        logger.level("ORDER_HIGH", no=45, color="red")
        assert logger.level("ORDER_LOW") < logger.level("INFO")
        assert logger.level("ORDER_HIGH") > logger.level("WARNING")

    def test_ordering_rejects_other_types(self) -> None:
        logger = Logger()
        with pytest.raises(TypeError):
            assert logger.level("INFO") < "ERROR"  # type: ignore[operator]


class TestElapsed:
    def test_record_dict_has_elapsed(self) -> None:
        logger = Logger()
        record = logger.opt(record=True).log("INFO", "probe")
        assert record is not None
        assert isinstance(record["elapsed"], datetime.timedelta)
        assert record["elapsed"] >= datetime.timedelta(0)

    def test_native_callback_dict_has_elapsed(self) -> None:
        logger = Logger()
        seen: list[object] = []

        def collect(record: dict[str, object]) -> str:
            seen.append(record["elapsed"])
            return str(record["message"])

        messages: list[str] = []
        sink_id = logger.add(messages.append, format=collect)
        try:
            logger.info("probe")
        finally:
            logger.remove(sink_id)
        assert messages == ["probe\n"]
        assert len(seen) == 1
        assert isinstance(seen[0], datetime.timedelta)


class TestTemplateStrings:
    @staticmethod
    def _render(template_source: str) -> str:
        logger = Logger()
        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), format="{message}")
        namespace: dict[str, object] = {"logger": logger}
        try:
            exec(f"logger.info({template_source})", namespace)
            logger.complete()
        finally:
            logger.remove(sink_id)
        assert len(messages) == 1
        return messages[0]

    @pytest.mark.skipif(sys.version_info < (3, 14), reason="template strings need 3.14+")
    def test_basic_interpolation(self) -> None:
        assert self._render('t"calc {40 + 2} items"') == "calc 42 items\n"

    @pytest.mark.skipif(sys.version_info < (3, 14), reason="template strings need 3.14+")
    def test_conversion_and_spec(self) -> None:
        assert self._render('t"user {"ann"!r} scored {3.14159:.1f}"') == "user 'ann' scored 3.1\n"

    @pytest.mark.skipif(sys.version_info < (3, 14), reason="template strings need 3.14+")
    def test_template_with_args_raises(self) -> None:
        logger = Logger()
        sink_id = logger.add(io.StringIO(), format="{message}")
        namespace: dict[str, object] = {"logger": logger}
        try:
            with pytest.raises(ValueError, match="template string"):
                exec('logger.info(t"value {1}", "extra")', namespace)
        finally:
            logger.remove(sink_id)


class TestParityAPIs:
    def test_native_warn(self) -> None:
        native = _Logger()
        assert hasattr(native, "warn")
        native.warn("native warning")

    def test_native_audit_after_registration(self) -> None:
        from logly import logger as module_logger

        module_logger.level("AUDIT", no=35, color="green")
        native = _Logger()
        native.audit("native audit")

    def test_udp_flush_exists(self) -> None:
        from logly._logly import UdpSink

        sink = UdpSink()
        assert hasattr(sink, "flush")
        sink.flush()

    def test_python_warn_alias(self) -> None:
        logger = Logger()
        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), format="{message}")
        try:
            logger.warn("alias works")
        finally:
            logger.remove(sink_id)
        assert messages == ["alias works\n"]


class TestEnvironment:
    def test_logly_level_env(self) -> None:
        script = "from logly import logger;logger.info('shown?');logger.complete()"
        env = {**dict(os.environ), "LOGLY_LEVEL": "WARNING"}
        proc = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            env=env,
            timeout=120,
        )
        assert proc.returncode == 0, proc.stderr
        assert "shown?" not in proc.stderr

    def test_logly_level_invalid_falls_back(self) -> None:
        script = "from logly import logger; logger.info('fallback works')"
        env = {**dict(os.environ), "LOGLY_LEVEL": "NOT_A_LEVEL"}
        proc = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            env=env,
            timeout=120,
        )
        assert proc.returncode == 0, proc.stderr
        assert "fallback works" in proc.stderr
