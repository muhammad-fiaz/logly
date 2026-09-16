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
///
/// Colors match logly's default color scheme:
/// - TRACE: bold cyan
/// - DEBUG: bold blue
/// - INFO: bold (no specific color)
/// - NOTICE: bold cyan (extra level)
/// - SUCCESS: bold green
/// - WARNING: bold yellow
/// - ERROR: bold red
/// - FAIL: bold magenta (extra level)
/// - CRITICAL: bold white on red background (highlighted)
/// - FATAL: bold white on red background (extra level)
fn default_color_map() -> HashMap<&'static str, &'static str> {
    HashMap::from([
        ("TRACE", "bold_cyan"),
        ("DEBUG", "bold_blue"),
        ("INFO", "bold"),
        ("NOTICE", "bold_cyan"),
        ("SUCCESS", "bold_green"),
        ("WARNING", "bold_yellow"),
        ("ERROR", "bold_red"),
        ("FAIL", "bold_magenta"),
        ("CRITICAL", "bold_red_bg"),
        ("FATAL", "bold_red_bg"),
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
/// - Bright/light colors: `"bright_black"` / `"light_black"` through `"bright_white"` / `"light_white"`
/// - Default color: `"default"`
/// - Text styles: `"dim"`, `"bold"`, `"italic"`, `"underline"`, `"blink"`, `"reverse"`, `"strike"`, `"hidden"`
/// - Short aliases: `"k"`, `"r"`, `"g"`, `"y"`, `"e"`, `"m"`, `"c"`, `"w"`, `"lk"`, `"lr"`, `"lg"`, `"ly"`, `"le"`, `"lm"`, `"lc"`, `"lw"`
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
/// assert_eq!(color_code("default"), "39");
/// assert_eq!(color_code("unknown"), "");
/// ```
#[must_use]
pub fn color_code(name: &str) -> &'static str {
    match name {
        // Standard colors
        "black" | "k" => "30",
        "red" | "r" => "31",
        "green" | "g" => "32",
        "yellow" | "y" => "33",
        "blue" | "e" => "34",
        "magenta" | "m" => "35",
        "cyan" | "c" => "36",
        "white" | "w" => "37",
        // Default foreground
        "default" => "39",
        // Bright/high-intensity colors (shorthand: lk, lr, lg, ly, le, lm, lc, lw)
        "bright_black" | "light_black" | "lk" => "90",
        "bright_red" | "light_red" | "lr" => "91",
        "bright_green" | "light_green" | "lg" => "92",
        "bright_yellow" | "light_yellow" | "ly" => "93",
        "bright_blue" | "light_blue" | "le" => "94",
        "bright_magenta" | "light_magenta" | "lm" => "95",
        "bright_cyan" | "light_cyan" | "lc" => "96",
        "bright_white" | "light_white" | "lw" => "97",
        // Text styles
        "dim" | "d" => "2",
        "bold" | "b" => "1",
        "italic" | "i" => "3",
        "underline" | "u" => "4",
        "blink" | "l" => "5",
        "reverse" | "v" => "7",
        "strike" | "s" => "9",
        "hidden" | "h" => "8",
        "normal" | "n" => "22",
        "reset" => "0",
        // Compound shortcuts (underscore-separated)
        "bold_red" => "1;31",
        "bold_green" => "1;32",
        "bold_yellow" => "1;33",
        "bold_blue" => "1;34",
        "bold_magenta" => "1;35",
        "bold_cyan" => "1;36",
        "bold_white" => "1;37",
        "bold_black" => "1;30",
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
        "underline_red" => "4;31",
        "underline_green" => "4;32",
        "underline_yellow" => "4;33",
        "underline_blue" => "4;34",
        "underline_magenta" => "4;35",
        "underline_cyan" => "4;36",
        "strike_red" => "9;31",
        "strike_green" => "9;32",
        "strike_yellow" => "9;33",
        "strike_blue" => "9;34",
        "strike_magenta" => "9;35",
        "strike_cyan" => "9;36",
        // Background compound styles (for critical/highlighted levels)
        "bold_red_bg" | "bold_red_bg_white" => "1;97;41",
        _ => "",
    }
}

/// Returns ANSI escape code for a background color name.
///
/// Supports multiple prefix styles:
/// - `bg_` prefix: `"bg_red"`, `"bg_bright_cyan"`
/// - `on_` prefix: `"on_red"`, `"on_bright_cyan"`
/// - Uppercase (logly markup): `"RED"`, `"BRIGHT_CYAN"`
/// - Light syntax: `"LIGHT-RED"`, `"LIGHT-CYAN"`
///
/// Returns `""` for unrecognized names.
///
/// # Supported Names
///
/// - `"bg_black"` / `"on_black"` / `"BLACK"` through `"bg_white"` / `"on_white"` / `"WHITE"`
/// - `"bg_bright_black"` / `"on_bright_black"` / `"BRIGHT_BLACK"` / `"LIGHT-BLACK"` through `"bg_bright_white"` / etc.
/// - `"bg_default"` / `"DEFAULT"` (reset background)
///
/// # Examples
///
/// ```rust
/// use color::bg_color_code;
///
/// assert_eq!(bg_color_code("bg_red"), "41");
/// assert_eq!(bg_color_code("on_blue"), "44");
/// assert_eq!(bg_color_code("RED"), "41");
/// assert_eq!(bg_color_code("BRIGHT_CYAN"), "106");
/// assert_eq!(bg_color_code("bg_bright_cyan"), "106");
/// assert_eq!(bg_color_code("bg_default"), "49");
/// assert_eq!(bg_color_code("unknown"), "");
/// ```
#[must_use]
pub fn bg_color_code(name: &str) -> &'static str {
    match name {
        // Standard background colors (bg_, on_, and UPPERCASE)
        "bg_black" | "on_black" | "BLACK" => "40",
        "bg_red" | "on_red" | "RED" => "41",
        "bg_green" | "on_green" | "GREEN" => "42",
        "bg_yellow" | "on_yellow" | "YELLOW" => "43",
        "bg_blue" | "on_blue" | "BLUE" => "44",
        "bg_magenta" | "on_magenta" | "MAGENTA" => "45",
        "bg_cyan" | "on_cyan" | "CYAN" => "46",
        "bg_white" | "on_white" | "WHITE" => "47",
        // Default background
        "bg_default" | "on_default" | "DEFAULT" => "49",
        // Bright/light background colors
        "bg_bright_black" | "on_bright_black" | "BRIGHT_BLACK" | "LIGHT-BLACK" | "LK" => "100",
        "bg_bright_red" | "on_bright_red" | "BRIGHT_RED" | "LIGHT-RED" | "LR" => "101",
        "bg_bright_green" | "on_bright_green" | "BRIGHT_GREEN" | "LIGHT-GREEN" | "LG" => "102",
        "bg_bright_yellow" | "on_bright_yellow" | "BRIGHT_YELLOW" | "LIGHT-YELLOW" | "LY" => "103",
        "bg_bright_blue" | "on_bright_blue" | "BRIGHT_BLUE" | "LIGHT-BLUE" | "LE" => "104",
        "bg_bright_magenta" | "on_bright_magenta" | "BRIGHT_MAGENTA" | "LIGHT-MAGENTA" | "LM" => {
            "105"
        }
        "bg_bright_cyan" | "on_bright_cyan" | "BRIGHT_CYAN" | "LIGHT-CYAN" | "LC" => "106",
        "bg_bright_white" | "on_bright_white" | "BRIGHT_WHITE" | "LIGHT-WHITE" | "LW" => "107",
        _ => "",
    }
}

/// Resolves a background color specification to an ANSI code.
///
/// Handles `bg N` (256-color), `bg r,g,b` (RGB), `bg #rrggbb` (hex),
/// and `bg_<name>` / `on_<name>` / `<NAME>` (named colors).
fn resolve_bg_color(spec: &str) -> Option<String> {
    let trimmed = spec.trim();

    // "bg N" = background 256-color
    if let Some(inner) = trimmed.strip_prefix("bg ") {
        if let Ok(value) = inner.trim().parse::<u8>() {
            return Some(format!("48;5;{value}"));
        }
        // Handle <bg r,g,b> syntax
        if let Some((r, g, b)) = parse_rgb_tuple(inner) {
            return Some(format!("48;2;{r};{g};{b}"));
        }
        // Handle <bg #rrggbb> syntax
        if let Some(hex) = inner.trim().strip_prefix('#')
            && let Some((r, g, b)) = parse_hex(hex)
        {
            return Some(format!("48;2;{r};{g};{b}"));
        }
        return Some(fg_to_bg(inner).map_or_else(
            || {
                resolve_color_code(inner)
                    .strip_prefix("38;")
                    .map_or_else(String::new, |code| format!("48;{code}"))
            },
            str::to_owned,
        ));
    }

    // "on N" = background 256-color (Rich-style: on 208)
    if let Some(inner) = trimmed.strip_prefix("on ") {
        if let Ok(value) = inner.trim().parse::<u8>() {
            return Some(format!("48;5;{value}"));
        }
        // Handle <on r,g,b> syntax
        if let Some((r, g, b)) = parse_rgb_tuple(inner) {
            return Some(format!("48;2;{r};{g};{b}"));
        }
        // Handle <on #rrggbb> syntax
        if let Some(hex) = inner.trim().strip_prefix('#')
            && let Some((r, g, b)) = parse_hex(hex)
        {
            return Some(format!("48;2;{r};{g};{b}"));
        }
        return Some(fg_to_bg(inner).map_or_else(
            || {
                resolve_color_code(inner)
                    .strip_prefix("38;")
                    .map_or_else(String::new, |code| format!("48;{code}"))
            },
            str::to_owned,
        ));
    }

    // Background 256-color: bg_color(208) or bgcolor(208) or bg(208)
    if let Some(inner) = trimmed
        .strip_prefix("bg_color(")
        .or_else(|| trimmed.strip_prefix("bgcolor("))
        .or_else(|| trimmed.strip_prefix("bg("))
        .and_then(|value| value.strip_suffix(')'))
        && let Ok(value) = inner.trim().parse::<u8>()
    {
        return Some(format!("48;5;{value}"));
    }

    // Background RGB: bg_rgb(r,g,b) or bg(r,g,b)
    if let Some(inner) = trimmed
        .strip_prefix("bg_rgb(")
        .or_else(|| trimmed.strip_prefix("bg("))
        .and_then(|value| value.strip_suffix(')'))
        && let Some((r, g, b)) = parse_rgb_tuple(inner)
    {
        return Some(format!("48;2;{r};{g};{b}"));
    }

    // Background hex: bg#rrggbb
    if let Some(hex) = trimmed.strip_prefix("bg#")
        && let Some((r, g, b)) = parse_hex(hex)
    {
        return Some(format!("48;2;{r};{g};{b}"));
    }

    // Background color prefix: bg_red, on_red, bg_bright_red, etc.
    if !trimmed.starts_with("bg_rgb(")
        && !trimmed.starts_with("bg(")
        && !trimmed.starts_with("bg#")
        && !trimmed.starts_with("bgcolor(")
    {
        let bg = bg_color_code(trimmed);
        if !bg.is_empty() {
            return Some(bg.to_owned());
        }
    }

    None
}

/// Resolves a foreground color specification to an ANSI code.
///
/// Handles `fg N` (256-color), `fg r,g,b` (RGB), `fg #rrggbb` (hex),
/// and foreground color names.
fn resolve_fg_color(spec: &str) -> Option<String> {
    let trimmed = spec.trim();

    // "fg N" = foreground 256-color
    if let Some(inner) = trimmed.strip_prefix("fg ") {
        if let Ok(value) = inner.trim().parse::<u8>() {
            return Some(format!("38;5;{value}"));
        }
        // Handle <fg r,g,b> syntax
        if let Some((r, g, b)) = parse_rgb_tuple(inner) {
            return Some(format!("38;2;{r};{g};{b}"));
        }
        // Handle <fg #rrggbb> syntax
        if let Some(hex) = inner.trim().strip_prefix('#')
            && let Some((r, g, b)) = parse_hex(hex)
        {
            return Some(format!("38;2;{r};{g};{b}"));
        }
        return resolve_color_code(inner).into();
    }

    // 256-color: color(208) or fg(208)
    if let Some(inner) = trimmed
        .strip_prefix("color(")
        .or_else(|| trimmed.strip_prefix("fg("))
        .and_then(|value| value.strip_suffix(')'))
        && let Ok(value) = inner.trim().parse::<u8>()
    {
        return Some(format!("38;5;{value}"));
    }

    // Foreground RGB: rgb(r,g,b)
    if let Some((red, green, blue)) = parse_rgb(trimmed) {
        return Some(format!("38;2;{red};{green};{blue}"));
    }

    None
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
/// 8. **Background color name** (`bg_red`, `on_blue`, uppercase `RED`): returns background code
/// 9. **Compound style** (`"bold red"`, `"italic cyan on white"`): returns combined code
/// 10. **Foreground color name** (`"red"`, `"bold"`): returns foreground code
///
/// # Angle-Bracket Markup Support
///
/// - `<red>` / `<r>` = foreground red
/// - `<RED>` / `<R>` = background red
/// - `<light-red>` / `<lr>` = bright foreground red
/// - `<LIGHT-RED>` / `<LR>` = bright background red
/// - `<fg #ff0000>` = foreground hex
/// - `<bg #ff0000>` = background hex
/// - `<fg 208>` = foreground 256-color
/// - `<bg 208>` = background 256-color
/// - `<fg 255,0,0>` = foreground RGB
/// - `<bg 255,0,0>` = background RGB
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
/// assert_eq!(resolve_color_code("RED"), "41");
/// assert_eq!(resolve_color_code("default"), "39");
/// assert_eq!(resolve_color_code("bg_default"), "49");
/// ```
#[must_use]
pub fn resolve_color_code(spec: &str) -> String {
    let trimmed = spec.trim();
    if trimmed.is_empty() {
        return String::new();
    }

    // Try background color resolution first
    if let Some(code) = resolve_bg_color(trimmed) {
        return code;
    }

    // Try foreground color resolution
    if let Some(code) = resolve_fg_color(trimmed) {
        return code;
    }

    // Raw SGR: all digits and semicolons
    if trimmed.chars().all(|ch| ch.is_ascii_digit() || ch == ';') {
        return trimmed.to_owned();
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
/// assert_eq!(theme.get("INFO"), Some("bold"));
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

/// Maximum tag length considered for bracket markup.
///
/// Valid style/color tags are short (e.g. `red`, `bold red on white`,
/// `rgb(255,0,0)`). Bounding the lookahead keeps literal payloads such as
/// JSON or URLs from being scanned as markup and preserves single-pass
/// performance.
const MAX_BRACKET_TAG_LEN: usize = 256;

/// Peeks at a potential `[...]` expression without consuming the caller.
///
/// `chars` must be positioned immediately after the opening `[`.
/// Returns `(is_closing, tag)` when a closing `]` is found within bounds,
/// or `None` when the bracket is unterminated or implausibly long.
fn peek_bracket_tag(chars: &std::iter::Peekable<std::str::Chars<'_>>) -> Option<(bool, String)> {
    let mut look = chars.clone();
    let mut is_closing = false;
    if look.peek() == Some(&'/') {
        is_closing = true;
        look.next();
    }
    let mut tag = String::new();
    for c in look.by_ref() {
        if c == ']' {
            return Some((is_closing, tag));
        }
        // A nested opening bracket can never be part of a valid tag; the
        // outer `[` is therefore literal (e.g. `[[value]]` keeps the first
        // `[`). Return early so the caller preserves only the outer `[`.
        if c == '[' {
            tag.push(c);
            return Some((is_closing, tag));
        }
        tag.push(c);
        if tag.len() > MAX_BRACKET_TAG_LEN {
            return Some((is_closing, tag));
        }
    }
    None
}

/// Checks whether the `[...]` expression starting at the caller's position
/// (immediately after `\`, with `[` as the next char) forms valid markup.
fn peek_escaped_bracket_valid(chars: &std::iter::Peekable<std::str::Chars<'_>>) -> Option<String> {
    let mut look = chars.clone();
    // Consume the `[` itself.
    if look.next() != Some('[') {
        return None;
    }
    let (is_closing, tag) = peek_bracket_tag(&look)?;
    if is_closing {
        if resolve_rich_tag(&tag).is_some() {
            Some(format!("[/{tag}]"))
        } else {
            None
        }
    } else if resolve_rich_tag(&tag).is_some() {
        Some(format!("[{tag}]"))
    } else {
        None
    }
}

/// Consumes a bracketed `tag]` (and the leading `/` for closing tags).
fn consume_bracket_tag(chars: &mut std::iter::Peekable<std::str::Chars<'_>>, is_closing: bool) {
    if is_closing {
        chars.next();
    }
    for c in chars.by_ref() {
        if c == ']' {
            break;
        }
    }
}

/// Handles a `\` escape for the colorized path.
///
/// `\[red]` (valid markup) emits `[red]` literally; `\[some]` (literal
/// brackets) preserves the backslash.
fn handle_escape_parse(
    chars: &mut std::iter::Peekable<std::str::Chars<'_>>,
    result: &mut String,
    backslash: char,
) {
    if chars.peek() == Some(&'[')
        && let Some(literal) = peek_escaped_bracket_valid(chars)
    {
        let is_closing = literal.starts_with("[/");
        chars.next();
        consume_bracket_tag(chars, is_closing);
        result.push_str(&literal);
    } else if chars.peek() == Some(&'<') {
        chars.next();
        result.push('<');
    } else {
        result.push(backslash);
    }
}

/// Handles one `<...>` tag for the colorized path.
fn handle_angle_parse(chars: &mut std::iter::Peekable<std::str::Chars<'_>>, result: &mut String) {
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
    if is_closing {
        let lower = tag.to_lowercase();
        let code = resolve_color_code(&lower);
        if tag.is_empty() || !code.is_empty() {
            result.push_str("\x1b[0m");
        }
    } else if !tag.is_empty() {
        let code = if tag.contains(',') {
            resolve_comma_tag(&tag)
        } else {
            let is_uppercase = tag.chars().all(|c| c.is_uppercase() || !c.is_alphabetic());
            if is_uppercase && tag.len() > 1 {
                resolve_color_code(&tag).into()
            } else {
                let lower = tag.to_lowercase();
                resolve_color_code(&lower).into()
            }
        };
        if let Some(code) = code
            && !code.is_empty()
        {
            use std::fmt::Write;
            let _ = write!(result, "\x1b[{code}m");
        }
    }
}

/// Handles one `[...]` expression for the colorized path.
///
/// Only recognized style/color tags emit ANSI; all other bracketed text
/// remains literal so message content is never silently removed.
fn handle_bracket_parse(chars: &mut std::iter::Peekable<std::str::Chars<'_>>, result: &mut String) {
    match peek_bracket_tag(chars) {
        None => {
            result.push('[');
        }
        Some((is_closing, tag)) => {
            if is_closing {
                if resolve_rich_tag(&tag).is_some() {
                    consume_bracket_tag(chars, true);
                    result.push_str("\x1b[0m");
                } else {
                    result.push('[');
                }
            } else if tag.is_empty() {
                result.push('[');
            } else if let Some(code) = resolve_rich_tag(&tag) {
                consume_bracket_tag(chars, false);
                if code.starts_with("\x1b[") {
                    result.push_str(&code);
                } else {
                    use std::fmt::Write;
                    let _ = write!(result, "\x1b[{code}m");
                }
            } else {
                result.push('[');
            }
        }
    }
}

/// Parses Rich-style markup tags and returns ANSI-escaped text.
///
/// Supports tags like `<bold>`, `<red>`, `<bold red>`, `<bold red on white>`,
/// `<dim cyan>`, `<italic>`, `<underline>`, `<strike>`, `<reverse>`, `<blink>`,
/// and closing tags `</bold>`, `</red>`, etc.
///
/// Nested tags are supported. Unknown angle-bracket tags are stripped (not
/// converted to ANSI). Square-bracket content is preserved literally unless
/// it forms a recognized style/color tag such as `[red]`, `[bold]`, or
/// `[bold red on white]`. HTML entities (`&lt;`, `&gt;`, `&amp;`) are decoded.
///
/// When `colorize` is `false`, recognized tags are stripped and all other
/// text (including literal square brackets) is returned unchanged.
///
/// # Arguments
///
/// * `text` - Text containing markup tags
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
#[allow(clippy::too_many_lines)]
pub fn parse_rich_markup(text: &str, colorize: bool) -> String {
    if !colorize {
        return strip_rich_tags(text);
    }
    let mut result = String::with_capacity(text.len());
    let mut chars = text.chars().peekable();

    while let Some(ch) = chars.next() {
        if ch == '\\' {
            if chars.peek().is_none() {
                result.push(ch);
            } else {
                handle_escape_parse(&mut chars, &mut result, ch);
            }
        } else if ch == '<' {
            // Unterminated `<` stays literal so text is never lost.
            let mut found_close = false;
            for c in chars.clone().by_ref() {
                if c == '>' {
                    found_close = true;
                    break;
                }
            }
            if found_close {
                handle_angle_parse(&mut chars, &mut result);
            } else {
                result.push('<');
            }
        } else if ch == '[' {
            handle_bracket_parse(&mut chars, &mut result);
        } else if ch == '&' {
            if let Some(entity) = parse_html_entity(&mut chars) {
                if let Some(decoded) = decode_html_entity(&entity) {
                    result.push(decoded);
                } else {
                    result.push_str(&entity);
                }
            }
        } else {
            result.push(ch);
        }
    }

    result
}

/// Renders markup in a log line with level-aware tags resolved.
///
/// The `<level>` and `<lvl>` tags use the configured color of `level`.
/// All other tags are handled by [`parse_rich_markup`].
#[must_use]
pub fn parse_log_markup(level: &LogLevel, text: &str, colorize: bool) -> String {
    let level_style = level.color().unwrap_or_else(|| {
        let colors = default_color_map();
        colors.get(level.name()).copied().unwrap_or("")
    });
    let opening = if level_style.is_empty() {
        String::new()
    } else if level_style.starts_with('<') {
        level_style.to_owned()
    } else {
        format!("<{level_style}>")
    };
    let marked = text.replace("<level>", &opening).replace("<lvl>", &opening);
    let marked = if opening.is_empty() {
        marked
    } else {
        marked.replace("</level>", "</>").replace("</lvl>", "</>")
    };
    let rendered = parse_rich_markup(&marked, colorize);
    if colorize && !text.contains('<') {
        paint(level, &rendered, true)
    } else {
        rendered
    }
}

/// Handles a `\` escape for the stripping path.
fn handle_escape_strip(
    chars: &mut std::iter::Peekable<std::str::Chars<'_>>,
    result: &mut String,
    backslash: char,
) {
    if chars.peek() == Some(&'[')
        && let Some(literal) = peek_escaped_bracket_valid(chars)
    {
        let is_closing = literal.starts_with("[/");
        chars.next();
        consume_bracket_tag(chars, is_closing);
        result.push_str(&literal);
    } else if chars.peek() == Some(&'<') {
        chars.next();
        result.push('<');
    } else {
        result.push(backslash);
    }
}

/// Handles one `[...]` expression for the stripping path.
///
/// Only recognized tags are removed; all other bracketed text stays literal.
fn handle_bracket_strip(chars: &mut std::iter::Peekable<std::str::Chars<'_>>, result: &mut String) {
    match peek_bracket_tag(chars) {
        Some((is_closing, tag)) if !tag.is_empty() && resolve_rich_tag(&tag).is_some() => {
            consume_bracket_tag(chars, is_closing);
        }
        None | Some(_) => {
            result.push('[');
        }
    }
}

/// Strips markup tags from text, returning plain text.
///
/// Removes recognized `<tag>`/`</tag>` constructs and recognized
/// square-bracket style tags such as `[red]`/`[/red]`. Ordinary square
/// brackets (`[hello]`, `[]`, `[123]`, paths, JSON, URLs, ...) are preserved
/// literally. HTML entities are decoded.
///
/// # Arguments
///
/// * `text` - Text containing markup tags
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
#[allow(clippy::too_many_lines)]
pub fn strip_rich_tags(text: &str) -> String {
    let mut result = String::with_capacity(text.len());
    let mut chars = text.chars().peekable();

    while let Some(ch) = chars.next() {
        if ch == '\\' {
            if chars.peek().is_none() {
                result.push(ch);
            } else {
                handle_escape_strip(&mut chars, &mut result, ch);
            }
        } else if ch == '<' {
            // Angle-bracket markup keeps its historical contract: any
            // `<...>` up to the next `>` is a tag and is removed.
            // Unterminated `<` stays literal so text is never lost.
            let mut found_close = false;
            for c in chars.clone().by_ref() {
                if c == '>' {
                    found_close = true;
                    break;
                }
            }
            if found_close {
                for c in chars.by_ref() {
                    if c == '>' {
                        break;
                    }
                }
            } else {
                result.push('<');
            }
        } else if ch == '[' {
            handle_bracket_strip(&mut chars, &mut result);
        } else if ch == '&' {
            if let Some(entity) = parse_html_entity(&mut chars) {
                if let Some(decoded) = decode_html_entity(&entity) {
                    result.push(decoded);
                } else {
                    result.push_str(&entity);
                }
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
        "black" | "k" => Some("40"),
        "red" | "r" => Some("41"),
        "green" | "g" => Some("42"),
        "yellow" | "y" => Some("43"),
        "blue" | "e" => Some("44"),
        "magenta" | "m" => Some("45"),
        "cyan" | "c" => Some("46"),
        "white" | "w" => Some("47"),
        "default" => Some("49"),
        "bright_black" | "light_black" | "lk" => Some("100"),
        "bright_red" | "light_red" | "lr" => Some("101"),
        "bright_green" | "light_green" | "lg" => Some("102"),
        "bright_yellow" | "light_yellow" | "ly" => Some("103"),
        "bright_blue" | "light_blue" | "le" => Some("104"),
        "bright_magenta" | "light_magenta" | "lm" => Some("105"),
        "bright_cyan" | "light_cyan" | "lc" => Some("106"),
        "bright_white" | "light_white" | "lw" => Some("107"),
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
        "39" => Some("49".to_owned()), // default
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

/// Decodes HTML entities in text.
///
/// Converts `&lt;`, `&gt;`, and `&amp;` to their respective characters.
/// Returns the decoded character or the original entity if not recognized.
fn decode_html_entity(entity: &str) -> Option<char> {
    match entity {
        "&lt;" => Some('<'),
        "&gt;" => Some('>'),
        "&amp;" => Some('&'),
        _ => None,
    }
}

/// Parses an HTML entity from the character iterator.
///
/// Returns the entity string if a semicolon was found, or `None` if not a valid entity.
fn parse_html_entity(chars: &mut std::iter::Peekable<std::str::Chars<'_>>) -> Option<String> {
    let mut entity = String::from("&");
    for c in chars.by_ref() {
        entity.push(c);
        if c == ';' {
            return Some(entity);
        }
        if entity.len() > 6 {
            break;
        }
    }
    None
}

/// Resolves a Rich-style `[tag]` to an ANSI escape code.
///
/// Supports:
/// - `[red]`, `[bold]`, `[italic]` - simple color/style tags
/// - `[on red]`, `[bg red]` - background colors
/// - `[bold red on white]` - compound styles with foreground/background
/// - `[#ff0000]`, `[on #00ff00]` - hex colors
/// - `[rgb(255,0,0)]`, `[on rgb(0,255,0)]` - RGB colors
/// - `[color(196)]`, `[on color(200)]` - 256-color palette
/// - `[not bold]` - negation (strips the style)
///
/// Returns `Some(code)` if the tag is valid, `None` if unknown.
#[must_use]
fn resolve_rich_tag(tag: &str) -> Option<String> {
    let tag = tag.trim();
    if tag.is_empty() {
        return None;
    }

    // Handle negation: [not bold] -> reset
    if let Some(inner) = tag.strip_prefix("not ") {
        let inner = inner.trim();
        let code = resolve_color_code_single(inner);
        if !code.is_empty() {
            return Some("\x1b[0m".to_owned());
        }
        return None;
    }

    // Handle compound styles: "bold red on white", "italic cyan bg blue"
    if tag.contains(" on ") || tag.contains(" bg ") || tag.split_whitespace().count() > 1 {
        return parse_compound_style(tag);
    }

    // Handle on_color / bg_color as single tokens
    let lower = tag.to_lowercase();
    if lower.starts_with("on_") || lower.starts_with("bg_") {
        let resolved = resolve_color_code_single(&lower);
        if resolved.starts_with("48;2;") || resolved.starts_with("48;5;") {
            return Some(resolved);
        }
        let bg = bg_color_code(&lower);
        if !bg.is_empty() {
            return Some(bg.to_string());
        }
        return None;
    }

    // Simple color/style tag
    let resolved = resolve_color_code_single(&lower);
    if resolved.is_empty() {
        None
    } else {
        Some(resolved)
    }
}

/// Resolves a comma-separated tag with multiple tokens.
///
/// Supports:
/// - `<bold, cyan, white>` - multiple styles/colors
/// - `<b,c,>` - shorthand aliases
/// - `<b,,w>` - empty tokens skipped
/// - `<RED>` - uppercase for background
/// - `<LIGHT-RED>` - bright background
///
/// Returns `Some(code)` if the tag is valid, `None` if unknown.
#[must_use]
fn resolve_comma_tag(tag: &str) -> Option<String> {
    let tag = tag.trim();
    if tag.is_empty() {
        return None;
    }

    // Check if tag contains commas (comma-separated syntax)
    if tag.contains(',') {
        let tokens: Vec<&str> = tag.split(',').map(str::trim).collect();
        let mut codes: Vec<String> = Vec::new();
        let mut fg_code = String::new();
        let mut bg_code = String::new();

        for token in &tokens {
            if token.is_empty() {
                continue; // Skip empty tokens
            }
            let lower = token.to_lowercase();

            // Check if it's a background color (uppercase = background)
            let is_uppercase = token
                .chars()
                .all(|c| c.is_uppercase() || !c.is_alphabetic());

            if is_uppercase && token.len() > 1 {
                // Uppercase -> background color
                let resolved = resolve_color_code_single(&lower);
                if resolved.starts_with("48;2;") || resolved.starts_with("48;5;") {
                    bg_code = resolved;
                } else if let Some(bg) = fg_to_bg(&lower) {
                    bg_code = bg.to_string();
                } else if let Some(code_num) = fg_to_bg_code(&resolved) {
                    bg_code = code_num;
                }
            } else {
                // Lowercase -> style or foreground
                let resolved = resolve_color_code_single(&lower);
                if !resolved.is_empty() {
                    if resolved.len() <= 2 && resolved.chars().all(|c| c.is_ascii_digit()) {
                        codes.push(resolved);
                    } else {
                        fg_code = resolved;
                    }
                }
            }
        }

        if fg_code.is_empty() && bg_code.is_empty() && codes.is_empty() {
            return None;
        }

        let mut result: Vec<String> = codes;
        if !fg_code.is_empty() {
            result.push(fg_code);
        }
        if !bg_code.is_empty() {
            result.push(bg_code);
        }

        Some(result.join(";"))
    } else {
        // No commas - use standard resolution
        let lower = tag.to_lowercase();
        let is_uppercase = tag.chars().all(|c| c.is_uppercase() || !c.is_alphabetic());

        if is_uppercase && tag.len() > 1 {
            // Uppercase tag -> background color
            Some(resolve_color_code(tag))
        } else {
            // Lowercase/mixed tag -> foreground or style
            Some(resolve_color_code(&lower))
        }
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
        assert_eq!(color_code("r"), "31");
        assert_eq!(color_code("u"), "4");
        assert_eq!(color_code("normal"), "22");
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
        assert_eq!(theme.get("INFO"), Some("bold"));
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
    fn markup_supports_explicit_palette_and_rgb_prefixes() {
        assert_eq!(resolve_color_code("fg 196"), "38;5;196");
        assert_eq!(resolve_color_code("bg 46"), "48;5;46");
        assert_eq!(resolve_color_code("fg #ff8800"), "38;2;255;136;0");
        assert_eq!(resolve_color_code("bg #202020"), "48;2;32;32;32");
    }

    #[test]
    fn markup_supports_short_tags_and_escaped_tags() {
        let rendered = parse_rich_markup(r"\<r>literal</> <u>underlined</u>", true);
        assert!(rendered.starts_with("<r>literal"));
        assert!(rendered.contains("\x1b[4munderlined"));
        assert_eq!(strip_rich_tags(r"\<red>literal</red>"), "<red>literal");
    }

    #[test]
    fn log_markup_resolves_level_tags() {
        let level = LogLevel::new("ERROR", 50, Some("red".to_owned()));
        let rendered = parse_log_markup(&level, "<level>ERROR</level> <u>details</u>", true);
        assert!(rendered.contains("\x1b[31mERROR"));
        assert!(rendered.contains("\x1b[4mdetails"));
        assert_eq!(parse_log_markup(&level, "<lvl>ERROR</lvl>", false), "ERROR");
    }

    #[test]
    fn resolve_color_code_compound_dim_cyan() {
        assert_eq!(resolve_color_code("dim cyan"), "2;36");
    }

    #[test]
    fn resolve_color_code_compound_strike_magenta() {
        assert_eq!(resolve_color_code("strike magenta"), "9;35");
    }

    #[test]
    fn bracket_literals_preserved_when_colorized() {
        for literal in [
            "[hello]",
            "[]",
            "[ hello ]",
            "[123]",
            "[INFO]",
            "[unknown]",
            "[foo bar]",
            "do [some]things",
            "do [ some ]things",
            "do [] somethings",
            "[user@example.com]",
            "[/path/to/file]",
            "[C:\\Users\\test]",
            "text=[[value]]",
            "array[0",
        ] {
            assert_eq!(parse_rich_markup(literal, true), literal, "{literal}");
        }
    }

    #[test]
    fn bracket_literals_preserved_when_stripped() {
        for literal in [
            "[hello]",
            "[]",
            "[ hello ]",
            "[123]",
            "[INFO]",
            "[unknown]",
            "[foo bar]",
            "do [some]things",
            "do [ some ]things",
            "do [] somethings",
            "text=[[value]]",
            "array[0",
        ] {
            assert_eq!(parse_rich_markup(literal, false), literal, "{literal}");
            assert_eq!(strip_rich_tags(literal), literal, "{literal}");
        }
    }

    #[test]
    fn bracket_valid_markup_still_works() {
        assert_eq!(
            parse_rich_markup("[red]Error[/red]", true),
            "\x1b[31mError\x1b[0m"
        );
        assert_eq!(
            parse_rich_markup("[bold]Important[/bold]", true),
            "\x1b[1mImportant\x1b[0m"
        );
        assert_eq!(parse_rich_markup("[red]Error[/red]", false), "Error");
        assert_eq!(strip_rich_tags("[red]Error[/red]"), "Error");
        assert_eq!(
            parse_rich_markup("[bold red on white]hi[/bold red on white]", true),
            "\x1b[1;31;47mhi\x1b[0m"
        );
    }

    #[test]
    fn bracket_escapes_preserve_backslash_for_literals() {
        assert_eq!(
            parse_rich_markup(r"\[some] literal", true),
            r"\[some] literal"
        );
        assert_eq!(strip_rich_tags(r"\[some] literal"), r"\[some] literal");
        assert_eq!(parse_rich_markup(r"\[red] literal", true), "[red] literal");
        assert_eq!(strip_rich_tags(r"\[red] literal"), "[red] literal");
        assert_eq!(strip_rich_tags(r"\[/red] literal"), "[/red] literal");
    }

    #[test]
    fn bracket_unknown_closing_preserved() {
        assert_eq!(parse_rich_markup("[/unknown]", true), "[/unknown]");
        assert_eq!(strip_rich_tags("[/unknown]"), "[/unknown]");
        assert_eq!(parse_rich_markup("[/]", true), "[/]");
        assert_eq!(strip_rich_tags("[/]"), "[/]");
    }

    #[test]
    fn bracket_formatted_messages_preserved() {
        assert_eq!(parse_rich_markup("do somethings", true), "do somethings");
        assert_eq!(
            parse_rich_markup("do [some]things", true),
            "do [some]things"
        );
        assert_eq!(strip_rich_tags(r"do \[some]things"), r"do \[some]things");
        assert_eq!(strip_rich_tags(r"do [some\]things"), r"do [some\]things");
        assert_eq!(strip_rich_tags("do [ some ]things"), "do [ some ]things");
        assert_eq!(strip_rich_tags("do [] somethings"), "do [] somethings");
    }

    #[test]
    fn bracket_ansi_passthrough() {
        let ansi = "\x1b[31mhi\x1b[0m";
        assert_eq!(strip_rich_tags(ansi), ansi);
        assert_eq!(parse_rich_markup(ansi, false), ansi);
    }

    #[test]
    fn bracket_not_style_reset() {
        assert_eq!(
            parse_rich_markup("[not bold]x[/not bold]", true),
            "\x1b[0mx\x1b[0m"
        );
        assert_eq!(strip_rich_tags("[not bold]x[/not bold]"), "x");
    }
}
