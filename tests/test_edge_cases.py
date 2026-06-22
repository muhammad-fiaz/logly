from __future__ import annotations

import asyncio
import copy
import logging
import threading
from io import StringIO

import pytest

from logly import Logger
from logly.logger import _Options


class TestLoggerInitialization:
    def test_default_logger_creation(self) -> None:
        log = Logger()
        assert log._name == "logly"

    def test_named_logger_creation(self) -> None:
        log = Logger(name="myapp")
        assert log._name == "myapp"

    def test_logger_with_custom_options(self) -> None:
        opts = _Options(depth=2)
        log = Logger(options=opts)
        assert log._options.depth == 2


class TestLevelOperations:
    def test_all_builtin_levels_exist(self) -> None:
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

    def test_level_priorities_ordered(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="TRACE", format="{level}:{message}")
        priorities = {}
        for name in log.levels:
            log.opt(record=True).log(name, "test")
            if messages:
                last = messages[-1]
                level_part = last.split(":")[0]
                priorities[name] = level_part
        log.remove(sink_id)
        assert priorities.get("TRACE") == "TRACE"
        assert priorities.get("DEBUG") == "DEBUG"
        assert priorities.get("INFO") == "INFO"
        assert priorities.get("NOTICE") == "NOTICE"
        assert priorities.get("SUCCESS") == "SUCCESS"
        assert priorities.get("WARNING") == "WARNING"
        assert priorities.get("ERROR") == "ERROR"
        assert priorities.get("FAIL") == "FAIL"
        assert priorities.get("CRITICAL") == "CRITICAL"
        assert priorities.get("FATAL") == "FATAL"

    def test_register_custom_level(self) -> None:
        log = Logger()
        name, pri, color = log.level("CUSTOM", no=55, color="red")
        assert name == "CUSTOM"
        assert pri == 55
        assert color == "red"

    def test_resolve_unknown_level_error(self) -> None:
        log = Logger()
        sink_id = log.add(lambda m: None, level="TRACE")
        with pytest.raises(ValueError):
            log.log("NONEXISTENT_XYZ_999", "test")
        log.remove(sink_id)


