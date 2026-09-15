"""Tests for integration utilities."""

from __future__ import annotations

from logly.integrations._utils import detect_canonical_level, strip_ansi


class TestStripAnsi:
    def test_strip_color_codes(self) -> None:
        text = "\x1b[31mred\x1b[0m"
        assert strip_ansi(text) == "red"

    def test_strip_bold_code(self) -> None:
        text = "\x1b[1mbold\x1b[0m"
        assert strip_ansi(text) == "bold"

    def test_strip_multiple_codes(self) -> None:
        text = "\x1b[1m\x1b[31mbold red\x1b[0m"
        assert strip_ansi(text) == "bold red"

    def test_no_ansi_codes(self) -> None:
        text = "plain text"
        assert strip_ansi(text) == "plain text"

    def test_empty_string(self) -> None:
        assert strip_ansi("") == ""

    def test_only_ansi_codes(self) -> None:
        text = "\x1b[0m"
        assert strip_ansi(text) == ""

    def test_nested_ansi_codes(self) -> None:
        text = "\x1b[1;31;4mbold red underline\x1b[0m"
        assert strip_ansi(text) == "bold red underline"

    def test_ansi_in_middle(self) -> None:
        text = "before\x1b[31m middle\x1b[0m after"
        assert strip_ansi(text) == "before middle after"

    def test_256_color_code(self) -> None:
        text = "\x1b[38;5;196mred256\x1b[0m"
        assert strip_ansi(text) == "red256"

    def test_truecolor_code(self) -> None:
        text = "\x1b[38;2;255;0;0mredrgb\x1b[0m"
        assert strip_ansi(text) == "redrgb"

    def test_cursor_movement_not_stripped(self) -> None:
        text = "\x1b[2J\x1b[HCleared"
        result = strip_ansi(text)
        assert "Cleared" in result

    def test_text_without_escape(self) -> None:
        text = "hello world 123"
        assert strip_ansi(text) == text


class TestDetectCanonicalLevel:
    def test_critical_priority(self) -> None:
        assert detect_canonical_level("CRITICAL failure") == "CRITICAL"
        assert detect_canonical_level("fatal error") == "CRITICAL"

    def test_error_priority(self) -> None:
        assert detect_canonical_level("ERROR boom") == "ERROR"
        assert detect_canonical_level("operation failed") == "ERROR"

    def test_warning(self) -> None:
        assert detect_canonical_level("WARNING slow") == "WARNING"
        assert detect_canonical_level("warn: deprecated") == "WARNING"

    def test_notice_success(self) -> None:
        assert detect_canonical_level("NOTICE served") == "NOTICE"
        assert detect_canonical_level("SUCCESS done") == "SUCCESS"

    def test_trace_debug(self) -> None:
        assert detect_canonical_level("TRACE enter") == "TRACE"
        assert detect_canonical_level("DEBUG detail") == "DEBUG"

    def test_default_info(self) -> None:
        assert detect_canonical_level("hello world") == "INFO"

    def test_most_severe_wins(self) -> None:
        assert detect_canonical_level("CRITICAL ... ERROR ...") == "CRITICAL"
        assert detect_canonical_level("ERROR ... WARNING ...") == "ERROR"
