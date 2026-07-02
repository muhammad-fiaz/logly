//! File rotation policies for log sinks.
//!
//! This module implements a flexible rotation system that supports multiple
//! rotation strategies:
//!
//! - **Size-based**: Rotate when the file exceeds a byte threshold.
//! - **Time-based (interval)**: Rotate after a fixed elapsed duration.
//! - **Clock-based**: Rotate at a specific time of day (`HH:MM`).
//! - **Weekday-based**: Rotate on a specific day of the week.
//!
//! Rotation is non-destructive — the current file is renamed with a timestamp
//! suffix, and a new file is created. The [`OverwriteMode`] controls whether
//! subsequent writes truncate or append. Rotation events can be consumed by
//! the `compress` and `schedule` crates for automated archiving.
//!
//! # Examples
//!
//! ```rust
//! use rotate::{RotationPolicy, check_rotation, RotationAction};
//! use std::path::Path;
//!
//! let action = check_rotation(
//!     Path::new("app.log"),
//!     &RotationPolicy::SizeBytes(10 * 1024 * 1024),
//!     0,
//! );
//! ```

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use chrono::{Datelike, Timelike};
use error::LoglyResult;
use std::path::{Path, PathBuf};
use std::time::SystemTime;

/// Day of week for weekday rotation.
///
/// Uses ISO 8601 numbering: `0` = Monday, `6` = Sunday.
pub type Weekday = u8;

/// Defines when and how a log file should be rotated.
///
/// Each variant encodes a different rotation trigger. The engine evaluates
/// the policy against the current file state to determine if rotation is
/// required.
#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub enum RotationPolicy {
    /// Rotation is disabled.
    #[default]
    Never,
    /// Rotate when a file reaches this many bytes.
    SizeBytes(u64),
    /// Rotate after this many seconds.
    IntervalSeconds(u64),
    /// Rotate at a specific time of day (HH:MM format, 24-hour).
    ClockRotation(String),
    /// Rotate on a specific day of the week (0=Monday through 6=Sunday).
    WeekdayRotation(Weekday),
    /// Rotate on a specific day of the week at a specific time.
    /// Tuple of `(weekday_index, time_string)`.
    WeekdayClockRotation(u8, String),
}

impl std::fmt::Display for RotationPolicy {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Never => write!(f, "Never"),
            Self::SizeBytes(n) => write!(f, "SizeBytes({n})"),
            Self::IntervalSeconds(s) => write!(f, "IntervalSeconds({s})"),
            Self::ClockRotation(s) => write!(f, "ClockRotation(\"{s}\")"),
            Self::WeekdayRotation(d) => write!(f, "WeekdayRotation({d})"),
            Self::WeekdayClockRotation(d, t) => {
                write!(f, "WeekdayClockRotation({d}, \"{t}\")")
            }
        }
    }
}

/// Controls file behavior after a rotation event.
///
/// Determines whether the original file is truncated and reused, or whether
/// a new file is appended to.
#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub enum OverwriteMode {
    /// Truncate the original file after rotation.
    Overwrite,
    /// Keep appending to a new file after rotation.
    #[default]
    Append,
}

impl std::fmt::Display for OverwriteMode {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Overwrite => write!(f, "Overwrite"),
            Self::Append => write!(f, "Append"),
        }
    }
}

/// Result of evaluating a rotation policy against a file.
///
/// Returned by [`check_rotation`] to indicate whether rotation should occur.
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum RotationAction {
    /// No rotation needed.
    None,
    /// Rotation is needed; the current file should be moved to the given path.
    RotateTo(PathBuf),
}

