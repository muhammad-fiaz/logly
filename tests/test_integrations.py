from __future__ import annotations

import copy
import logging
import sys
from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from logly import Logger, logger
from logly.logger import _Options


class TestStdlibIntegration:
    def test_intercept_handler_routes_to_logly(self) -> None:
        from logly.integrations.stdlib import InterceptHandler

        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        handler = InterceptHandler()
        record = logging.LogRecord("test", logging.INFO, "", 0, "stdlib hello", (), None)
        handler.emit(record)
        logger.remove(sink_id)
        assert len(messages) >= 1
        assert "stdlib hello" in messages[0]

    def test_intercept_handler_with_exception(self) -> None:
        from logly.integrations.stdlib import InterceptHandler

        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        handler = InterceptHandler()
        try:
            raise ValueError("test exc")
        except ValueError:
            record = logging.LogRecord(
                "test", logging.ERROR, "", 0, "error occurred", (), sys.exc_info()
            )
            handler.emit(record)
        logger.remove(sink_id)
        assert len(messages) >= 1

    def test_resolve_level_maps_standard_levels(self) -> None:
        from logly.integrations.stdlib import _resolve_level

        for py_lvl, expected in [
            (logging.DEBUG, "DEBUG"),
            (logging.INFO, "INFO"),
            (logging.WARNING, "WARNING"),
            (logging.ERROR, "ERROR"),
            (logging.CRITICAL, "CRITICAL"),
        ]:
            record = logging.LogRecord("test", py_lvl, "", 0, "msg", (), None)
            assert _resolve_level(record) == expected

    def test_resolve_level_fallback_for_custom(self) -> None:
        from logly.integrations.stdlib import _resolve_level

        record = logging.LogRecord("test", 25, "", 0, "msg", (), None)
        record.levelname = "CUSTOM"
        assert _resolve_level(record) == "CUSTOM"


class TestFlaskIntegration:
    def test_logly_handler_emit(self) -> None:
        from logly.integrations.flask import LoglyHandler

        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        handler = LoglyHandler()
        record = logging.LogRecord("test", logging.WARNING, "", 0, "flask warning", (), None)
        handler.emit(record)
        logger.remove(sink_id)
        assert len(messages) >= 1
        assert "flask warning" in messages[0]

    def test_resolve_level_standard_mapping(self) -> None:
        from logly.integrations.flask import _resolve_level

        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        assert _resolve_level(record) == "INFO"

        record = logging.LogRecord("test", logging.ERROR, "", 0, "msg", (), None)
        assert _resolve_level(record) == "ERROR"


class TestOpenTelemetryIntegration:
    def test_otel_sink_init_import_error(self) -> None:
        from logly.integrations.opentelemetry import OTelLogSink

        saved = sys.modules.get("opentelemetry.sdk._logs")
        cast(dict[str, Any], sys.modules)["opentelemetry.sdk._logs"] = None
        try:
            with pytest.raises(ImportError):
                OTelLogSink(service_name="test")
        finally:
            if saved is not None:
                sys.modules["opentelemetry.sdk._logs"] = saved
            else:
                sys.modules.pop("opentelemetry.sdk._logs", None)

    def test_otel_sink_write(self) -> None:
        from logly.integrations.opentelemetry import OTelLogSink

        mock_severity = MagicMock()
        mock_otel_logger = MagicMock()

        saved = sys.modules.get("opentelemetry._logs")
        otel_logs_mod = MagicMock()
        otel_logs_mod.Severity = mock_severity
        sys.modules["opentelemetry._logs"] = otel_logs_mod

        try:
            sink = OTelLogSink.__new__(OTelLogSink)
            sink._otel_logger = mock_otel_logger

            sink.write("hello otel\n")
            mock_otel_logger.emit.assert_called_once()
            call_kwargs = mock_otel_logger.emit.call_args[1]
            assert call_kwargs["body"] == "hello otel"
        finally:
            if saved is not None:
                sys.modules["opentelemetry._logs"] = saved
            else:
                sys.modules.pop("opentelemetry._logs", None)


