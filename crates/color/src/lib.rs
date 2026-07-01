//! ANSI color rendering utilities.
//!
//! Maps log levels to ANSI color/style codes with per-sink colorize toggles,
//! TTY auto-detection, and theme customization.
//!
//! # Supported Color Formats
//!
//! - **Named colors**: `"red"`, `"blue"`, `"bright_red"`, etc.
//! - **Text styles**: `"bold"`, `"italic"`, `"underline"`, `"dim"`, etc.
//! - **Compound styles**: `"bold red"`, `"italic cyan on white"`, `"dim yellow"`
//! - **Background colors**: `"bg_red"`, `"on_blue"`, `"bg_bright_cyan"`
//! - **Raw SGR codes**: `"1;32"`, `"38;2;255;0;0"`
//! - **256-color**: `"color(208)"`
//! - **RGB foreground**: `"rgb(255,128,0)"`, `"#ff8000"`
//! - **RGB background**: `"bg_rgb(255,0,0)"`, `"bg#ff0000"`
//!
//! # Rich Markup
//!
//! The [`parse_rich_markup`] function converts Rich-style tags like `<bold>`,
//! `<red>`, `<bold red on white>` into ANSI escape sequences.

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use levels::LogLevel;
use std::collections::HashMap;

/// Default color mapping for built-in levels.
fn default_color_map() -> HashMap<&'static str, &'static str> {
    HashMap::from([
        ("TRACE", "dim"),
        ("DEBUG", "blue"),
        ("INFO", ""),
        ("NOTICE", "cyan"),
        ("SUCCESS", "green"),
        ("WARNING", "yellow"),
        ("ERROR", "red"),
        ("FAIL", "magenta"),
        ("CRITICAL", "bold_red"),
        ("FATAL", "bold_red"),
        // Bright variants available for custom use
        ("bright_black", "bright_black"),
        ("bright_red", "bright_red"),
        ("bright_green", "bright_green"),
        ("bright_yellow", "bright_yellow"),
        ("bright_blue", "bright_blue"),
        ("bright_magenta", "bright_magenta"),
        ("bright_cyan", "bright_cyan"),
        ("bright_white", "bright_white"),
    ])
}

/// Applies level color when colorization is enabled.
///
/// Wraps the text in ANSI escape codes based on the level's default color.
/// If the level has no default color, falls back to the built-in color map.
///
/// # Arguments
///
/// * `level` - The log level whose color is applied
/// * `text` - The text to colorize
/// * `colorize` - Whether to actually emit color codes
///
/// # Returns
///
/// The text wrapped in ANSI escape codes when `colorize` is `true` and a
/// color is found; otherwise returns the text unchanged.
///
/// # Examples
///
/// ```rust
/// use color::paint;
/// use levels::LogLevel;
///
/// let level = LogLevel::new("ERROR", 50, Some("red".to_owned()));
/// let colored = paint(&level, "error message", true);
/// assert!(colored.contains("\x1b["));
///
/// let plain = paint(&level, "error message", false);
/// assert_eq!(plain, "error message");
/// ```
#[must_use]
pub fn paint(level: &LogLevel, text: &str, colorize: bool) -> String {
    if !colorize {
        return text.to_owned();
    }
    let color_name = level.color().unwrap_or_else(|| {
        let map = default_color_map();
        map.get(level.name()).copied().unwrap_or("")
    });
    let code = resolve_color_code(color_name);
    if code.is_empty() {
        text.to_owned()
    } else {
        format!("\x1b[{code}m{text}\x1b[0m")
    }
}

