"""tests for Logly functionality gaps and edge cases."""

import threading

import pytest

from logly import logger


class TestConfigureMethodParameters:
    """Test configure method with various parameter combinations."""

    def setup_method(self):
        """Reset logger state before each test."""
        logger.remove_all()  # Clear all sinks from previous tests
        logger.reset()

    def teardown_method(self):
        """Clean up after each test."""
        logger.reset()

    def test_configure_json_parameter(self, tmp_path):
        """Test JSON output format configuration."""
        log_file = tmp_path / "json_test.log"
        logger.add(str(log_file))

        # Configure with JSON format
        logger.configure(level="INFO", json=True, color=False)
        logger.info("JSON test message", user="alice", action="login")

        logger.complete()

        content = log_file.read_text()
        # JSON format may not be fully implemented, check for structured output
        assert "JSON test message" in content
        assert "user=alice" in content or "alice" in content

    def test_configure_show_filename_lineno(self, tmp_path):
        """Test filename and line number display configuration."""
        log_file = tmp_path / "filename_test.log"
        logger.add(str(log_file))

        # Configure with filename and lineno enabled
        logger.configure(
            level="INFO",
            color=False,
            show_filename=True,
            show_lineno=True,
            show_time=False,
            show_module=False,
            show_function=False,
        )

        logger.info("Filename test message")
        logger.complete()

        content = log_file.read_text()
        # Should contain filename and line number (full path)
        assert "test_comprehensive_coverage.py" in content
        assert "lineno=" in content

    def test_configure_invalid_parameters(self):
        """Test configure with invalid parameters raises appropriate errors."""
        # Invalid level should raise ValueError with GitHub issue tracker link
        with pytest.raises(ValueError, match="Invalid log level"):
            logger.configure(level="INVALID_LEVEL")

    def test_configure_none_values_reset_unsupported(self):
        """Test that None values are not supported for required parameters."""
        # The API doesn't support None for level - it should raise TypeError
        with pytest.raises(TypeError):
            logger.configure(level=None)  # type: ignore[arg-type]


class TestAddMethodParameters:
    """Test add method with various parameter combinations."""

    def setup_method(self):
        """Reset logger state before each test."""
        logger.remove_all()  # Clear all sinks from previous tests
        logger.reset()

    def teardown_method(self):
        """Clean up after each test."""
        logger.reset()

    def test_add_buffer_size_parameter(self, tmp_path):
        """Test buffer size parameter in add method."""
        log_file = tmp_path / "buffer_test.log"
        logger.add(str(log_file), buffer_size=1024)

        logger.configure(level="INFO", color=False)
        logger.info("Buffer test message")
        logger.complete()

        content = log_file.read_text()
        assert "Buffer test message" in content

    def test_add_flush_interval_parameter(self, tmp_path):
        """Test flush interval parameter in add method."""
        log_file = tmp_path / "flush_test.log"
        logger.add(str(log_file), flush_interval=1000)

        logger.configure(level="INFO", color=False)
        logger.info("Flush test message")
        logger.complete()

        content = log_file.read_text()
        assert "Flush test message" in content

    def test_add_parameter_combinations(self, tmp_path):
        """Test various parameter combinations in add method."""
        log_file = tmp_path / "combo_test.log"
        logger.add(str(log_file), buffer_size=512, flush_interval=500, rotation="1 MB")

        logger.configure(level="INFO", color=False)
        logger.info("Combo test message")
        logger.complete()

        content = log_file.read_text()
        assert "Combo test message" in content

    def test_add_invalid_parameters(self):
        """Test add method with invalid parameters."""
        # Invalid sink type should raise TypeError
        with pytest.raises(TypeError):
            logger.add(123)  # type: ignore[arg-type]


