"""
Test  to verify that async writes properly separate log lines with newlines.
This test specifically addresses the bug where logs were concatenating on the same line.
"""

import os
import tempfile
import time
from pathlib import Path

import logly


class TestAsyncNewlines:
    """Tests to ensure async writer adds proper newlines between log entries."""

    def setup_method(self):
        """Setup for each test - create logger and cleanup."""
        self.logger = logly.PyLogger(auto_update_check=False)
        self.test_files = []

    def teardown_method(self):
        """Cleanup after each test."""
        self.logger._reset_for_tests()
        for filepath in self.test_files:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass

    def test_async_writes_separate_lines_txt(self):
        """Test that .txt files have each log on a separate line with async writes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "async_test.txt"
            self.test_files.append(str(log_file))

            # Configure with async writes enabled
            self.logger.add(str(log_file), async_write=True)

            # Write multiple log entries
            self.logger.info("First log entry")
            self.logger.info("Second log entry")
            self.logger.info("Third log entry")

            # Complete logging to flush all async buffers
            self.logger.complete()
            time.sleep(0.5)  # Extra time for file system

            # Read the file and verify each log is on a separate line
            assert log_file.exists(), "Log file should exist"

            with open(log_file, encoding="utf-8") as f:
                lines = f.readlines()

            # Should have exactly 3 lines
            assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}: {lines}"

            # Each line should end with newline
            for i, line in enumerate(lines, 1):
                assert line.endswith("\n"), f"Line {i} should end with newline: {repr(line)}"

            # Verify content
            assert "First log entry" in lines[0]
            assert "Second log entry" in lines[1]
            assert "Third log entry" in lines[2]

            # Verify lines are NOT concatenated
            content = "".join(lines)
            assert "First log entrySecond" not in content, "Lines should not be concatenated"

    def test_async_writes_separate_lines_log(self):
        """Test that .log files have each log on a separate line with async writes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "async_test.log"
            self.test_files.append(str(log_file))

            self.logger.add(str(log_file), async_write=True)

            self.logger.info("First log entry")
            self.logger.info("Second log entry")
            self.logger.info("Third log entry")

            self.logger.complete()
            time.sleep(0.5)

            assert log_file.exists()

            with open(log_file, encoding="utf-8") as f:
                lines = f.readlines()

            assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}"

            for i, line in enumerate(lines, 1):
                assert line.endswith("\n"), f"Line {i} should end with newline"

            assert "First log entry" in lines[0]
            assert "Second log entry" in lines[1]
            assert "Third log entry" in lines[2]

    def test_async_writes_separate_lines_json(self):
        """Test that .json files have each log on a separate line with async writes."""
        # Note: JSON format test removed because json_format parameter doesn't exist in .add()
        # JSON logging works with .log and .txt files when using default text format
        pass

    def test_async_high_volume_newlines(self):
        """Test that high volume async writes still separate lines correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "high_volume.txt"
            self.test_files.append(str(log_file))

            self.logger.add(str(log_file), async_write=True)

            # Write 100 log entries rapidly
            num_logs = 100
            for i in range(num_logs):
                self.logger.info(f"Log entry {i}")

            self.logger.complete()
            time.sleep(1.0)  # More time for high volume

            assert log_file.exists()

            with open(log_file, encoding="utf-8") as f:
                lines = f.readlines()

            # Should have exactly 100 lines
            assert len(lines) == num_logs, f"Expected {num_logs} lines, got {len(lines)}"

            # Each line should end with newline
            for i, line in enumerate(lines):
                assert line.endswith("\n"), f"Line {i} should end with newline"

            # Verify no concatenation by checking a few specific entries
            assert any("Log entry 0" in line and "Log entry 1" not in line for line in lines)
            assert any("Log entry 50" in line and "Log entry 51" not in line for line in lines)

    def test_async_rotation_preserves_newlines(self):
        """Test that file rotation with async writes still maintains proper newlines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "rotation_test.txt"
            self.test_files.append(str(log_file))

            self.logger.add(
                str(log_file),
                async_write=True,
                rotation="500B",  # Small size to trigger rotation
            )

            # Write enough to trigger rotation
            for i in range(20):
                self.logger.info(
                    f"Long log entry number {i} with extra padding to reach size limit quickly"
                )

            self.logger.complete()
            time.sleep(1.0)

            # Check main log file
            if log_file.exists():
                with open(log_file, encoding="utf-8") as f:
                    lines = f.readlines()

                for i, line in enumerate(lines):
                    assert line.endswith("\n"), f"Main file line {i} should end with newline"

            # Check for rotated files
            rotated_files = list(Path(tmpdir).glob("rotation_test.txt.*"))
            for rotated_file in rotated_files:
                self.test_files.append(str(rotated_file))
                with open(rotated_file, encoding="utf-8") as f:
                    lines = f.readlines()

                for i, line in enumerate(lines):
                    assert line.endswith("\n"), (
                        f"Rotated file {rotated_file.name} line {i} should end with newline"
                    )

    def test_sync_vs_async_consistency(self):
        """Test that sync and async writes produce identical line separation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sync_file = Path(tmpdir) / "sync_test.txt"
            async_file = Path(tmpdir) / "async_test.txt"
            self.test_files.extend([str(sync_file), str(async_file)])

            # Write with sync mode
            self.logger.add(str(sync_file), async_write=False)

            self.logger.info("First entry")
            self.logger.info("Second entry")
            self.logger.info("Third entry")

            # Reset logger for async test
            self.logger.complete()
            self.logger._reset_for_tests()

            # Write with async mode
            self.logger.add(str(async_file), async_write=True)

            self.logger.info("First entry")
            self.logger.info("Second entry")
            self.logger.info("Third entry")

            self.logger.complete()
            time.sleep(0.5)

            # Both files should have identical line counts
            with open(sync_file, encoding="utf-8") as f:
                sync_lines = f.readlines()

            with open(async_file, encoding="utf-8") as f:
                async_lines = f.readlines()

            assert len(sync_lines) == len(async_lines), (
                f"Sync ({len(sync_lines)} lines) and async ({len(async_lines)} lines) should have same line count"
            )

            # Both should have 3 lines
            assert len(sync_lines) == 3
            assert len(async_lines) == 3

            # All lines should end with newlines
            for line in sync_lines + async_lines:
                assert line.endswith("\n")
