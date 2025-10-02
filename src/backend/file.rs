use std::fs::{File, OpenOptions};
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::sync::Arc;

use chrono::Utc;
use parking_lot::Mutex;

use crate::utils::levels::Rotation;

/// Parse rotation string to Rotation enum.
///
/// Converts string representations of rotation policies to the internal Rotation enum.
/// Supported values: "daily", "hourly", "minutely", "never" (default).
///
/// # Arguments
///
/// * `rotation` - Optional string specifying the rotation policy
///
/// # Returns
///
/// The corresponding Rotation enum value
pub fn rotation_from_str(rotation: Option<&str>) -> Rotation {
    match rotation.unwrap_or("never") {
        "daily" => Rotation::DAILY,
        "hourly" => Rotation::HOURLY,
        "minutely" => Rotation::MINUTELY,
        _ => Rotation::NEVER,
    }
}

/// Parse size strings like "5KB", "10MB", "1GB" into bytes
pub fn parse_size_limit(size_str: Option<&str>) -> Option<u64> {
    size_str.and_then(|s| {
        let s = s.trim();
        if s.is_empty() {
            return None;
        }

        // Find where the number ends and unit begins
        let mut num_end = 0;
        for (i, c) in s.chars().enumerate() {
            if !c.is_ascii_digit() {
                num_end = i;
                break;
            }
            num_end = i + 1; // Include this digit
        }

        if num_end == 0 {
            return None; // No number found
        }

        let num_str = &s[..num_end];
        let unit = s[num_end..].trim().to_uppercase();

        let multiplier = match unit.as_str() {
            "B" | "" => 1,
            "KB" | "K" => 1024,
            "MB" | "M" => 1024 * 1024,
            "GB" | "G" => 1024 * 1024 * 1024,
            _ => return None, // Invalid unit
        };

        num_str.parse::<u64>().ok().map(|n| n * multiplier)
    })
}

/// A simple rolling writer that places the rotation timestamp before the file extension,
/// e.g. `app.log` -> `app.2025-08-22.log` for daily rotation. This avoids appending
/// the date after the extension which some users find unexpected.
pub struct SimpleRollingWriter {
    base_path: PathBuf,
    rotation: Rotation,
    current_period: String,
    file: File,
    date_style: String, // "before_ext" or "prefix"
    retention_count: Option<usize>,
    size_limit: Option<u64>, // Maximum file size in bytes
    current_size: u64,       // Current file size in bytes
}

impl SimpleRollingWriter {
    fn new(
        path: &Path,
        rotation: Rotation,
        date_style: Option<&str>,
        retention: Option<usize>,
        size_limit: Option<u64>,
    ) -> io::Result<Self> {
        let style = date_style.unwrap_or("before_ext").to_string();
        let current_period = Self::period_string(&rotation);
        let file = Self::open_for_period(path, &current_period, &style)?;
        let current_size = file.metadata()?.len();
        Ok(SimpleRollingWriter {
            base_path: path.to_path_buf(),
            rotation,
            current_period,
            file,
            date_style: style,
            retention_count: retention,
            size_limit,
            current_size,
        })
    }

    fn period_string(rotation: &Rotation) -> String {
        let now = Utc::now();
        match *rotation {
            Rotation::DAILY => now.format("%Y-%m-%d").to_string(),
            Rotation::HOURLY => now.format("%Y-%m-%d_%H").to_string(),
            Rotation::MINUTELY => now.format("%Y-%m-%d_%H-%M").to_string(),
            Rotation::NEVER => String::new(),
        }
    }

    fn path_for_period(base: &Path, period: &str, date_style: &str) -> PathBuf {
        if period.is_empty() {
            return base.to_path_buf();
        }
        let file_name = base
            .file_name()
            .and_then(|s| s.to_str())
            .unwrap_or_default();
        if date_style == "prefix" {
            // prefix style: place the date before the filename separated by a dot
            // e.g. `2025-08-22.app.log` (preferred) and handle dot-leading filenames
            let new_name = if file_name.starts_with('.') {
                // file_name like `.hidden` -> `2025-08-22.hidden`
                format!("{}{}", period, file_name)
            } else {
                format!("{}.{}", period, file_name)
            };
            base.with_file_name(new_name)
        } else {
            // default: insert before extension
            if let Some(pos) = file_name.rfind('.') {
                let (stem, ext) = file_name.split_at(pos);
                let new_name = format!("{}.{}{}", stem, period, ext);
                base.with_file_name(new_name)
            } else {
                // no extension
                let new_name = format!("{}.{}", file_name, period);
                base.with_file_name(new_name)
            }
        }
    }

