"""Tests for logger.parse() log file parsing."""

from __future__ import annotations

import tempfile
from pathlib import Path

from logly import logger


class TestParseMethod:
    def test_parse_with_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.log"
            path.write_text("2024-01-01 INFO hello\n2024-01-02 ERROR world\n")
            results = list(logger.parse(str(path), r"(?P<date>\S+) (?P<level>\S+) (?P<msg>.*)"))
            assert len(results) == 2
            assert results[0]["date"] == "2024-01-01"
            assert results[0]["level"] == "INFO"
            assert results[0]["msg"] == "hello"
            assert results[1]["level"] == "ERROR"

    def test_parse_no_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.log"
            path.write_text("line1\nline2\n")
            results = list(logger.parse(str(path)))
            assert len(results) == 2
            assert results[0]["message"] == "line1"

    def test_parse_nonexistent_file(self) -> None:
        results = list(logger.parse("/nonexistent/file.log"))
        assert results == []
