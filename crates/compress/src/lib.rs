//! Compression codecs for rotated and retained log files.
//!
//! This module provides lossless compression for log files after rotation.
//! Supported codecs:
//!
//! | Codec    | Extension | Typical Ratio | Speed    |
//! |----------|-----------|---------------|----------|
//! | `Gzip`   | `.gz`     | Good          | Fast     |
//! | `Zip`    | `.zip`    | Good          | Fast     |
//! | `Bz2`    | `.bz2`    | Better        | Moderate |
//! | `Xz`     | `.xz`     | Best          | Slow     |
//! | `Zstd`   | `.zst`    | Best          | Fast     |
//!
//! The [`compress_file`] function compresses a single file and returns the
//! path of the compressed output. The original file is **not** deleted — the
//! caller is responsible for cleanup.
//!
//! The [`cleanup_old_archives`] function prunes old compressed archives by
//! count or age, useful for retention policies.
//!
//! # Examples
//!
//! ```rust,no_run
//! use compress::{compress_file, CompressionCodec};
//! use std::path::Path;
//!
//! let compressed = compress_file(Path::new("app.log"), &CompressionCodec::Gzip).unwrap();
//! assert!(compressed.ends_with(".gz"));
//! ```

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use bzip2::Compression as BzCompression;
use bzip2::write::BzEncoder;
use error::{LoglyError, LoglyResult};
use flate2::Compression;
use flate2::write::GzEncoder;
use std::path::Path;
use xz2::write::XzEncoder;
use zstd::Encoder as ZstdEncoder;

/// Supported compression codecs for log file archiving.
///
/// Each variant maps to a specific compression algorithm with different
/// trade-offs between compression ratio and CPU usage.
#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub enum CompressionCodec {
    /// No compression.
    #[default]
    None,
    /// Gzip compression.
    Gzip,
    /// Zip archive compression.
    Zip,
    /// Bzip2 compression.
    Bz2,
    /// XZ/LZMA compression.
    Xz,
    /// Zstandard compression.
    Zstd,
}

impl std::fmt::Display for CompressionCodec {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::None => write!(f, "none"),
            Self::Gzip => write!(f, "gzip"),
            Self::Zip => write!(f, "zip"),
            Self::Bz2 => write!(f, "bz2"),
            Self::Xz => write!(f, "xz"),
            Self::Zstd => write!(f, "zstd"),
        }
    }
}

/// Compresses a single file using the specified codec.
///
/// Reads the source file, applies the chosen compression algorithm, and writes
/// the result to a new file with the appropriate extension. The original file
/// is left untouched.
///
/// # Arguments
///
/// * `path` - Path to the file to compress.
/// * `codec` - The compression algorithm to use.
///
/// # Returns
///
/// The path of the newly created compressed file.
///
/// # Errors
///
/// Returns a [`LoglyError::Compression`] if reading, compression, or file
/// creation fails.
///
/// # Examples
///
/// ```rust,no_run
/// use compress::{compress_file, CompressionCodec};
/// use std::path::Path;
///
/// let compressed = compress_file(Path::new("app.log"), &CompressionCodec::Gzip).unwrap();
/// assert!(compressed.ends_with(".gz"));
/// ```
pub fn compress_file(path: &Path, codec: &CompressionCodec) -> LoglyResult<std::path::PathBuf> {
    match codec {
        CompressionCodec::None => Ok(path.to_path_buf()),
        CompressionCodec::Gzip => compress_gzip(path),
        CompressionCodec::Zip => compress_zip(path),
        CompressionCodec::Bz2 => compress_bz2(path),
        CompressionCodec::Xz => compress_xz(path),
        CompressionCodec::Zstd => compress_zstd(path),
    }
}