    fn open_for_period(base: &Path, period: &str, date_style: &str) -> io::Result<File> {
        let p = Self::path_for_period(base, period, date_style);
        if let Some(parent) = p.parent() {
            std::fs::create_dir_all(parent)?;
        }
        OpenOptions::new().create(true).append(true).open(p)
    }

    fn rotate_if_needed(&mut self, upcoming_write_size: usize) -> io::Result<()> {
        let new_period = Self::period_string(&self.rotation);
        let needs_time_rotation = new_period != self.current_period;
        let needs_size_rotation = self
            .size_limit
            .is_some_and(|limit| self.current_size + upcoming_write_size as u64 >= limit);

        if needs_time_rotation || needs_size_rotation {
            let actual_period = if needs_size_rotation && !needs_time_rotation {
                // For size-based rotation when time rotation is disabled, use timestamp
                Utc::now().format("%Y-%m-%d_%H-%M-%S").to_string()
            } else {
                new_period.clone()
            };

            self.current_period = actual_period.clone();
            self.file = Self::open_for_period(&self.base_path, &actual_period, &self.date_style)?;
            self.current_size = 0; // Reset size for new file

            // prune old files if retention is configured
            if let Some(keep) = self.retention_count {
                let current_path =
                    Self::path_for_period(&self.base_path, &self.current_period, &self.date_style);
                if let Some(dir) = current_path.parent() {
                    let _ = prune_old_files(
                        dir,
                        &self.base_path,
                        &self.date_style,
                        keep,
                        &current_path,
                    );
                }
            }
        }
        Ok(())
    }
}

impl Write for SimpleRollingWriter {
    fn write(&mut self, buf: &[u8]) -> io::Result<usize> {
        // Check if we need to rotate due to time or size
        let needs_rotation = if self.rotation != Rotation::NEVER {
            let new_period = Self::period_string(&self.rotation);
            new_period != self.current_period
        } else {
            false
        } || self
            .size_limit
            .is_some_and(|limit| self.current_size + buf.len() as u64 > limit);

        if needs_rotation {
            let _ = self.rotate_if_needed(buf.len());
        }

        let written = self.file.write(buf)?;
        self.current_size += written as u64;
        Ok(written)
    }

    fn flush(&mut self) -> io::Result<()> {
        self.file.flush()
    }
}

/// Prune old rotated files based on retention count
fn prune_old_files(
    dir: &Path,
    base: &Path,
    date_style: &str,
    keep: usize,
    current_path: &Path,
) -> io::Result<()> {
    use std::fs;
    let base_name = base.file_name().and_then(|s| s.to_str()).unwrap_or("");
    let (stem, ext_opt) = match base_name.rfind('.') {
        Some(pos) => (&base_name[..pos], Some(&base_name[pos + 1..])),
        None => (base_name, None),
    };
    let mut candidates: Vec<(std::time::SystemTime, PathBuf)> = Vec::new();
    for entry in fs::read_dir(dir)? {
        let entry = match entry {
            Ok(e) => e,
            Err(_) => continue,
        };
        let path = entry.path();
        if path == current_path {
            continue;
        }
        if !path.is_file() {
            continue;
        }
        let name = match path.file_name().and_then(|s| s.to_str()) {
            Some(n) => n,
            None => continue,
        };
        let matches = if date_style == "prefix" {
            // rotated form ends with ".<base_name>"
            name.ends_with(&format!(".{}", base_name))
        } else {
            // before_ext: stem.period.ext or name starts with "stem." (no ext)
            match ext_opt {
                Some(ext) => {
                    name.starts_with(&format!("{}.", stem)) && name.ends_with(&format!(".{}", ext))
                }
                None => name.starts_with(&format!("{}.", stem)),
            }
        };
        if !matches {
            continue;
        }
        let modified = entry
            .metadata()
            .and_then(|m| m.modified())
            .unwrap_or(std::time::SystemTime::UNIX_EPOCH);
        candidates.push((modified, path));
    }
    if candidates.len() > keep {
        candidates.sort_by_key(|(t, _)| *t);
        let to_delete = candidates.len().saturating_sub(keep);
        for (_, p) in candidates.into_iter().take(to_delete) {
            let _ = fs::remove_file(p);
        }
    }
    Ok(())
}

