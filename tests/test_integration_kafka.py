from __future__ import annotations

import json
import sys
from unittest.mock import MagicMock, patch

import pytest

from logly.integrations.kafka import KafkaHandler


class TestKafkaHandlerInit:
    def test_init_import_guard(self) -> None:
        with patch("importlib.util.find_spec", return_value=None):
            with pytest.raises(ImportError, match="confluent-kafka is required"):
                KafkaHandler("localhost:9092")

    def test_init_creates_producer(self) -> None:
        mock_producer_cls = MagicMock()
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer
        fake_kafka = MagicMock()
        fake_kafka.Producer = mock_producer_cls
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"confluent_kafka": fake_kafka}):
                handler = KafkaHandler("localhost:9092", topic="test-logs")
                assert handler.topic == "test-logs"
                mock_producer_cls.assert_called_once()

    def test_init_default_params(self) -> None:
        mock_producer_cls = MagicMock()
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer
        fake_kafka = MagicMock()
        fake_kafka.Producer = mock_producer_cls
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"confluent_kafka": fake_kafka}):
                handler = KafkaHandler()
                assert handler.topic == "logly-logs"

    def test_init_custom_params(self) -> None:
        mock_producer_cls = MagicMock()
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer
        fake_kafka = MagicMock()
        fake_kafka.Producer = mock_producer_cls
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"confluent_kafka": fake_kafka}):
                handler = KafkaHandler(
                    "broker1:9092",
                    topic="my-topic",
                    client_id="my-client",
                    acks="all",
                    timeout=10.0,
                )
                assert handler.topic == "my-topic"
                call_kwargs = mock_producer_cls.call_args[0][0]
                assert call_kwargs["bootstrap.servers"] == "broker1:9092"
                assert call_kwargs["client.id"] == "my-client"
                assert call_kwargs["acks"] == "all"
                assert call_kwargs["message.timeout.ms"] == 10000


class TestKafkaHandlerWrite:
    def _make_handler(self) -> KafkaHandler:
        mock_producer_cls = MagicMock()
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer
        fake_kafka = MagicMock()
        fake_kafka.Producer = mock_producer_cls
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"confluent_kafka": fake_kafka}):
                handler = KafkaHandler()
        return handler

    def test_write_produces_message(self) -> None:
        handler = self._make_handler()
        handler.write("hello kafka\n")
        handler._producer.produce.assert_called_once()  # type: ignore[attr-defined]
        handler._producer.poll.assert_called_once_with(0)  # type: ignore[attr-defined]

    def test_write_payload_is_json(self) -> None:
        handler = self._make_handler()
        handler.write("test msg\n")
        call_args = handler._producer.produce.call_args  # type: ignore[attr-defined]
        payload = json.loads(call_args[1]["value"])
        assert payload["message"] == "test msg"
        assert "timestamp" in payload

    def test_write_strips_newline(self) -> None:
        handler = self._make_handler()
        handler.write("msg\n\n")
        call_args = handler._producer.produce.call_args  # type: ignore[attr-defined]
        payload = json.loads(call_args[1]["value"])
        assert payload["message"] == "msg"

    def test_write_empty_message(self) -> None:
        handler = self._make_handler()
        handler.write("\n")
        handler._producer.produce.assert_called_once()  # type: ignore[attr-defined]


class TestKafkaHandlerFlush:
    def test_flush_calls_producer_flush(self) -> None:
        mock_producer_cls = MagicMock()
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer
        fake_kafka = MagicMock()
        fake_kafka.Producer = mock_producer_cls
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"confluent_kafka": fake_kafka}):
                handler = KafkaHandler()
                handler.flush()
                mock_producer.flush.assert_called_once_with(timeout=5.0)


class TestKafkaHandlerClose:
    def test_close_calls_producer_flush(self) -> None:
        mock_producer_cls = MagicMock()
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer
        fake_kafka = MagicMock()
        fake_kafka.Producer = mock_producer_cls
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"confluent_kafka": fake_kafka}):
                handler = KafkaHandler()
                handler.close()
                mock_producer.flush.assert_called_once_with(timeout=5.0)
