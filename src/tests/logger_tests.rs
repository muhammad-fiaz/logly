use crate::logger::PyLogger;
use pyo3::prelude::*;

fn create_test_logger() -> PyLogger {
    PyLogger::new(true, false, None)
}

#[cfg(test)]
mod logging_tests {
    use super::*;

    #[test]
    fn test_basic_configuration() {
        Python::initialize();

        Python::attach(|py| {
            let logger = create_test_logger();
            let result = logger.configure(
                py, "INFO", true, None, false, false, true, true, true, true, false, false, None,
                None, None, None, None, true, None, false,
            );
            assert!(result.is_ok());
        });
    }

    #[test]
    fn test_configure_with_custom_level() {
        Python::initialize();

        Python::attach(|py| {
            let logger = create_test_logger();
            let result = logger.configure(
                py, "DEBUG", true, None, false, false, true, true, true, true, false, false, None,
                None, None, None, None, true, None, false,
            );
            assert!(result.is_ok());
        });
    }

    #[test]
    fn test_configure_with_invalid_level() {
        Python::initialize();

        Python::attach(|py| {
            let logger = create_test_logger();
            let result = logger.configure(
                py, "INVALID", true, None, false, false, true, true, true, true, false, false,
                None, None, None, None, None, true, None, false,
            );
            assert!(result.is_err());
        });
    }

    #[test]
    fn test_configure_with_color_disabled() {
        Python::initialize();

        Python::attach(|py| {
            let logger = create_test_logger();
            let result = logger.configure(
                py, "INFO", false, None, false, false, true, true, true, true, false, false, None,
                None, None, None, None, true, None, false,
            );
            assert!(result.is_ok());
        });
    }

    #[test]
    fn test_configure_with_json_enabled() {
        Python::initialize();

        Python::attach(|py| {
            let logger = create_test_logger();
            let result = logger.configure(
                py, "INFO", true, None, true, false, true, true, true, true, false, false, None,
                None, None, None, None, true, None, false,
            );
            assert!(result.is_ok());
        });
    }

    #[test]
    fn test_configure_with_pretty_json() {
        Python::initialize();

        Python::attach(|py| {
            let logger = create_test_logger();
            let result = logger.configure(
                py, "INFO", true, None, true, true, true, true, true, true, false, false, None,
                None, None, None, None, true, None, false,
            );
            assert!(result.is_ok());
        });
    }

    #[test]
    fn test_configure_without_console() {
        Python::initialize();

        Python::attach(|py| {
            let logger = create_test_logger();
            let result = logger.configure(
                py, "INFO", true, None, false, false, false, true, true, true, false, false, None,
                None, None, None, None, true, None, false,
            );
            assert!(result.is_ok());
        });
    }

    #[test]
    fn test_configure_without_time() {
        Python::initialize();

        Python::attach(|py| {
            let logger = create_test_logger();
            let result = logger.configure(
                py, "INFO", true, None, false, false, true, false, true, true, false, false, None,
                None, None, None, None, true, None, false,
            );
            assert!(result.is_ok());
        });
    }

    #[test]
    fn test_configure_without_module() {
        Python::initialize();

        Python::attach(|py| {
            let logger = create_test_logger();
            let result = logger.configure(
                py, "INFO", true, None, false, false, true, true, false, true, false, false, None,
                None, None, None, None, true, None, false,
            );
            assert!(result.is_ok());
        });
    }

    #[test]
    fn test_configure_without_function() {
        Python::initialize();

        Python::attach(|py| {
            let logger = create_test_logger();
            let result = logger.configure(
                py, "INFO", true, None, false, false, true, true, true, false, false, false, None,
                None, None, None, None, true, None, false,
            );
            assert!(result.is_ok());
        });
    }

    #[test]
    fn test_configure_with_filename() {
        Python::initialize();

        Python::attach(|py| {
            let logger = create_test_logger();
            let result = logger.configure(
                py, "INFO", true, None, false, false, true, true, true, true, true, false, None,
                None, None, None, None, true, None, false,
            );
            assert!(result.is_ok());
        });
    }

    #[test]
    fn test_configure_with_lineno() {
        Python::initialize();

        Python::attach(|py| {
            let logger = create_test_logger();
            let result = logger.configure(
                py, "INFO", true, None, false, false, true, true, true, true, false, true, None,
                None, None, None, None, true, None, false,
            );
            assert!(result.is_ok());
        });
    }

    #[test]
    fn test_configure_with_debug_level() {
        Python::initialize();

        Python::attach(|py| {
            let logger = create_test_logger();
            let result = logger.configure(
                py, "DEBUG", false, None, true, false, false, false, false, false, true, true,
                None, None, None, None, None, true, None, false,
            );
            assert!(result.is_ok());
        });
    }
}