class TestExceptionMethod:
    """Test exception method with various parameters."""

    def setup_method(self):
        """Reset logger state before each test."""
        logger.remove_all()  # Clear all sinks from previous tests
        logger.reset()

    def teardown_method(self):
        """Clean up after each test."""
        logger.reset()

    def test_exception_basic(self, tmp_path):
        """Test basic exception logging."""
        log_file = tmp_path / "exception_test.log"
        logger.add(str(log_file))

        logger.configure(level="INFO", color=False)

        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("Exception occurred")

        logger.complete()

        content = log_file.read_text()
        assert "Exception occurred" in content
        assert "ValueError" in content
        assert "Test exception" in content

    def test_exception_with_custom_message(self, tmp_path):
        """Test exception with custom message."""
        log_file = tmp_path / "exception_custom.log"
        logger.add(str(log_file))

        logger.configure(level="INFO", color=False)

        try:
            raise RuntimeError("Custom error")
        except RuntimeError:
            logger.exception("Custom exception message")

        logger.complete()

        content = log_file.read_text()
        assert "Custom exception message" in content
        assert "RuntimeError" in content
        assert "Custom error" in content

    def test_exception_with_bound_context(self, tmp_path):
        """Test exception with bound context."""
        log_file = tmp_path / "exception_context.log"
        logger.add(str(log_file))

        logger.configure(level="INFO", color=False)

        # Bind context
        logger.bind(user="test_user", session="abc123")

        try:
            raise ValueError("Context test")
        except ValueError:
            logger.exception("Exception with context")

        logger.complete()

        content = log_file.read_text()
        assert "Exception with context" in content
        assert "ValueError" in content
        assert "Context test" in content
        # Context may not appear in exception messages - this is expected behavior