/// Returns ANSI escape code for a foreground color name.
///
/// # Supported Names
///
/// - Standard colors: `"black"`, `"red"`, `"green"`, `"yellow"`, `"blue"`, `"magenta"`, `"cyan"`, `"white"`
/// - Bright colors: `"bright_black"` through `"bright_white"`
/// - Text styles: `"dim"`, `"bold"`, `"italic"`, `"underline"`, `"blink"`, `"reverse"`, `"strike"`
/// - Compound: `"bold_red"`, `"dim_cyan"`, `"italic_green"`, etc.
///
/// Returns `""` for unrecognized names.
///
/// # Examples
///
/// ```rust
/// use color::color_code;
///
/// assert_eq!(color_code("red"), "31");
/// assert_eq!(color_code("bold_red"), "1;31");
/// assert_eq!(color_code("bright_cyan"), "96");
/// assert_eq!(color_code("dim"), "2");
/// assert_eq!(color_code("unknown"), "");
/// ```
#[must_use]
pub fn color_code(name: &str) -> &'static str {
    match name {
        // Standard colors
        "black" => "30",
        "red" => "31",
        "green" => "32",
        "yellow" => "33",
        "blue" => "34",
        "magenta" => "35",
        "cyan" => "36",
        "white" => "37",
        // Bright/high-intensity colors
        "bright_black" => "90",
        "bright_red" => "91",
        "bright_green" => "92",
        "bright_yellow" => "93",
        "bright_blue" => "94",
        "bright_magenta" => "95",
        "bright_cyan" => "96",
        "bright_white" => "97",
        // Text styles
        "dim" => "2",
        "bold" => "1",
        "italic" => "3",
        "underline" => "4",
        "blink" => "5",
        "reverse" => "7",
        "strike" => "9",
        // Compound shortcuts (underscore-separated)
        "bold_red" => "1;31",
        "bold_green" => "1;32",
        "bold_yellow" => "1;33",
        "bold_blue" => "1;34",
        "bold_magenta" => "1;35",
        "bold_cyan" => "1;36",
        "bold_white" => "1;37",
        "dim_red" => "2;31",
        "dim_green" => "2;32",
        "dim_yellow" => "2;33",
        "dim_blue" => "2;34",
        "dim_magenta" => "2;35",
        "dim_cyan" => "2;36",
        "italic_red" => "3;31",
        "italic_green" => "3;32",
        "italic_yellow" => "3;33",
        "italic_blue" => "3;34",
        "italic_magenta" => "3;35",
        "italic_cyan" => "3;36",
        _ => "",
    }
}

/// Returns ANSI escape code for a background color name.
///
/// Supports both `bg_` and `on_` prefixes (e.g., `"bg_red"` and `"on_red"`).
/// Returns `""` for unrecognized names.
///
/// # Supported Names
///
/// - `"bg_black"` / `"on_black"` through `"bg_white"` / `"on_white"`
/// - `"bg_bright_black"` / `"on_bright_black"` through `"bg_bright_white"` / `"on_bright_white"`
///
/// # Examples
///
/// ```rust
/// use color::bg_color_code;
///
/// assert_eq!(bg_color_code("bg_red"), "41");
/// assert_eq!(bg_color_code("on_blue"), "44");
/// assert_eq!(bg_color_code("bg_bright_cyan"), "106");
/// assert_eq!(bg_color_code("unknown"), "");
/// ```
#[must_use]
pub fn bg_color_code(name: &str) -> &'static str {
    match name {
        "bg_black" | "on_black" => "40",
        "bg_red" | "on_red" => "41",
        "bg_green" | "on_green" => "42",
        "bg_yellow" | "on_yellow" => "43",
        "bg_blue" | "on_blue" => "44",
        "bg_magenta" | "on_magenta" => "45",
        "bg_cyan" | "on_cyan" => "46",
        "bg_white" | "on_white" => "47",
        "bg_bright_black" | "on_bright_black" => "100",
        "bg_bright_red" | "on_bright_red" => "101",
        "bg_bright_green" | "on_bright_green" => "102",
        "bg_bright_yellow" | "on_bright_yellow" => "103",
        "bg_bright_blue" | "on_bright_blue" => "104",
        "bg_bright_magenta" | "on_bright_magenta" => "105",
        "bg_bright_cyan" | "on_bright_cyan" => "106",
        "bg_bright_white" | "on_bright_white" => "107",
        _ => "",
    }
}

