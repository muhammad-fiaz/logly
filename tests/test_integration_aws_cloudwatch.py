"""Tests for AWS CloudWatch integration."""

from __future__ import annotations

import sys
import threading
from unittest.mock import MagicMock, patch

import pytest

from logly.integrations.aws_cloudwatch import CloudWatchSink


class TestCloudWatchSinkInit:
    def test_init_import_guard(self) -> None:
        with patch("importlib.util.find_spec", return_value=None):
            with pytest.raises(ImportError, match="boto3 is required"):
                CloudWatchSink(log_group="test", log_stream="stream")

    def test_init_default_params(self) -> None:
        mock_boto3 = MagicMock()
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"boto3": mock_boto3}):
                sink = CloudWatchSink(log_group="grp", log_stream="stm")
                assert sink.log_group == "grp"
                assert sink.log_stream == "stm"
                assert sink.batch_size == 10000
                assert sink.flush_interval == 5.0

    def test_init_custom_params(self) -> None:
        mock_boto3 = MagicMock()
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"boto3": mock_boto3}):
                sink = CloudWatchSink(
                    log_group="g",
                    log_stream="s",
                    region="us-west-2",
                    batch_size=500,
                    flush_interval=10.0,
                    create_group=False,
                    create_stream=False,
                )
                assert sink.batch_size == 500
                assert sink.flush_interval == 10.0

    def test_init_batch_size_capped(self) -> None:
        mock_boto3 = MagicMock()
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"boto3": mock_boto3}):
                sink = CloudWatchSink(log_group="g", log_stream="s", batch_size=99999)
                assert sink.batch_size == 10000

    def test_init_with_aws_credentials(self) -> None:
        mock_boto3 = MagicMock()
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"boto3": mock_boto3}):
                sink = CloudWatchSink(
                    log_group="g",
                    log_stream="s",
                    region="eu-west-1",
                    aws_access_key_id="AKID",
                    aws_secret_access_key="SECRET",
                )
                assert sink.log_group == "g"


class TestCloudWatchSinkWrite:
    def test_write_adds_to_buffer(self) -> None:
        mock_boto3 = MagicMock()
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"boto3": mock_boto3}):
                sink = CloudWatchSink(log_group="g", log_stream="s", batch_size=100)
                sink.write("hello cloudwatch\n")
                assert len(sink._buffer) == 1

    def test_write_auto_flushes_when_full(self) -> None:
        mock_boto3 = MagicMock()
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"boto3": mock_boto3}):
                sink = CloudWatchSink(log_group="g", log_stream="s", batch_size=2)
                sink.write("msg1\n")
                sink.write("msg2\n")
                mock_client.put_log_events.assert_called()


class TestCloudWatchSinkFlush:
    def test_flush_noop_when_empty(self) -> None:
        mock_boto3 = MagicMock()
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"boto3": mock_boto3}):
                sink = CloudWatchSink(log_group="g", log_stream="s")
                sink.flush()

    def test_flush_sends_buffer(self) -> None:
        mock_boto3 = MagicMock()
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"boto3": mock_boto3}):
                sink = CloudWatchSink(log_group="g", log_stream="s")
                sink._buffer = [{"timestamp": 1, "message": "test"}]
                sink.flush()
                mock_client.put_log_events.assert_called_once()


class TestCloudWatchSinkClose:
    def test_close_stops_thread(self) -> None:
        mock_boto3 = MagicMock()
        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"boto3": mock_boto3}):
                sink = CloudWatchSink(log_group="g", log_stream="s")
                sink._flush_thread = MagicMock(spec=threading.Thread)
                sink._stop_event = MagicMock()
                sink.close()
                sink._stop_event.set.assert_called_once()
                sink._flush_thread.join.assert_called_once()
