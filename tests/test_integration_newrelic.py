"""Tests for New Relic integration."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest


class TestNewRelicSinkInit:
    def test_init_import_guard(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        with patch("importlib.util.find_spec", return_value=None):
            with pytest.raises(ImportError):
                NewRelicSink()

    def test_init_success(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        mock_nr_agent = MagicMock()
        mock_nr_agent.application.return_value = MagicMock()
        mock_nr = MagicMock()
        mock_nr.agent = mock_nr_agent

        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"newrelic": mock_nr, "newrelic.agent": mock_nr_agent}):
                sink = NewRelicSink()
                assert sink._application is not None

    def test_init_with_settings(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        mock_nr_agent = MagicMock()
        mock_nr_agent.application.return_value = MagicMock()
        mock_nr = MagicMock()
        mock_nr.agent = mock_nr_agent

        with patch("importlib.util.find_spec", return_value=MagicMock()):
            with patch.dict(sys.modules, {"newrelic": mock_nr, "newrelic.agent": mock_nr_agent}):
                NewRelicSink(license_key="key123", app_name="MyApp")
                mock_nr_agent.initialize.assert_called_once_with(
                    license_key="key123", app_name="MyApp"
                )


class TestNewRelicDetectSeverity:
    def test_detect_fatal(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("FATAL error") == "critical"

    def test_detect_critical(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("CRITICAL failure") == "critical"

    def test_detect_error(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("ERROR 500") == "error"

    def test_detect_fail(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("FAIL connect") == "error"

    def test_detect_warning(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("WARNING low") == "warning"

    def test_detect_warn(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("WARN deprecated") == "warning"

    def test_detect_notice(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("NOTICE loaded") == "info"

    def test_detect_success(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("SUCCESS deployed") == "info"

    def test_detect_debug(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("DEBUG var") == "debug"

    def test_detect_trace(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("TRACE entry") == "debug"

    def test_detect_info_default(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("server started") == "info"

    def test_detect_case_insensitive(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("error lowercase") == "error"


class TestNewRelicSinkWrite:
    def test_write_calls_agent_log(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        mock_nr_agent = MagicMock()
        mock_nr = MagicMock()
        mock_nr.agent = mock_nr_agent

        with patch.dict(sys.modules, {"newrelic": mock_nr, "newrelic.agent": mock_nr_agent}):
            sink = NewRelicSink.__new__(NewRelicSink)
            sink._application = MagicMock()
            sink.write("test message\n")
            mock_nr_agent.log.assert_called_once()


class TestNewRelicSinkFlushClose:
    def test_flush_noop(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        sink = NewRelicSink.__new__(NewRelicSink)
        sink.flush()

    def test_close_noop(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        sink = NewRelicSink.__new__(NewRelicSink)
        sink.close()
