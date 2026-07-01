from __future__ import annotations

import sys
import time
from unittest.mock import MagicMock, patch

import pytest

from logly.integrations.mongodb import MongoHandler


class TestMongoHandlerInit:
    def test_init_import_guard(self) -> None:
        with patch("importlib.util.find_spec", return_value=None):
            with pytest.raises(ImportError, match="pymongo is required"):
                MongoHandler("mongodb://localhost:27017")

    def test_init_creates_client(self) -> None:
        mock_pymongo = MagicMock()
        mock_client = MagicMock()
        mock_pymongo.MongoClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.__getitem__ = MagicMock(
            return_value=MagicMock(__getitem__=MagicMock(return_value=mock_collection))
        )
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"pymongo": mock_pymongo}):
                handler = MongoHandler(
                    "mongodb://localhost:27017", database="logs", collection="app"
                )
                assert handler._collection is mock_collection

    def test_init_default_params(self) -> None:
        mock_pymongo = MagicMock()
        mock_client = MagicMock()
        mock_pymongo.MongoClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.__getitem__ = MagicMock(
            return_value=MagicMock(__getitem__=MagicMock(return_value=mock_collection))
        )
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"pymongo": mock_pymongo}):
                MongoHandler()
                mock_pymongo.MongoClient.assert_called_once()


class TestMongoHandlerWrite:
    def _make_handler(self) -> MongoHandler:
        mock_pymongo = MagicMock()
        mock_client = MagicMock()
        mock_pymongo.MongoClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.__getitem__ = MagicMock(
            return_value=MagicMock(__getitem__=MagicMock(return_value=mock_collection))
        )
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"pymongo": mock_pymongo}):
                handler = MongoHandler()
                handler._collection = mock_collection
        return handler

    def test_write_inserts_document(self) -> None:
        handler = self._make_handler()
        handler.write("hello mongo\n")
        handler._collection.insert_one.assert_called_once()
        call_args = handler._collection.insert_one.call_args[0][0]
        assert call_args["message"] == "hello mongo"
        assert "timestamp" in call_args

    def test_write_strips_newline(self) -> None:
        handler = self._make_handler()
        handler.write("msg\n")
        call_args = handler._collection.insert_one.call_args[0][0]
        assert call_args["message"] == "msg"

    def test_write_empty_message(self) -> None:
        handler = self._make_handler()
        handler.write("\n")
        call_args = handler._collection.insert_one.call_args[0][0]
        assert call_args["message"] == ""

    def test_write_includes_timestamp(self) -> None:
        handler = self._make_handler()
        before = time.time()
        handler.write("ts test\n")
        after = time.time()
        call_args = handler._collection.insert_one.call_args[0][0]
        assert before <= call_args["timestamp"] <= after


class TestMongoHandlerFlush:
    def test_flush_noop(self) -> None:
        mock_pymongo = MagicMock()
        mock_client = MagicMock()
        mock_pymongo.MongoClient.return_value = mock_client
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"pymongo": mock_pymongo}):
                handler = MongoHandler()
                handler.flush()


class TestMongoHandlerClose:
    def test_close_calls_client_close(self) -> None:
        mock_pymongo = MagicMock()
        mock_client = MagicMock()
        mock_pymongo.MongoClient.return_value = mock_client
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"pymongo": mock_pymongo}):
                handler = MongoHandler()
                handler.close()
                mock_client.close.assert_called_once()
