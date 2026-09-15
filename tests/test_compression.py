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

    def test_bz2_compression(self, tmp_path: Path) -> None:
        """Should compress rotated files with bz2 (Rust-backed)."""
        import bz2

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
        bz2_files = list(tmp_path.glob("*.bz2"))
        assert len(bz2_files) >= 1
        payload = bz2.decompress(bz2_files[0].read_bytes()).decode("utf-8")
        assert "bz2 compress this" in payload

    def test_xz_compression(self, tmp_path: Path) -> None:
        """Should compress rotated files with xz (Rust-backed)."""
        import lzma

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
        xz_files = list(tmp_path.glob("*.xz"))
        assert len(xz_files) >= 1
        payload = lzma.decompress(xz_files[0].read_bytes()).decode("utf-8")
        assert "xz compress this" in payload

    def test_zstd_compression(self, tmp_path: Path) -> None:
        """Should compress rotated files with zstd (Rust-backed)."""
        log_file = tmp_path / "app.log"
        sink_id = logger.add(
            str(log_file),
            rotation="20 B",
            compression="zstd",
            level="DEBUG",
        )
        for _ in range(20):
            logger.info("zstd compress this")
        logger.remove(sink_id)
        zst_files = list(tmp_path.glob("*.zst"))
        assert len(zst_files) >= 1
        # zstd frame magic: 0xFD2FB528 little-endian (no py dep required)
        assert zst_files[0].read_bytes()[:4] == bytes((0x28, 0xB5, 0x2F, 0xFD))

    def test_gzip_unicode_roundtrip(self, tmp_path: Path) -> None:
        """Unicode content must survive gzip rotation."""
        import gzip

        log_file = tmp_path / "app.log"
        sink_id = logger.add(
            str(log_file),
            rotation="20 B",
            compression="gzip",
            level="DEBUG",
        )
        for _ in range(20):
            logger.info("unicode héllo wörld 🚀")
        logger.remove(sink_id)
        gz_files = list(tmp_path.glob("*.gz"))
        assert len(gz_files) >= 1
        payload = gzip.decompress(gz_files[0].read_bytes()).decode("utf-8")
        assert "héllo" in payload

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
