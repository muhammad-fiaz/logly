"""Tests for Celery integration."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

from logly.integrations.celery import patch_task_logger, setup_celery_logging


class TestSetupCeleryLogging:
    def test_configures_celery_logger(self) -> None:
        with patch("logly.integrations.celery.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.INFO = logging.INFO
            setup_celery_logging()
            calls = [c[0][0] for c in mock_logging.getLogger.call_args_list]
            assert "celery" in calls

    def test_configures_child_loggers(self) -> None:
        with patch("logly.integrations.celery.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.INFO = logging.INFO
            setup_celery_logging()
            calls = [c[0][0] for c in mock_logging.getLogger.call_args_list]
            for name in ("celery.app", "celery.task", "celery.worker"):
                assert name in calls

    def test_propagate_false(self) -> None:
        with patch("logly.integrations.celery.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.INFO = logging.INFO
            setup_celery_logging()
            logger = mock_logging.getLogger.return_value
            assert logger.propagate is False

    def test_default_level(self) -> None:
        with patch("logly.integrations.celery.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.INFO = logging.INFO
            setup_celery_logging()
            logger = mock_logging.getLogger.return_value
            logger.setLevel.assert_called_with(logging.INFO)

    def test_custom_level(self) -> None:
        with patch("logly.integrations.celery.logging") as mock_logging:
            mock_logging.getLogger.return_value.handlers = []
            mock_logging.DEBUG = logging.DEBUG
            mock_logging.INFO = logging.INFO
            setup_celery_logging(level="DEBUG")
            logger = mock_logging.getLogger.return_value
            logger.setLevel.assert_called_with(logging.DEBUG)


class TestPatchTaskLogger:
    def test_replaces_handlers(self) -> None:
        task_logger = MagicMock()
        task_logger.handlers = [MagicMock()]
        patch_task_logger(task_logger)
        assert len(task_logger.handlers) == 1

    def test_sets_level(self) -> None:
        task_logger = MagicMock()
        task_logger.handlers = [MagicMock()]
        patch_task_logger(task_logger, level="DEBUG")
        task_logger.setLevel.assert_called_once()

    def test_no_handlers_attr(self) -> None:
        task_logger = MagicMock(spec=[])
        patch_task_logger(task_logger)

    def test_no_setlevel_attr(self) -> None:
        task_logger = MagicMock(spec=["handlers"])
        task_logger.handlers = [MagicMock()]
        patch_task_logger(task_logger)
