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
///
/// # Examples
///
/// ```rust
/// use logly::backend::rotation::rotation_from_str;
/// use logly::utils::levels::Rotation;
///
/// assert_eq!(rotation_from_str(Some("daily")), Rotation::DAILY);
/// assert_eq!(rotation_from_str(Some("hourly")), Rotation::HOURLY);
/// assert_eq!(rotation_from_str(None), Rotation::NEVER);
/// ```
pub fn rotation_from_str(rotation: Option<&str>) -> Rotation {
    match rotation.unwrap_or("never") {
        "daily" => Rotation::DAILY,
        "hourly" => Rotation::HOURLY,
        "minutely" => Rotation::MINUTELY,
        _ => Rotation::NEVER,
    }
}

/// Parse size strings like "5KB", "10MB", "1GB" into bytes.
///
/// Supports case-insensitive size units with the following formats:
/// - Bytes: "100B", "100b", "100" (number only defaults to bytes)
/// - Kilobytes: "5KB", "5kb", "5K", "5k"
/// - Megabytes: "10MB", "10mb", "10M", "10m"
/// - Gigabytes: "1GB", "1gb", "1G", "1g"
/// - Terabytes: "2TB", "2tb", "2T", "2t"
///
/// # Arguments
///
/// * `size_str` - Optional string specifying the size with unit (e.g., "5KB", "10mb", "1G")
///
/// # Returns
///
/// The size in bytes, or None if parsing fails
///
/// # Examples
///
/// ```rust
/// use logly::backend::rotation::parse_size_limit;
///
/// assert_eq!(parse_size_limit(Some("100")), Some(100));      // bytes (no unit)
/// assert_eq!(parse_size_limit(Some("100B")), Some(100));     // bytes
/// assert_eq!(parse_size_limit(Some("5KB")), Some(5120));     // kilobytes
/// assert_eq!(parse_size_limit(Some("10mb")), Some(10485760));// megabytes (lowercase)
/// assert_eq!(parse_size_limit(Some("1G")), Some(1073741824));// gigabytes (short form)
/// assert_eq!(parse_size_limit(Some("invalid")), None);       // invalid format
/// ```
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
            "TB" | "T" => 1024u64 * 1024 * 1024 * 1024,
            _ => return None, // Invalid unit
        };

        num_str.parse::<u64>().ok().map(|n| n * multiplier)
    })
}

#[cfg(test)]
mod tests {
    use super::*;

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
    fn test_parse_size_limit_case_insensitive() {
        assert_eq!(parse_size_limit(Some("1kb")), Some(1024));
        assert_eq!(parse_size_limit(Some("1Mb")), Some(1024 * 1024));
        assert_eq!(parse_size_limit(Some("1gB")), Some(1024 * 1024 * 1024));
    }

    #[test]
    fn test_parse_size_limit_short_units() {
        assert_eq!(parse_size_limit(Some("5k")), Some(5120));
        assert_eq!(parse_size_limit(Some("10m")), Some(10485760));
        assert_eq!(parse_size_limit(Some("2g")), Some(2147483648));
    }

    #[test]
    fn test_parse_size_limit_terabytes() {
        assert_eq!(
            parse_size_limit(Some("1TB")),
            Some(1024u64 * 1024 * 1024 * 1024)
        );
        assert_eq!(
            parse_size_limit(Some("2T")),
            Some(2 * 1024u64 * 1024 * 1024 * 1024)
        );
    }

    #[test]
    fn test_parse_size_limit_whitespace() {
        assert_eq!(parse_size_limit(Some("  1024  ")), Some(1024));
        assert_eq!(parse_size_limit(Some(" 5 KB ")), Some(5120));
    }

    #[test]
    fn test_rotation_from_str_case_variations() {
        // Test that we handle exact matches (case-sensitive by default)
        assert_eq!(rotation_from_str(Some("DAILY")), Rotation::NEVER); // Not matched
        assert_eq!(rotation_from_str(Some("Daily")), Rotation::NEVER); // Not matched
        assert_eq!(rotation_from_str(Some("daily")), Rotation::DAILY); // Matched
    }
}