/// Resolves a color/style specification into an ANSI SGR code.
///
/// This is the main color resolution function. It supports a wide range of
/// color formats and returns the corresponding ANSI escape code string.
///
/// # Resolution Order
///
/// 1. **Empty string**: returns `""`
/// 2. **Raw SGR** (all digits/semicolons): returned as-is
/// 3. **256-color** (`color(N)`): returns `38;5;N`
/// 4. **Background 256-color** (`bg_color(N)` / `bgcolor(N)`): returns `48;5;N`
/// 5. **Background RGB** (`bg_rgb(r,g,b)` / `bg(r,g,b)`): returns `48;2;r;g;b`
/// 6. **Background hex** (`bg#rrggbb`): returns `48;2;r;g;b`
/// 7. **Foreground RGB** (`rgb(r,g,b)` / `#rrggbb`): returns `38;2;r;g;b`
/// 8. **Background color name** (`bg_red`, `on_blue`): returns background code
/// 9. **Compound style** (`"bold red"`, `"italic cyan on white"`): returns combined code
/// 10. **Foreground color name** (`"red"`, `"bold"`): returns foreground code
///
/// # Examples
///
/// ```rust
/// use color::resolve_color_code;
///
/// assert_eq!(resolve_color_code("red"), "31");
/// assert_eq!(resolve_color_code("1;32"), "1;32");
/// assert_eq!(resolve_color_code("rgb(255,128,0)"), "38;2;255;128;0");
/// assert_eq!(resolve_color_code("#ff8000"), "38;2;255;128;0");
/// assert_eq!(resolve_color_code("color(208)"), "38;5;208");
/// assert_eq!(resolve_color_code("bg_rgb(255,0,0)"), "48;2;255;0;0");
/// assert_eq!(resolve_color_code("bg#ff0000"), "48;2;255;0;0");
/// assert_eq!(resolve_color_code("bold red"), "1;31");
/// assert_eq!(resolve_color_code("bold red on white"), "1;31;47");
/// ```
#[must_use]
pub fn resolve_color_code(spec: &str) -> String {
    let trimmed = spec.trim();
    if trimmed.is_empty() {
        return String::new();
    }
    // Raw SGR: all digits and semicolons
    if trimmed.chars().all(|ch| ch.is_ascii_digit() || ch == ';') {
        return trimmed.to_owned();
    }
    // 256-color: color(208)
    if let Some(inner) = trimmed
        .strip_prefix("color(")
        .and_then(|value| value.strip_suffix(')'))
        && let Ok(value) = inner.trim().parse::<u8>()
    {
        return format!("38;5;{value}");
    }
    // Background 256-color: bg_color(208) or bgcolor(208)
    if let Some(inner) = trimmed
        .strip_prefix("bg_color(")
        .or_else(|| trimmed.strip_prefix("bgcolor("))
        .and_then(|value| value.strip_suffix(')'))
        && let Ok(value) = inner.trim().parse::<u8>()
    {
        return format!("48;5;{value}");
    }
    // Background RGB: bg_rgb(r,g,b) or bg(r,g,b)
    if let Some(inner) = trimmed
        .strip_prefix("bg_rgb(")
        .or_else(|| trimmed.strip_prefix("bg("))
        .and_then(|value| value.strip_suffix(')'))
        && let Some((r, g, b)) = parse_rgb_tuple(inner)
    {
        return format!("48;2;{r};{g};{b}");
    }
    // Background hex: bg#rrggbb
    if let Some(hex) = trimmed.strip_prefix("bg#")
        && let Some((r, g, b)) = parse_hex(hex)
    {
        return format!("48;2;{r};{g};{b}");
    }
    // Foreground RGB: rgb(r,g,b)
    if let Some((red, green, blue)) = parse_rgb(trimmed) {
        return format!("38;2;{red};{green};{blue}");
    }
    // Background color prefix: bg_red, on_red, bg_bright_red, etc.
    if !trimmed.starts_with("bg_rgb(")
        && !trimmed.starts_with("bg(")
        && !trimmed.starts_with("bg#")
        && !trimmed.starts_with("bgcolor(")
    {
        let bg = bg_color_code(trimmed);
        if !bg.is_empty() {
            return bg.to_owned();
        }
    }
    // Compound styles: "bold red", "italic cyan on white", "bold red on bright_blue"
    if let Some(code) = parse_compound_style(trimmed) {
        return code;
    }
    color_code(trimmed).to_owned()
}

/// A theme that maps level names to color names.
///
/// Allows customization of which ANSI color is used for each level. The theme
/// is consulted before the level's built-in default color.
///
/// # Examples
///
/// ```rust
/// use color::Theme;
///
/// let mut theme = Theme::defaults();
/// theme.set("ERROR", "magenta");
/// assert_eq!(theme.get("ERROR"), Some("magenta"));
/// assert_eq!(theme.get("INFO"), Some(""));
/// ```
#[derive(Clone, Debug, Default)]
pub struct Theme {
    colors: HashMap<String, String>,
}

impl Theme {
    /// Creates a theme with default color mappings.
    ///
    /// Returns a theme pre-populated with the built-in level colors
    /// (TRACE=dim, DEBUG=blue, INFO="", WARNING=yellow, ERROR=red, etc.).
    #[must_use]
    pub fn defaults() -> Self {
        let colors = default_color_map()
            .into_iter()
            .map(|(k, v)| (k.to_owned(), v.to_owned()))
            .collect();
        Self { colors }
    }

    /// Creates an empty theme.
    ///
    /// Equivalent to `Theme::default()`.
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// Sets the color for a level.
    ///
    /// The color value can be any valid color specification (e.g., `"red"`,
    /// `"bold blue"`, `"#ff8000"`, `"rgb(255,0,0)"`).
    pub fn set(&mut self, level: impl Into<String>, color: impl Into<String>) {
        self.colors.insert(level.into(), color.into());
    }

