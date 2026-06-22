"""Tests for logger.add() parameters: patch, encoding, delay, catch, mode."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from logly import logger


class TestAddPatch:
    def test_patch_param(self) -> None:
        messages: list[str] = []

        def patcher(record: dict[str, Any]) -> None:
            record.setdefault("extra", {})["patched"] = "yes"

        sink_id = logger.add(lambda m: messages.append(m), level="TRACE", patch=patcher)
        logger.info("test")
        logger.remove(sink_id)
        assert len(messages) == 1


class TestAddEncoding:
    def test_encoding_param(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.log"
            sink_id = logger.add(str(path), level="INFO", encoding="utf-8")
            logger.info("test encoding")
            logger.remove(sink_id)
            assert path.exists()
            content = path.read_text(encoding="utf-8")
            assert "test encoding" in content


class TestAddDelay:
    def test_delay_param(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "delayed.log"
            sink_id = logger.add(str(path), level="INFO", delay=True)
            assert not path.exists() or path.stat().st_size == 0
            logger.info("delayed write")
            logger.remove(sink_id)


class TestAddCatch:
    def test_catch_prevents_sink_error(self) -> None:
        def broken_sink(msg: str) -> None:
            raise OSError("sink broken")

        sink_id = logger.add(broken_sink, level="INFO", catch=True)
        logger.info("this should not raise")
        logger.remove(sink_id)


class TestAddMode:
    def test_mode_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "overwrite.log"
            path.write_text("old content\n")
            sink_id = logger.add(str(path), level="INFO", mode="w")
            logger.info("new content")
            logger.remove(sink_id)
            content = path.read_text()
            assert "old content" not in content
