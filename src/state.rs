use once_cell::sync::Lazy;
use std::sync::Mutex;
use std::thread::JoinHandle;
use tracing_subscriber::filter::LevelFilter;
use std::io::Write;
use std::sync::mpsc::Sender;

pub struct LoggerState {
    pub inited: bool,
    pub console_enabled: bool,
    pub level_filter: LevelFilter,
    pub color: bool,
    pub format_json: bool,
    pub pretty_json: bool,
    pub file_path: Option<String>,
    pub file_rotation: Option<String>,
    // file_writer is a boxed writer that may implement simple rotation (date inserted before extension)
    pub file_writer: Option<Box<dyn Write + Send>>,
    // how to place the date when rotation is enabled: "before_ext" (default) or "prefix"
    pub file_date_style: Option<String>,
    // whether to include date in rotated filenames (true by default). If false, rotation is effectively disabled.
    pub file_date_enabled: bool,
    // retain at most this many rotated files (count-based retention)
    pub retention_count: Option<usize>,
    // optional async channel for non-blocking file writes
    pub async_sender: Option<Sender<String>>,
    pub async_write: bool,
    pub async_handle: Option<JoinHandle<()>>,
    // simple per-sink filters (file sink)
    pub filter_min_level: Option<LevelFilter>,
    pub filter_module: Option<String>,
    pub filter_function: Option<String>,
}

impl Default for LoggerState {
    fn default() -> Self {
        Self {
            inited: false,
            console_enabled: true,
            level_filter: LevelFilter::INFO,
            color: true,
            format_json: false,
            pretty_json: false,
            file_path: None,
            file_rotation: None,
            file_writer: None,
            file_date_style: None,
            file_date_enabled: false,
            retention_count: None,
            async_sender: None,
            async_write: true,
            async_handle: None,
            filter_min_level: None,
            filter_module: None,
            filter_function: None,
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
