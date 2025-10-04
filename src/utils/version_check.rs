use std::sync::atomic::{AtomicBool, Ordering};
use std::thread;
use std::time::Duration;

static VERSION_CHECK_DONE: AtomicBool = AtomicBool::new(false);
const CURRENT_VERSION: &str = env!("CARGO_PKG_VERSION");
const PYPI_API_URL: &str = "https://pypi.org/pypi/logly/json";
const CHECK_TIMEOUT_MS: u64 = 2000;

/// Performs asynchronous version check against PyPI.
/// Spawns a background thread to avoid blocking the main application.
/// Only runs once per process lifetime.
pub fn check_version_async() {
    if VERSION_CHECK_DONE.swap(true, Ordering::Relaxed) {
        return;
    }

    thread::spawn(|| {
        if let Some(latest) = fetch_latest_version()
            && is_newer_version(&latest, CURRENT_VERSION)
        {
            print_upgrade_warning(&latest);
        }
    });
}

/// Fetches the latest version from PyPI using HTTP API.
/// Returns None if the request fails or times out.
fn fetch_latest_version() -> Option<String> {
    let config = ureq::Agent::config_builder()
        .timeout_global(Some(Duration::from_millis(CHECK_TIMEOUT_MS)))
        .build();

    let agent: ureq::Agent = config.into();

    match agent.get(PYPI_API_URL).call() {
        Ok(mut response) => {
            if let Ok(body) = response.body_mut().read_to_string()
                && let Ok(json) = serde_json::from_str::<serde_json::Value>(&body)
            {
                return json
                    .get("info")
                    .and_then(|info| info.get("version"))
                    .and_then(|v| v.as_str())
                    .map(|s| s.to_string());
            }
            None
        }
        Err(_) => None,
    }
}

/// Compares semantic versions to determine if an update is available.
/// Returns true if latest version is newer than current version.
fn is_newer_version(latest: &str, current: &str) -> bool {
    let parse_version =
        |v: &str| -> Vec<u32> { v.split('.').filter_map(|s| s.parse::<u32>().ok()).collect() };

    let latest_parts = parse_version(latest);
    let current_parts = parse_version(current);

    for i in 0..latest_parts.len().max(current_parts.len()) {
        let l = latest_parts.get(i).unwrap_or(&0);
        let c = current_parts.get(i).unwrap_or(&0);

        if l > c {
            return true;
        } else if l < c {
            return false;
        }
    }

    false
}

/// Prints a formatted warning message to stderr with version information.
/// Uses ANSI color codes for better visibility.
fn print_upgrade_warning(latest_version: &str) {
    eprintln!("\n\x1b[33m⚠ Warning: A new version of Logly is available!\x1b[0m");
    eprintln!("\x1b[33m  Current version: {}\x1b[0m", CURRENT_VERSION);
    eprintln!("\x1b[33m  Latest version:  {}\x1b[0m", latest_version);
    eprintln!("\x1b[33m  Upgrade with: pip install --upgrade logly\x1b[0m\n");
}