/// Parses a clock rotation specification string into `(hours, minutes)`.
///
/// The spec must be in `HH:MM` format (24-hour clock). Hours must be 0–23
/// and minutes must be 0–59.
///
/// # Arguments
///
/// * `spec` - A time string in `"HH:MM"` format.
///
/// # Returns
///
/// `Some((hours, minutes))` if the spec is valid, `None` otherwise.
///
/// # Examples
///
/// ```rust
/// use rotate::parse_clock_spec;
///
/// assert_eq!(parse_clock_spec("00:00"), Some((0, 0)));
/// assert_eq!(parse_clock_spec("23:59"), Some((23, 59)));
/// assert_eq!(parse_clock_spec("24:00"), None);
/// ```
#[must_use]
pub fn parse_clock_spec(spec: &str) -> Option<(u32, u32)> {
    let parts: Vec<&str> = spec.split(':').collect();
    if parts.len() != 2 {
        return None;
    }
    let hours = parts[0].parse::<u32>().ok()?;
    let minutes = parts[1].parse::<u32>().ok()?;
    if hours > 23 || minutes > 59 {
        return None;
    }
    Some((hours, minutes))
}

/// Evaluates whether a file requires rotation under the given policy.
///
/// For size-based policies, rotation triggers when the current file size
/// plus `next_message_bytes` exceeds the threshold. For time-based policies,
/// rotation triggers when the file's last modification time exceeds the
/// interval. For clock-based and weekday-based policies, rotation triggers
/// when the current time matches the target and the file is sufficiently old.
///
/// # Arguments
///
/// * `path` - Path to the log file to check.
/// * `policy` - The rotation policy to evaluate against.
/// * `next_message_bytes` - Size in bytes of the message about to be written.
///
/// # Returns
///
/// * `Ok(RotationAction::None)` — no rotation needed.
/// * `Ok(RotationAction::RotateTo(path))` — rotation needed; the file should
///   be moved to the returned path.
///
/// # Errors
///
/// Returns an error if file metadata cannot be read.
///
/// # Examples
///
/// ```rust
/// use rotate::{RotationPolicy, check_rotation, RotationAction};
/// use std::path::Path;
///
/// let action = check_rotation(Path::new("/nonexistent"), &RotationPolicy::Never, 100);
/// assert!(matches!(action, Ok(RotationAction::None)));
/// ```
pub fn check_rotation(
    path: &Path,
    policy: &RotationPolicy,
    next_message_bytes: usize,
) -> LoglyResult<RotationAction> {
    match policy {
        RotationPolicy::Never => Ok(RotationAction::None),
        RotationPolicy::SizeBytes(max_bytes) => {
            if !path.exists() {
                return Ok(RotationAction::None);
            }
            let metadata = path.metadata()?;
            if metadata.len() + next_message_bytes as u64 > *max_bytes {
                Ok(RotationAction::RotateTo(generate_rotated_path(path)))
            } else {
                Ok(RotationAction::None)
            }
        }
        RotationPolicy::IntervalSeconds(secs) => {
            if !path.exists() {
                return Ok(RotationAction::None);
            }
            let metadata = path.metadata()?;
            let modified = metadata.modified().unwrap_or_else(|_| SystemTime::now());
            let elapsed = modified.elapsed().unwrap_or_default().as_secs();
            if elapsed > *secs {
                Ok(RotationAction::RotateTo(generate_rotated_path(path)))
            } else {
                Ok(RotationAction::None)
            }
        }
        RotationPolicy::ClockRotation(spec) => {
            if !path.exists() {
                return Ok(RotationAction::None);
            }
            let Some((target_hours, target_minutes)) = parse_clock_spec(spec) else {
                return Ok(RotationAction::None);
            };
            let now = chrono::Local::now();
            let current_minutes_since_midnight = now.hour() * 60 + now.minute();
            let target_minutes_since_midnight = target_hours * 60 + target_minutes;

            if current_minutes_since_midnight >= target_minutes_since_midnight {
                let metadata = path.metadata()?;
                let modified = metadata.modified().unwrap_or_else(|_| SystemTime::now());
                let elapsed = modified.elapsed().unwrap_or_default().as_secs();
                if elapsed > 60 {
                    return Ok(RotationAction::RotateTo(generate_rotated_path(path)));
                }
            }
            Ok(RotationAction::None)
        }
        RotationPolicy::WeekdayRotation(target_day) => {
            if !path.exists() {
                return Ok(RotationAction::None);
            }
            let now = chrono::Local::now();
            #[expect(clippy::cast_possible_truncation, reason = "weekday is always 0..6")]
            let current_weekday = now.weekday().num_days_from_monday() as u8;
            if current_weekday == *target_day {
                let metadata = path.metadata()?;
                let modified = metadata.modified().unwrap_or_else(|_| SystemTime::now());
                let elapsed = modified.elapsed().unwrap_or_default().as_secs();
                if elapsed > 3600 {
                    return Ok(RotationAction::RotateTo(generate_rotated_path(path)));
                }
            }
            Ok(RotationAction::None)
        }
        RotationPolicy::WeekdayClockRotation(target_day, time_spec) => {
            if !path.exists() {
                return Ok(RotationAction::None);
            }
            let Some((target_hours, target_minutes)) = parse_clock_spec(time_spec) else {
                return Ok(RotationAction::None);
            };
            let now = chrono::Local::now();
            #[expect(clippy::cast_possible_truncation, reason = "weekday is always 0..6")]
            let current_weekday = now.weekday().num_days_from_monday() as u8;
            if current_weekday != *target_day {
                return Ok(RotationAction::None);
            }
            let current_minutes_since_midnight = now.hour() * 60 + now.minute();
            let target_minutes_since_midnight = target_hours * 60 + target_minutes;
            if current_minutes_since_midnight >= target_minutes_since_midnight {
                let metadata = path.metadata()?;
                let modified = metadata.modified().unwrap_or_else(|_| SystemTime::now());
                let elapsed = modified.elapsed().unwrap_or_default().as_secs();
                if elapsed > 60 {
                    return Ok(RotationAction::RotateTo(generate_rotated_path(path)));
                }
            }
            Ok(RotationAction::None)
        }
    }
}

