"""Tests for Click integration."""

from __future__ import annotations

from unittest.mock import patch

from logly.integrations.click import click_echo


class TestClickEcho:
    def test_message_logs_info(self) -> None:
        with patch("logly.integrations.click.logger") as mock_logger:
            click_echo("hello")
            mock_logger.log.assert_called_once_with("INFO", "hello")

    def test_none_message_is_noop(self) -> None:
        with patch("logly.integrations.click.logger") as mock_logger:
            click_echo(None)
            mock_logger.log.assert_not_called()

    def test_err_true_logs_warning(self) -> None:
        with patch("logly.integrations.click.logger") as mock_logger:
            click_echo("error msg", err=True)
            mock_logger.log.assert_called_once_with("WARNING", "error msg")

    def test_err_false_logs_info(self) -> None:
        with patch("logly.integrations.click.logger") as mock_logger:
            click_echo("info msg", err=False)
            mock_logger.log.assert_called_once_with("INFO", "info msg")

    def test_message_converted_to_string(self) -> None:
        with patch("logly.integrations.click.logger") as mock_logger:
            click_echo(42)
            mock_logger.log.assert_called_once_with("INFO", "42")

    def test_nl_ignored(self) -> None:
        with patch("logly.integrations.click.logger") as mock_logger:
            click_echo("msg", nl=False)
            mock_logger.log.assert_called_once_with("INFO", "msg")

    def test_file_ignored(self) -> None:
        with patch("logly.integrations.click.logger") as mock_logger:
            click_echo("msg", file="some_file")
            mock_logger.log.assert_called_once_with("INFO", "msg")

    def test_color_ignored(self) -> None:
        with patch("logly.integrations.click.logger") as mock_logger:
            click_echo("msg", color=True)
            mock_logger.log.assert_called_once_with("INFO", "msg")

    def test_extra_kwargs_ignored(self) -> None:
        with patch("logly.integrations.click.logger") as mock_logger:
            click_echo("msg", foo="bar", baz=123)
            mock_logger.log.assert_called_once_with("INFO", "msg")

    def test_logger_exception_is_swallowed(self) -> None:
        with patch("logly.integrations.click.logger") as mock_logger:
            mock_logger.log.side_effect = Exception("fail")
            click_echo("msg")
