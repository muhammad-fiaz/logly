"""Tests for log rotation."""

from __future__ import annotations

from pathlib import Path

from logly import logger


class TestRotation:
    """Tests for file rotation policies."""

    def test_size_rotation(self, tmp_path: Path) -> None:
        """File should rotate when size limit is exceeded."""
        log_file = tmp_path / "app.log"
        sink_id = logger.add(
            str(log_file),
            rotation="20 B",
            level="DEBUG",
        )
        logger.info("short")
        logger.info("another message to exceed size limit")
        logger.remove(sink_id)
        # Check that rotated files exist
        rotated = list(tmp_path.glob("app.log.*"))
        assert len(rotated) >= 1

    def test_rotation_disabled(self, tmp_path: Path) -> None:
        """No rotation when rotation=never."""
        log_file = tmp_path / "app.log"
        sink_id = logger.add(str(log_file), rotation="never")
        for _ in range(50):
            logger.info("no rotation message")
        logger.remove(sink_id)
        rotated = list(tmp_path.glob("app.log.*"))
        assert len(rotated) == 0

    def test_daily_rotation(self, tmp_path: Path) -> None:
        """Should accept daily rotation parameter."""
        log_file = tmp_path / "app.log"
        sink_id = logger.add(str(log_file), rotation="daily")
        logger.info("daily rotation test")
        logger.remove(sink_id)
        assert log_file.exists()

    def test_hourly_rotation(self, tmp_path: Path) -> None:
        """Should accept hourly rotation parameter."""
        log_file = tmp_path / "app.log"
        sink_id = logger.add(str(log_file), rotation="hourly")
        logger.info("hourly rotation test")
        logger.remove(sink_id)
        assert log_file.exists()
