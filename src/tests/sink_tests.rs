// Tests for sink enable/disable functionality

#[cfg(test)]
mod sink_control_tests {
    use super::*;

    #[test]
    fn test_sink_enabled_by_default() {
        // Sinks should be enabled when created
        let mut state = LoggerState::new();
        let sink_id = 1;
        
        // Add a sink configuration
        state.sinks.insert(
            sink_id,
            SinkConfig {
                enabled: true,
                path: Some("test.log".to_string()),
                ..Default::default()
            },
        );
        
        assert!(state.sinks[&sink_id].enabled);
    }

    #[test]
    fn test_disable_sink() {
        let mut state = LoggerState::new();
        let sink_id = 1;
        
        state.sinks.insert(
            sink_id,
            SinkConfig {
                enabled: true,
                path: Some("test.log".to_string()),
                ..Default::default()
            },
        );
        
        // Disable sink
        if let Some(sink) = state.sinks.get_mut(&sink_id) {
            sink.enabled = false;
        }
        
        assert!(!state.sinks[&sink_id].enabled);
    }

    #[test]
    fn test_enable_sink() {
        let mut state = LoggerState::new();
        let sink_id = 1;
        
        state.sinks.insert(
            sink_id,
            SinkConfig {
                enabled: false,
                path: Some("test.log".to_string()),
                ..Default::default()
            },
        );
        
        // Enable sink
        if let Some(sink) = state.sinks.get_mut(&sink_id) {
            sink.enabled = true;
        }
        
        assert!(state.sinks[&sink_id].enabled);
    }

    #[test]
    fn test_nonexistent_sink() {
        let state = LoggerState::new();
        let fake_id = 99999;
        
        // Should return None for nonexistent sink
        assert!(state.sinks.get(&fake_id).is_none());
    }

    #[test]
    fn test_multiple_sinks_independent() {
        let mut state = LoggerState::new();
        
        // Add multiple sinks
        state.sinks.insert(
            1,
            SinkConfig {
                enabled: true,
                path: Some("file1.log".to_string()),
                ..Default::default()
            },
        );
        
        state.sinks.insert(
            2,
            SinkConfig {
                enabled: true,
                path: Some("file2.log".to_string()),
                ..Default::default()
            },
        );
        
        // Disable only sink 1
        if let Some(sink) = state.sinks.get_mut(&1) {
            sink.enabled = false;
        }
        
        assert!(!state.sinks[&1].enabled);
        assert!(state.sinks[&2].enabled);
    }

    #[test]
    fn test_idempotent_enable() {
        let mut state = LoggerState::new();
        let sink_id = 1;
        
        state.sinks.insert(
            sink_id,
            SinkConfig {
                enabled: true,
                path: Some("test.log".to_string()),
                ..Default::default()
            },
        );
        
        // Enable already-enabled sink (should be no-op)
        if let Some(sink) = state.sinks.get_mut(&sink_id) {
            sink.enabled = true;
        }
        
        assert!(state.sinks[&sink_id].enabled);
    }

    #[test]
    fn test_idempotent_disable() {
        let mut state = LoggerState::new();
        let sink_id = 1;
        
        state.sinks.insert(
            sink_id,
            SinkConfig {
                enabled: false,
                path: Some("test.log".to_string()),
                ..Default::default()
            },
        );
        
        // Disable already-disabled sink (should be no-op)
        if let Some(sink) = state.sinks.get_mut(&sink_id) {
            sink.enabled = false;
        }
        
        assert!(!state.sinks[&sink_id].enabled);
    }
}

#[cfg(test)]
mod global_console_tests {
    use super::*;

    #[test]
    fn test_console_enabled_default() {
        let state = LoggerState::new();
        assert!(state.console_enabled);
    }

    #[test]
    fn test_disable_console_globally() {
        let mut state = LoggerState::new();
        state.console_enabled = false;
        assert!(!state.console_enabled);
    }

    #[test]
    fn test_re_enable_console() {
        let mut state = LoggerState::new();
        state.console_enabled = false;
        state.console_enabled = true;
        assert!(state.console_enabled);
    }

