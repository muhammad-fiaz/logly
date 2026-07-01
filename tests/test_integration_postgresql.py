from __future__ import annotations

import sys
import time
from unittest.mock import MagicMock, patch

import pytest

from logly.integrations.postgresql import _IDENTIFIER_RE, PostgresHandler


class TestPostgresHandlerInit:
    def test_init_import_guard(self) -> None:
        with patch("importlib.util.find_spec", return_value=None):
            with pytest.raises(ImportError, match="psycopg2 is required"):
                PostgresHandler("postgresql://localhost:5432/test")

    def test_init_invalid_table_name(self) -> None:
        mock_psycopg2 = MagicMock()
        mock_conn = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"psycopg2": mock_psycopg2}):
                with pytest.raises(ValueError, match="Invalid table name"):
                    PostgresHandler(table="DROP TABLE users; --")

    def test_init_valid_table_name(self) -> None:
        mock_psycopg2 = MagicMock()
        mock_conn = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"psycopg2": mock_psycopg2}):
                handler = PostgresHandler(table="app_logs")
                assert handler._table == "app_logs"

    def test_init_creates_table_by_default(self) -> None:
        mock_psycopg2 = MagicMock()
        mock_conn = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"psycopg2": mock_psycopg2}):
                PostgresHandler(create_table=True)
                mock_conn.cursor.assert_called()

    def test_init_skip_table_creation(self) -> None:
        mock_psycopg2 = MagicMock()
        mock_conn = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"psycopg2": mock_psycopg2}):
                PostgresHandler(create_table=False)
                mock_conn.cursor.assert_not_called()


class TestIdentifierRegex:
    def test_valid_identifiers(self) -> None:
        assert _IDENTIFIER_RE.match("app_logs") is not None
        assert _IDENTIFIER_RE.match("logs123") is not None
        assert _IDENTIFIER_RE.match("_private") is not None
        assert _IDENTIFIER_RE.match("MyTable") is not None

    def test_invalid_identifiers(self) -> None:
        assert _IDENTIFIER_RE.match("123table") is None
        assert _IDENTIFIER_RE.match("my-table") is None
        assert _IDENTIFIER_RE.match("my table") is None
        assert _IDENTIFIER_RE.match("DROP TABLE") is None
        assert _IDENTIFIER_RE.match("") is None


class TestPostgresHandlerWrite:
    def _make_handler(self) -> PostgresHandler:
        mock_psycopg2 = MagicMock()
        mock_conn = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"psycopg2": mock_psycopg2}):
                handler = PostgresHandler(create_table=False)
                handler._conn = mock_conn
        return handler

    def test_write_inserts_row(self) -> None:
        handler = self._make_handler()
        handler.write("hello pg\n")
        handler._conn.cursor.assert_called()
        handler._conn.commit.assert_called()

    def test_write_strips_newline(self) -> None:
        handler = self._make_handler()
        handler.write("msg\n")
        mock_cursor = handler._conn.cursor.return_value.__enter__.return_value
        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][0] == "msg"

    def test_write_empty_message(self) -> None:
        handler = self._make_handler()
        handler.write("\n")
        mock_cursor = handler._conn.cursor.return_value.__enter__.return_value
        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][0] == ""

    def test_write_includes_timestamp(self) -> None:
        handler = self._make_handler()
        before = time.time()
        handler.write("ts test\n")
        after = time.time()
        mock_cursor = handler._conn.cursor.return_value.__enter__.return_value
        call_args = mock_cursor.execute.call_args
        ts = call_args[0][1][1]
        assert before <= ts <= after


class TestPostgresHandlerFlush:
    def test_flush_commits(self) -> None:
        mock_psycopg2 = MagicMock()
        mock_conn = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"psycopg2": mock_psycopg2}):
                handler = PostgresHandler(create_table=False)
                handler.flush()
                mock_conn.commit.assert_called_once()


class TestPostgresHandlerClose:
    def test_close_closes_connection(self) -> None:
        mock_psycopg2 = MagicMock()
        mock_conn = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"psycopg2": mock_psycopg2}):
                handler = PostgresHandler(create_table=False)
                handler.close()
                mock_conn.close.assert_called_once()
