use once_cell::sync::Lazy;
use std::sync::Mutex;
use tracing_appender::rolling::RollingFileAppender;
use tracing_subscriber::filter::LevelFilter;

pub struct LoggerState {
    pub inited: bool,
    pub console_enabled: bool,
    pub level_filter: LevelFilter,
    pub color: bool,
    pub format_json: bool,
    pub file_path: Option<String>,
    pub file_rotation: Option<String>,
    pub file_writer: Option<RollingFileAppender>,
}

impl Default for LoggerState {
    fn default() -> Self {
        Self {
            inited: false,
            console_enabled: true,
            level_filter: LevelFilter::INFO,
            color: true,
            format_json: false,
            file_path: None,
            file_rotation: None,
            file_writer: None,
        }
    }
}

static LOGGER: Lazy<Mutex<LoggerState>> = Lazy::new(|| Mutex::new(LoggerState::default()));

pub fn with_state<R>(f: impl FnOnce(&mut LoggerState) -> R) -> R {
    let mut guard = LOGGER.lock().expect("logger state poisoned");
    f(&mut guard)
}

pub fn reset_state() {
    with_state(|s| {
        *s = LoggerState::default();
    });
}