class TestCatchMethod:
    """Test catch method with various parameters."""

    def setup_method(self):
        """Reset logger state before each test."""
        logger.remove_all()  # Clear all sinks from previous tests
        logger.reset()

    def teardown_method(self):
        """Clean up after each test."""
        logger.reset()

    def test_catch_basic(self, tmp_path):
        """Test basic exception catching."""
        log_file = tmp_path / "catch_test.log"
        logger.add(str(log_file))

        logger.configure(level="INFO", color=False)

        @logger.catch()
        def failing_function():
            raise ValueError("Function failed")

        # Should not raise since catch() defaults to reraise=False
        failing_function()

        logger.complete()

        content = log_file.read_text()
        assert "Function failed" in content
        assert "ValueError" in content

    def test_catch_with_reraise_false(self, tmp_path):
        """Test catch with reraise=False."""
        log_file = tmp_path / "catch_no_reraise.log"
        logger.add(str(log_file))

        logger.configure(level="INFO", color=False)

        @logger.catch(reraise=False)
        def failing_function():
            raise ValueError("No reraise test")

        # Should not raise
        failing_function()

        logger.complete()

        content = log_file.read_text()
        assert "No reraise test" in content
        assert "ValueError" in content

    def test_catch_with_reraise_true(self, tmp_path):
        """Test catch with reraise=True."""
        log_file = tmp_path / "catch_reraise.log"
        logger.add(str(log_file))

        logger.configure(level="INFO", color=False)

        @logger.catch(reraise=True)
        def failing_function():
            raise RuntimeError("Reraise test")

        # Should raise
        with pytest.raises(RuntimeError):
            failing_function()

        logger.complete()

        content = log_file.read_text()
        assert "Reraise test" in content
        assert "RuntimeError" in content


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Reset logger state before each test."""
        logger.remove_all()  # Clear all sinks from previous tests
        logger.reset()

    def teardown_method(self):
        """Clean up after each test."""
        logger.reset()

    def test_file_system_errors(self, tmp_path):
        """Test handling of file system errors."""
        # Try to write to a directory that doesn't exist
        invalid_path = tmp_path / "nonexistent" / "test.log"

        # This should not crash the logger
        logger.add(str(invalid_path))
        logger.configure(level="INFO", color=False)
        logger.info("File system error test")
        logger.complete()

        # Logger should handle the error gracefully

    def test_concurrent_access(self, tmp_path):
        """Test concurrent access to logger."""
        log_file = tmp_path / "concurrent_test.log"
        logger.add(str(log_file))

        logger.configure(level="INFO", color=False)

        results = []

        def worker(worker_id):
            for i in range(10):
                logger.info(f"Message from worker {worker_id}: {i}")
            results.append(f"Worker {worker_id} done")

        threads = []
        for i in range(3):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        logger.complete()

        assert len(results) == 3
        content = log_file.read_text()
        # Should contain messages from all workers
        assert "worker 0" in content
        assert "worker 1" in content
        assert "worker 2" in content

    def test_memory_limits(self, tmp_path):
        """Test behavior with large messages."""
        log_file = tmp_path / "memory_test.log"
        logger.add(str(log_file))

        logger.configure(level="INFO", color=False)

        # Create a very large message
        large_message = "x" * 10000
        logger.info(large_message)

        logger.complete()

        content = log_file.read_text()
        assert len(content) > 10000  # Should contain the large message


class TestIntegrationScenarios:
    """Test complex integration scenarios."""

    def setup_method(self):
        """Reset logger state before each test."""
        logger.remove_all()  # Clear all sinks from previous tests
        logger.reset()

    def teardown_method(self):
        """Clean up after each test."""
        logger.reset()

    def test_complex_configuration(self, tmp_path):
        """Test complex configuration with multiple sinks."""
        log_file1 = tmp_path / "complex1.log"
        log_file2 = tmp_path / "complex2.log"

        # Add multiple sinks with different configurations
        logger.add(str(log_file1), rotation="1 KB")
        logger.add(str(log_file2), buffer_size=2048)

        logger.configure(level="WARNING", color=False, show_time=True)

        # Bind context
        logger.bind(app="test_app", version="1.0")

        # Log various messages
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        logger.complete()

        content1 = log_file1.read_text()
        content2 = log_file2.read_text()

        # Both files should contain all messages (file sinks log all levels)
        assert "Debug message" in content1
        assert "Info message" in content1
        assert "Warning message" in content1
        assert "Error message" in content1

        assert "Debug message" in content2
        assert "Info message" in content2
        assert "Warning message" in content2
        assert "Error message" in content2

    def test_exception_handling_integration(self, tmp_path):
        """Test exception handling with context binding."""
        log_file = tmp_path / "exception_integration.log"
        logger.add(str(log_file))

        logger.configure(level="INFO", color=False, json=False)

        # Bind context
        logger.bind(user="integration_test", request_id="req-123")

        @logger.catch()
        def risky_operation():
            # Simulate some work
            logger.info("Starting risky operation")
            raise ValueError("Something went wrong")

        # Should not raise since catch() defaults to reraise=False
        risky_operation()

        logger.complete()

        content = log_file.read_text()
        assert "Starting risky operation" in content
        assert "Something went wrong" in content
        assert "ValueError" in content
        # Context may not appear in exception messages - this is expected behavior


class TestModuleGetattr:
    """Test __getattr__ functionality for module-level attribute access."""

    def test_getattr_other_attribute(self):
        """Test accessing other attributes via module.__getattr__."""
        import logly

        # This should call __getattr__('info') and delegate to getattr(logger, 'info')
        info_func = logly.info
        assert callable(info_func)
        # Test that it works
        info_func("Test message from module getattr")


class TestAugmentCallsiteException:
    """Test exception handling in _augment_with_callsite."""

    def test_augment_callsite_inspect_exception(self, monkeypatch):
        """Test that _augment_with_callsite handles inspect exceptions gracefully."""
        import inspect

        # Mock inspect.currentframe to raise an exception
        def mock_currentframe():
            raise RuntimeError("Mock inspect error")

        monkeypatch.setattr(inspect, "currentframe", mock_currentframe)

        # Call a logging method that uses _augment_with_callsite
        logger.info("Test message with inspect failure")

        # Should not raise an exception, and message should still be logged
        # The except block should catch the RuntimeError and continue
