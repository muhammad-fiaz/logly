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

    def test_truncated_gzip_is_detected(self, tmp_path: Path) -> None:
        """A truncated gzip archive must fail decompression, not read clean."""
        import gzip

        import pytest

        log_file = tmp_path / "app.log"
        sink_id = logger.add(str(log_file), rotation="20 B", compression="gzip", level="DEBUG")
        for _ in range(20):
            logger.info("truncate me gzip")
        logger.remove(sink_id)
        gz_files = list(tmp_path.glob("*.gz"))
        assert len(gz_files) >= 1
        raw = gz_files[0].read_bytes()
        with pytest.raises((EOFError, OSError)):
            gzip.decompress(raw[: len(raw) // 2])

    def test_truncated_bz2_is_detected(self, tmp_path: Path) -> None:
        """A truncated bz2 archive must fail decompression."""
        import bz2

        import pytest

        log_file = tmp_path / "app.log"
        sink_id = logger.add(str(log_file), rotation="20 B", compression="bz2", level="DEBUG")
        for _ in range(20):
            logger.info("truncate me bz2")
        logger.remove(sink_id)
        bz2_files = list(tmp_path.glob("*.bz2"))
        assert len(bz2_files) >= 1
        raw = bz2_files[0].read_bytes()
        with pytest.raises((ValueError, OSError, EOFError)):
            bz2.decompress(raw[: len(raw) // 2])

    def test_truncated_xz_is_detected(self, tmp_path: Path) -> None:
        """A truncated xz archive must fail decompression."""
        import lzma

        import pytest

        log_file = tmp_path / "app.log"
        sink_id = logger.add(str(log_file), rotation="20 B", compression="xz", level="DEBUG")
        for _ in range(20):
            logger.info("truncate me xz")
        logger.remove(sink_id)
        xz_files = list(tmp_path.glob("*.xz"))
        assert len(xz_files) >= 1
        raw = xz_files[0].read_bytes()
        with pytest.raises((lzma.LZMAError, EOFError, OSError)):
            lzma.decompress(raw[: len(raw) // 2])

    def test_truncated_zip_is_detected(self, tmp_path: Path) -> None:
        """A truncated zip archive must fail to open/read."""
        import zipfile

        import pytest

        log_file = tmp_path / "app.log"
        sink_id = logger.add(str(log_file), rotation="20 B", compression="zip", level="DEBUG")
        for _ in range(20):
            logger.info("truncate me zip")
        logger.remove(sink_id)
        zip_files = list(tmp_path.glob("*.zip"))
        assert len(zip_files) >= 1
        raw = zip_files[0].read_bytes()
        truncated = tmp_path / "truncated.zip"
        truncated.write_bytes(raw[: len(raw) // 2])
        with pytest.raises((zipfile.BadZipFile, EOFError)):
            with zipfile.ZipFile(truncated) as archive:
                archive.read(archive.namelist()[0])

    def test_large_stream_gzip_roundtrip(self, tmp_path: Path) -> None:
        """~1 MB across many rotations must round-trip without loss."""
        import gzip

        log_file = tmp_path / "big.log"
        sink_id = logger.add(
            str(log_file),
            rotation="50 KB",
            compression="gzip",
            level="DEBUG",
            format="{message}",
        )
        marker = "large-stream-marker-42"
        for i in range(400):
            logger.info(f"{marker} {i:04d} " + "x" * 200)
        logger.remove(sink_id)
        archives = sorted(tmp_path.glob("*.gz"))
        assert len(archives) >= 1
        combined = b"".join(gzip.decompress(p.read_bytes()) for p in archives)
        combined += log_file.read_bytes()
        assert combined.count(marker.encode()) >= 400

    def test_unicode_path_gzip_roundtrip(self, tmp_path: Path) -> None:
        """Unicode directories must survive rotation plus compression."""
        import gzip

        nested = tmp_path / "lög dir 🚀" / "nested"
        nested.mkdir(parents=True)
        log_file = nested / "app.log"
        sink_id = logger.add(str(log_file), rotation="20 B", compression="gzip", level="DEBUG")
        for _ in range(20):
            logger.info("unicode path payload")
        logger.remove(sink_id)
        gz_files = list(nested.glob("*.gz"))
        assert len(gz_files) >= 1
        payload = gzip.decompress(gz_files[0].read_bytes()).decode("utf-8")
        assert "unicode path payload" in payload

    def test_enqueue_gzip_roundtrip(self, tmp_path: Path) -> None:
        """Enqueue mode must finalize compressed archives on complete()."""
        import gzip

        log_file = tmp_path / "async.log"
        sink_id = logger.add(
            str(log_file),
            rotation="20 B",
            compression="gzip",
            level="DEBUG",
            enqueue=True,
        )
        for _ in range(20):
            logger.info("enqueue compressed payload")
        logger.complete()
        logger.remove(sink_id)
        gz_files = list(tmp_path.glob("*.gz"))
        assert len(gz_files) >= 1
        payload = gzip.decompress(gz_files[0].read_bytes()).decode("utf-8")
        assert "enqueue compressed payload" in payload

    def test_retention_applies_to_compressed_archives(self, tmp_path: Path) -> None:
        """Count retention must bound archives while keeping the active log."""
        log_file = tmp_path / "app.log"
        sink_id = logger.add(
            str(log_file),
            rotation="20 B",
            retention=2,
            compression="gzip",
            level="DEBUG",
        )
        for _ in range(60):
            logger.info("retention compressed payload")
        logger.remove(sink_id)
        assert log_file.exists()
        assert len(list(tmp_path.glob("*.gz"))) <= 2
