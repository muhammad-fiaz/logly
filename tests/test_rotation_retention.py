"""Tests for rotation, retention, and compression policy parsing via Rust."""

from __future__ import annotations

import pytest

from logly._logly import parse_compression_str, parse_retention_str, parse_rotation_str


class TestRotationParsing:
    def test_weekly(self) -> None:
        result = parse_rotation_str("weekly")
        assert result == "interval:604800"

    def test_monthly(self) -> None:
        result = parse_rotation_str("monthly")
        assert result == "interval:2592000"

    def test_yearly(self) -> None:
        result = parse_rotation_str("yearly")
        assert result == "interval:31536000"

    def test_minutely(self) -> None:
        result = parse_rotation_str("minutely")
        assert result == "interval:60"

    def test_daily(self) -> None:
        result = parse_rotation_str("daily")
        assert result == "interval:86400"

    def test_hourly(self) -> None:
        result = parse_rotation_str("hourly")
        assert result == "interval:3600"

    def test_clock_rotation(self) -> None:
        result = parse_rotation_str("00:00")
        assert result == "clock:00:00"

    def test_weekday_rotation(self) -> None:
        result = parse_rotation_str("Monday")
        assert result == "weekday:0"

    def test_weekday_case_insensitive(self) -> None:
        result = parse_rotation_str("friday")
        assert result == "weekday:4"

    def test_size_rotation_bytes(self) -> None:
        result = parse_rotation_str("10000000")
        assert result == "size:10000000"

    def test_never(self) -> None:
        result = parse_rotation_str("never")
        assert result == "never"

    def test_none(self) -> None:
        result = parse_rotation_str("none")
        assert result == "never"

    def test_empty_returns_never(self) -> None:
        result = parse_rotation_str("")
        assert result == "never"

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_rotation_str("not_a_valid_spec!!")


class TestRetentionParsing:
    def test_weeks(self) -> None:
        result = parse_retention_str("4 weeks")
        assert result == "None:2419200"

    def test_months(self) -> None:
        result = parse_retention_str("6 months")
        assert result == "None:15552000"

    def test_days(self) -> None:
        result = parse_retention_str("30 days")
        assert result == "None:2592000"

    def test_hours(self) -> None:
        result = parse_retention_str("12 hours")
        assert result == "None:43200"

    def test_count(self) -> None:
        result = parse_retention_str("10")
        assert result == "10:None"

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_retention_str("invalid garbage")


class TestCompressionParsing:
    def test_gzip(self) -> None:
        result = parse_compression_str("gzip")
        assert result == "gzip"

    def test_gz_alias(self) -> None:
        result = parse_compression_str("gz")
        assert result == "gzip"

    def test_tar_alias(self) -> None:
        result = parse_compression_str("tar")
        assert result == "gzip"

    def test_tar_gz_alias(self) -> None:
        result = parse_compression_str("tar.gz")
        assert result == "gzip"

    def test_tgz_alias(self) -> None:
        result = parse_compression_str("tgz")
        assert result == "gzip"

    def test_tar_bz2_alias(self) -> None:
        result = parse_compression_str("tar.bz2")
        assert result == "bz2"

    def test_tar_xz_alias(self) -> None:
        result = parse_compression_str("tar.xz")
        assert result == "xz"

    def test_bz2(self) -> None:
        result = parse_compression_str("bz2")
        assert result == "bz2"

    def test_xz(self) -> None:
        result = parse_compression_str("xz")
        assert result == "xz"

    def test_zip(self) -> None:
        result = parse_compression_str("zip")
        assert result == "zip"

    def test_zstd(self) -> None:
        result = parse_compression_str("zstd")
        assert result == "zstd"

    def test_none(self) -> None:
        result = parse_compression_str("none")
        assert result == "none"

    def test_case_insensitive(self) -> None:
        result = parse_compression_str("GZIP")
        assert result == "gzip"

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_compression_str("bogus")