/// Compress `path` into a sibling file with extension `file_ext`.
///
/// The payload is written to a temporary `.part` file first. Only after the
/// writer succeeds and the staged output is synced and closed is it
/// atomically renamed to its final name, so a crash or error can never leave
/// a truncated archive masquerading as a complete one (staged files are
/// removed best-effort on failure). Handles are dropped before the rename
/// because Windows refuses to rename open files. A failed call never
/// modifies or deletes `path`.
///
/// # Errors
///
/// Returns [`LoglyError::Compression`] when any step fails.
fn write_compressed_artifact(
    path: &Path,
    file_ext: &str,
    write_payload: impl FnOnce(&mut std::fs::File, &mut std::fs::File) -> LoglyResult<()>,
) -> LoglyResult<std::path::PathBuf> {
    let output = path.with_extension(format!(
        "{}.{}",
        path.extension().unwrap_or_default().to_string_lossy(),
        file_ext
    ));
    let mut tmp_name = output.as_os_str().to_owned();
    tmp_name.push(".part");
    let tmp = std::path::PathBuf::from(tmp_name);

    let result = (|| {
        let mut input = std::fs::File::open(path).map_err(|e| {
            LoglyError::Compression(format!("failed to open {}: {e}", path.display()))
        })?;
        let mut staged = std::fs::File::create(&tmp).map_err(|e| {
            LoglyError::Compression(format!("failed to create {}: {e}", tmp.display()))
        })?;
        write_payload(&mut input, &mut staged)?;
        staged.sync_all().map_err(|e| {
            LoglyError::Compression(format!("failed to sync {}: {e}", tmp.display()))
        })?;
        Ok::<(), LoglyError>(())
    })();
    // `input` and `staged` are dropped here, before any rename.

    match result {
        Ok(()) => {
            std::fs::rename(&tmp, &output).map_err(|e| {
                let _ = std::fs::remove_file(&tmp);
                LoglyError::Compression(format!("failed to finalize {}: {e}", output.display()))
            })?;
            Ok(output)
        }
        Err(error) => {
            let _ = std::fs::remove_file(&tmp);
            Err(error)
        }
    }
}

/// Deletes old compressed archives matching a base name pattern.
///
/// Scans the directory for files whose names start with `base_name` and have
/// a compressed extension (`.gz`, `.zip`, `.bz2`, `.xz`, `.zst`). Archives
/// are pruned by two optional criteria:
///
/// - **Count**: Keep at most `keep_count` newest archives.
/// - **Age**: Delete archives older than `max_age_secs`.
///
/// Both criteria can be combined. Files are sorted by modification time
/// (newest first) before pruning.
///
/// # Arguments
///
/// * `dir` - Directory to scan for archives.
/// * `base_name` - Prefix to match archive filenames against.
/// * `keep_count` - Maximum number of archives to retain.
/// * `max_age_secs` - Maximum age in seconds before an archive is deleted.
///
/// # Errors
///
/// Returns a [`LoglyError::Compression`] if directory listing fails.
pub fn cleanup_old_archives(
    dir: &Path,
    base_name: &str,
    keep_count: Option<u32>,
    max_age_secs: Option<u64>,
) -> LoglyResult<()> {
    let extensions = ["gz", "zip", "bz2", "xz", "zst"];
    let mut candidates: Vec<std::path::PathBuf> = Vec::new();

    if dir.is_dir() {
        let entries = std::fs::read_dir(dir).map_err(|e| {
            LoglyError::Compression(format!("failed to read directory {}: {e}", dir.display()))
        })?;
        for entry in entries.flatten() {
            let file_name = entry.file_name();
            let name = file_name.to_string_lossy();
            if let Some(remainder) = name.strip_prefix(base_name) {
                let is_compressed = extensions
                    .iter()
                    .any(|ext| remainder.ends_with(&format!(".{ext}")));
                if is_compressed || is_rotated_suffix(remainder) {
                    candidates.push(entry.path());
                }
            }
        }
    }

    candidates.sort_by(|a, b| {
        let ma = a.metadata().and_then(|m| m.modified()).ok();
        let mb = b.metadata().and_then(|m| m.modified()).ok();
        mb.cmp(&ma)
    });

    let mut to_remove = Vec::new();

    if let Some(count) = keep_count
        && candidates.len() > count as usize
    {
        to_remove.extend_from_slice(&candidates[count as usize..]);
        candidates.truncate(count as usize);
    }

    if let Some(max_age) = max_age_secs {
        let now = std::time::SystemTime::now();
        let max_duration = std::time::Duration::from_secs(max_age);
        for path in &candidates {
            if let Ok(modified) = path.metadata().and_then(|m| m.modified()) {
                let is_old = match now.duration_since(modified) {
                    Ok(age) => age > max_duration,
                    Err(_) => false, // File is in the future; don't delete
                };
                if is_old {
                    to_remove.push(path.clone());
                }
            }
        }
    }

    for path in &to_remove {
        let _ = std::fs::remove_file(path);
    }

    Ok(())
}