/// Performs a file rotation by renaming the current file.
///
/// The file at `path` is renamed to a timestamped variant via
/// [`generate_rotated_path`]. If the file does not exist, no error is
/// returned — only the would-be rotated path.
///
/// # Arguments
///
/// * `path` - The current log file to rotate.
/// * `_mode` - The overwrite mode (currently unused; reserved for future
///   truncation semantics).
///
/// # Returns
///
/// The path of the rotated file.
///
/// # Errors
///
/// Returns an error if the rename operation fails.
///
/// # Examples
///
/// ```rust,no_run
/// use rotate::{perform_rotation, OverwriteMode};
/// use std::path::Path;
///
/// let rotated = perform_rotation(Path::new("app.log"), OverwriteMode::Append).unwrap();
/// // app.log has been moved to app.log.1234567890
/// ```
pub fn perform_rotation(path: &Path, _mode: OverwriteMode) -> LoglyResult<PathBuf> {
    let rotated = generate_rotated_path(path);
    if path.exists() {
        std::fs::rename(path, &rotated)?;
    }
    Ok(rotated)
}

/// Generates a unique rotated file path based on the current Unix timestamp.
///
/// The rotated path has the format `{stem}.{ext}.{timestamp}`. If that path
/// already exists, a numeric counter suffix is appended:
/// `{stem}.{ext}.{timestamp}.{counter}`.
///
/// # Arguments
///
/// * `path` - The original file path to derive the rotated name from.
///
/// # Returns
///
/// A [`PathBuf`] containing the rotated file path.
#[must_use]
pub fn generate_rotated_path(path: &Path) -> PathBuf {
    let timestamp = chrono_timestamp();
    let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("log");
    let stem = path
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("rotated");
    let parent = path.parent().unwrap_or_else(|| Path::new("."));
    let mut rotated = parent.join(format!("{stem}.{ext}.{timestamp}"));
    let mut counter = 1u64;
    while rotated.exists() {
        rotated = parent.join(format!("{stem}.{ext}.{timestamp}.{counter}"));
        counter += 1;
    }
    rotated
}

