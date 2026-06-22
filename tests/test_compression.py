"""Tests for compression of rotated files."""

from __future__ import annotations

from pathlib import Path

from logly import logger


class TestCompression:
    """Tests for file compression policies."""

    def test_gzip_compression(self, tmp_path: Path) -> None:
        """Should compress rotated files with gzip."""
        log_file = tmp_path / "app.log"
        sink_id = logger.add(
            str(log_file),
            rotation="20 B",
            compression="gzip",
            level="DEBUG",
        )
        for _ in range(20):
            logger.info("compress this message")
        logger.remove(sink_id)
        gz_files = list(tmp_path.glob("*.gz"))
        assert len(gz_files) >= 1

    def test_zip_compression(self, tmp_path: Path) -> None:
        """Should compress rotated files with zip."""
        log_file = tmp_path / "app.log"
        sink_id = logger.add(
            str(log_file),
            rotation="20 B",
            compression="zip",
            level="DEBUG",
        )
        for _ in range(20):
            logger.info("zip compress this")
        logger.remove(sink_id)
        zip_files = list(tmp_path.glob("*.zip"))
        assert len(zip_files) >= 1

    def test_bz2_compression_not_supported(self, tmp_path: Path) -> None:
        """bz2 compression is not yet supported, should still create rotated files."""
        log_file = tmp_path / "app.log"
        sink_id = logger.add(
            str(log_file),
            rotation="20 B",
            compression="bz2",
            level="DEBUG",
        )
        for _ in range(20):
            logger.info("bz2 compress this")
        logger.remove(sink_id)
        # bz2 not supported - files are not compressed but rotation still works
        rotated_files = list(tmp_path.glob("app.log.*"))
        assert len(rotated_files) >= 1

    def test_xz_compression_not_supported(self, tmp_path: Path) -> None:
        """xz compression is not yet supported, should still create rotated files."""
        log_file = tmp_path / "app.log"
        sink_id = logger.add(
            str(log_file),
            rotation="20 B",
            compression="xz",
            level="DEBUG",
        )
        for _ in range(20):
            logger.info("xz compress this")
        logger.remove(sink_id)
        # xz not supported - files are not compressed but rotation still works
        rotated_files = list(tmp_path.glob("app.log.*"))
        assert len(rotated_files) >= 1

    def test_no_compression(self, tmp_path: Path) -> None:
        """No compression when codec=none."""
        log_file = tmp_path / "app.log"
        sink_id = logger.add(
            str(log_file),
            rotation="20 B",
            compression="none",
            level="DEBUG",
        )
        for _ in range(20):
            logger.info("no compression")
        logger.remove(sink_id)
        compressed = list(tmp_path.glob("*.gz")) + list(tmp_path.glob("*.zip"))
        assert len(compressed) == 0

    def test_invalid_compression_raises(self) -> None:
        """Invalid compression codec should raise ValueError."""
        import pytest

        with pytest.raises(ValueError):
            logger.add("test.log", compression="invalid_codec")