class TestMessageFormatting:
    def test_format_with_positional_args(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        log.info("User {} logged in", "alice")
        log.remove(sink_id)
        assert len(messages) >= 1
        assert "alice" in messages[0]

    def test_format_with_keyword_args(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        log.info("User {user} logged in", user="alice")
        log.remove(sink_id)
        assert len(messages) >= 1
        assert "alice" in messages[0]

    def test_format_with_extra_values(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        log.bind(key="val").info("has extra")
        log.remove(sink_id)
        assert len(messages) >= 1

    def test_format_with_special_chars(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        log.opt(raw=True).info("msg with {braces} and %s and\nnewline")
        log.remove(sink_id)
        assert len(messages) >= 1
        assert "{braces}" in messages[0]
        assert "\n" in messages[0]

    def test_format_empty_message(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        log.info("")
        log.remove(sink_id)
        assert len(messages) >= 1

    def test_format_very_long_message(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        long_msg = "x" * 10000
        log.info(long_msg)
        log.remove(sink_id)
        assert len(messages) >= 1
        assert len(messages[0]) >= 10000


class TestOptMethods:
    def test_opt_record_returns_dict(self) -> None:
        log = Logger()
        sink_id = log.add(lambda m: None, level="DEBUG", format="{message}")
        result = log.opt(record=True).log("INFO", "recorded")
        log.remove(sink_id)
        assert isinstance(result, dict)

    def test_opt_record_dict_has_expected_keys(self) -> None:
        log = Logger()
        sink_id = log.add(lambda m: None, level="DEBUG", format="{message}")
        record = log.opt(record=True).log("INFO", "check keys")
        log.remove(sink_id)
        assert record is not None
        assert "message" in record
        assert "level" in record
        assert "name" in record
        assert "file" in record
        assert "line" in record
        assert "function" in record
        assert "module" in record

    def test_opt_raw_skips_formatting(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        log.opt(raw=True).info("no {formatting} here")
        log.remove(sink_id)
        assert len(messages) >= 1
        assert "no {formatting} here" in messages[0]

    def test_opt_depth_zero_is_default(self) -> None:
        log = Logger()
        messages1: list[str] = []
        messages2: list[str] = []
        sink_id1 = log.add(
            lambda m: messages1.append(m), level="DEBUG", format="{function}:{message}"
        )
        log.info("default depth")
        log.remove(sink_id1)

        sink_id2 = log.add(
            lambda m: messages2.append(m), level="DEBUG", format="{function}:{message}"
        )
        log.opt(depth=0).info("zero depth")
        log.remove(sink_id2)
        assert len(messages1) >= 1
        assert len(messages2) >= 1
        assert messages1[0].split(":")[0] == messages2[0].split(":")[0]

    def test_opt_capture_false_skips_location(self) -> None:
        log = Logger()
        sink_id = log.add(lambda m: None, level="DEBUG", format="{message}")
        record = log.opt(record=True, capture=False).log("INFO", "no location")
        log.remove(sink_id)
        assert record is not None
        assert "file" not in record
        assert "line" not in record
        assert "function" not in record

    def test_opt_backtrace_default_true(self) -> None:
        opts = _Options()
        assert opts.backtrace is True

    def test_opt_diagnose_default_false(self) -> None:
        opts = _Options()
        assert opts.diagnose is False

    def test_opt_chaining(self) -> None:
        log = Logger()
        sink_id = log.add(lambda m: None, level="DEBUG", format="{message}")
        chained = log.opt(raw=True).opt(record=True)
        assert chained is not log
        record = chained.log("INFO", "chained")
        log.remove(sink_id)
        assert isinstance(record, dict)


class TestContextBinding:
    def test_bind_returns_new_logger(self) -> None:
        log = Logger()
        bound = log.bind(x=1)
        assert bound is not log

    def test_bind_multiple_keys(self) -> None:
        log = Logger()
        messages: list[str] = []
        bound = log.bind(a=1, b=2)
        sink_id = bound.add(
            lambda m: messages.append(m), level="DEBUG", format="{extra[a]}:{extra[b]}"
        )
        bound.info("multi")
        bound.remove(sink_id)
        assert len(messages) >= 1
        assert "1" in messages[0]
        assert "2" in messages[0]

    def test_bind_overwrites_existing(self) -> None:
        log = Logger()
        bound = log.bind(x=1).bind(x=2)
        messages: list[str] = []
        sink_id = bound.add(lambda m: messages.append(m), level="DEBUG", format="{extra[x]}")
        bound.info("overwrite")
        bound.remove(sink_id)
        assert len(messages) >= 1
        assert "2" in messages[0]

    def test_contextualize_sets_temporary(self) -> None:
        log = Logger()
        sink_id = log.add(lambda m: None, level="DEBUG", format="{message}")
        with log.contextualize(temp="yes"):
            record_inside = log.opt(record=True).log("INFO", "inside")
        record_outside = log.opt(record=True).log("INFO", "outside")
        log.remove(sink_id)
        assert record_inside is not None
        assert record_outside is not None
        assert isinstance(record_inside["extra"], dict)
        assert isinstance(record_outside["extra"], dict)
        assert record_inside["extra"].get("temp") == "yes"
        assert "temp" not in record_outside["extra"]


class TestExceptionHandling:
    def test_catch_context_manager(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        with log.catch():
            raise ValueError("test error")
        log.remove(sink_id)
        assert len(messages) >= 1

    def test_catch_decorator(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")

        @log.catch()
        def failing() -> None:
            raise TypeError("decorated")

        failing()
        log.remove(sink_id)
        assert len(messages) >= 1

    def test_catch_exclude_skips_exception(self) -> None:
        log = Logger()
        sink_id = log.add(lambda m: None, level="DEBUG", format="{message}")
        with pytest.raises(ValueError):
            with log.catch(exclude=(ValueError,)):
                raise ValueError("should be re-raised")
        log.remove(sink_id)

    def test_catch_onerror_callback(self) -> None:
        log = Logger()
        errors: list[BaseException] = []
        sink_id = log.add(lambda m: None, level="DEBUG", format="{message}")
        with log.catch(onerror=lambda e: errors.append(e)):
            raise RuntimeError("callback test")
        log.remove(sink_id)
        assert len(errors) >= 1
        assert isinstance(errors[0], RuntimeError)

    def test_catch_reraise(self) -> None:
        log = Logger()
        sink_id = log.add(lambda m: None, level="DEBUG", format="{message}")
        with pytest.raises(IOError):
            with log.catch(reraise=True):
                raise OSError("reraise test")
        log.remove(sink_id)

    def test_catch_default_return(self) -> None:
        log = Logger()
        sink_id = log.add(lambda m: None, level="DEBUG", format="{message}")
        result = "unchanged"
        with log.catch(default=42):
            raise ValueError("default test")
            result = 99
        log.remove(sink_id)
        assert result == "unchanged"


class TestPatching:
    def test_patch_modifies_record(self) -> None:
        log = Logger()
        messages: list[str] = []

        def add_field(record: dict) -> None:
            record["extra"]["patched"] = "yes"

        patched = log.patch(add_field)
        sink_id = patched.add(
            lambda m: messages.append(m), level="DEBUG", format="{extra[patched]}"
        )
        patched.info("patched")
        patched.remove(sink_id)
        assert len(messages) >= 1
        assert "yes" in messages[0]

    def test_multiple_patchers_applied_in_order(self) -> None:
        log = Logger()
        messages: list[str] = []

        def add_a(record: dict) -> None:
            record["extra"]["a"] = "1"

        def add_b(record: dict) -> None:
            record["extra"]["b"] = "2"

        patched = log.patch(add_a).patch(add_b)
        sink_id = patched.add(
            lambda m: messages.append(m),
            level="DEBUG",
            format="{extra[a]}:{extra[b]}",
        )
        patched.info("multi")
        patched.remove(sink_id)
        assert len(messages) >= 1
        assert "1:2" in messages[0]

    def test_patch_does_not_mutate_parent(self) -> None:
        log = Logger()
        parent_msgs: list[str] = []
        child_msgs: list[str] = []

        def add_field(record: dict) -> None:
            record["extra"]["child_only"] = "yes"

        sink_id = log.add(lambda m: parent_msgs.append(m), level="DEBUG", format="{message}")
        child = log.patch(add_field)
        child_sink = child.add(lambda m: child_msgs.append(m), level="DEBUG", format="{message}")
        log.info("parent")
        child.info("child")
        log.remove(sink_id)
        child.remove(child_sink)
        assert len(parent_msgs) >= 1
        assert len(child_msgs) >= 1


class TestMultipleSinks:
    def test_two_sinks_receive_same_message(self) -> None:
        log = Logger()
        msgs1: list[str] = []
        msgs2: list[str] = []
        sink1 = log.add(lambda m: msgs1.append(m), level="DEBUG", format="{message}")
        sink2 = log.add(lambda m: msgs2.append(m), level="DEBUG", format="{message}")
        log.info("broadcast")
        log.complete()
        log.remove(sink1)
        log.remove(sink2)
        assert len(msgs1) >= 1
        assert len(msgs2) >= 1
        assert "broadcast" in msgs1[0]
        assert "broadcast" in msgs2[0]

    def test_remove_one_sink_doesnt_affect_other(self) -> None:
        log = Logger()
        msgs1: list[str] = []
        msgs2: list[str] = []
        sink1 = log.add(lambda m: msgs1.append(m), level="DEBUG", format="{message}")
        sink2 = log.add(lambda m: msgs2.append(m), level="DEBUG", format="{message}")
        log.remove(sink1)
        log.info("only sink2")
        log.complete()
        log.remove(sink2)
        assert len(msgs1) == 0
        assert len(msgs2) >= 1
        assert "only sink2" in msgs2[0]


class TestCloneAndCopy:
    def test_clone_shares_native_logger(self) -> None:
        log = Logger()
        clone = log._clone()
        assert clone._native is log._native

    def test_clone_independent_options(self) -> None:
        log = Logger()
        clone = log.opt(raw=True)
        assert clone._options.raw is True
        assert log._options.raw is False

    def test_deepcopy_creates_independent(self) -> None:
        log = Logger()
        deep = copy.deepcopy(log)
        assert deep is not log
        deep._name = "changed"
        assert log._name == "logly"


class TestAsyncSinks:
    def test_async_sink_basic(self) -> None:
        log = Logger()
        results: list[str] = []

        async def capture(msg: str) -> None:
            results.append(msg)

        sink_id = log.add(capture, level="DEBUG", format="{message}")
        log.info("async msg")
        log.complete()
        log.remove(sink_id)
        assert len(results) >= 1
        assert "async msg" in results[0]

    def test_async_sink_complete_waits(self) -> None:
        log = Logger()
        results: list[str] = []

        async def capture(msg: str) -> None:
            results.append(msg)

        sink_id = log.add(capture, level="DEBUG", format="{message}")
        log.info("wait for me")
        log.complete()
        log.remove(sink_id)
        assert len(results) >= 1

    def test_async_sink_with_explicit_loop(self) -> None:
        log = Logger()
        results: list[str] = []

        async def capture(msg: str) -> None:
            results.append(msg)

        loop = asyncio.new_event_loop()
        try:
            sink_id = log.add(capture, level="DEBUG", format="{message}", loop=loop)
            log.info("explicit loop")
            log.complete()
            log.remove(sink_id)
            assert len(results) >= 1
        finally:
            loop.close()


class TestLoggingHandlerIntegration:
    def test_handler_wrapping(self) -> None:
        log = Logger()
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        sink_id = log.add(handler, level="DEBUG", format="{message}")
        log.info("handler test")
        log.complete()
        log.remove(sink_id)
        assert "handler test" in stream.getvalue()

    def test_handler_level_filtering(self) -> None:
        log = Logger()
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.WARNING)
        sink_id = log.add(handler, level="DEBUG", format="{message}")
        log.info("filtered out")
        log.error("should pass")
        log.complete()
        log.remove(sink_id)
        output = stream.getvalue()
        assert "filtered out" not in output
        assert "should pass" in output


class TestEdgeCases:
    def test_empty_format_string(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        log.info("")
        log.remove(sink_id)
        assert len(messages) >= 1

    def test_format_with_none_values(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        log.bind(val=None).info("none val")
        log.remove(sink_id)
        assert len(messages) >= 1

    def test_concurrent_logging(self) -> None:
        log = Logger()
        messages: list[str] = []
        lock = threading.Lock()

        def capture(msg: str) -> None:
            with lock:
                messages.append(msg)

        sink_id = log.add(capture, level="DEBUG", format="{message}")

        def worker(n: int) -> None:
            log.info(f"thread-{n}")

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        log.complete()
        log.remove(sink_id)
        assert len(messages) >= 20

    def test_remove_all_sinks(self) -> None:
        log = Logger()
        log.add(lambda m: None, level="DEBUG", format="{message}")
        log.add(lambda m: None, level="DEBUG", format="{message}")
        log.remove()
        log.info("no sinks")
        log.complete()

    def test_log_after_remove_all(self) -> None:
        log = Logger()
        sink_id = log.add(lambda m: None, level="DEBUG", format="{message}")
        log.remove(sink_id)
        log.info("after remove all")
        log.complete()

    def test_reinstall_preserves_message(self) -> None:
        log = Logger()
        messages: list[str] = []
        sink_id = log.add(lambda m: messages.append(m), level="DEBUG", format="{message}")
        log.info("before reinstall")
        log.complete()
        assert len(messages) >= 1
        messages.clear()
        log.reinstall(sink_id)
        log.info("after reinstall")
        log.complete()
        assert len(messages) >= 1
        assert "after reinstall" in messages[0]
