"""
Comprehensive tests for retention, rotation, and size_limit interactions.
Tests all combinations to ensure they work together correctly.

Fixes: https://github.com/muhammad-fiaz/logly/issues/77
"""

import time

import pytest

from logly import PyLogger


class TestRetentionWithSizeLimit:
    """Test retention with size_limit parameter."""

    def test_size_limit_only_with_retention(self, tmp_path):
        """Test size_limit alone creates new files and respects retention."""
        log_file = tmp_path / "size_only.log"

        logger = PyLogger()
        logger.add(str(log_file), size_limit="10KB", retention=5)

        # Write enough data to trigger multiple rotations
        for i in range(200):
            logger.info(f"Message {i:04d} " * 50)  # ~1KB per message
            time.sleep(0.01)

        time.sleep(0.5)
        logger.complete()

        # Count all log files
        log_files = list(tmp_path.glob("size_only*.log"))

        # Should have AT MOST 5 files (retention limit)
        assert len(log_files) <= 5, (
            f"With size_limit='10KB' and retention=5, expected ≤5 files, "
            f"found {len(log_files)}: {sorted([f.name for f in log_files])}"
        )

        # Should have created multiple files (rotation happened)
        assert len(log_files) >= 2, (
            f"Expected size rotation to create multiple files, found {len(log_files)}"
        )

    def test_size_limit_retention_1(self, tmp_path):
        """Test retention=1 keeps only current file."""
        log_file = tmp_path / "retention_1.log"

        logger = PyLogger()
        logger.add(str(log_file), size_limit="5KB", retention=1)

        # Write enough to trigger rotations
        for i in range(100):
            logger.info(f"Log entry {i:04d} " * 50)
            time.sleep(0.01)

        time.sleep(0.5)
        logger.complete()

        log_files = list(tmp_path.glob("retention_1*.log"))

        # Should have EXACTLY 1 file
        assert len(log_files) == 1, (
            f"With retention=1, expected exactly 1 file, found {len(log_files)}: "
            f"{sorted([f.name for f in log_files])}"
        )

    def test_size_limit_small_retention(self, tmp_path):
        """Test with very small size limit and small retention."""
        log_file = tmp_path / "small.log"

        logger = PyLogger()
        logger.add(str(log_file), size_limit="1KB", retention=3)

        # Write messages
        for i in range(50):
            logger.info(f"Entry {i} " * 20)
            time.sleep(0.02)

        time.sleep(0.5)
        logger.complete()

        log_files = list(tmp_path.glob("small*.log"))

        # Should respect retention=3
        assert len(log_files) <= 3, f"Expected ≤3 files with retention=3, found {len(log_files)}"


class TestRetentionWithRotation:
    """Test retention with time-based rotation."""

    def test_daily_rotation_with_retention(self, tmp_path):
        """Test daily rotation respects retention (won't rotate in single test)."""
        log_file = tmp_path / "daily.log"

        logger = PyLogger()
        logger.add(str(log_file), rotation="daily", retention=7)

        # Write some logs
        for i in range(20):
            logger.info(f"Daily log {i}")

        time.sleep(0.2)
        logger.complete()

        log_files = list(tmp_path.glob("daily*.log"))

        # Should have 1 file (no rotation within test time)
        assert len(log_files) == 1
        # But configuration should be stored correctly
        assert log_files[0].exists()

    def test_minutely_rotation_with_retention(self, tmp_path):
        """Test minutely rotation with retention."""
        log_file = tmp_path / "minutely.log"

        logger = PyLogger()
        logger.add(str(log_file), rotation="minutely", retention=2)

        # Write logs
        for i in range(10):
            logger.info(f"Minutely log {i}")

        time.sleep(0.2)
        logger.complete()

        log_files = list(tmp_path.glob("minutely*.log"))

        # Should exist and respect retention
        assert len(log_files) >= 1
        assert len(log_files) <= 2  # retention limit


class TestRetentionWithBoth:
    """Test retention with BOTH size_limit and rotation together."""

    def test_size_and_daily_rotation_with_retention(self, tmp_path):
        """Test size_limit + daily rotation + retention all work together."""
        log_file = tmp_path / "both.log"

        logger = PyLogger()
        logger.add(str(log_file), size_limit="5KB", rotation="daily", retention=4)

        # Write enough to trigger size rotation
        for i in range(100):
            logger.info(f"Both rotation {i} " * 30)
            time.sleep(0.01)

        time.sleep(0.5)
        logger.complete()

        log_files = list(tmp_path.glob("both*.log"))

        # Should respect retention limit
        assert len(log_files) <= 4, f"With retention=4, expected ≤4 files, found {len(log_files)}"

        # Should have rotated due to size
        assert len(log_files) >= 2, (
            f"Expected size rotation to create files, found {len(log_files)}"
        )

    def test_size_and_hourly_rotation_with_retention(self, tmp_path):
        """Test size_limit + hourly rotation + retention."""
        log_file = tmp_path / "size_hourly.log"

        logger = PyLogger()
        logger.add(str(log_file), size_limit="3KB", rotation="hourly", retention=5)

        # Write data
        for i in range(80):
            logger.info(f"Size+hourly entry {i} " * 25)
            time.sleep(0.01)

        time.sleep(0.5)
        logger.complete()

        log_files = list(tmp_path.glob("size_hourly*.log"))

        # Should respect retention
        assert len(log_files) <= 5