/// Returns `true` if `remainder` (the part of a filename after `base_name`)
/// is a rotation suffix: a dot followed by the 10-digit rotation timestamp,
/// optionally followed by a numeric counter (e.g. `.1789476036` or
/// `.1789476036.2`).
///
/// Anything else (e.g. `back` in `app.logback`, or `.config`) belongs to an
/// unrelated file that retention must never delete.
fn is_rotated_suffix(remainder: &str) -> bool {
    let dotted = remainder.strip_prefix('.').unwrap_or("");
    let (stamp, rest) = match dotted.split_once('.') {
        Some((stamp, rest)) => (stamp, Some(rest)),
        None => (dotted, None),
    };
    if stamp.len() != 10 || !stamp.bytes().all(|b| b.is_ascii_digit()) {
        return false;
    }
    match rest {
        None => true,
        Some(counter) => !counter.is_empty() && counter.bytes().all(|b| b.is_ascii_digit()),
    }
}

fn compress_gzip(path: &Path) -> LoglyResult<std::path::PathBuf> {
    write_compressed_artifact(path, "gz", |input, staged| {
        let mut encoder = GzEncoder::new(staged, Compression::default());
        std::io::copy(input, &mut encoder).map_err(|e| {
            LoglyError::Compression(format!("failed to compress {}: {e}", path.display()))
        })?;
        encoder.finish().map_err(|e| {
            LoglyError::Compression(format!("failed to finish gzip compression: {e}"))
        })?;
        Ok(())
    })
}

fn compress_zip(path: &Path) -> LoglyResult<std::path::PathBuf> {
    let file_name = path
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();

    // Stream the input into the entry instead of buffering the whole file:
    // `ZipWriter` implements `Write` once the entry is started, and only the
    // central directory (written at `finish`) requires seeking.
    write_compressed_artifact(path, "zip", |input, staged| {
        let mut zip = zip::ZipWriter::new(staged);
        let options = zip::write::SimpleFileOptions::default()
            .compression_method(zip::CompressionMethod::Deflated);
        zip.start_file(&file_name, options)
            .map_err(|e| LoglyError::Compression(format!("failed to start zip entry: {e}")))?;
        std::io::copy(input, &mut zip)
            .map_err(|e| LoglyError::Compression(format!("failed to write zip entry: {e}")))?;
        zip.finish()
            .map_err(|e| LoglyError::Compression(format!("failed to finish zip archive: {e}")))?;
        Ok(())
    })
}

fn compress_bz2(path: &Path) -> LoglyResult<std::path::PathBuf> {
    write_compressed_artifact(path, "bz2", |input, staged| {
        let mut encoder = BzEncoder::new(staged, BzCompression::default());
        std::io::copy(input, &mut encoder).map_err(|e| {
            LoglyError::Compression(format!("failed to compress {}: {e}", path.display()))
        })?;
        encoder.finish().map_err(|e| {
            LoglyError::Compression(format!("failed to finish bz2 compression: {e}"))
        })?;
        Ok(())
    })
}

fn compress_xz(path: &Path) -> LoglyResult<std::path::PathBuf> {
    write_compressed_artifact(path, "xz", |input, staged| {
        let mut encoder = XzEncoder::new(staged, 6);
        std::io::copy(input, &mut encoder).map_err(|e| {
            LoglyError::Compression(format!("failed to compress {}: {e}", path.display()))
        })?;
        encoder.finish().map_err(|e| {
            LoglyError::Compression(format!("failed to finish xz compression: {e}"))
        })?;
        Ok(())
    })
}

