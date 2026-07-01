"""Tests for Prometheus integration."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from logly.integrations.prometheus import PrometheusLogSink


class TestPrometheusLogSinkInit:
    def test_init_import_guard(self) -> None:
        saved = sys.modules.get("prometheus_client")
        sys.modules["prometheus_client"] = None  # type: ignore[assignment]
        try:
            with pytest.raises(ImportError, match="prometheus-client"):
                PrometheusLogSink()
        finally:
            if saved is not None:
                sys.modules["prometheus_client"] = saved
            else:
                sys.modules.pop("prometheus_client", None)

    def test_init_creates_metrics(self) -> None:
        mock_prom = MagicMock()
        mock_prom.Counter.return_value = MagicMock()
        mock_prom.Histogram.return_value = MagicMock()
        mock_prom.Gauge.return_value = MagicMock()
        with patch.dict(sys.modules, {"prometheus_client": mock_prom}):
            sink = PrometheusLogSink(namespace="myapp")
            assert sink._namespace == "myapp"


class TestPrometheusLogSinkWrite:
    def test_write_increments_counter(self) -> None:
        mock_counter = MagicMock()
        mock_histogram = MagicMock()
        mock_gauge = MagicMock()

        sink = object.__new__(PrometheusLogSink)
        sink._log_total = mock_counter
        sink._log_size = mock_histogram
        sink._log_level = mock_gauge
        sink._level_numeric = {"INFO": 20, "ERROR": 50, "DEBUG": 10}

        sink.write("[INFO] hello prometheus\n")
        mock_counter.labels.assert_called_with(level="INFO")
        mock_counter.labels.return_value.inc.assert_called_once()
        mock_histogram.observe.assert_called_once()
        mock_gauge.set.assert_called_with(20)

    def test_write_detects_error_level(self) -> None:
        mock_counter = MagicMock()
        mock_histogram = MagicMock()
        mock_gauge = MagicMock()

        sink = object.__new__(PrometheusLogSink)
        sink._log_total = mock_counter
        sink._log_size = mock_histogram
        sink._log_level = mock_gauge
        sink._level_numeric = {"INFO": 20, "ERROR": 50, "DEBUG": 10}

        sink.write("[ERROR] something broke\n")
        mock_counter.labels.assert_called_with(level="ERROR")


class TestPrometheusLogSinkFlush:
    def test_flush_noop(self) -> None:
        sink = object.__new__(PrometheusLogSink)
        sink.flush()


class TestPrometheusLogSinkClose:
    def test_close_noop(self) -> None:
        sink = object.__new__(PrometheusLogSink)
        sink.close()
