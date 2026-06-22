"""Tests for retention policies."""

from __future__ import annotations

from pathlib import Path

from logly import logger


class TestRetention:
    """Tests for rotated file retention."""

    def test_count_retention(self, tmp_path: Path) -> None:
        """Should retain only N rotated files."""
        log_file = tmp_path / "app.log"
        sink_id = logger.add(
            str(log_file),
            rotation="20 B",
            retention=2,
            level="DEBUG",
        )
        for _ in range(20):
            logger.info("retention test message")
        logger.remove(sink_id)
        rotated = list(tmp_path.glob("app.log.*"))
        assert len(rotated) <= 3  # 2 retained + possibly 1 current

    def test_age_retention(self, tmp_path: Path) -> None:
        """Should accept age-based retention."""
        log_file = tmp_path / "app.log"
        sink_id = logger.add(
            str(log_file),
            rotation="20 B",
            retention="1 days",
            level="DEBUG",
        )
        logger.info("age retention test")
        logger.remove(sink_id)
        assert log_file.exists()

    def test_retention_string_parse(self, tmp_path: Path) -> None:
        """Should parse retention strings like '5 days'."""
        log_file = tmp_path / "app.log"
        sink_id = logger.add(
            str(log_file),
            retention="5 days",
        )
        logger.info("parsed retention")
        logger.remove(sink_id)
        assert log_file.exists()