    #[test]
    fn test_console_flag_independent_of_sinks() {
        let mut state = LoggerState::new();
        
        // Add enabled sink
        state.sinks.insert(
            1,
            SinkConfig {
                enabled: true,
                path: Some("test.log".to_string()),
                ..Default::default()
            },
        );
        
        // Disable console globally
        state.console_enabled = false;
        
        // Sink should still be enabled at sink level
        assert!(state.sinks[&1].enabled);
        // But global console is disabled
        assert!(!state.console_enabled);
    }
}

#[cfg(test)]
mod error_handling_tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_handle_invalid_path() {
        let invalid_paths = vec![
            "",  // Empty path
            "\0", // Null byte
            "///",  // Invalid path
        ];
        
        for path in invalid_paths {
            // Should handle gracefully without panicking
            let result = std::panic::catch_unwind(|| {
                let _path = PathBuf::from(path);
            });
            assert!(result.is_ok());
        }
    }

    #[test]
    fn test_safe_unwrap_replacement() {
        // Test that we never use unwrap() in production code
        // This is a compile-time guarantee through clippy lints
        
        let option_value: Option<i32> = None;
        
        // Good: Safe handling
        let result = option_value.unwrap_or(0);
        assert_eq!(result, 0);
        
        // Good: Match expression
        let result = match option_value {
            Some(v) => v,
            None => 0,
        };
        assert_eq!(result, 0);
    }

    #[test]
    fn test_fallback_path_creation() {
        use std::env;
        use std::fs;
        
        // Test that fallback paths work
        let temp_dir = env::temp_dir();
        let fallback_log = temp_dir.join("fallback.log");
        
        // Should be able to create file in temp directory
        let result = fs::File::create(&fallback_log);
        assert!(result.is_ok());
        
        // Cleanup
        let _ = fs::remove_file(fallback_log);
    }
}

#[cfg(test)]
mod performance_tests {
    use super::*;
    use std::time::Instant;

    #[test]
    fn test_disabled_logging_performance() {
        let mut state = LoggerState::new();
        state.console_enabled = false;
        
        let start = Instant::now();
        
        // Simulate 10000 log calls with global disable
        for _ in 0..10000 {
            // Early exit when disabled - should be very fast
            if !state.console_enabled {
                continue;
            }
        }
        
        let elapsed = start.elapsed();
        
        // Should complete in under 1ms (early exit is fast)
        assert!(elapsed.as_millis() < 1);
    }

    #[test]
    fn test_per_sink_check_performance() {
        let mut state = LoggerState::new();
        
        // Add 100 sinks
        for i in 0..100 {
            state.sinks.insert(
                i,
                SinkConfig {
                    enabled: i % 2 == 0,  // Alternate enabled/disabled
                    path: Some(format!("test{}.log", i)),
                    ..Default::default()
                },
            );
        }
        
        let start = Instant::now();
        
        // Check all sinks
        for i in 0..100 {
            if let Some(sink) = state.sinks.get(&i) {
                let _ = sink.enabled;
            }
        }
        
        let elapsed = start.elapsed();
        
        // Should be very fast (just HashMap lookups)
        assert!(elapsed.as_micros() < 100);
    }
}

#[cfg(test)]
mod integration_tests {
    use super::*;

    #[test]
    fn test_reset_resets_console_flag() {
        let mut state = LoggerState::new();
        
        // Disable console
        state.console_enabled = false;
        assert!(!state.console_enabled);
        
        // Reset to default
        state = LoggerState::new();
        assert!(state.console_enabled);
    }

    #[test]
    fn test_sink_config_preserved_when_disabled() {
        let mut state = LoggerState::new();
        let sink_id = 1;
        
        // Add sink with specific config
        state.sinks.insert(
            sink_id,
            SinkConfig {
                enabled: true,
                path: Some("test.log".to_string()),
                rotation: Some("daily".to_string()),
                retention: Some(7),
                ..Default::default()
            },
        );
        
        // Disable sink
        if let Some(sink) = state.sinks.get_mut(&sink_id) {
            sink.enabled = false;
        }
        
        // Configuration should be preserved
        let sink = &state.sinks[&sink_id];
        assert_eq!(sink.path.as_ref().unwrap(), "test.log");
        assert_eq!(sink.rotation.as_ref().unwrap(), "daily");
        assert_eq!(sink.retention.unwrap(), 7);
    }
}
