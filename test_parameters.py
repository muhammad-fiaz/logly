#!/usr/bin/env python3
"""Test to verify all parameters are correctly defined and working."""

from logly import logger


def test_pylogger_init_parameters():
    """Test PyLogger.__init__() parameters."""
    print("Testing PyLogger initialization parameters...")

    # Test all three parameters
    custom_logger = logger(
        auto_update_check=False, internal_debug=True, debug_log_path="test_params_debug.log"
    )

    print("✅ PyLogger accepts: auto_update_check, internal_debug, debug_log_path")

    # Configure and use it
    custom_logger.configure(level="DEBUG")
    custom_logger.info("Test message from custom logger")

    print("✅ Custom logger works correctly")
    return custom_logger


def test_logger_proxy_init_parameters():
    """Test _LoggerProxy.__init__() parameters."""
    print("\nTesting _LoggerProxy initialization parameters...")

    from logly._logly import PyLogger

    # Create a PyLogger instance
    py_logger = PyLogger(auto_update_check=False, internal_debug=False, debug_log_path=None)

    # Create _LoggerProxy with correct parameters
    from logly import _LoggerProxy

    proxy = _LoggerProxy(
        inner=py_logger,
        auto_configure=False,  # Don't auto-configure
        internal_debug=False,
        debug_log_path=None,
    )

    print("✅ _LoggerProxy accepts: inner, auto_configure, internal_debug, debug_log_path")

    # Manually configure
    proxy.configure(level="INFO")
    proxy.info("Test message from proxy")

    print("✅ _LoggerProxy works correctly")
    return proxy


def test_parameter_alignment():
    """Verify parameter alignment between stub file and implementation."""
    print("\nVerifying parameters work correctly...")

    from logly._logly import PyLogger

    # Test all PyLogger.__init__ parameters work (from stub file)
    try:
        p1 = PyLogger()  # All defaults
        p2 = PyLogger(auto_update_check=False)
        p3 = PyLogger(auto_update_check=False, internal_debug=True)
        p4 = PyLogger(auto_update_check=False, internal_debug=True, debug_log_path="test.log")
        print("✅ PyLogger.__init__ accepts all parameters correctly")
    except Exception as e:
        raise AssertionError(f"PyLogger.__init__ parameter test failed: {e}")

    # Test _LoggerProxy.__init__ parameters
    from logly import _LoggerProxy

    try:
        proxy1 = _LoggerProxy(p1, auto_configure=False)
        proxy2 = _LoggerProxy(p1, auto_configure=True, internal_debug=False)
        proxy3 = _LoggerProxy(
            p1, auto_configure=True, internal_debug=True, debug_log_path="test.log"
        )
        print("✅ _LoggerProxy.__init__ accepts all parameters correctly")
    except Exception as e:
        raise AssertionError(f"_LoggerProxy.__init__ parameter test failed: {e}")

    print("\n✅ All parameters are correctly aligned and functional!")


def main():
    print("=" * 60)
    print("PARAMETER VERIFICATION TEST")
    print("=" * 60)

    try:
        test_pylogger_init_parameters()
        test_logger_proxy_init_parameters()
        test_parameter_alignment()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