/// Returns a timestamp string for rotation filenames.
fn chrono_timestamp() -> String {
    let now = SystemTime::now()
        .duration_since(SystemTime::UNIX_EPOCH)
        .unwrap_or_default();
    let secs = now.as_secs();
    format!("{secs:010}")
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn never_policy_always_returns_none() {
        let action = check_rotation(Path::new("fake"), &RotationPolicy::Never, 100).unwrap();
        assert_eq!(action, RotationAction::None);
    }

    #[test]
    fn size_policy_triggers_when_exceeded() {
        let dir = std::env::temp_dir().join("logly_rotate_test_size");
        let _ = fs::create_dir_all(&dir);
        let path = dir.join("test.log");
        fs::write(&path, "hello").unwrap();

        let action = check_rotation(&path, &RotationPolicy::SizeBytes(3), 1).unwrap();
        assert!(matches!(action, RotationAction::RotateTo(_)));

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn size_policy_does_not_trigger_when_under() {
        let dir = std::env::temp_dir().join("logly_rotate_test_under");
        let _ = fs::create_dir_all(&dir);
        let path = dir.join("test.log");
        fs::write(&path, "hello").unwrap();

        let action = check_rotation(&path, &RotationPolicy::SizeBytes(1000), 0).unwrap();
        assert_eq!(action, RotationAction::None);

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn perform_rotation_renames_file() {
        let dir = std::env::temp_dir().join("logly_rotate_test_rename");
        let _ = fs::create_dir_all(&dir);
        let path = dir.join("test.log");
        fs::write(&path, "content").unwrap();

        let rotated = perform_rotation(&path, OverwriteMode::Append).unwrap();
        assert!(!path.exists());
        assert!(rotated.exists());
        assert_eq!(fs::read_to_string(&rotated).unwrap(), "content");

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn overwrite_mode_default_is_append() {
        assert_eq!(OverwriteMode::default(), OverwriteMode::Append);
    }

    #[test]
    fn size_policy_exact_boundary() {
        let dir = std::env::temp_dir().join("logly_rotate_exact_boundary");
        let _ = fs::create_dir_all(&dir);
        let path = dir.join("test.log");
        fs::write(&path, "hello").unwrap();

        let action = check_rotation(&path, &RotationPolicy::SizeBytes(5), 1).unwrap();
        assert!(matches!(action, RotationAction::RotateTo(_)));

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn size_policy_zero_message_bytes() {
        let dir = std::env::temp_dir().join("logly_rotate_zero_bytes");
        let _ = fs::create_dir_all(&dir);
        let path = dir.join("test.log");
        fs::write(&path, "hello").unwrap();

        let action = check_rotation(&path, &RotationPolicy::SizeBytes(10), 0).unwrap();
        assert_eq!(action, RotationAction::None);

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn perform_rotation_on_nonexistent_file() {
        let dir = std::env::temp_dir().join("logly_rotate_nonexistent");
        let _ = fs::create_dir_all(&dir);
        let path = dir.join("nonexistent.log");

        let rotated = perform_rotation(&path, OverwriteMode::Append).unwrap();
        assert!(!rotated.exists());

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn rotated_path_format() {
        let dir = std::env::temp_dir().join("logly_rotate_path_format");
        let _ = fs::create_dir_all(&dir);
        let path = dir.join("test.log");
        let rotated = generate_rotated_path(&path);
        let name = rotated.file_name().unwrap().to_string_lossy();
        assert!(name.starts_with("test.log."));
        assert!(!name.ends_with(".log"));

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn parse_clock_spec_valid() {
        assert_eq!(parse_clock_spec("00:00"), Some((0, 0)));
        assert_eq!(parse_clock_spec("23:59"), Some((23, 59)));
        assert_eq!(parse_clock_spec("12:30"), Some((12, 30)));
    }

    #[test]
    fn parse_clock_spec_invalid() {
        assert_eq!(parse_clock_spec(""), None);
        assert_eq!(parse_clock_spec("24:00"), None);
        assert_eq!(parse_clock_spec("12:60"), None);
        assert_eq!(parse_clock_spec("abc"), None);
        assert_eq!(parse_clock_spec("12"), None);
    }

    #[test]
    fn clock_rotation_on_nonexistent_returns_none() {
        let action = check_rotation(
            Path::new("/nonexistent"),
            &RotationPolicy::ClockRotation("00:00".to_owned()),
            0,
        )
        .unwrap();
        assert_eq!(action, RotationAction::None);
    }

    #[test]
    fn weekday_rotation_on_nonexistent_returns_none() {
        let action = check_rotation(
            Path::new("/nonexistent"),
            &RotationPolicy::WeekdayRotation(0),
            0,
        )
        .unwrap();
        assert_eq!(action, RotationAction::None);
    }

    #[test]
    fn rotation_policy_display() {
        assert_eq!(RotationPolicy::Never.to_string(), "Never");
        assert_eq!(
            RotationPolicy::SizeBytes(1024).to_string(),
            "SizeBytes(1024)"
        );
        assert_eq!(
            RotationPolicy::IntervalSeconds(3600).to_string(),
            "IntervalSeconds(3600)"
        );
        assert_eq!(
            RotationPolicy::ClockRotation("00:00".to_owned()).to_string(),
            "ClockRotation(\"00:00\")"
        );
        assert_eq!(
            RotationPolicy::WeekdayRotation(0).to_string(),
            "WeekdayRotation(0)"
        );
    }

    #[test]
    fn parse_clock_spec_12_00() {
        assert_eq!(parse_clock_spec("12:00"), Some((12, 0)));
    }

    #[test]
    fn parse_clock_spec_01_01() {
        assert_eq!(parse_clock_spec("01:01"), Some((1, 1)));
    }

    #[test]
    fn parse_clock_spec_colon_only() {
        assert_eq!(parse_clock_spec(":"), None);
    }

    #[test]
    fn parse_clock_spec_empty_parts() {
        assert_eq!(parse_clock_spec(":"), None);
    }

    #[test]
    fn parse_clock_spec_hours_24() {
        assert_eq!(parse_clock_spec("24:00"), None);
    }

    #[test]
    fn parse_clock_spec_minutes_60() {
        assert_eq!(parse_clock_spec("12:60"), None);
    }

    #[test]
    fn parse_clock_spec_trailing_colon() {
        assert_eq!(parse_clock_spec("12:30:"), None);
    }

    #[test]
    fn parse_clock_spec_leading_colon() {
        assert_eq!(parse_clock_spec(":30"), None);
    }

    #[test]
    fn size_policy_does_not_trigger_nonexistent() {
        let action = check_rotation(
            Path::new("/nonexistent/file.log"),
            &RotationPolicy::SizeBytes(100),
            0,
        )
        .unwrap();
        assert_eq!(action, RotationAction::None);
    }

    #[test]
    fn size_policy_zero_max_bytes() {
        let dir = std::env::temp_dir().join("logly_rotate_zero_max");
        let _ = fs::create_dir_all(&dir);
        let path = dir.join("test.log");
        fs::write(&path, "").unwrap();

        let action = check_rotation(&path, &RotationPolicy::SizeBytes(0), 0).unwrap();
        assert_eq!(action, RotationAction::None);

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn size_policy_exact_match() {
        let dir = std::env::temp_dir().join("logly_rotate_exact_match");
        let _ = fs::create_dir_all(&dir);
        let path = dir.join("test.log");
        fs::write(&path, "12345").unwrap();

        // File is 5 bytes, max is 5, message is 0 -> no rotation
        let action = check_rotation(&path, &RotationPolicy::SizeBytes(5), 0).unwrap();
        assert_eq!(action, RotationAction::None);

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn rotation_policy_display_all_variants() {
        assert_eq!(RotationPolicy::Never.to_string(), "Never");
        assert_eq!(RotationPolicy::SizeBytes(500).to_string(), "SizeBytes(500)");
        assert_eq!(
            RotationPolicy::IntervalSeconds(60).to_string(),
            "IntervalSeconds(60)"
        );
        assert_eq!(
            RotationPolicy::ClockRotation("23:59".to_owned()).to_string(),
            "ClockRotation(\"23:59\")"
        );
        assert_eq!(
            RotationPolicy::ClockRotation("12:00".to_owned()).to_string(),
            "ClockRotation(\"12:00\")"
        );
        for day in 0..=6u8 {
            assert_eq!(
                RotationPolicy::WeekdayRotation(day).to_string(),
                format!("WeekdayRotation({day})")
            );
        }
    }

    #[test]
    fn weekday_rotation_all_days_nonexistent() {
        for day in 0..=6u8 {
            let action = check_rotation(
                Path::new("/nonexistent"),
                &RotationPolicy::WeekdayRotation(day),
                0,
            )
            .unwrap();
            assert_eq!(action, RotationAction::None);
        }
    }

    #[test]
    fn interval_seconds_nonexistent_file() {
        let action = check_rotation(
            Path::new("/nonexistent"),
            &RotationPolicy::IntervalSeconds(60),
            0,
        )
        .unwrap();
        assert_eq!(action, RotationAction::None);
    }

    #[test]
    fn clock_rotation_invalid_spec_returns_none() {
        let action = check_rotation(
            Path::new("/nonexistent"),
            &RotationPolicy::ClockRotation("invalid".to_owned()),
            0,
        )
        .unwrap();
        assert_eq!(action, RotationAction::None);
    }

    #[test]
    fn generate_rotated_path_unique() {
        let dir = std::env::temp_dir().join("logly_rotate_unique");
        let _ = fs::create_dir_all(&dir);
        let path = dir.join("test.log");

        let p1 = generate_rotated_path(&path);
        std::thread::sleep(std::time::Duration::from_secs(1));
        let p2 = generate_rotated_path(&path);
        assert_ne!(p1, p2);

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn rotated_path_preserves_parent_dir() {
        let dir = std::env::temp_dir().join("logly_rotate_parent");
        let _ = fs::create_dir_all(&dir);
        let path = dir.join("test.log");
        let rotated = generate_rotated_path(&path);
        assert_eq!(rotated.parent(), Some(dir.as_path()));

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn perform_rotation_overwrite_mode() {
        let dir = std::env::temp_dir().join("logly_rotate_overwrite");
        let _ = fs::create_dir_all(&dir);
        let path = dir.join("test.log");
        fs::write(&path, "content").unwrap();

        let rotated = perform_rotation(&path, OverwriteMode::Overwrite).unwrap();
        assert!(!path.exists());
        assert!(rotated.exists());
        assert_eq!(fs::read_to_string(&rotated).unwrap(), "content");

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn overwrite_mode_display() {
        assert_eq!(OverwriteMode::Overwrite.to_string(), "Overwrite");
        assert_eq!(OverwriteMode::Append.to_string(), "Append");
    }

    #[test]
    fn rotation_action_equality() {
        assert_eq!(RotationAction::None, RotationAction::None);
        let path = PathBuf::from("/tmp/test.log.123");
        assert_eq!(
            RotationAction::RotateTo(path.clone()),
            RotationAction::RotateTo(path)
        );
        assert_ne!(
            RotationAction::None,
            RotationAction::RotateTo(PathBuf::from("/tmp/test"))
        );
    }

    #[test]
    fn rotation_policy_clone() {
        let policy = RotationPolicy::ClockRotation("12:00".to_owned());
        let cloned = policy.clone();
        assert_eq!(policy, cloned);
    }

    #[test]
    fn rotation_policy_default() {
        assert_eq!(RotationPolicy::default(), RotationPolicy::Never);
    }
}
