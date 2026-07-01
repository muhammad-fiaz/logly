"""Tests for Rich integration."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from logly.integrations.rich import LoglyRichSink, RichHandler, RichSink


class TestLoglyRichSinkInit:
    def test_init_import_guard(self) -> None:
        saved_console = sys.modules.get("rich.console")
        saved_text = sys.modules.get("rich.text")
        sys.modules["rich.console"] = None  # type: ignore[assignment]
        sys.modules["rich.text"] = None  # type: ignore[assignment]
        try:
            with pytest.raises(ImportError, match="rich"):
                LoglyRichSink()
        finally:
            if saved_console is not None:
                sys.modules["rich.console"] = saved_console
            else:
                sys.modules.pop("rich.console", None)
            if saved_text is not None:
                sys.modules["rich.text"] = saved_text
            else:
                sys.modules.pop("rich.text", None)

    def test_init_default(self) -> None:
        mock_console = MagicMock()
        mock_text = MagicMock()
        with patch.dict(
            sys.modules,
            {
                "rich.console": MagicMock(Console=lambda **kw: mock_console),
                "rich.text": MagicMock(Text=lambda *a, **kw: mock_text),
            },
        ):
            sink = LoglyRichSink()
            assert sink is not None

    def test_init_with_file(self) -> None:
        mock_file = MagicMock()
        mock_console = MagicMock()
        mock_text = MagicMock()
        with patch.dict(
            sys.modules,
            {
                "rich.console": MagicMock(Console=lambda **kw: mock_console),
                "rich.text": MagicMock(Text=lambda *a, **kw: mock_text),
            },
        ):
            sink = LoglyRichSink(file=mock_file)
            assert sink is not None


class TestLoglyRichSinkWrite:
    def test_write_strips_newline(self) -> None:
        mock_console = MagicMock()
        mock_text_cls = MagicMock()
        mock_text_instance = MagicMock()
        mock_text_cls.return_value = mock_text_instance

        sink = object.__new__(LoglyRichSink)
        sink._console = mock_console
        sink._text_class = mock_text_cls

        sink.write("hello rich\n")
        mock_console.print.assert_called_once()

    def test_write_empty_message(self) -> None:
        mock_console = MagicMock()
        sink = object.__new__(LoglyRichSink)
        sink._console = mock_console
        sink.write("")
        mock_console.print.assert_not_called()

    def test_write_plain_fallback(self) -> None:
        mock_console = MagicMock()
        mock_console.print.side_effect = None
        mock_text_cls = MagicMock()
        mock_text_cls.side_effect = Exception("text error")

        sink = object.__new__(LoglyRichSink)
        sink._console = mock_console
        sink._text_class = mock_text_cls

        sink.write("plain msg\n")
        assert mock_console.print.call_count == 1
        mock_console.print.assert_called_with("plain msg", end="", highlight=False)


class TestLoglyRichSinkFlush:
    def test_flush(self) -> None:
        mock_console = MagicMock()
        mock_console.file = MagicMock()
        sink = object.__new__(LoglyRichSink)
        sink._console = mock_console
        sink.flush()
        mock_console.file.flush.assert_called_once()


class TestRichSinkAlias:
    def test_rich_sink_is_alias(self) -> None:
        assert RichSink is LoglyRichSink


class TestRichHandler:
    def test_init_import_guard(self) -> None:
        saved = sys.modules.get("rich.logging")
        sys.modules["rich.logging"] = None  # type: ignore[assignment]
        try:
            with pytest.raises(ImportError, match="rich"):
                RichHandler()
        finally:
            if saved is not None:
                sys.modules["rich.logging"] = saved
            else:
                sys.modules.pop("rich.logging", None)

    def test_emit_delegates(self) -> None:
        mock_handler = MagicMock()
        mock_logging = MagicMock()
        mock_logging.RichHandler.return_value = mock_handler
        with patch.dict(sys.modules, {"rich.logging": mock_logging}):
            handler = RichHandler()
            record = MagicMock()
            handler.emit(record)

    def test_flush(self) -> None:
        mock_handler = MagicMock()
        mock_logging = MagicMock()
        mock_logging.RichHandler.return_value = mock_handler
        with patch.dict(sys.modules, {"rich.logging": mock_logging}):
            handler = RichHandler()
            handler.flush()
