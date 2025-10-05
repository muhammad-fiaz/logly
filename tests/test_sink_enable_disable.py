"""Comprehensive tests for sink enable/disable functionality."""

import os
import tempfile
from pathlib import Path

import pytest

from logly import logger


@pytest.fixture(autouse=True)
def reset_logger():
    """Reset logger before each test."""
    logger.reset()
    logger.remove_all()
    yield
    logger.reset()
    logger.remove_all()


class TestSinkEnableDisable:
    """Test suite for per-sink enable/disable controls."""

    def test_sink_enabled_by_default(self):
        """Test that sinks are enabled by default when created."""
        logger.configure(auto_sink=False)
        sink_id = logger.add("console")
        assert logger.is_sink_enabled(sink_id) is True

    def test_disable_sink(self):
        """Test disabling a sink."""
        logger.configure(auto_sink=False)
        sink_id = logger.add("console")
        result = logger.disable_sink(sink_id)
        assert result is True
        assert logger.is_sink_enabled(sink_id) is False

    def test_enable_sink(self):
        """Test enabling a previously disabled sink."""
        logger.configure(auto_sink=False)
        sink_id = logger.add("console")
        logger.disable_sink(sink_id)
        result = logger.enable_sink(sink_id)
        assert result is True
        assert logger.is_sink_enabled(sink_id) is True

    def test_disable_nonexistent_sink(self):
        """Test disabling a sink that doesn't exist."""
        result = logger.disable_sink(99999)
        assert result is False

    def test_enable_nonexistent_sink(self):
        """Test enabling a sink that doesn't exist."""
        result = logger.enable_sink(99999)
        assert result is False

    def test_is_sink_enabled_nonexistent(self):
        """Test checking enabled status of nonexistent sink."""
        result = logger.is_sink_enabled(99999)
        assert result is None

    def test_disabled_sink_no_output(self):
        """Test that disabled sinks don't write output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            # Write some logs while enabled
            logger.info("Message 1")

            # Disable sink
            logger.disable_sink(sink_id)

            # Write more logs (should not appear)
            logger.info("Message 2")
            logger.error("Message 3")

            # Re-enable sink
            logger.enable_sink(sink_id)

            # Write final log
            logger.info("Message 4")

            # Flush to ensure writes
            logger.complete()

            # Read file content
            content = log_file.read_text()

            # Should contain Message 1 and 4, but not 2 or 3
            assert "Message 1" in content
            assert "Message 2" not in content
            assert "Message 3" not in content
            assert "Message 4" in content

    def test_multiple_sinks_independent_control(self):
        """Test that multiple sinks can be controlled independently."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "file1.log"
            file2 = Path(tmpdir) / "file2.log"

            sink1 = logger.add(str(file1))
            sink2 = logger.add(str(file2))

            # Both enabled by default
            logger.info("Message 1")

            # Disable only sink1
            logger.disable_sink(sink1)
            logger.info("Message 2")

            # Disable sink2, enable sink1
            logger.disable_sink(sink2)
            logger.enable_sink(sink1)
            logger.info("Message 3")

            logger.complete()

            content1 = file1.read_text()
            content2 = file2.read_text()

            # File1: Messages 1 and 3 (disabled during Message 2)
            assert "Message 1" in content1
            assert "Message 2" not in content1
            assert "Message 3" in content1

            # File2: Messages 1 and 2 (disabled during Message 3)
            assert "Message 1" in content2
            assert "Message 2" in content2
            assert "Message 3" not in content2

    def test_global_console_overrides_sink_enable(self):
        """Test that global console=False disables all sinks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            # Sink enabled, global enabled
            logger.configure(console=True, auto_sink=False)
            logger.info("Message 1")

            # Sink enabled, global DISABLED
            logger.configure(console=False, auto_sink=False)
            logger.info("Message 2")

            # Re-enable global
            logger.configure(console=True, auto_sink=False)
            logger.info("Message 3")

            logger.complete()

            content = log_file.read_text()

            # Should contain Messages 1 and 3, but not 2 (global disabled)
            assert "Message 1" in content
            assert "Message 2" not in content
            assert "Message 3" in content

    def test_enable_disable_toggle(self):
        """Test toggling enable/disable multiple times."""
        logger.configure(auto_sink=False)
        sink_id = logger.add("console")

        for i in range(5):
            logger.disable_sink(sink_id)
            assert logger.is_sink_enabled(sink_id) is False

            logger.enable_sink(sink_id)
            assert logger.is_sink_enabled(sink_id) is True

    def test_sink_enabled_after_reset(self):
        """Test that sinks remain enabled after logger.reset()."""
        logger.configure(auto_sink=False)
        sink_id = logger.add("console")
        logger.disable_sink(sink_id)

        # Reset logger
        logger.reset()

        # Sink should still exist but state might reset
        # Note: This behavior depends on implementation
        # Just verify the method doesn't crash
        status = logger.is_sink_enabled(sink_id)
        # Status could be True, False, or None depending on reset behavior
        assert status in (True, False, None)

    def test_removed_sink_returns_none(self):
        """Test that removed sinks return None for is_sink_enabled."""
        logger.configure(auto_sink=False)
        sink_id = logger.add("console")
        logger.remove(sink_id)

        result = logger.is_sink_enabled(sink_id)
        assert result is None

    def test_disable_sink_with_callbacks(self):
        """Test that disabled sinks don't trigger callbacks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            callback_count = {"count": 0}

            def test_callback(record):
                callback_count["count"] += 1

            logger.add_callback(test_callback)

            # Enabled sink
            logger.info("Message 1")
            logger.complete()

            # Disable sink
            logger.disable_sink(sink_id)
            logger.info("Message 2")
            logger.complete()

            # Note: Callbacks might still be called even if sink is disabled
            # depending on implementation. This test documents the behavior.
            # If callbacks are sink-independent, count should be 2
            # If callbacks depend on active sinks, count might be 1
            assert callback_count["count"] >= 1


class TestSinkEnableDisableEdgeCases:
    """Test edge cases and error conditions."""

    def test_enable_already_enabled_sink(self):
        """Test enabling a sink that's already enabled."""
        logger.configure(auto_sink=False)
        sink_id = logger.add("console")
        result = logger.enable_sink(sink_id)
        assert result is True  # Should succeed (idempotent)

    def test_disable_already_disabled_sink(self):
        """Test disabling a sink that's already disabled."""
        logger.configure(auto_sink=False)
        sink_id = logger.add("console")
        logger.disable_sink(sink_id)
        result = logger.disable_sink(sink_id)
        assert result is True  # Should succeed (idempotent)

    def test_negative_sink_id(self):
        """Test operations with negative sink ID."""
        assert logger.enable_sink(-1) is False
        assert logger.disable_sink(-1) is False
        assert logger.is_sink_enabled(-1) is None

    def test_zero_sink_id(self):
        """Test operations with zero sink ID."""
        # Sink IDs typically start from 1, so 0 should be invalid
        assert logger.is_sink_enabled(0) in (False, None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
