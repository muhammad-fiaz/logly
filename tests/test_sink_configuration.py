"""Tests for sink configuration validation and file-sink behavior."""

from __future__ import annotations

import io
import multiprocessing as mp
import os
from pathlib import Path
from typing import Any

import pytest

from logly import Logger
from logly.models import RotationPolicy


def _spawn_worker(path: str) -> None:
    from logly import Logger as ChildLogger

    child = ChildLogger()
    child.add(path, format="{message}", level="INFO")
    child.info("hello from child")
    child.complete()
    child.remove()


def _messages_sink(logger: Logger, **kwargs: Any) -> tuple[list[str], int]:
    messages: list[str] = []
    sink_id = logger.add(lambda m: messages.append(m), level="DEBUG", format="{message}", **kwargs)
    return messages, sink_id


class TestLevelResolution:
    def test_int_level_accepted(self) -> None:
        logger = Logger()
        messages: list[str] = []
        sink_id = logger.add(messages.append, level=20, format="{message}")
        try:
            logger.info("numeric threshold")
        finally:
            logger.remove(sink_id)
        assert messages == ["numeric threshold\n"]

    def test_int_level_filters(self) -> None:
        logger = Logger()
        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), level=50, format="{message}")
        try:
            logger.info("dropped")
            logger.error("kept")
        finally:
            logger.remove(sink_id)
        assert messages == ["kept\n"]

    def test_unknown_level_raises(self) -> None:
        logger = Logger()
        with pytest.raises(ValueError):
            logger.add(io.StringIO(), level="NO_SUCH_LEVEL")

    def test_bool_level_rejected(self) -> None:
        logger = Logger()
        with pytest.raises(TypeError):
            logger.add(io.StringIO(), level=True)  # type: ignore[arg-type]


class TestModeValidation:
    def test_write_mode_truncates(self, tmp_path: Path) -> None:
        target = tmp_path / "mode.log"
        target.write_text("stale", encoding="utf-8")
        logger = Logger()
        sink_id = logger.add(str(target), format="{message}", mode="w")
        try:
            logger.info("fresh")
            logger.complete()
        finally:
            logger.remove(sink_id)
        assert target.read_text(encoding="utf-8") == "fresh\n"

    def test_invalid_mode_raises(self) -> None:
        logger = Logger()
        with pytest.raises(ValueError, match="mode"):
            logger.add(io.StringIO(), mode="x")


class TestRotationValidation:
    def test_garbage_rotation_raises(self) -> None:
        logger = Logger()
        with pytest.raises((ValueError, TypeError)):
            logger.add(io.StringIO(), rotation=3.5)
        with pytest.raises((ValueError, TypeError)):
            logger.add(io.StringIO(), rotation=True)
        with pytest.raises((ValueError, TypeError)):
            logger.add(io.StringIO(), rotation=object())

    def test_rotation_requires_file_sink(self) -> None:
        logger = Logger()
        with pytest.raises(ValueError, match="file path"):
            logger.add(io.StringIO(), rotation="1 KB")
        with pytest.raises(ValueError, match="file path"):
            logger.add(io.StringIO(), retention=2)
        with pytest.raises(ValueError, match="file path"):
            logger.add(io.StringIO(), compression="gzip")
        with pytest.raises(ValueError, match="file path"):
            logger.add(io.StringIO(), delay=True)
        with pytest.raises(ValueError, match="file path"):
            logger.add(io.StringIO(), watch=True)

    def test_callable_rotation(self, tmp_path: Path) -> None:
        log_file = tmp_path / "cond.log"
        logger = Logger()
        sink_id = logger.add(
            str(log_file), format="{message}", rotation=lambda path, size: size > 100
        )
        try:
            for i in range(30):
                logger.info("cond-message-{:02d}-padding", i)
            logger.complete()
        finally:
            logger.remove(sink_id)
        rotated = [p for p in tmp_path.iterdir() if p.name.startswith("cond.log.")]
        assert len(rotated) >= 1

    def test_callable_rotation_failure_surfaces(self, tmp_path: Path) -> None:
        log_file = tmp_path / "cond.log"

        def broken(path: str, size: int) -> bool:
            raise RuntimeError("condition exploded")

        logger = Logger()
        sink_id = logger.add(str(log_file), format="{message}", rotation=broken)
        try:
            with pytest.raises(RuntimeError, match="condition exploded"):
                logger.info("trigger")
                logger.complete()
        finally:
            logger.remove(sink_id)

    def test_callable_must_return_bool(self, tmp_path: Path) -> None:
        log_file = tmp_path / "cond.log"
        logger = Logger()
        sink_id = logger.add(str(log_file), format="{message}", rotation=lambda path, size: "yes")
        try:
            with pytest.raises(RuntimeError, match="bool"):
                logger.info("y" * 200)
                logger.complete()
        finally:
            logger.remove(sink_id)

    def test_policy_object_kinds(self, tmp_path: Path) -> None:
        for kind, value in (
            ("clock", "00:00"),
            ("weekday", 0),
            ("weekday", "monday"),
            ("never", None),
            ("size", 1024),
            ("interval", 60),
        ):
            log_file = tmp_path / f"{kind}.log"
            logger = Logger()
            sink_id = logger.add(
                str(log_file),
                format="{message}",
                rotation=RotationPolicy(kind=kind, value=value),  # type: ignore[arg-type]
            )
            try:
                logger.info("ok")
                logger.complete()
            finally:
                logger.remove(sink_id)

    def test_policy_object_invalid(self) -> None:
        logger = Logger()
        for kind, value in (
            ("clock", "99:99"),
            ("weekday", 7),
            ("weekday", "funday"),
            ("bogus", 1),
            ("callable", 42),
        ):
            with pytest.raises((ValueError, TypeError)):
                logger.add(
                    io.StringIO(),
                    rotation=RotationPolicy(kind=kind, value=value),  # type: ignore[arg-type]
                )


