"""Tests for RabbitMQ integration."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest


class TestRabbitMQHandlerInit:
    def test_init_import_guard(self) -> None:
        from logly.integrations.rabbitmq import RabbitMQHandler

        with patch("importlib.util.find_spec", return_value=None):
            with pytest.raises(ImportError):
                RabbitMQHandler()

    def test_init_success(self) -> None:
        from logly.integrations.rabbitmq import RabbitMQHandler

        mock_pika = MagicMock()

        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"pika": mock_pika}):
                handler = RabbitMQHandler(
                    "amqp://guest:guest@localhost:5672/",
                    queue="test-logs",
                    exchange="logs",
                    routing_key="app.logs",
                    durable=False,
                    timeout=10.0,
                )
                assert handler._url == "amqp://guest:guest@localhost:5672/"
                assert handler._queue == "test-logs"
                assert handler._exchange == "logs"
                assert handler._routing_key == "app.logs"
                assert handler._durable is False
                assert handler._timeout == 10.0

    def test_init_defaults(self) -> None:
        from logly.integrations.rabbitmq import RabbitMQHandler

        with patch("importlib.util.find_spec", return_value=MagicMock()):
            handler = RabbitMQHandler()
            assert handler._queue == "logly-logs"
            assert handler._exchange == ""
            assert handler._routing_key == "logly-logs"
            assert handler._durable is True


class TestRabbitMQHandlerWrite:
    @patch("logly.integrations.rabbitmq.RabbitMQHandler._ensure_connection")
    def test_write_publishes(self, mock_ensure: MagicMock) -> None:
        from logly.integrations.rabbitmq import RabbitMQHandler

        mock_channel = MagicMock()
        mock_ensure.return_value = mock_channel
        mock_pika = MagicMock()

        with patch.dict(sys.modules, {"pika": mock_pika}):
            handler = RabbitMQHandler.__new__(RabbitMQHandler)
            handler._exchange = ""
            handler._routing_key = "test-queue"
            handler._durable = True
            handler._channel = mock_channel
            handler._connection = MagicMock()

            handler.write("hello rabbitmq\n")
            mock_channel.basic_publish.assert_called_once()

    @patch("logly.integrations.rabbitmq.RabbitMQHandler._ensure_connection")
    def test_write_exception_resets(self, mock_ensure: MagicMock) -> None:
        from logly.integrations.rabbitmq import RabbitMQHandler

        mock_ensure.side_effect = ConnectionError("fail")
        mock_pika = MagicMock()

        with patch.dict(sys.modules, {"pika": mock_pika}):
            handler = RabbitMQHandler.__new__(RabbitMQHandler)
            handler._exchange = ""
            handler._routing_key = "q"
            handler._durable = True
            handler._channel = MagicMock()
            handler._connection = MagicMock()

            handler.write("msg")
            assert handler._channel is None
            assert handler._connection is None


class TestRabbitMQHandlerFlushClose:
    def test_flush_noop(self) -> None:
        from logly.integrations.rabbitmq import RabbitMQHandler

        handler = RabbitMQHandler.__new__(RabbitMQHandler)
        handler.flush()

    def test_close_clears_connection(self) -> None:
        from logly.integrations.rabbitmq import RabbitMQHandler

        handler = RabbitMQHandler.__new__(RabbitMQHandler)
        mock_channel = MagicMock()
        mock_channel.is_open = True
        mock_connection = MagicMock()
        mock_connection.is_open = True
        handler._channel = mock_channel
        handler._connection = mock_connection

        handler.close()

        mock_channel.close.assert_called_once()
        mock_connection.close.assert_called_once()
        assert handler._channel is None
        assert handler._connection is None

    def test_close_no_connection(self) -> None:
        from logly.integrations.rabbitmq import RabbitMQHandler

        handler = RabbitMQHandler.__new__(RabbitMQHandler)
        handler._channel = None
        handler._connection = None
        handler.close()  # should not raise

    def test_close_exception_swallows(self) -> None:
        from logly.integrations.rabbitmq import RabbitMQHandler

        handler = RabbitMQHandler.__new__(RabbitMQHandler)
        mock_channel = MagicMock()
        mock_channel.is_open = True
        mock_channel.close.side_effect = Exception("fail")
        handler._channel = mock_channel
        handler._connection = MagicMock()

        handler.close()  # should not raise
        assert handler._channel is None
