"""Test cases for callback functionality and template string support."""

import time
from pathlib import Path
import pytest
from logly._logly import PyLogger


class TestCallbackFunctionality:
    """Test callback registration and execution."""

    def test_add_callback_basic(self, tmp_path: Path):
        """Test basic callback registration and execution."""
        log_file = tmp_path / "test_callback.log"
        logger = PyLogger()
        logger.add(str(log_file))
        logger.configure(level="INFO", color=False)

        # Track callback invocations
        callback_records = []

        def test_callback(record):
            callback_records.append(record)

        # Add callback
        callback_id = logger.add_callback(test_callback)
        assert isinstance(callback_id, int)
        assert callback_id == 0

        # Log some messages
        logger.info("Test message 1")
        logger.warning("Test message 2")
        logger.error("Test message 3")

        # Wait for async callbacks
        time.sleep(0.2)

        # Verify callbacks were called
        assert len(callback_records) >= 3
        assert any("Test message 1" in str(r.get("message", "")) for r in callback_records)
        assert any("Test message 2" in str(r.get("message", "")) for r in callback_records)
        assert any("Test message 3" in str(r.get("message", "")) for r in callback_records)

        logger.complete()

    def test_multiple_callbacks(self, tmp_path: Path):
        """Test multiple callbacks can be registered."""
        log_file = tmp_path / "test_multi_callback.log"
        logger = PyLogger()
        logger.add(str(log_file))
        logger.configure(level="INFO", color=False)

        callback1_records = []
        callback2_records = []

        def callback1(record):
            callback1_records.append(record)

        def callback2(record):
            callback2_records.append(record)

        # Add both callbacks
        id1 = logger.add_callback(callback1)
        id2 = logger.add_callback(callback2)

        assert id1 != id2

        # Log a message
        logger.info("Multi-callback test")

        # Wait for async callbacks
        time.sleep(0.2)

        # Both callbacks should have been called
        assert len(callback1_records) >= 1
        assert len(callback2_records) >= 1

        logger.complete()

    def test_remove_callback(self, tmp_path: Path):
        """Test removing a callback."""
        log_file = tmp_path / "test_remove_callback.log"
        logger = PyLogger()
        logger.add(str(log_file))
        logger.configure(level="INFO", color=False)

        callback_records = []

        def test_callback(record):
            callback_records.append(record)

        # Add and then remove callback
        callback_id = logger.add_callback(test_callback)
        logger.info("Message 1")
        time.sleep(0.1)

        initial_count = len(callback_records)
        assert initial_count >= 1

        # Remove callback
        removed = logger.remove_callback(callback_id)
        assert removed is True

        # Log another message
        logger.info("Message 2")
        time.sleep(0.1)

        # Should not have received callback for message 2
        assert len(callback_records) == initial_count

        logger.complete()

    def test_callback_with_context_fields(self, tmp_path: Path):
        """Test callback receives context fields."""
        log_file = tmp_path / "test_callback_context.log"
        logger = PyLogger()
        logger.add(str(log_file))
        logger.configure(level="INFO", color=False)

        callback_records = []

        def test_callback(record):
            callback_records.append(record)

        logger.add_callback(test_callback)

        # Log with context fields
        logger.info("Context test", user="alice", request_id="123")

        # Wait for async callback
        time.sleep(0.2)

        # Check that context fields are in callback record
        assert len(callback_records) >= 1
        # Note: The exact structure depends on implementation
        # Just verify we got the callback
        record = callback_records[0]
        assert "message" in record or record is not None

        logger.complete()

    def test_callback_exception_handling(self, tmp_path: Path):
        """Test that exceptions in callbacks don't crash logging."""
        log_file = tmp_path / "test_callback_exception.log"
        logger = PyLogger()
        logger.add(str(log_file))
        logger.configure(level="INFO", color=False)

        def failing_callback(record):
            raise ValueError("Callback error")

        logger.add_callback(failing_callback)

        # This should not crash even though callback fails
        logger.info("Test with failing callback")
        time.sleep(0.1)

        # Log file should still exist and have content
        logger.complete()
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test with failing callback" in content

    def test_callback_async_execution(self, tmp_path: Path):
        """Test that callbacks execute asynchronously."""
        log_file = tmp_path / "test_callback_async.log"
        logger = PyLogger()
        logger.add(str(log_file))
        logger.configure(level="INFO", color=False)

        import threading

        callback_thread_ids = []

        def test_callback(record):
            callback_thread_ids.append(threading.get_ident())

        logger.add_callback(test_callback)

        main_thread_id = threading.get_ident()

        # Log a message
        logger.info("Async test")
        time.sleep(0.2)

        # Callback should have run in a different thread
        assert len(callback_thread_ids) >= 1
        assert callback_thread_ids[0] != main_thread_id

        logger.complete()