class TestRetentionCompressionValidation:
    def test_garbage_policies_raise(self) -> None:
        logger = Logger()
        with pytest.raises((ValueError, TypeError)):
            logger.add(io.StringIO(), retention=object())
        with pytest.raises((ValueError, TypeError)):
            logger.add(io.StringIO(), retention=True)
        with pytest.raises((ValueError, TypeError)):
            logger.add(io.StringIO(), compression=123)
        with pytest.raises((ValueError, TypeError)):
            logger.add(io.StringIO(), compression=object())


class TestPythonOpenedFiles:
    def test_opener_called(self, tmp_path: Path) -> None:
        log_file = tmp_path / "op.log"
        seen: list[str] = []

        def opener(path: str, flags: int) -> int:
            seen.append(path)
            return os.open(path, flags, 0o600)

        logger = Logger()
        sink_id = logger.add(str(log_file), format="{message}", opener=opener)
        try:
            logger.info("via-opener")
            logger.complete()
        finally:
            logger.remove(sink_id)
        assert log_file.read_text(encoding="utf-8") == "via-opener\n"
        assert seen

    def test_opener_with_rotation_raises(self, tmp_path: Path) -> None:
        def opener(path: str, flags: int) -> int:
            return os.open(path, flags)

        logger = Logger()
        with pytest.raises(ValueError, match="rotation"):
            logger.add(str(tmp_path / "op.log"), opener=opener, rotation="1 KB")

    def test_non_utf8_encoding(self, tmp_path: Path) -> None:
        log_file = tmp_path / "latin.log"
        logger = Logger()
        sink_id = logger.add(str(log_file), format="{message}", encoding="latin-1")
        try:
            logger.info("héllo")
            logger.complete()
        finally:
            logger.remove(sink_id)
        assert log_file.read_bytes() == "héllo\n".encode("latin-1")

    def test_reinstall_reopens(self, tmp_path: Path) -> None:
        log_file = tmp_path / "re.log"
        logger = Logger()
        sink_id = logger.add(str(log_file), format="{message}", encoding="latin-1")
        try:
            logger.info("one")
            logger.complete()
            logger.reinstall(sink_id)
            logger.info("two")
            logger.complete()
        finally:
            logger.remove()
        assert log_file.read_bytes() == "one\ntwo\n".encode("latin-1")


class TestBinaryStreams:
    def test_bytesio_sink(self) -> None:
        logger = Logger()
        stream = io.BytesIO()
        sink_id = logger.add(stream, format="{message}")
        try:
            logger.info("hello-bytes")
            logger.complete()
        finally:
            logger.remove(sink_id)
        assert stream.getvalue() == b"hello-bytes\n"

    def test_sink_not_closed_on_remove(self) -> None:
        logger = Logger()
        stream = io.BytesIO()
        sink_id = logger.add(stream, format="{message}")
        logger.info("x")
        logger.complete()
        logger.remove(sink_id)
        assert stream.getvalue() == b"x\n"
        assert not stream.closed

    def test_binary_with_encoding(self) -> None:
        logger = Logger()
        stream = io.BytesIO()
        sink_id = logger.add(stream, format="{message}", encoding="latin-1")
        try:
            logger.info("héllo")
            logger.complete()
        finally:
            logger.remove(sink_id)
        assert stream.getvalue() == "héllo\n".encode("latin-1")


class TestSinkShape:
    def test_write_less_object_rejected(self) -> None:
        logger = Logger()
        with pytest.raises(TypeError, match="sink must be"):
            logger.add(object())

    def test_console_rotation_rejected(self) -> None:
        logger = Logger()
        with pytest.raises(ValueError, match="file path"):
            logger.add("stderr", rotation="1 KB")


class TestContextRejected:
    def test_non_none_context_raises(self) -> None:
        logger = Logger()
        with pytest.raises(TypeError, match="context"):
            logger.add(io.StringIO(), context="spawn")  # type: ignore[arg-type]


class TestConfigureRollback:
    def test_invalid_handler_keeps_existing_sinks(self) -> None:
        logger = Logger()
        messages: list[str] = []
        sink_id = logger.add(lambda m: messages.append(m), format="{message}")
        try:
            with pytest.raises((ValueError, TypeError)):
                logger.configure(
                    handlers=[
                        {"sink": io.StringIO(), "rotation": "1 KB"},
                        {"sink": io.StringIO(), "mode": "bogus"},
                    ]
                )
            logger.info("still here")
            logger.complete()
        finally:
            logger.remove(sink_id)
        assert messages == ["still here\n"]

    def test_valid_configure_replaces(self) -> None:
        logger = Logger()
        first: list[str] = []
        logger.add(lambda m: first.append(m), format="{message}")
        second: list[str] = []
        logger.configure(handlers=[{"sink": second.append, "format": "{message}"}])
        try:
            logger.info("moved")
            logger.complete()
        finally:
            logger.remove()
        assert first == []
        assert second == ["moved\n"]


class TestSpawnMultiprocessing:
    def test_spawn_child_logs(self, tmp_path: Path) -> None:
        ctx = mp.get_context("spawn")
        target = str(tmp_path / "child.log")
        proc = ctx.Process(target=_spawn_worker, args=(target,))
        proc.start()
        proc.join(timeout=60)
        assert proc.exitcode == 0
        assert Path(target).read_text(encoding="utf-8") == "hello from child\n"
