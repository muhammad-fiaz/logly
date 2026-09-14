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
        import os

        from logly.integrations.newrelic import NewRelicSink

        mock_nr_agent = MagicMock()
        mock_nr_agent.application.return_value = MagicMock()
        mock_nr = MagicMock()
        mock_nr.agent = mock_nr_agent

        old_key = os.environ.get("NEW_RELIC_LICENSE_KEY")
        old_app = os.environ.get("NEW_RELIC_APP_NAME")
        try:
            with patch("importlib.util.find_spec", return_value=MagicMock()):
                with patch.dict(
                    sys.modules, {"newrelic": mock_nr, "newrelic.agent": mock_nr_agent}
                ):
                    NewRelicSink(license_key="key123", app_name="MyApp")
                    mock_nr_agent.initialize.assert_called_once_with()
            assert os.environ.get("NEW_RELIC_LICENSE_KEY") == "key123"
            assert os.environ.get("NEW_RELIC_APP_NAME") == "MyApp"
        finally:
            if old_key is None:
                os.environ.pop("NEW_RELIC_LICENSE_KEY", None)
            else:
                os.environ["NEW_RELIC_LICENSE_KEY"] = old_key
            if old_app is None:
                os.environ.pop("NEW_RELIC_APP_NAME", None)
            else:
                os.environ["NEW_RELIC_APP_NAME"] = old_app


class TestNewRelicDetectSeverity:
    def test_detect_fatal(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("FATAL error") == "CRITICAL"

    def test_detect_critical(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("CRITICAL failure") == "CRITICAL"

    def test_detect_error(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("ERROR 500") == "ERROR"

    def test_detect_fail(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("FAIL connect") == "ERROR"

    def test_detect_warning(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("WARNING low") == "WARNING"

    def test_detect_warn(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("WARN deprecated") == "WARNING"

    def test_detect_notice(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("NOTICE loaded") == "INFO"

    def test_detect_success(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("SUCCESS deployed") == "INFO"

    def test_detect_debug(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("DEBUG var") == "DEBUG"

    def test_detect_trace(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("TRACE entry") == "DEBUG"

    def test_detect_info_default(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("server started") == "INFO"

    def test_detect_case_insensitive(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        assert NewRelicSink._detect_severity("error lowercase") == "ERROR"


class TestNewRelicSinkWrite:
    def test_write_records_log_event(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        mock_nr_agent = MagicMock()
        mock_nr = MagicMock()
        mock_nr.agent = mock_nr_agent

        with patch.dict(sys.modules, {"newrelic": mock_nr, "newrelic.agent": mock_nr_agent}):
            sink = NewRelicSink.__new__(NewRelicSink)
            sink._application = MagicMock()
            sink.write("test message\n")
            mock_nr_agent.record_log_event.assert_called_once()


class TestNewRelicSinkFlushClose:
    def test_flush_noop(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        sink = NewRelicSink.__new__(NewRelicSink)
        sink.flush()

    def test_close_noop(self) -> None:
        from logly.integrations.newrelic import NewRelicSink

        sink = NewRelicSink.__new__(NewRelicSink)
        sink.close()
