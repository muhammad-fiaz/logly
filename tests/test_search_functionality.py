"""
Comprehensive tests for log file search functionality.

Tests the search_log() method with various scenarios including:
- Case-sensitive and case-insensitive searches
- First match only vs all matches
- Multiple occurrences handling
- Edge cases (empty files, no matches, invalid sinks)
"""

import tempfile
from pathlib import Path

import pytest

from logly import logger


@pytest.fixture(autouse=True)
def reset_logger():
    """Reset logger state before each test."""
    logger.reset()
    logger.remove_all()
    yield
    logger.reset()
    logger.remove_all()


class TestBasicSearch:
    """Test basic search functionality."""

    def test_search_finds_single_match(self):
        """Test searching for a string with single occurrence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("Error: Connection failed")
            logger.info("Warning: Retrying connection")
            logger.complete()

            results = logger.search_log(sink_id, "Error")

            assert results is not None
            assert len(results) == 1
            assert results[0]["line"] == 1
            assert "Error: Connection failed" in results[0]["content"]  # type: ignore
            assert results[0]["match"] == "Error"

    def test_search_finds_multiple_matches(self):
        """Test searching for a string with multiple occurrences."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.error("Error: Connection failed")
            logger.info("Processing data")
            logger.error("Error: Timeout occurred")
            logger.complete()

            results = logger.search_log(sink_id, "Error")

            assert results is not None
            assert len(results) == 2
            assert results[0]["line"] == 1
            assert results[1]["line"] == 3
            assert "Connection failed" in results[0]["content"]  # type: ignore
            assert "Timeout occurred" in results[1]["content"]  # type: ignore

    def test_search_no_matches(self):
        """Test searching for a string that doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("Normal log message")
            logger.complete()

            results = logger.search_log(sink_id, "NonExistent")

            assert results is not None
            assert len(results) == 0  # Empty list, not None

    def test_search_empty_file(self):
        """Test searching in an empty log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))
            logger.complete()  # Ensure file is created

            results = logger.search_log(sink_id, "anything")

            assert results is not None
            assert len(results) == 0


class TestCaseSensitivity:
    """Test case-sensitive and case-insensitive searches."""

    def test_case_insensitive_search_default(self):
        """Test that search is case-insensitive by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("ERROR: System failure")
            logger.info("error: User mistake")
            logger.info("Error: Network issue")
            logger.complete()

            results = logger.search_log(sink_id, "error")

            assert results is not None
            assert len(results) == 3  # Finds all case variants
            assert all("error" in r["content"].lower() for r in results)  # type: ignore

    def test_case_sensitive_search(self):
        """Test case-sensitive search mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("ERROR: System failure")
            logger.info("error: User mistake")
            logger.info("Error: Network issue")
            logger.complete()

            results = logger.search_log(sink_id, "error", case_sensitive=True)

            assert results is not None
            assert len(results) == 1  # Only lowercase "error"
            assert results[0]["line"] == 2  # type: ignore
            assert "error: User mistake" in results[0]["content"]  # type: ignore

    def test_case_sensitive_uppercase(self):
        """Test case-sensitive search for uppercase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("ERROR: System failure")
            logger.info("error: User mistake")
            logger.info("Error: Network issue")
            logger.complete()

            results = logger.search_log(sink_id, "ERROR", case_sensitive=True)

            assert results is not None
            assert len(results) == 1  # Only uppercase "ERROR"
            assert "ERROR: System failure" in results[0]["content"]  # type: ignore


class TestFirstOnly:
    """Test first_only parameter."""

    def test_first_only_returns_one_result(self):
        """Test that first_only=True returns only the first match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("Match 1")
            logger.info("Match 2")
            logger.info("Match 3")
            logger.complete()

            results = logger.search_log(sink_id, "Match", first_only=True)

            assert results is not None
            assert len(results) == 1
            assert results[0]["line"] == 1
            assert "Match 1" in results[0]["content"]  # type: ignore

    def test_first_only_with_no_match(self):
        """Test first_only=True when no matches exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("Nothing here")
            logger.complete()

            results = logger.search_log(sink_id, "Match", first_only=True)

            assert results is not None
            assert len(results) == 0

    def test_first_only_finds_middle_line(self):
        """Test first_only returns first occurrence even if it's not on line 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("Line 1: no match")
            logger.info("Line 2: no match")
            logger.info("Line 3: TARGET found")
            logger.info("Line 4: TARGET again")
            logger.complete()

            results = logger.search_log(sink_id, "TARGET", first_only=True)

            assert results is not None
            assert len(results) == 1
            assert results[0]["line"] == 3


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_sink_id_returns_none(self):
        """Test searching with invalid sink ID."""
        results = logger.search_log(99999, "anything")
        assert results is None

    def test_negative_sink_id_returns_none(self):
        """Test searching with negative sink ID."""
        results = logger.search_log(-1, "anything")
        assert results is None

    def test_console_sink_returns_none(self):
        """Test searching console sink (has no file)."""
        logger.configure(auto_sink=False)
        sink_id = logger.add("console")
        results = logger.search_log(sink_id, "anything")
        assert results is None  # Console has no file to search

    def test_search_special_characters(self):
        """Test searching for strings with special characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("Error: [Connection] failed (timeout)")
            logger.complete()

            results = logger.search_log(sink_id, "[Connection]")

            assert results is not None
            assert len(results) == 1
            assert "[Connection]" in results[0]["content"]  # type: ignore

    def test_search_json_logs(self):
        """Test searching in JSON-formatted logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.json"
            sink_id = logger.add(str(log_file), json=True)

            logger.info("Connection established", server="db.example.com")
            logger.complete()

            results = logger.search_log(sink_id, "db.example.com")

            assert results is not None
            assert len(results) >= 1  # JSON formatting may vary

    def test_search_multiline_match(self):
        """Test searching in logs with multiline content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("First line with KEYWORD")
            logger.info("Second line also has KEYWORD here")
            logger.complete()

            results = logger.search_log(sink_id, "KEYWORD")

            assert results is not None
            assert len(results) == 2

    def test_search_after_rotation(self):
        """Test that search works on current file after rotation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("Before rotation")
            logger.complete()

            # Manually rotate (simplified test)
            logger.remove(sink_id)
            sink_id = logger.add(str(log_file))

            logger.info("After rotation with TARGET")
            logger.complete()

            results = logger.search_log(sink_id, "TARGET")

            assert results is not None
            assert len(results) == 1
            assert "After rotation" in results[0]["content"]  # type: ignore


