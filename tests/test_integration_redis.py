from __future__ import annotations

import json
import sys
from unittest.mock import MagicMock, patch

import pytest

from logly.integrations.redis import RedisHandler


class TestRedisHandlerInit:
    def test_init_import_guard(self) -> None:
        with patch("importlib.util.find_spec", return_value=None):
            with pytest.raises(ImportError, match="redis is required"):
                RedisHandler("redis://localhost:6379/0")

    def test_init_creates_client(self) -> None:
        mock_redis = MagicMock()
        mock_client = MagicMock()
        mock_redis.Redis.fromurl.return_value = mock_client
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"redis": mock_redis}):
                handler = RedisHandler("redis://localhost:6379/0", key="test:logs")
                assert handler.key == "test:logs"
                assert handler.mode == "list"
                mock_redis.Redis.fromurl.assert_called_once()

    def test_init_default_params(self) -> None:
        mock_redis = MagicMock()
        mock_client = MagicMock()
        mock_redis.Redis.fromurl.return_value = mock_client
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"redis": mock_redis}):
                handler = RedisHandler()
                assert handler.key == "logly:logs"
                assert handler.mode == "list"
                assert handler.max_stream_len == 10000

    def test_init_stream_mode(self) -> None:
        mock_redis = MagicMock()
        mock_client = MagicMock()
        mock_redis.Redis.fromurl.return_value = mock_client
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"redis": mock_redis}):
                handler = RedisHandler(mode="stream")
                assert handler.mode == "stream"


class TestRedisHandlerWrite:
    def _make_handler(self, mode: str = "list") -> RedisHandler:
        mock_redis = MagicMock()
        mock_client = MagicMock()
        mock_redis.Redis.fromurl.return_value = mock_client
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"redis": mock_redis}):
                handler = RedisHandler(mode=mode)
        return handler

    def test_write_list_mode(self) -> None:
        handler = self._make_handler(mode="list")
        handler.write("hello redis\n")
        handler._client.lpush.assert_called_once()
        handler._client.ltrim.assert_called_once()

    def test_write_stream_mode(self) -> None:
        handler = self._make_handler(mode="stream")
        handler.write("hello redis\n")
        handler._client.xadd.assert_called_once()

    def test_write_strips_newline(self) -> None:
        handler = self._make_handler(mode="list")
        handler.write("msg\n")
        call_args = handler._client.lpush.call_args
        entry = json.loads(call_args[0][1])
        assert entry["message"] == "msg"

    def test_write_empty_message(self) -> None:
        handler = self._make_handler(mode="list")
        handler.write("\n")
        handler._client.lpush.assert_called_once()


class TestRedisHandlerFlush:
    def test_flush_noop(self) -> None:
        mock_redis = MagicMock()
        mock_client = MagicMock()
        mock_redis.Redis.fromurl.return_value = mock_client
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"redis": mock_redis}):
                handler = RedisHandler()
                handler.flush()


class TestRedisHandlerClose:
    def test_close_calls_client_close(self) -> None:
        mock_redis = MagicMock()
        mock_client = MagicMock()
        mock_redis.Redis.fromurl.return_value = mock_client
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"redis": mock_redis}):
                handler = RedisHandler()
                handler.close()
                mock_client.close.assert_called_once()
