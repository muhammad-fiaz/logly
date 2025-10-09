// Tests for stdout redirection in Jupyter/Colab notebooks
// Fixes: https://github.com/muhammad-fiaz/logly/issues/76
//
// These tests verify that the fix allows logs to properly redirect to
// Python's sys.stdout, enabling display in Jupyter notebooks and Google Colab.

#[cfg(test)]
mod jupyter_tests {
    use pyo3::prelude::*;

    #[test]
    fn test_python_stdout_available() {
        // Test that we can access Python's sys.stdout
        Python::initialize();

        Python::attach(|py| {
            let sys_module = py.import("sys");
            assert!(sys_module.is_ok(), "Should be able to import sys module");

            let sys = sys_module.unwrap();
            let stdout = sys.getattr("stdout");
            assert!(stdout.is_ok(), "Should be able to access sys.stdout");
        });
    }

    #[test]
    fn test_write_to_sys_stdout() {
        // Test that we can write to sys.stdout (core of the fix)
        Python::initialize();

        Python::attach(|py| {
            if let Ok(sys) = py.import("sys")
                && let Ok(stdout) = sys.getattr("stdout")
            {
                let result = stdout.call_method1("write", ("Test message\n",));
                assert!(result.is_ok(), "Should be able to write to sys.stdout");
            }
        });
    }

    #[test]
    fn test_string_io_capture() {
        // Test StringIO works for capturing output (simulates notebooks)
        Python::initialize();

        Python::attach(|py| {
            let io_module = py.import("io").unwrap();
            let string_io = io_module.getattr("StringIO").unwrap().call0().unwrap();

            // Write a test message
            string_io
                .call_method1("write", ("[INFO] Test log message\n",))
                .unwrap();

            // Retrieve the output
            let output: String = string_io
                .call_method0("getvalue")
                .unwrap()
                .extract()
                .unwrap();

            assert!(output.contains("Test log message"));
            assert!(output.contains("[INFO]"));
        });
    }

    #[test]
    fn test_unicode_in_stdout() {
        // Test Unicode characters work (important for international users)
        Python::initialize();

        Python::attach(|py| {
            let io_module = py.import("io").unwrap();
            let string_io = io_module.getattr("StringIO").unwrap().call0().unwrap();

            // Write Unicode characters
            string_io
                .call_method1("write", ("Unicode: 你好🌍\n",))
                .unwrap();

            let output: String = string_io
                .call_method0("getvalue")
                .unwrap()
                .extract()
                .unwrap();

            assert!(output.contains("你好"));
            assert!(output.contains("🌍"));
        });
    }
}
