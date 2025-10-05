"""Tests for global console parameter as kill-switch."""

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


class TestGlobalConsoleControl:
    """Test suite for global console parameter controlling ALL logging."""

    def test_console_true_enables_logging(self):
        """Test that console=True enables logging."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger.add(str(log_file))
            logger.configure(console=True)

            logger.info("Test message")
            logger.complete()

            content = log_file.read_text()
            assert "Test message" in content

    def test_console_false_disables_all_logging(self):
        """Test that console=False disables ALL logging (kill-switch)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger.add(str(log_file))

            # Enable logging first
            logger.configure(console=True)
            logger.info("Message 1")

            # Disable ALL logging
            logger.configure(console=False)
            logger.info("Message 2")
            logger.error("Message 3")
            logger.critical("Message 4")

            # Re-enable logging
            logger.configure(console=True)
            logger.info("Message 5")

            logger.complete()

            content = log_file.read_text()

            # Should contain Messages 1 and 5, but not 2, 3, or 4
            assert "Message 1" in content
            assert "Message 2" not in content
            assert "Message 3" not in content
            assert "Message 4" not in content
            assert "Message 5" in content

    def test_console_false_affects_all_sinks(self):
        """Test that console=False disables multiple sinks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "file1.log"
            file2 = Path(tmpdir) / "file2.log"
            file3 = Path(tmpdir) / "file3.log"

            logger.add(str(file1))
            logger.add(str(file2))
            logger.add(str(file3))

            logger.configure(console=True)
            logger.info("Before disable")

            logger.configure(console=False)
            logger.info("During disable")

            logger.configure(console=True)
            logger.info("After enable")

            logger.complete()

            # Check all three files
            for log_file in [file1, file2, file3]:
                content = log_file.read_text()
                assert "Before disable" in content
                assert "During disable" not in content
                assert "After enable" in content

    def test_reset_enables_logging(self):
        """Test that reset() re-enables logging."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger.add(str(log_file))

            # Disable logging
            logger.configure(console=False)
            logger.info("Disabled message")

            # Reset should enable logging
            logger.reset()
            logger.add(str(log_file))  # Re-add sink after reset
            logger.info("After reset")

            logger.complete()

            content = log_file.read_text()
            assert "Disabled message" not in content
            assert "After reset" in content

    def test_console_parameter_performance(self):
        """Test that console=False provides early exit (performance)."""
        # When console=False, logging should return immediately
        # without any formatting or processing overhead
        logger.configure(console=False)

        # These should all return immediately with minimal overhead
        for _ in range(1000):
            logger.info("Test message with %s formatting", "expensive")
            logger.error("Error with dict", data={"key": "value"})

        # No assertions needed - just verify no crashes
        logger.configure(console=True)

    def test_console_false_with_callbacks(self):
        """Test that console=False prevents callback execution."""
        callback_calls = {"count": 0}

        def test_callback(record):
            callback_calls["count"] += 1

        logger.add_callback(test_callback)

        logger.configure(console=True)
        logger.info("Message 1")

        logger.configure(console=False)
        logger.info("Message 2")

        logger.configure(console=True)
        logger.info("Message 3")

        logger.complete()

        # Callbacks should only be called for Messages 1 and 3
        # (when console=True)
        assert callback_calls["count"] == 2

    def test_console_false_with_exception(self):
        """Test that console=False disables exception logging."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger.add(str(log_file))

            logger.configure(console=False)

            try:
                raise ValueError("Test error")
            except ValueError:
                logger.exception("Exception occurred")

            logger.complete()

            content = log_file.read_text()
            assert "Exception occurred" not in content
            assert "ValueError" not in content

    def test_console_toggle_stress(self):
        """Test rapid toggling of console parameter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger.add(str(log_file))

            for i in range(100):
                if i % 2 == 0:
                    logger.configure(console=True)
                    logger.info(f"Message {i}")
                else:
                    logger.configure(console=False)
                    logger.info(f"Message {i}")

            logger.complete()

            content = log_file.read_text()

            # Only even-numbered messages should appear
            assert "Message 0 |" in content
            assert "Message 1 |" not in content
            assert "Message 2 |" in content
            assert "Message 3 |" not in content


class TestGlobalConsoleWithSinkControl:
    """Test interaction between global console and per-sink enable/disable."""

    def test_both_global_and_sink_disabled(self):
        """Test that both global and sink disable work together."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            # Disable at sink level
            logger.disable_sink(sink_id)
            logger.info("Sink disabled")

            # Enable sink, disable globally
            logger.enable_sink(sink_id)
            logger.configure(console=False)
            logger.info("Global disabled")

            # Enable both
            logger.configure(console=True)
            logger.enable_sink(sink_id)
            logger.info("Both enabled")

            logger.complete()

            content = log_file.read_text()
            assert "Sink disabled" not in content
            assert "Global disabled" not in content
            assert "Both enabled" in content

    def test_sink_disabled_global_enabled(self):
        """Test sink-level disable with global enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.configure(console=True)
            logger.disable_sink(sink_id)
            logger.info("Test message")

            logger.complete()

            content = log_file.read_text()
            assert "Test message" not in content

    def test_global_disabled_sink_enabled(self):
        """Test global disable with sink-level enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            sink_id = logger.add(str(log_file))

            logger.configure(console=False)
            logger.enable_sink(sink_id)  # Should have no effect
            logger.info("Test message")

            logger.complete()

            content = log_file.read_text()
            assert "Test message" not in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