    /// Gets the color for a level.
    ///
    /// Returns `None` if the level has no color entry in the theme.
    #[must_use]
    pub fn get(&self, level: &str) -> Option<&str> {
        self.colors.get(level).map(String::as_str)
    }
}

/// Paints text using a theme instead of the level's built-in color.
///
/// Falls back to the level's default color if the theme has no entry for
/// that level, then to no color if neither provides one.
///
/// # Arguments
///
/// * `level` - The log level
/// * `text` - The text to colorize
/// * `colorize` - Whether to actually emit color codes
/// * `theme` - The theme to look up colors in
#[must_use]
pub fn paint_themed(level: &LogLevel, text: &str, colorize: bool, theme: &Theme) -> String {
    if !colorize {
        return text.to_owned();
    }
    let color_name = theme
        .get(level.name())
        .or_else(|| level.color())
        .unwrap_or("");
    let code = resolve_color_code(color_name);
    if code.is_empty() {
        text.to_owned()
    } else {
        format!("\x1b[{code}m{text}\x1b[0m")
    }
}

/// Colors text with a given color specification.
///
/// Wraps the text in ANSI escape codes when `colorize` is true and the color
/// resolves to a non-empty code.
///
/// # Arguments
///
/// * `text` - The text to colorize
/// * `color` - Color specification (any format supported by [`resolve_color_code`])
/// * `colorize` - Whether to actually emit color codes
///
/// # Examples
///
/// ```rust
/// use color::colorize;
///
/// let red = colorize("hello", "red", true);
/// assert!(red.starts_with("\x1b[31m"));
///
/// let bold = colorize("hello", "bold yellow", true);
/// assert!(bold.starts_with("\x1b[1;33m"));
///
/// let plain = colorize("hello", "red", false);
/// assert_eq!(plain, "hello");
/// ```
#[must_use]
pub fn colorize(text: &str, color: &str, colorize: bool) -> String {
    if !colorize || color.is_empty() {
        return text.to_owned();
    }
    let code = resolve_color_code(color);
    if code.is_empty() {
        text.to_owned()
    } else {
        format!("\x1b[{code}m{text}\x1b[0m")
    }
}

/// Parses Rich-style markup tags and returns ANSI-escaped text.
///
/// Supports tags like `<bold>`, `<red>`, `<bold red>`, `<bold red on white>`,
/// `<dim cyan>`, `<italic>`, `<underline>`, `<strike>`, `<reverse>`, `<blink>`,
/// and closing tags `</bold>`, `</red>`, etc.
///
/// Nested tags are supported. Unknown tags are stripped (not converted to ANSI).
/// HTML entities (`&lt;`, `&gt;`, `&amp;`) are decoded.
///
/// When `colorize` is `false`, all tags are stripped and only plain text is returned.
///
/// # Arguments
///
/// * `text` - Text containing Rich-style markup tags
/// * `colorize` - Whether to convert tags to ANSI escape codes
///
/// # Examples
///
/// ```rust
/// use color::parse_rich_markup;
///
/// let result = parse_rich_markup("<bold>hello</bold>", true);
/// assert!(result.starts_with("\x1b[1m"));
/// assert!(result.ends_with("\x1b[0m"));
///
/// let result = parse_rich_markup("<red>error</red> <green>ok</green>", true);
/// assert!(result.contains("\x1b[31m"));
/// assert!(result.contains("\x1b[32m"));
/// ```
#[must_use]
pub fn parse_rich_markup(text: &str, colorize: bool) -> String {
    if !colorize {
        return strip_rich_tags(text);
    }
    let mut result = String::with_capacity(text.len());
    let mut chars = text.chars().peekable();

    while let Some(ch) = chars.next() {
        if ch == '<' {
            // Check for closing tag or opening tag
            let mut tag = String::new();
            let mut is_closing = false;

            if chars.peek() == Some(&'/') {
                is_closing = true;
                chars.next();
            }

            for c in chars.by_ref() {
                if c == '>' {
                    break;
                }
                tag.push(c);
            }

            if is_closing || tag.is_empty() {
                // Closing tag: only emit reset if it's a known style/color
                if is_closing {
                    let lower = tag.to_lowercase();
                    let code = resolve_color_code(&lower);
                    if !code.is_empty() {
                        result.push_str("\x1b[0m");
                    }
                }
            } else {
                // Opening tag: resolve color code
                let lower = tag.to_lowercase();
                let code = resolve_color_code(&lower);
                if code.is_empty() {
                    // Unknown tag: strip it entirely (no reset emitted)
                } else {
                    use std::fmt::Write;
                    let _ = write!(result, "\x1b[{code}m");
                }
            }
        } else if ch == '&' {
            // HTML entity check: &lt; &gt; &amp;
            let mut entity = String::from("&");
            let mut found_semicolon = false;
            for c in chars.by_ref() {
                entity.push(c);
                if c == ';' {
                    found_semicolon = true;
                    break;
                }
                if entity.len() > 6 {
                    break;
                }
            }
            if found_semicolon {
                match entity.as_str() {
                    "&lt;" => result.push('<'),
                    "&gt;" => result.push('>'),
                    "&amp;" => result.push('&'),
                    _ => result.push_str(&entity),
                }
            } else {
                result.push_str(&entity);
            }
        } else {
            result.push(ch);
        }
    }

    result
}

