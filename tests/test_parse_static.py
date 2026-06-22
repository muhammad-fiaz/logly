"""Tests for Logger.parse() as a static method."""

from __future__ import annotations

from pathlib import Path

from logly import Logger


def test_parse_returns_list_of_dicts(tmp_path: Path) -> None:
    log_file = tmp_path / "test.log"
    log_file.write_text("INFO hello\nERROR world\n", encoding="utf-8")
    results = list(Logger.parse(log_file, r"(?P<level>\w+) (?P<msg>.*)"))
    assert len(results) == 2
    assert results[0]["level"] == "INFO"
    assert results[0]["msg"] == "hello"


def test_parse_no_pattern_returns_full_line(tmp_path: Path) -> None:
    log_file = tmp_path / "test.log"
    log_file.write_text("line one\nline two\n", encoding="utf-8")
    results = list(Logger.parse(log_file))
    assert len(results) == 2
    assert results[0]["message"] == "line one"
    assert results[1]["message"] == "line two"


def test_parse_nonexistent_file_returns_empty() -> None:
    results = list(Logger.parse("/nonexistent/path.log"))
    assert results == []


def test_parse_with_cast(tmp_path: Path) -> None:
    log_file = tmp_path / "test.log"
    log_file.write_text("2024-01-15 42 INFO done\n", encoding="utf-8")
    results = list(
        Logger.parse(
            log_file,
            r"(?P<date>\S+) (?P<count>\d+) (?P<level>\w+) (?P<msg>.*)",
            cast={"count": int},
        )
    )
    assert len(results) == 1
    assert results[0]["count"] == 42
    assert isinstance(results[0]["count"], int)


def test_parse_with_compiled_pattern(tmp_path: Path) -> None:
    import re

    log_file = tmp_path / "test.log"
    log_file.write_text("ERROR: something broke\n", encoding="utf-8")
    pattern = re.compile(r"(?P<level>\w+): (?P<msg>.*)")
    results = list(Logger.parse(log_file, pattern))
    assert len(results) == 1
    assert results[0]["level"] == "ERROR"
    assert results[0]["msg"] == "something broke"


def test_parse_empty_file(tmp_path: Path) -> None:
    log_file = tmp_path / "empty.log"
    log_file.write_text("", encoding="utf-8")
    results = list(Logger.parse(log_file, r"(?P<level>\w+)"))
    assert results == []


def test_parse_line_not_matching_pattern(tmp_path: Path) -> None:
    log_file = tmp_path / "test.log"
    log_file.write_text(
        "2024-01-01 INFO hello\n---separator---\n2024-01-02 ERROR world\n", encoding="utf-8"
    )
    results = list(Logger.parse(log_file, r"(?P<date>\S+) (?P<level>\w+) (?P<msg>.*)"))
    assert len(results) == 2


def test_parse_chunk_parameter(tmp_path: Path) -> None:
    log_file = tmp_path / "test.log"
    log_file.write_text("A\nB\n", encoding="utf-8")
    results = list(Logger.parse(log_file, chunk=1))
    assert len(results) == 2


def test_parse_encoding_parameter(tmp_path: Path) -> None:
    log_file = tmp_path / "test.log"
    log_file.write_text("hello\n", encoding="utf-8")
    results = list(Logger.parse(log_file, encoding="utf-8"))
    assert len(results) == 1
    assert results[0]["message"] == "hello"


def test_parse_cast_key_not_in_result(tmp_path: Path) -> None:
    log_file = tmp_path / "test.log"
    log_file.write_text("INFO hello\n", encoding="utf-8")
    results = list(Logger.parse(log_file, r"(?P<level>\w+) (?P<msg>.*)", cast={"missing": int}))
    assert len(results) == 1
    assert results[0]["level"] == "INFO"


def test_parse_cast_value_error_handled(tmp_path: Path) -> None:
    log_file = tmp_path / "test.log"
    log_file.write_text("INFO hello\n", encoding="utf-8")
    results = list(Logger.parse(log_file, r"(?P<level>\w+) (?P<msg>.*)", cast={"level": int}))
    # "INFO" cannot be cast to int, so original value is kept
    assert results[0]["level"] == "INFO"