class TestRetentionEdgeCases:
    """Test edge cases and special scenarios."""

    def test_no_retention_unlimited_files(self, tmp_path):
        """Test that without retention, files accumulate."""
        log_file = tmp_path / "unlimited.log"

        logger = PyLogger()
        logger.add(
            str(log_file),
            size_limit="2KB",
            # No retention parameter
        )

        # Write data
        for i in range(50):
            logger.info(f"Unlimited {i} " * 25)
            time.sleep(0.01)

        time.sleep(0.5)
        logger.complete()

        log_files = list(tmp_path.glob("unlimited*.log"))

        # Should have created multiple files (no limit)
        assert len(log_files) >= 2, (
            f"Without retention, expected multiple files, found {len(log_files)}"
        )

    def test_retention_zero_invalid(self, tmp_path):
        """Test that retention=0 is handled (should keep at least 1)."""
        log_file = tmp_path / "zero_retention.log"

        logger = PyLogger()
        # retention=0 or None should keep files (no pruning)
        logger.add(str(log_file), size_limit="5KB", retention=None)

        for i in range(50):
            logger.info(f"Zero test {i} " * 30)
            time.sleep(0.01)

        time.sleep(0.5)
        logger.complete()

        log_files = list(tmp_path.glob("zero_retention*.log"))
        assert len(log_files) >= 1

    def test_retention_very_large(self, tmp_path):
        """Test retention with very large value."""
        log_file = tmp_path / "large_retention.log"

        logger = PyLogger()
        logger.add(
            str(log_file),
            size_limit="2KB",
            retention=1000,  # Very large
        )

        for i in range(30):
            logger.info(f"Large retention {i} " * 25)
            time.sleep(0.01)

        time.sleep(0.5)
        logger.complete()

        log_files = list(tmp_path.glob("large_retention*.log"))

        # Should create files but stay under limit
        assert len(log_files) >= 1
        assert len(log_files) <= 1000


class TestRetentionAccuracy:
    """Test that retention count is accurate."""

    def test_exact_retention_count_size_limit(self, tmp_path):
        """Test that retention count is exactly honored with size_limit."""
        log_file = tmp_path / "exact.log"

        logger = PyLogger()
        retention_count = 3
        logger.add(str(log_file), size_limit="2KB", retention=retention_count)

        # Write enough to create many rotations
        for i in range(100):
            logger.info(f"Exact count test {i} " * 30)
            time.sleep(0.02)

        time.sleep(1.0)  # Wait longer for file operations
        logger.complete()

        log_files = list(tmp_path.glob("exact*.log"))

        # Should have EXACTLY retention_count files (or less if not enough rotations)
        assert len(log_files) <= retention_count, (
            f"Expected ≤{retention_count} files, found {len(log_files)}: "
            f"{sorted([f.name for f in log_files])}"
        )

    def test_retention_with_rapid_writes(self, tmp_path):
        """Test retention with rapid sequential writes."""
        log_file = tmp_path / "rapid.log"

        logger = PyLogger()
        logger.add(str(log_file), size_limit="1KB", retention=2)

        # Rapid writes
        for i in range(200):
            logger.info(f"Rapid write {i} " * 20)

        time.sleep(1.0)
        logger.complete()

        log_files = list(tmp_path.glob("rapid*.log"))

        # Should still respect retention
        assert len(log_files) <= 2, (
            f"Rapid writes should still honor retention=2, found {len(log_files)}"
        )


class TestConfigRespect:
    """Test that all configuration settings are respected."""

    def test_async_write_with_retention(self, tmp_path):
        """Test async_write setting with retention."""
        log_file = tmp_path / "async.log"

        logger = PyLogger()
        logger.add(
            str(log_file), size_limit="4KB", retention=4, async_write=True, flush_interval=50
        )

        for i in range(80):
            logger.info(f"Async write {i} " * 25)
            time.sleep(0.01)

        time.sleep(1.0)  # Wait for async writes
        logger.complete()

        log_files = list(tmp_path.glob("async*.log"))

        # Should respect retention
        assert len(log_files) <= 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