/// Create a file appender with rotation support
pub fn make_file_appender(
    path: &str,
    rotation: Option<&str>,
    date_style: Option<&str>,
    date_enabled: bool,
    retention: Option<usize>,
    size_limit: Option<&str>,
) -> Arc<Mutex<Box<dyn Write + Send>>> {
    let mut rot = rotation_from_str(rotation);
    if !date_enabled {
        rot = Rotation::NEVER;
    }
    let size_bytes = parse_size_limit(size_limit);
    let p = Path::new(path);
    // try to create a SimpleRollingWriter; on error, fallback to writing directly to the given path
    match SimpleRollingWriter::new(p, rot, date_style, retention, size_bytes) {
        Ok(w) => Arc::new(Mutex::new(Box::new(w))),
        Err(_) => {
            // fallback: open a simple append file
            let _ = std::fs::create_dir_all(p.parent().unwrap_or_else(|| Path::new(".")));
            let f = OpenOptions::new()
                .create(true)
                .append(true)
                .open(p)
                .unwrap_or_else(|_| {
                    // If all else fails, create a no-op writer
                    File::create("fallback.log").expect("Cannot create fallback log file")
                });
            Arc::new(Mutex::new(Box::new(f)))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use std::io::Read;
    use tempfile::TempDir;

    #[test]
    fn test_rotation_from_str() {
        assert_eq!(rotation_from_str(Some("daily")), Rotation::DAILY);
        assert_eq!(rotation_from_str(Some("hourly")), Rotation::HOURLY);
        assert_eq!(rotation_from_str(Some("minutely")), Rotation::MINUTELY);
        assert_eq!(rotation_from_str(Some("never")), Rotation::NEVER);
        assert_eq!(rotation_from_str(Some("invalid")), Rotation::NEVER);
        assert_eq!(rotation_from_str(None), Rotation::NEVER);
    }

    #[test]
    fn test_parse_size_limit() {
        assert_eq!(parse_size_limit(Some("1024")), Some(1024));
        assert_eq!(parse_size_limit(Some("1KB")), Some(1024));
        assert_eq!(parse_size_limit(Some("1MB")), Some(1024 * 1024));
        assert_eq!(parse_size_limit(Some("1GB")), Some(1024 * 1024 * 1024));
        assert_eq!(parse_size_limit(Some("2K")), Some(2048));
        assert_eq!(parse_size_limit(Some("3M")), Some(3 * 1024 * 1024));
        assert_eq!(parse_size_limit(Some("4G")), Some(4 * 1024 * 1024 * 1024));
        assert_eq!(parse_size_limit(Some("5B")), Some(5));
        assert_eq!(parse_size_limit(Some("")), None);
        assert_eq!(parse_size_limit(Some("invalid")), None);
        assert_eq!(parse_size_limit(Some("KB")), None);
        assert_eq!(parse_size_limit(None), None);
    }

    #[test]
    fn test_period_string() {
        // Test that period strings are generated correctly
        let daily = SimpleRollingWriter::period_string(&Rotation::DAILY);
        assert!(daily.len() == 10); // YYYY-MM-DD format
        assert!(daily.contains('-'));

        let hourly = SimpleRollingWriter::period_string(&Rotation::HOURLY);
        assert!(hourly.contains('_'));
        assert!(hourly.contains('-'));

        let minutely = SimpleRollingWriter::period_string(&Rotation::MINUTELY);
        assert!(minutely.contains('_'));
        assert!(minutely.contains('-'));

        let never = SimpleRollingWriter::period_string(&Rotation::NEVER);
        assert_eq!(never, "");
    }

    #[test]
    fn test_path_for_period() {
        let base = Path::new("test.log");

        // Test never rotation
        assert_eq!(
            SimpleRollingWriter::path_for_period(base, "", "before_ext"),
            Path::new("test.log")
        );

        // Test before_ext style
        let daily_path = SimpleRollingWriter::path_for_period(base, "2023-01-01", "before_ext");
        assert_eq!(daily_path, Path::new("test.2023-01-01.log"));

        // Test file without extension
        let base_no_ext = Path::new("test");
        let daily_path_no_ext =
            SimpleRollingWriter::path_for_period(base_no_ext, "2023-01-01", "before_ext");
        assert_eq!(daily_path_no_ext, Path::new("test.2023-01-01"));

        // Test prefix style
        let prefix_path = SimpleRollingWriter::path_for_period(base, "2023-01-01", "prefix");
        assert_eq!(prefix_path, Path::new("2023-01-01.test.log"));

        // Test hidden file with prefix
        let hidden_base = Path::new(".hidden.log");
        let hidden_prefix =
            SimpleRollingWriter::path_for_period(hidden_base, "2023-01-01", "prefix");
        assert_eq!(hidden_prefix, Path::new("2023-01-01.hidden.log"));
    }

    #[test]
    fn test_simple_rolling_writer_creation() {
        let temp_dir = TempDir::new().unwrap();
        let file_path = temp_dir.path().join("test.log");

        let writer = SimpleRollingWriter::new(&file_path, Rotation::NEVER, None, None, None);
        assert!(writer.is_ok());

        let writer = writer.unwrap();
        assert_eq!(writer.base_path, file_path);
        assert_eq!(writer.rotation, Rotation::NEVER);
        assert_eq!(writer.date_style, "before_ext");
        assert_eq!(writer.retention_count, None);
        assert_eq!(writer.size_limit, None);
    }

    #[test]
    fn test_simple_rolling_writer_write() -> io::Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let file_path = temp_dir.path().join("test.log");

        let mut writer = SimpleRollingWriter::new(&file_path, Rotation::NEVER, None, None, None)?;

        // Write some data
        let data = b"Hello, World!";
        let written = writer.write(data)?;
        assert_eq!(written, data.len());
        writer.flush()?;

        // Verify the data was written
        let mut file = File::open(&file_path)?;
        let mut contents = Vec::new();
        file.read_to_end(&mut contents)?;
        assert_eq!(contents, data);

        Ok(())
    }

    #[test]
    fn test_simple_rolling_writer_size_rotation() -> io::Result<()> {
        let temp_dir = TempDir::new().unwrap();
        let file_path = temp_dir.path().join("test.log");

        // Set size limit to 10 bytes
        let mut writer =
            SimpleRollingWriter::new(&file_path, Rotation::NEVER, None, None, Some(10))?;

        // Write data that exceeds the limit
        writer.write_all(b"Hello, ")?; // 7 bytes
        writer.write_all(b"World! Extra text")?; // This should trigger rotation
        writer.flush()?;

        // Check that files were created
        let mut files: Vec<_> = fs::read_dir(&temp_dir)?
            .filter_map(|e| e.ok())
            .map(|e| e.path())
            .collect();
        files.sort();

        // Should have at least 2 files (original + rotated)
        assert!(files.len() >= 2);

        Ok(())
    }

    #[test]
    fn test_make_file_appender() {
        let temp_dir = TempDir::new().unwrap();
        let file_path = temp_dir
            .path()
            .join("test.log")
            .to_str()
            .unwrap()
            .to_string();

        let appender = make_file_appender(&file_path, None, None, true, None, None);
        assert!(appender.try_lock().is_some()); // Should be able to lock

        // Test with rotation
        let appender_rotated =
            make_file_appender(&file_path, Some("daily"), None, true, Some(5), Some("1MB"));
        assert!(appender_rotated.try_lock().is_some());
    }

    #[test]
    fn test_make_file_appender_no_date() {
        let temp_dir = TempDir::new().unwrap();
        let file_path = temp_dir
            .path()
            .join("test.log")
            .to_str()
            .unwrap()
            .to_string();

        let appender = make_file_appender(&file_path, Some("daily"), None, false, None, None);
        // Should still work but with NEVER rotation since date_enabled is false
        assert!(appender.try_lock().is_some());
    }
}
