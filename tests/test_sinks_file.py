"""Tests for file sinks."""

from __future__ import annotations

from pathlib import Path

from logly import logger


class TestFileSink:
    """Tests for file-based sinks."""

    def test_file_sink_creates_file(self, tmp_path: Path) -> None:
        """File sink should create the file."""
        log_file = tmp_path / "test.log"
        sink_id = logger.add(str(log_file), level="DEBUG")
        logger.info("hello file")
        logger.remove(sink_id)
        assert log_file.exists()

    def test_file_sink_writes_content(self, tmp_path: Path) -> None:
        """File sink should write formatted content."""
        log_file = tmp_path / "test.log"
        sink_id = logger.add(str(log_file))
        logger.info("test content")
        logger.remove(sink_id)
        content = log_file.read_text()
        assert "test content" in content

    def test_file_sink_append_mode(self, tmp_path: Path) -> None:
        """File sink should append by default."""
        log_file = tmp_path / "test.log"
        sink_id = logger.add(str(log_file))
        logger.info("first line")
        logger.info("second line")
        logger.remove(sink_id)
        content = log_file.read_text()
        assert "first line" in content
        assert "second line" in content

    def test_file_sink_multiple_messages(self, tmp_path: Path) -> None:
        """File sink should append multiple messages."""
        log_file = tmp_path / "test.log"
        sink_id = logger.add(str(log_file))
        logger.info("first")
        logger.info("second")
        logger.remove(sink_id)
        content = log_file.read_text()
        assert "first" in content
        assert "second" in content

    def test_file_sink_with_path_object(self, tmp_path: Path) -> None:
        """File sink should accept Path objects."""
        log_file = tmp_path / "test.log"
        sink_id = logger.add(log_file)
        logger.info("path object test")
        logger.remove(sink_id)
        assert log_file.exists()

    def test_file_sink_with_format(self, tmp_path: Path) -> None:
        """File sink should support custom format."""
        log_file = tmp_path / "test.log"
        sink_id = logger.add(str(log_file), format="{message}")
        logger.info("no level prefix")
        logger.remove(sink_id)
        content = log_file.read_text()
        assert "no level prefix" in content
        assert "INFO" not in content

    def test_file_sink_json_format(self, tmp_path: Path) -> None:
        """File sink should support JSON format."""
        log_file = tmp_path / "test.log"
        sink_id = logger.add(str(log_file), serialize=True)
        logger.info("json test")
        logger.remove(sink_id)
        content = log_file.read_text()
        assert '"level"' in content
        assert '"message"' in content