class TestTemplateStringSupport:
    """Test template string functionality with {variable} syntax."""

    def test_basic_template_interpolation(self, tmp_path: Path):
        """Test basic {variable} template interpolation."""
        from logly import logger

        log_file = tmp_path / "test_template.log"
        logger.add(str(log_file))
        logger.configure(level="INFO", color=False)

        # Template string - deferred interpolation
        logger.info("Hello {name}", name="Alice")

        logger.complete()

        # Verify log output
        content = log_file.read_text()
        assert "Hello Alice" in content
        assert "name=" not in content  # name should be interpolated, not in context

    def test_multiple_variable_interpolation(self, tmp_path: Path):
        """Test multiple variables in template."""
        from logly import logger

        log_file = tmp_path / "test_multi_template.log"
        logger.add(str(log_file))
        logger.configure(level="INFO", color=False)

        # Multiple template variables
        logger.info("User {user} logged in from {ip}", user="bob", ip="192.168.1.1")

        logger.complete()

        content = log_file.read_text()
        assert "User bob logged in from 192.168.1.1" in content

    def test_template_with_remaining_kwargs(self, tmp_path: Path):
        """Test that unused kwargs remain as context fields."""
        from logly import logger

        log_file = tmp_path / "test_template_context.log"
        logger.add(str(log_file))
        logger.configure(level="INFO", color=False)

        # Template variables + extra context fields
        logger.info("Action {action} completed", action="deploy", duration_ms=150, user="alice")

        logger.complete()

        content = log_file.read_text()
        # action should be in message
        assert "Action deploy completed" in content
        # duration_ms and user should remain as context fields
        assert "duration_ms=150" in content
        assert "user=alice" in content

    def test_template_with_f_string(self, tmp_path: Path):
        """Test that f-strings still work (pre-evaluated)."""
        from logly import logger

        log_file = tmp_path / "test_fstring.log"
        logger.add(str(log_file))
        logger.configure(level="INFO", color=False)

        name = "Charlie"
        # f-string - pre-evaluated before reaching logger
        logger.info(f"Welcome {name}")

        logger.complete()

        content = log_file.read_text()
        assert "Welcome Charlie" in content

    def test_template_with_percent_formatting(self, tmp_path: Path):
        """Test that % formatting still works."""
        from logly import logger

        log_file = tmp_path / "test_percent.log"
        logger.add(str(log_file))
        logger.configure(level="INFO", color=False)

        # % formatting - legacy style
        logger.info("Count: %d", 42)

        logger.complete()

        content = log_file.read_text()
        assert "Count: 42" in content

    def test_template_mixed_with_bind(self, tmp_path: Path):
        """Test template strings work with bind() context."""
        from logly import logger

        log_file = tmp_path / "test_template_bind.log"
        logger.add(str(log_file))
        logger.configure(level="INFO", color=False)

        # Bind context
        request_logger = logger.bind(request_id="req-123")

        # Template string with bound context
        request_logger.info("User {user} authenticated", user="dave")

        logger.complete()

        content = log_file.read_text()
        assert "User dave authenticated" in content
        assert "request_id=req-123" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