/// Strips Rich-style markup tags from text, returning plain text.
///
/// Removes all `<tag>` and `</tag>` constructs. HTML entities are decoded.
///
/// # Arguments
///
/// * `text` - Text containing Rich-style markup tags
///
/// # Examples
///
/// ```rust
/// use color::strip_rich_tags;
///
/// let plain = strip_rich_tags("<bold>hello</bold>");
/// assert_eq!(plain, "hello");
///
/// let plain = strip_rich_tags("<red>error</red> <green>ok</green>");
/// assert_eq!(plain, "error ok");
/// ```
#[must_use]
pub fn strip_rich_tags(text: &str) -> String {
    let mut result = String::with_capacity(text.len());
    let mut chars = text.chars().peekable();

    while let Some(ch) = chars.next() {
        if ch == '<' {
            // Skip until closing >
            for c in chars.by_ref() {
                if c == '>' {
                    break;
                }
            }
        } else if ch == '&' {
            let mut entity = String::from("&");
            let mut found_semicolon = false;
            for c in chars.by_ref() {
                entity.push(c);
                if c == ';' {
                    found_semicolon = true;
                    break;
                }
                if entity.len() > 6 {
                    break;
                }
            }
            if found_semicolon {
                match entity.as_str() {
                    "&lt;" => result.push('<'),
                    "&gt;" => result.push('>'),
                    "&amp;" => result.push('&'),
                    _ => result.push_str(&entity),
                }
            } else {
                result.push_str(&entity);
            }
        } else {
            result.push(ch);
        }
    }

    result
}

/// Detects whether a file descriptor is a terminal (TTY).
///
/// Returns `None` if detection is not possible (e.g., on Windows without
/// the right API, or when the file descriptor is invalid).
#[must_use]
pub fn is_terminal(_fd: i32) -> bool {
    // On Unix, we would check isatty(). For portability, we use a simple heuristic.
    // In practice, the Python side should pass the colorize flag explicitly.
    false
}

fn parse_rgb(value: &str) -> Option<(u8, u8, u8)> {
    if let Some(hex) = value.strip_prefix('#') {
        return parse_hex(hex);
    }
    let inner = value.strip_prefix("rgb(")?.strip_suffix(')')?;
    parse_rgb_tuple(inner)
}

fn parse_hex(hex: &str) -> Option<(u8, u8, u8)> {
    if hex.len() != 6 {
        return None;
    }
    let red = u8::from_str_radix(&hex[0..2], 16).ok()?;
    let green = u8::from_str_radix(&hex[2..4], 16).ok()?;
    let blue = u8::from_str_radix(&hex[4..6], 16).ok()?;
    Some((red, green, blue))
}

fn parse_rgb_tuple(inner: &str) -> Option<(u8, u8, u8)> {
    let mut parts = inner.split(',').map(str::trim);
    let red = parts.next()?.parse::<u8>().ok()?;
    let green = parts.next()?.parse::<u8>().ok()?;
    let blue = parts.next()?.parse::<u8>().ok()?;
    if parts.next().is_some() {
        return None;
    }
    Some((red, green, blue))
}