class TestSinkManagement:
    def test_add_returns_unique_ids(self) -> None:
        log = Logger()
        id1 = log.add(lambda m: None, level="DEBUG", format="{message}")
        id2 = log.add(lambda m: None, level="DEBUG", format="{message}")
        id3 = log.add(lambda m: None, level="DEBUG", format="{message}")
        log.remove()
        assert id1 != id2 != id3

    def test_remove_by_id(self) -> None:
        log = Logger()
        msgs1: list[str] = []
        msgs2: list[str] = []
        sink1 = log.add(lambda m: msgs1.append(m), level="DEBUG", format="{message}")
        sink2 = log.add(lambda m: msgs2.append(m), level="DEBUG", format="{message}")
        log.remove(sink1)
        log.info("only second")
        log.complete()
        log.remove(sink2)
        assert len(msgs1) == 0
        assert len(msgs2) >= 1

    def test_remove_all(self) -> None:
        log = Logger()
        log.add(lambda m: None, level="DEBUG", format="{message}")
        log.add(lambda m: None, level="DEBUG", format="{message}")
        log.remove()
        log.info("no sinks active")
        log.complete()

    def test_add_stderr_sink(self) -> None:
        log = Logger()
        sink_id = log.add(sys.stderr, level="DEBUG", format="{message}")
        assert isinstance(sink_id, int)
        log.remove(sink_id)

    def test_add_string_callable_sink(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        log.info("callable sink")
        log.complete()
        log.remove(sink_id)
        assert len(messages) >= 1

    def test_add_file_sink(self, tmp_path: Path) -> None:
        log = Logger()
        log_file = tmp_path / "sink_test.log"
        sink_id = log.add(str(log_file), level="DEBUG", format="{message}")
        log.info("file sink test")
        log.complete()
        log.remove(sink_id)
        content = log_file.read_text(encoding="utf-8")
        assert "file sink test" in content


class TestFormatTemplate:
    def test_default_format_renders_correctly(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG")
        log.info("default format check")
        log.complete()
        log.remove(sink_id)
        assert len(messages) >= 1

    def test_custom_format_string(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{level} - {message}")
        log.info("custom fmt")
        log.complete()
        log.remove(sink_id)
        assert len(messages) >= 1
        assert "custom fmt" in messages[0]

    def test_format_with_color_markup_tags(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(
            lambda m: messages.append(m),
            level="DEBUG",
            format="<green>{time}</green> | <level>{level}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
            colorize=False,
        )
        log.info("color tags")
        log.complete()
        log.remove(sink_id)
        assert len(messages) >= 1
        assert "<green>" not in messages[0]
        assert "<level>" not in messages[0]
        assert "<cyan>" not in messages[0]

    def test_format_level_padding(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(
            lambda m: messages.append(m),
            level="DEBUG",
            format="{level: <8}:{message}",
            colorize=False,
        )
        log.info("pad test")
        log.complete()
        log.remove(sink_id)
        assert len(messages) >= 1
        level_part = messages[0].split(":")[0]
        assert len(level_part) == 8

    def test_format_callable(self) -> None:
        log = Logger()
        messages: list[str] = []

        def custom_fmt(record: dict[str, object]) -> str:
            return f"CALLABLE:{record['message']}"

        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format=custom_fmt)
        log.info("callable fmt")
        log.complete()
        log.remove(sink_id)
        assert len(messages) >= 1
        assert "CALLABLE:callable fmt" in messages[0]


class TestOptions:
    def test_opt_record_returns_dict(self) -> None:
        log = Logger()
        sink_id = log.add(lambda m: None, level="DEBUG", format="{message}")
        result = log.opt(record=True).log("INFO", "record test")
        log.remove(sink_id)
        assert isinstance(result, dict)

    def test_opt_raw_skips_formatting(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        log.opt(raw=True).info("no {interp} here")
        log.complete()
        log.remove(sink_id)
        assert len(messages) >= 1
        assert "no {interp} here" in messages[0]

    def test_opt_depth_captures_caller(self) -> None:
        log = Logger()
        msgs_depth: list[str] = []
        msgs_default: list[str] = []

        sink_d = log.add(
            lambda m: msgs_depth.append(m), level="DEBUG", format="{function}:{message}"
        )
        log.opt(depth=0).info("depth zero")
        log.remove(sink_d)

        sink_default = log.add(
            lambda m: msgs_default.append(m), level="DEBUG", format="{function}:{message}"
        )
        log.info("default depth")
        log.remove(sink_default)

        assert len(msgs_depth) >= 1
        assert len(msgs_default) >= 1
        assert msgs_depth[0].split(":")[0] == msgs_default[0].split(":")[0]

    def test_opt_backtrace_default(self) -> None:
        opts = _Options()
        assert opts.backtrace is True

    def test_opt_diagnose_default(self) -> None:
        opts = _Options()
        assert opts.diagnose is False


class TestContextBinding:
    def test_bind_creates_new_logger(self) -> None:
        log = Logger()
        bound = log.bind(x=1)
        assert bound is not log
        assert log._bound.get("x") is None

    def test_contextualize_scopes_to_block(self) -> None:
        log = Logger()
        sink_id = log.add(lambda m: None, level="DEBUG", format="{message}")
        with log.contextualize(temp="yes"):
            record_in = log.opt(record=True).log("INFO", "inside")
        record_out = log.opt(record=True).log("INFO", "outside")
        log.remove(sink_id)
        assert record_in is not None
        assert record_out is not None
        assert isinstance(record_in["extra"], dict)
        assert isinstance(record_out["extra"], dict)
        assert record_in["extra"].get("temp") == "yes"
        assert "temp" not in record_out["extra"]


class TestCatch:
    def test_catch_context_manager(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        with log.catch():
            raise ValueError("ctx test")
        log.remove(sink_id)
        assert len(messages) >= 1

    def test_catch_decorator(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")

        @log.catch()
        def fail() -> None:
            raise TypeError("dec test")

        fail()
        log.remove(sink_id)
        assert len(messages) >= 1

    def test_catch_exclude(self) -> None:
        log = Logger()
        sink_id = log.add(lambda m: None, level="DEBUG", format="{message}")
        with pytest.raises(ValueError):
            with log.catch(exclude=(ValueError,)):
                raise ValueError("excluded")
        log.remove(sink_id)

    def test_catch_reraise(self) -> None:
        log = Logger()
        sink_id = log.add(lambda m: None, level="DEBUG", format="{message}")
        with pytest.raises(IOError):
            with log.catch(reraise=True):
                raise OSError("reraise")
        log.remove(sink_id)

    def test_catch_default_return(self) -> None:
        log = Logger()
        sink_id = log.add(lambda m: None, level="DEBUG", format="{message}")
        val = "unchanged"
        with log.catch(default=42):
            raise ValueError("default")
            val = 99  # noqa: E501
        log.remove(sink_id)
        assert val == "unchanged"


class TestPatchAndClone:
    def test_patch_modifies_record(self) -> None:
        log = Logger()
        messages: list[str] = []

        def add_tag(record: dict[str, Any]) -> None:
            record["extra"]["tagged"] = "yes"

        patched = log.patch(add_tag)
        sink_id = patched.add(lambda m: messages.append(m), level="DEBUG", format="{extra[tagged]}")
        patched.info("patched msg")
        patched.remove(sink_id)
        assert len(messages) >= 1
        assert "yes" in messages[0]

    def test_clone_independent_options(self) -> None:
        log = Logger()
        clone = log.opt(raw=True)
        assert clone._options.raw is True
        assert log._options.raw is False

    def test_deepcopy_full_isolation(self) -> None:
        log = Logger()
        deep = copy.deepcopy(log)
        assert deep is not log
        deep._name = "changed"
        assert log._name == "logly"


class TestLevelManagement:
    def test_all_10_builtin_levels(self) -> None:
        log = Logger()
        builtins = [
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
        for lvl in builtins:
            assert lvl in log.levels

    def test_custom_level_registration(self) -> None:
        log = Logger()
        name, pri, color = log.level("MYLEVEL", no=42, color="magenta")
        assert name == "MYLEVEL"
        assert pri == 42
        assert color == "magenta"

    def test_level_priority_ordering(self) -> None:
        log = Logger()
        msgs: list[str] = []
        sink_id = log.add(lambda m: msgs.append(m), level="TRACE", format="{level}:{message}")
        priorities: dict[str, str] = {}
        for name in log.levels:
            log.opt(record=True).log(name, "test")
            if msgs:
                last = msgs[-1]
                priorities[name] = last.split(":")[0]
        log.remove(sink_id)
        assert priorities.get("TRACE") == "TRACE"
        assert priorities.get("DEBUG") == "DEBUG"
        assert priorities.get("INFO") == "INFO"
        assert priorities.get("WARNING") == "WARNING"
        assert priorities.get("ERROR") == "ERROR"
        assert priorities.get("CRITICAL") == "CRITICAL"
        assert priorities.get("FATAL") == "FATAL"


class TestFileRotation:
    def test_rotation_creates_new_files(self, tmp_path: Path) -> None:
        log = Logger()
        log_file = tmp_path / "rotate.log"
        sink_id = log.add(str(log_file), rotation="20 B", level="DEBUG")
        log.info("first message")
        log.info("second message to trigger rotation")
        log.complete()
        log.remove(sink_id)
        rotated = list(tmp_path.glob("rotate.log.*"))
        assert len(rotated) >= 1

    def test_retention_policy(self, tmp_path: Path) -> None:
        log = Logger()
        log_file = tmp_path / "retain.log"
        sink_id = log.add(str(log_file), rotation="20 B", retention=2, level="DEBUG")
        for _ in range(20):
            log.info("retention test")
        log.complete()
        log.remove(sink_id)
        rotated = list(tmp_path.glob("retain.log.*"))
        assert len(rotated) <= 3
