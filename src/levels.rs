use tracing::Level;
use tracing_subscriber::filter::LevelFilter;

pub fn to_level(name: &str) -> Option<Level> {
    match name.to_ascii_lowercase().as_str() {
        "trace" => Some(Level::TRACE),
        "debug" => Some(Level::DEBUG),
        "info" | "success" => Some(Level::INFO),
        "warn" | "warning" => Some(Level::WARN),
        "error" | "critical" | "fatal" => Some(Level::ERROR),
        _ => None,
    }
}

pub fn to_filter(level: Level) -> LevelFilter {
    level.into()
}

pub fn level_to_str(level: Level) -> &'static str {
    match level {
        Level::TRACE => "TRACE",
        Level::DEBUG => "DEBUG",
        Level::INFO => "INFO",
        Level::WARN => "WARN",
        Level::ERROR => "ERROR",
    }
}