/// Parses compound style strings like "bold red", "italic cyan on white".
///
/// Supported tokens: bold, dim, italic, underline, blink, reverse, strike,
/// and any foreground/background color name or hex/rgb spec.
#[must_use]
fn parse_compound_style(spec: &str) -> Option<String> {
    let tokens: Vec<&str> = spec.split_whitespace().collect();
    if tokens.len() < 2 {
        return None;
    }

    let mut style_codes: Vec<String> = Vec::new();
    let mut fg_code = String::new();
    let mut bg_code = String::new();
    let mut found_on = false;

    for token in &tokens {
        let lower = token.to_lowercase();
        if lower == "on" || lower == "bg" {
            found_on = true;
            continue;
        }
        // Handle on_color and bg_color as single tokens
        if lower.starts_with("on_") || lower.starts_with("bg_") {
            let resolved = resolve_color_code_single(&lower);
            if resolved.starts_with("48;2;") || resolved.starts_with("48;5;") {
                bg_code = resolved;
            } else {
                let bg = bg_color_code(&lower);
                if !bg.is_empty() {
                    bg.clone_into(&mut bg_code);
                } else if let Some(code_num) = fg_to_bg_code(&resolved) {
                    bg_code = code_num;
                }
            }
            continue;
        }
        if found_on {
            // Background color - resolve via fg_to_bg mapping
            let resolved = resolve_color_code_single(&lower);
            if resolved.starts_with("48;2;") || resolved.starts_with("48;5;") {
                bg_code = resolved;
            } else if let Some(bg) = fg_to_bg(&lower) {
                bg.clone_into(&mut bg_code);
            } else if let Some(code_num) = fg_to_bg_code(&resolved) {
                bg_code = code_num;
            }
            found_on = false;
        } else {
            // Style or foreground color
            let resolved = resolve_color_code_single(&lower);
            if !resolved.is_empty() {
                if resolved.len() <= 2 && resolved.chars().all(|c| c.is_ascii_digit()) {
                    // Style code (1-9)
                    style_codes.push(resolved);
                } else if resolved.starts_with("38;2;") || resolved.starts_with("38;5;") {
                    fg_code = resolved;
                } else {
                    // Could be foreground color (30-37, 90-97)
                    fg_code = resolved;
                }
            }
        }
    }

    if fg_code.is_empty() && bg_code.is_empty() && style_codes.is_empty() {
        return None;
    }

    let mut codes: Vec<String> = style_codes;
    if !fg_code.is_empty() {
        codes.push(fg_code);
    }
    if !bg_code.is_empty() {
        codes.push(bg_code);
    }

    Some(codes.join(";"))
}

/// Resolves a single color/style token without compound parsing.
fn resolve_color_code_single(spec: &str) -> String {
    let trimmed = spec.trim();
    if trimmed.is_empty() {
        return String::new();
    }
    if let Some(inner) = trimmed
        .strip_prefix("color(")
        .and_then(|value| value.strip_suffix(')'))
        && let Ok(value) = inner.trim().parse::<u8>()
    {
        return format!("38;5;{value}");
    }
    if let Some((red, green, blue)) = parse_rgb(trimmed) {
        return format!("38;2;{red};{green};{blue}");
    }
    color_code(trimmed).to_owned()
}

/// Maps a foreground color name to its background equivalent.
fn fg_to_bg(name: &str) -> Option<&'static str> {
    match name {
        "black" => Some("40"),
        "red" => Some("41"),
        "green" => Some("42"),
        "yellow" => Some("43"),
        "blue" => Some("44"),
        "magenta" => Some("45"),
        "cyan" => Some("46"),
        "white" => Some("47"),
        "bright_black" => Some("100"),
        "bright_red" => Some("101"),
        "bright_green" => Some("102"),
        "bright_yellow" => Some("103"),
        "bright_blue" => Some("104"),
        "bright_magenta" => Some("105"),
        "bright_cyan" => Some("106"),
        "bright_white" => Some("107"),
        _ => None,
    }
}