fn compress_zstd(path: &Path) -> LoglyResult<std::path::PathBuf> {
    write_compressed_artifact(path, "zst", |input, staged| {
        let mut encoder = ZstdEncoder::new(staged, 0)
            .map_err(|e| LoglyError::Compression(format!("failed to create zstd encoder: {e}")))?;
        std::io::copy(input, &mut encoder).map_err(|e| {
            LoglyError::Compression(format!("failed to compress {}: {e}", path.display()))
        })?;
        encoder.finish().map_err(|e| {
            LoglyError::Compression(format!("failed to finish zstd compression: {e}"))
        })?;
        Ok(())
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use std::io::{BufReader, Read};

    fn test_dir(suffix: &str) -> std::path::PathBuf {
        let dir = std::env::temp_dir().join(format!("logly_compress_test_{suffix}"));
        let _ = fs::create_dir_all(&dir);
        dir
    }

    fn create_test_file(dir: &std::path::Path, name: &str, content: &[u8]) -> std::path::PathBuf {
        let path = dir.join(name);
        fs::write(&path, content).unwrap();
        path
    }

    #[test]
    fn compress_none_returns_same_path() {
        let dir = test_dir("none");
        let path = create_test_file(&dir, "none_test.log", b"hello world");
        let result = compress_file(&path, &CompressionCodec::None).unwrap();
        assert_eq!(result, path);
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn compress_gzip_creates_valid_gzip() {
        let dir = test_dir("gzip");
        let content = b"The quick brown fox jumps over the lazy dog. ";
        let repeated: Vec<u8> = content.iter().copied().cycle().take(10000).collect();
        let path = create_test_file(&dir, "gzip_test.log", &repeated);
        let compressed = compress_file(&path, &CompressionCodec::Gzip).unwrap();
        assert!(compressed.to_string_lossy().ends_with(".gz"));

        // Verify the compressed file is smaller (gzip should compress repeated data)
        let compressed_size = fs::metadata(&compressed).unwrap().len();
        let original_size = fs::metadata(&path).unwrap().len();
        assert!(
            compressed_size < original_size,
            "gzip should compress: {compressed_size} >= {original_size}"
        );

        // Verify we can decompress it
        let decompressed = decompress_gzip(&compressed).unwrap();
        assert_eq!(decompressed, repeated);

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn compress_zip_creates_valid_zip() {
        let dir = test_dir("zip");
        let content = b"The quick brown fox jumps over the lazy dog. ";
        let repeated: Vec<u8> = content.iter().copied().cycle().take(10000).collect();
        let path = create_test_file(&dir, "zip_test.log", &repeated);
        let compressed = compress_file(&path, &CompressionCodec::Zip).unwrap();
        assert!(compressed.to_string_lossy().ends_with(".zip"));

        // Verify we can read the zip file
        let file = std::fs::File::open(&compressed).unwrap();
        let reader = BufReader::new(file);
        let mut archive = zip::ZipArchive::new(reader).unwrap();
        assert_eq!(archive.len(), 1);

        let mut zip_file = archive.by_index(0).unwrap();
        let mut extracted = Vec::new();
        zip_file.read_to_end(&mut extracted).unwrap();
        assert_eq!(extracted, repeated);

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn compress_bz2_creates_valid_bzip2() {
        let dir = test_dir("bz2");
        let content = b"The quick brown fox jumps over the lazy dog. ";
        let repeated: Vec<u8> = content.iter().copied().cycle().take(10000).collect();
        let path = create_test_file(&dir, "bz2_test.log", &repeated);
        let compressed = compress_file(&path, &CompressionCodec::Bz2).unwrap();
        assert!(compressed.to_string_lossy().ends_with(".bz2"));

        let compressed_size = fs::metadata(&compressed).unwrap().len();
        let original_size = fs::metadata(&path).unwrap().len();
        assert!(
            compressed_size < original_size,
            "bz2 should compress: {compressed_size} >= {original_size}"
        );

        let decompressed = decompress_bz2(&compressed).unwrap();
        assert_eq!(decompressed, repeated);

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn compress_xz_creates_valid_xz() {
        let dir = test_dir("xz");
        let content = b"The quick brown fox jumps over the lazy dog. ";
        let repeated: Vec<u8> = content.iter().copied().cycle().take(10000).collect();
        let path = create_test_file(&dir, "xz_test.log", &repeated);
        let compressed = compress_file(&path, &CompressionCodec::Xz).unwrap();
        assert!(compressed.to_string_lossy().ends_with(".xz"));

        let compressed_size = fs::metadata(&compressed).unwrap().len();
        let original_size = fs::metadata(&path).unwrap().len();
        assert!(
            compressed_size < original_size,
            "xz should compress: {compressed_size} >= {original_size}"
        );

        let decompressed = decompress_xz(&compressed).unwrap();
        assert_eq!(decompressed, repeated);

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn compress_zstd_creates_valid_zstd() {
        let dir = test_dir("zstd");
        let content = b"The quick brown fox jumps over the lazy dog. ";
        let repeated: Vec<u8> = content.iter().copied().cycle().take(10000).collect();
        let path = create_test_file(&dir, "zstd_test.log", &repeated);
        let compressed = compress_file(&path, &CompressionCodec::Zstd).unwrap();
        assert!(compressed.to_string_lossy().ends_with(".zst"));

        let compressed_size = fs::metadata(&compressed).unwrap().len();
        let original_size = fs::metadata(&path).unwrap().len();
        assert!(
            compressed_size < original_size,
            "zstd should compress: {compressed_size} >= {original_size}"
        );

        let decompressed = decompress_zstd(&compressed).unwrap();
        assert_eq!(decompressed, repeated);

        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn compress_empty_file() {
        let dir = test_dir("empty");
        let path = create_test_file(&dir, "empty_test.log", b"");
        let compressed = compress_file(&path, &CompressionCodec::Gzip).unwrap();
        let decompressed = decompress_gzip(&compressed).unwrap();
        assert!(decompressed.is_empty());
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn cleanup_no_files() {
        let dir = test_dir("cleanup_no");
        cleanup_old_archives(&dir, "app", Some(5), None).unwrap();
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn cleanup_removes_old_files() {
        let dir = test_dir("cleanup_old");
        for i in 0..5 {
            create_test_file(&dir, &format!("app.log.{i}.gz"), b"data");
        }
        cleanup_old_archives(&dir, "app", Some(2), None).unwrap();
        let remaining: Vec<_> = fs::read_dir(&dir)
            .unwrap()
            .filter_map(std::result::Result::ok)
            .filter(|e| e.file_name().to_string_lossy().starts_with("app"))
            .collect();
        assert!(
            remaining.len() <= 2,
            "should keep at most 2 files, got {}",
            remaining.len()
        );
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn codec_display() {
        assert_eq!(CompressionCodec::None.to_string(), "none");
        assert_eq!(CompressionCodec::Gzip.to_string(), "gzip");
        assert_eq!(CompressionCodec::Zip.to_string(), "zip");
        assert_eq!(CompressionCodec::Bz2.to_string(), "bz2");
        assert_eq!(CompressionCodec::Xz.to_string(), "xz");
        assert_eq!(CompressionCodec::Zstd.to_string(), "zstd");
    }

    #[test]
    fn cleanup_by_age() {
        let dir = test_dir("cleanup_age");
        // Create a file, then try to clean it up with very small max age
        let path = create_test_file(&dir, "app.log.0.gz", b"data");
        // Sleep to ensure file age exceeds 1 second (needed for as_secs() granularity)
        std::thread::sleep(std::time::Duration::from_millis(1100));
        let _ = cleanup_old_archives(&dir, "app", None, Some(1));
        // The file should have been deleted (age > 1 sec)
        assert!(
            !path.exists(),
            "file should have been deleted by age cleanup"
        );
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn rotated_suffix_matches_only_rotation_names() {
        assert!(is_rotated_suffix(".1789476036"));
        assert!(is_rotated_suffix(".1789476036.2"));
        assert!(!is_rotated_suffix(""));
        assert!(!is_rotated_suffix("back"));
        assert!(!is_rotated_suffix(".config"));
        assert!(!is_rotated_suffix(".123456789"));
        assert!(!is_rotated_suffix(".12345678901"));
        assert!(!is_rotated_suffix(".1789476036."));
        assert!(!is_rotated_suffix(".1789476036.x"));
    }

    #[test]
    fn cleanup_keeps_unrelated_files() {
        let dir = test_dir("cleanup_unrelated");
        for name in [
            "app.logback",
            "app.log.tmp",
            "app.log.gz.backup",
            "app.log.123",
            "app.log.123456789",
            "notes.txt",
        ] {
            create_test_file(&dir, name, b"do not delete");
        }
        create_test_file(&dir, "app.log.1789476036.gz", b"archive");
        cleanup_old_archives(&dir, "app.log", Some(0), None).unwrap();
        for name in [
            "app.logback",
            "app.log.tmp",
            "app.log.gz.backup",
            "app.log.123",
            "app.log.123456789",
            "notes.txt",
        ] {
            assert!(dir.join(name).exists(), "{name} must be preserved");
        }
        assert!(
            !dir.join("app.log.1789476036.gz").exists(),
            "managed archive must be pruned"
        );
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn staged_part_files_are_never_managed() {
        let dir = test_dir("cleanup_part");
        create_test_file(&dir, "app.log.1789476036.gz.part", b"partial");
        cleanup_old_archives(&dir, "app.log", Some(0), None).unwrap();
        assert!(dir.join("app.log.1789476036.gz.part").exists());
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn failed_compression_keeps_source_and_reports() {
        let dir = test_dir("compress_missing");
        let missing = dir.join("does-not-exist.log");
        let result = compress_file(&missing, &CompressionCodec::Gzip);
        assert!(result.is_err());
        assert!(
            dir.read_dir().unwrap().next().is_none(),
            "no artifact may remain after failure"
        );
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn staged_artifact_is_renamed_to_final_name() {
        let dir = test_dir("compress_staged");
        let path = create_test_file(&dir, "staged_test.log", b"staged payload");
        let compressed = compress_file(&path, &CompressionCodec::Gzip).unwrap();
        assert!(compressed.to_string_lossy().ends_with(".gz"));
        assert!(!compressed.to_string_lossy().ends_with(".part"));
        assert!(dir.join("staged_test.log.gz").exists());
        assert!(path.exists(), "source must survive successful compression");
        let _ = fs::remove_dir_all(&dir);
    }

    fn decompress_gzip(path: &Path) -> LoglyResult<Vec<u8>> {
        let file = std::fs::File::open(path)
            .map_err(|e| LoglyError::Compression(format!("failed to open gzip: {e}")))?;
        let mut decoder = flate2::read::GzDecoder::new(file);
        let mut output = Vec::new();
        decoder
            .read_to_end(&mut output)
            .map_err(|e| LoglyError::Compression(format!("failed to decompress gzip: {e}")))?;
        Ok(output)
    }

    fn decompress_bz2(path: &Path) -> LoglyResult<Vec<u8>> {
        let file = std::fs::File::open(path)
            .map_err(|e| LoglyError::Compression(format!("failed to open bz2: {e}")))?;
        let mut decoder = bzip2::read::BzDecoder::new(file);
        let mut output = Vec::new();
        decoder
            .read_to_end(&mut output)
            .map_err(|e| LoglyError::Compression(format!("failed to decompress bz2: {e}")))?;
        Ok(output)
    }

    fn decompress_xz(path: &Path) -> LoglyResult<Vec<u8>> {
        let file = std::fs::File::open(path)
            .map_err(|e| LoglyError::Compression(format!("failed to open xz: {e}")))?;
        let mut decoder = xz2::read::XzDecoder::new(file);
        let mut output = Vec::new();
        decoder
            .read_to_end(&mut output)
            .map_err(|e| LoglyError::Compression(format!("failed to decompress xz: {e}")))?;
        Ok(output)
    }

    fn decompress_zstd(path: &Path) -> LoglyResult<Vec<u8>> {
        let file = std::fs::File::open(path)
            .map_err(|e| LoglyError::Compression(format!("failed to open zstd: {e}")))?;
        let mut decoder = zstd::Decoder::new(file)
            .map_err(|e| LoglyError::Compression(format!("failed to create zstd decoder: {e}")))?;
        let mut output = Vec::new();
        decoder
            .read_to_end(&mut output)
            .map_err(|e| LoglyError::Compression(format!("failed to decompress zstd: {e}")))?;
        Ok(output)
    }
}