class TestResultStructure:
    """Test the structure of search results."""

    def test_result_has_required_fields(self):
        """Test that results contain all required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("Test message with KEYWORD")
            logger.complete()

            results = logger.search_log(sink_id, "KEYWORD")

            assert results is not None
            assert len(results) == 1

            result = results[0]
            assert "line" in result
            assert "content" in result
            assert "match" in result

            assert isinstance(result["line"], int)
            assert isinstance(result["content"], str)
            assert isinstance(result["match"], str)

    def test_line_numbers_are_correct(self):
        """Test that line numbers are 1-indexed and correct."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            for i in range(1, 11):
                logger.info(f"Line {i}")
            logger.complete()

            results = logger.search_log(sink_id, "Line 5")

            assert results is not None
            assert len(results) == 1
            assert results[0]["line"] == 5  # 1-indexed, not 0-indexed

    def test_match_field_contains_actual_match(self):
        """Test that 'match' field contains the found string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("Error: System failure")
            logger.complete()

            # Case-insensitive search
            results = logger.search_log(sink_id, "error")

            assert results is not None
            assert len(results) == 1
            # Match field should contain the actual string from file (Error, not error)
            assert results[0]["match"] in results[0]["content"]  # type: ignore


class TestPerformance:
    """Test search performance with larger files."""

    def test_search_large_file(self):
        """Test searching in a file with many lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "large.log"
            sink_id = logger.add(str(log_file))

            # Write 1000 lines
            for i in range(1000):
                if i == 500:
                    logger.info(f"Line {i}: TARGET found here")
                else:
                    logger.info(f"Line {i}: normal log message")
            logger.complete()

            results = logger.search_log(sink_id, "TARGET", first_only=True)

            assert results is not None
            assert len(results) == 1
            assert results[0]["line"] == 501  # 0-indexed iteration, 1-indexed result

    def test_first_only_is_faster(self):
        """Test that first_only stops searching after first match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.info("First MATCH")
            for i in range(100):
                logger.info(f"Line {i}: filler")
            logger.info("Second MATCH")
            logger.complete()

            # first_only should stop at line 1, not read all 102 lines
            results = logger.search_log(sink_id, "MATCH", first_only=True)

            assert results is not None
            assert len(results) == 1
            assert results[0]["line"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