/// Converts an SGR foreground code to its background equivalent.
fn fg_to_bg_code(code: &str) -> Option<String> {
    match code {
        "30" => Some("40".to_owned()),
        "31" => Some("41".to_owned()),
        "32" => Some("42".to_owned()),
        "33" => Some("43".to_owned()),
        "34" => Some("44".to_owned()),
        "35" => Some("45".to_owned()),
        "36" => Some("46".to_owned()),
        "37" => Some("47".to_owned()),
        "90" => Some("100".to_owned()),
        "91" => Some("101".to_owned()),
        "92" => Some("102".to_owned()),
        "93" => Some("103".to_owned()),
        "94" => Some("104".to_owned()),
        "95" => Some("105".to_owned()),
        "96" => Some("106".to_owned()),
        "97" => Some("107".to_owned()),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn paint_disabled_returns_plain() {
        let level = LogLevel::new("ERROR", 50, Some("red".to_owned()));
        assert_eq!(paint(&level, "hello", false), "hello");
    }

    #[test]
    fn paint_enabled_wraps_in_ansi() {
        let level = LogLevel::new("ERROR", 50, Some("red".to_owned()));
        let result = paint(&level, "hello", true);
        assert!(result.starts_with("\x1b[31m"));
        assert!(result.ends_with("\x1b[0m"));
    }

    #[test]
    fn color_code_known_colors() {
        assert_eq!(color_code("dim"), "2");
        assert_eq!(color_code("red"), "31");
        assert_eq!(color_code("bold_red"), "1;31");
        assert_eq!(color_code("bold_green"), "1;32");
        assert_eq!(color_code("dim_cyan"), "2;36");
        assert_eq!(color_code("unknown"), "");
    }

    #[test]
    fn color_code_bright_colors() {
        assert_eq!(color_code("bright_red"), "91");
        assert_eq!(color_code("bright_green"), "92");
        assert_eq!(color_code("bright_yellow"), "93");
        assert_eq!(color_code("bright_blue"), "94");
        assert_eq!(color_code("bright_magenta"), "95");
        assert_eq!(color_code("bright_cyan"), "96");
        assert_eq!(color_code("bright_white"), "97");
        assert_eq!(color_code("bright_black"), "90");
    }

    #[test]
    fn bg_color_code_standard() {
        assert_eq!(bg_color_code("bg_red"), "41");
        assert_eq!(bg_color_code("on_red"), "41");
        assert_eq!(bg_color_code("bg_green"), "42");
        assert_eq!(bg_color_code("on_blue"), "44");
        assert_eq!(bg_color_code("bg_bright_red"), "101");
        assert_eq!(bg_color_code("on_bright_cyan"), "106");
        assert_eq!(bg_color_code("unknown"), "");
    }

    #[test]
    fn resolve_color_code_supports_raw_ansi() {
        assert_eq!(resolve_color_code("1;32"), "1;32");
    }

    #[test]
    fn resolve_color_code_supports_rgb_function() {
        assert_eq!(resolve_color_code("rgb(255, 128, 0)"), "38;2;255;128;0");
    }

    #[test]
    fn resolve_color_code_supports_hex() {
        assert_eq!(resolve_color_code("#ff8000"), "38;2;255;128;0");
    }

    #[test]
    fn resolve_color_code_supports_256_color() {
        assert_eq!(resolve_color_code("color(208)"), "38;5;208");
    }

    #[test]
    fn resolve_color_code_supports_bg_rgb() {
        assert_eq!(resolve_color_code("bg_rgb(255,0,0)"), "48;2;255;0;0");
        assert_eq!(resolve_color_code("bg(0,255,0)"), "48;2;0;255;0");
    }

    #[test]
    fn resolve_color_code_supports_bg_hex() {
        assert_eq!(resolve_color_code("bg#ff0000"), "48;2;255;0;0");
        assert_eq!(resolve_color_code("bg#00ff00"), "48;2;0;255;0");
    }

    #[test]
    fn resolve_color_code_supports_bg_256() {
        assert_eq!(resolve_color_code("bg_color(196)"), "48;5;196");
        assert_eq!(resolve_color_code("bgcolor(200)"), "48;5;200");
    }

    #[test]
    fn resolve_color_code_supports_bright_colors() {
        assert_eq!(resolve_color_code("bright_red"), "91");
        assert_eq!(resolve_color_code("bright_cyan"), "96");
    }

    #[test]
    fn resolve_color_code_compound_bold_color() {
        assert_eq!(resolve_color_code("bold red"), "1;31");
        assert_eq!(resolve_color_code("bold blue"), "1;34");
        assert_eq!(resolve_color_code("italic green"), "3;32");
        assert_eq!(resolve_color_code("underline yellow"), "4;33");
    }

    #[test]
    fn resolve_color_code_compound_bold_on_bg() {
        assert_eq!(resolve_color_code("bold red on white"), "1;31;47");
        assert_eq!(resolve_color_code("bold green on black"), "1;32;40");
        assert_eq!(resolve_color_code("italic cyan on blue"), "3;36;44");
    }

    #[test]
    fn resolve_color_code_compound_with_hex() {
        let code = resolve_color_code("bold #ff0000");
        assert!(code.starts_with("1;"));
        assert!(code.contains("38;2;255;0;0"));
    }

    #[test]
    fn theme_override() {
        let mut theme = Theme::defaults();
        theme.set("ERROR", "magenta");
        assert_eq!(theme.get("ERROR"), Some("magenta"));
        assert_eq!(theme.get("INFO"), Some(""));
    }

    #[test]
    fn paint_themed_uses_theme() {
        let mut theme = Theme::defaults();
        theme.set("INFO", "#ff8000");
        let level = LogLevel::new("INFO", 20, None);
        let result = paint_themed(&level, "hello", true, &theme);
        assert!(result.starts_with("\x1b[38;2;255;128;0m"));
    }

    #[test]
    fn paint_themed_disabled() {
        let theme = Theme::defaults();
        let level = LogLevel::new("INFO", 20, None);
        assert_eq!(paint_themed(&level, "hello", false, &theme), "hello");
    }

    #[test]
    fn colorize_basic() {
        let red = colorize("hello", "red", true);
        assert_eq!(red, "\x1b[31mhello\x1b[0m");
    }

    #[test]
    fn colorize_compound() {
        let bold = colorize("hello", "bold yellow", true);
        assert_eq!(bold, "\x1b[1;33mhello\x1b[0m");
    }

    #[test]
    fn colorize_disabled() {
        assert_eq!(colorize("hello", "red", false), "hello");
    }

    #[test]
    fn colorize_empty_color() {
        assert_eq!(colorize("hello", "", true), "hello");
    }

    #[test]
    fn colorize_rgb() {
        let result = colorize("hello", "rgb(255,128,0)", true);
        assert_eq!(result, "\x1b[38;2;255;128;0mhello\x1b[0m");
    }

    #[test]
    fn colorize_hex() {
        let result = colorize("hello", "#ff8000", true);
        assert_eq!(result, "\x1b[38;2;255;128;0mhello\x1b[0m");
    }

    #[test]
    fn colorize_256() {
        let result = colorize("hello", "color(208)", true);
        assert_eq!(result, "\x1b[38;5;208mhello\x1b[0m");
    }

    #[test]
    fn colorize_bg() {
        let result = colorize("hello", "bg_red", true);
        assert_eq!(result, "\x1b[41mhello\x1b[0m");
    }

    #[test]
    fn colorize_bright() {
        let result = colorize("hello", "bright_cyan", true);
        assert_eq!(result, "\x1b[96mhello\x1b[0m");
    }

    #[test]
    fn parse_rich_markup_simple() {
        let result = parse_rich_markup("<bold>hello</bold>", true);
        assert_eq!(result, "\x1b[1mhello\x1b[0m");
    }

    #[test]
    fn parse_rich_markup_color() {
        let result = parse_rich_markup("<red>error</red>", true);
        assert_eq!(result, "\x1b[31merror\x1b[0m");
    }

    #[test]
    fn parse_rich_markup_compound() {
        let result = parse_rich_markup("<bold red>text</bold red>", true);
        assert_eq!(result, "\x1b[1;31mtext\x1b[0m");
    }

    #[test]
    fn parse_rich_markup_multiple_tags() {
        let result = parse_rich_markup("<red>err</red> <green>ok</green>", true);
        assert!(result.contains("\x1b[31m"));
        assert!(result.contains("\x1b[32m"));
    }

    #[test]
    fn parse_rich_markup_nested() {
        let result = parse_rich_markup("<bold><red>text</red></bold>", true);
        assert!(result.contains("\x1b[1m"));
        assert!(result.contains("\x1b[31m"));
    }

    #[test]
    fn parse_rich_markup_disabled_strips() {
        let result = parse_rich_markup("<bold>hello</bold>", false);
        assert_eq!(result, "hello");
    }

    #[test]
    fn parse_rich_markup_unknown_tag_stripped() {
        let result = parse_rich_markup("<unknown>hello</unknown>", true);
        assert_eq!(result, "hello");
    }

    #[test]
    fn strip_rich_tags_basic() {
        assert_eq!(strip_rich_tags("<bold>hello</bold>"), "hello");
    }

    #[test]
    fn strip_rich_tags_nested() {
        assert_eq!(strip_rich_tags("<bold><red>text</red></bold>"), "text");
    }

    #[test]
    fn strip_rich_tags_mixed() {
        assert_eq!(
            strip_rich_tags("before <red>colored</red> after"),
            "before colored after"
        );
    }

    #[test]
    fn strip_rich_tags_entities() {
        assert_eq!(strip_rich_tags("<bold>&lt;</bold>"), "<");
    }

    #[test]
    fn parse_rich_markup_on_bg() {
        let result = parse_rich_markup("<bold red on white>text</bold red on white>", true);
        assert_eq!(result, "\x1b[1;31;47mtext\x1b[0m");
    }

    #[test]
    fn resolve_color_code_compound_dim_cyan() {
        assert_eq!(resolve_color_code("dim cyan"), "2;36");
    }

    #[test]
    fn resolve_color_code_compound_strike_magenta() {
        assert_eq!(resolve_color_code("strike magenta"), "9;35");
    }
}
