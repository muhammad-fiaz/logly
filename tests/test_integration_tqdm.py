from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from logly.integrations.tqdm import TqdmSink


class TestTqdmSinkInit:
    def test_init_with_tqdm_available(self) -> None:
        mock_tqdm = MagicMock()
        sink = TqdmSink(tqdm_instance=mock_tqdm)
        assert sink._tqdm is mock_tqdm

    def test_init_without_tqdm_instance_uses_real_tqdm(self) -> None:
        fake_tqdm = MagicMock()
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"tqdm": fake_tqdm}):
                sink = TqdmSink()
                assert sink._tqdm is not None

    def test_init_import_error_when_tqdm_missing(self) -> None:
        with patch("importlib.util.find_spec", return_value=None):
            with pytest.raises(ImportError, match="tqdm is required"):
                TqdmSink()

    def test_init_stores_custom_tqdm(self) -> None:
        custom = MagicMock()
        sink = TqdmSink(tqdm_instance=custom)
        assert sink._tqdm is custom


class TestTqdmSinkWrite:
    def test_write_calls_tqdm_write(self) -> None:
        mock_tqdm = MagicMock()
        sink = TqdmSink(tqdm_instance=mock_tqdm)
        sink.write("hello world\n")
        mock_tqdm.write.assert_called_once_with("hello world")

    def test_write_strips_trailing_newlines(self) -> None:
        mock_tqdm = MagicMock()
        sink = TqdmSink(tqdm_instance=mock_tqdm)
        sink.write("msg\n\n\n")
        mock_tqdm.write.assert_called_once_with("msg")

    def test_write_no_newline(self) -> None:
        mock_tqdm = MagicMock()
        sink = TqdmSink(tqdm_instance=mock_tqdm)
        sink.write("plain")
        mock_tqdm.write.assert_called_once_with("plain")


class TestTqdmSinkFlush:
    def test_flush_noop(self) -> None:
        mock_tqdm = MagicMock()
        sink = TqdmSink(tqdm_instance=mock_tqdm)
        sink.flush()
        mock_tqdm.flush.assert_not_called()


class TestTqdmSinkClose:
    def test_close_noop(self) -> None:
        mock_tqdm = MagicMock()
        sink = TqdmSink(tqdm_instance=mock_tqdm)
        sink.close()
        mock_tqdm.close.assert_not_called()
