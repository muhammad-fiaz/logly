//! Source location capture and clickable link generation.
//!
//! Provides utilities for capturing, formatting, and generating clickable
//! source code location links for various editors and terminals.
//!
//! # Features
//!
//! - **Source location capture**: File, line, column, function, module
//! - **Clickable links**: Hyperlinks for VS Code, `IntelliJ`, Sublime, Vim, Emacs, macOS Terminal, iTerm2
//! - **Source context**: Read surrounding lines from source files
//! - **Format tokens**: `{file}`, `{line}`, `{function}`, `{source}` in templates

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use std::fmt;
use std::fmt::Write as _;

/// A captured source code location.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct SourceLocation {
    /// File path (absolute or relative).
    pub file: Option<String>,
    /// Line number (1-indexed).
    pub line: Option<u32>,
    /// Column number (1-indexed).
    pub column: Option<u32>,
    /// Function or method name.
    pub function: Option<String>,
    /// Module or namespace path.
    pub module: Option<String>,
}

impl SourceLocation {
    /// Creates a new empty source location.
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// Sets the file path.
    #[must_use]
    pub fn with_file(mut self, file: impl Into<String>) -> Self {
        self.file = Some(file.into());
        self
    }

    /// Sets the line number (1-indexed).
    #[must_use]
    pub fn with_line(mut self, line: u32) -> Self {
        self.line = Some(line);
        self
    }

    /// Sets the column number (1-indexed).
    #[must_use]
    pub fn with_column(mut self, column: u32) -> Self {
        self.column = Some(column);
        self
    }

    /// Sets the function name.
    #[must_use]
    pub fn with_function(mut self, function: impl Into<String>) -> Self {
        self.function = Some(function.into());
        self
    }

    /// Sets the module path.
    #[must_use]
    pub fn with_module(mut self, module: impl Into<String>) -> Self {
        self.module = Some(module.into());
        self
    }

    /// Returns `true` if the location has a file path.
    #[must_use]
    pub fn has_file(&self) -> bool {
        self.file.is_some()
    }

    /// Returns `true` if the location has both file and line.
    #[must_use]
    pub fn has_file_and_line(&self) -> bool {
        self.file.is_some() && self.line.is_some()
    }

    /// Returns the filename (last component of the file path).
    #[must_use]
    pub fn filename(&self) -> Option<&str> {
        self.file.as_ref().map(|f| {
            std::path::Path::new(f)
                .file_name()
                .and_then(|n| n.to_str())
                .unwrap_or(f)
        })
    }

    /// Formats as `file:line` (e.g., `src/main.rs:42`).
    #[must_use]
    pub fn file_line(&self) -> Option<String> {
        match (&self.file, self.line) {
            (Some(f), Some(l)) => Some(format!("{f}:{l}")),
            (Some(f), None) => Some(f.clone()),
            _ => None,
        }
    }

    /// Formats as `file:line:column` (e.g., `src/main.rs:42:10`).
    #[must_use]
    pub fn file_line_col(&self) -> Option<String> {
        match (&self.file, self.line, self.column) {
            (Some(f), Some(l), Some(c)) => Some(format!("{f}:{l}:{c}")),
            (Some(f), Some(l), None) => Some(format!("{f}:{l}")),
            (Some(f), None, None) => Some(f.clone()),
            _ => None,
        }
    }

    /// Formats as `function (file:line)` (e.g., `main (src/main.rs:42)`).
    #[must_use]
    pub fn function_location(&self) -> Option<String> {
        match (&self.function, &self.file, self.line) {
            (Some(func), Some(f), Some(l)) => Some(format!("{func} ({f}:{l})")),
            (Some(func), Some(f), None) => Some(format!("{func} ({f})")),
            (Some(func), None, _) => Some(func.clone()),
            (None, Some(f), Some(l)) => Some(format!("{f}:{l}")),
            (None, Some(f), None) => Some(f.clone()),
            _ => None,
        }
    }
}

impl fmt::Display for SourceLocation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if let Some(fl) = self.file_line() {
            write!(f, "{fl}")?;
        }
        if let Some(func) = &self.function {
            write!(f, " in {func}")?;
        }
        Ok(())
    }
}

/// Editor/terminal type for clickable link generation.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum LinkFormat {
    /// VS Code `vscode://file/path:line`
    VsCode,
    /// `JetBrains` IDEs `file:///path:line`
    JetBrains,
    /// Sublime Text `subl://open?url=file:///path&line=line`
    Sublime,
    /// macOS Terminal.app `file:///path:line`
    MacTerminal,
    /// iTerm2 with `iterm2://` URL
    Iterm2,
    /// Vim `+line path`
    Vim,
    /// Emacs `path:line:col`
    Emacs,
    /// Generic file URI `file:///path:line`
    FileUri,
    /// Plain text `path:line` (no link)
    #[default]
    Plain,
    /// Hyperlink escape `\e]8;;URL\e\\text\e]8;;\e\\`
    Hyperlink,
}

impl fmt::Display for LinkFormat {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::VsCode => write!(f, "vscode"),
            Self::JetBrains => write!(f, "jetbrains"),
            Self::Sublime => write!(f, "sublime"),
            Self::MacTerminal => write!(f, "mac-terminal"),
            Self::Iterm2 => write!(f, "iterm2"),
            Self::Vim => write!(f, "vim"),
            Self::Emacs => write!(f, "emacs"),
            Self::FileUri => write!(f, "file-uri"),
            Self::Plain => write!(f, "plain"),
            Self::Hyperlink => write!(f, "hyperlink"),
        }
    }
}

/// Generates a clickable link for the given source location.
///
/// # Errors
///
/// Returns `None` if the location lacks required fields (file path).
#[must_use]
pub fn clickable_link(loc: &SourceLocation, format: LinkFormat) -> Option<String> {
    let file = loc.file.as_deref()?;
    let line = loc.line.unwrap_or(1);
    let col = loc.column.unwrap_or(1);

    let normalized = normalize_path(file);
    let file_uri = format!("file:///{normalized}");

    match format {
        LinkFormat::VsCode => Some(format!("vscode://file/{normalized}:{line}:{col}")),
        LinkFormat::JetBrains | LinkFormat::FileUri => Some(format!("{file_uri}:{line}:{col}")),
        LinkFormat::Sublime => Some(format!(
            "subl://open?url={file_uri}&line={line}&column={col}"
        )),
        LinkFormat::MacTerminal => Some(format!("{file_uri}:{line}")),
        LinkFormat::Iterm2 => Some(format!(
            "iterm2://shell?command=cd%20{normalized}%20%26%26%20open%20{file_uri}:{line}"
        )),
        LinkFormat::Vim => Some(format!("+{line} {normalized}")),
        LinkFormat::Emacs => Some(format!("{normalized}:{line}:{col}")),
        LinkFormat::Plain => Some(format!("{normalized}:{line}")),
        LinkFormat::Hyperlink => {
            let url = format!("{file_uri}:{line}:{col}");
            let text = format!("{normalized}:{line}");
            Some(format!("\x1b]8;;{url}\x1b\\{text}\x1b]8;;\x1b\\"))
        }
    }
}

/// Normalizes a file path for cross-platform display.
///
/// Converts backslashes to forward slashes and removes `./` prefix.
fn normalize_path(path: &str) -> String {
    let normalized = path.replace('\\', "/");
    if let Some(stripped) = normalized.strip_prefix("./") {
        stripped.to_owned()
    } else {
        normalized
    }
}

/// Reads source context (surrounding lines) from a file.
///
/// Returns up to `context_lines` lines before and after the target line.
///
/// # Errors
///
/// Returns an error if the file cannot be read.
pub fn source_context(
    path: &str,
    line: u32,
    context_lines: u32,
) -> Result<Vec<SourceLine>, std::io::Error> {
    let content = std::fs::read_to_string(path)?;
    let target_idx = (line - 1) as usize;
    let total = content.lines().count();
    let start = target_idx.saturating_sub(context_lines as usize);
    let end = (target_idx + context_lines as usize + 1).min(total);

    let mut lines = Vec::new();
    for (idx, text) in content.lines().enumerate() {
        if idx >= start && idx < end {
            let line_num = u32::try_from(idx).unwrap_or(0) + 1;
            lines.push(SourceLine {
                number: line_num,
                text: text.to_owned(),
                is_target: line_num == line,
            });
        }
    }
    Ok(lines)
}

/// A single line of source code context.
#[derive(Clone, Debug)]
pub struct SourceLine {
    /// Line number (1-indexed).
    pub number: u32,
    /// Line content (without newline).
    pub text: String,
    /// Whether this is the target line.
    pub is_target: bool,
}

/// Formats source context lines for display.
///
/// Produces output like:
/// ```text
///    40 |     fn main() {
///    41 |         let x = 42;
/// >> 42 |         println!("{x}");
///    43 |     }
///    44 |
/// ```
#[must_use]
pub fn format_source_context(lines: &[SourceLine], gutter_width: Option<u32>) -> String {
    if lines.is_empty() {
        return String::new();
    }

    let max_num = lines.iter().map(|l| l.number).max().unwrap_or(0);
    let width = gutter_width.unwrap_or_else(|| {
        let mut w = 1;
        let mut n = max_num;
        while n >= 10 {
            w += 1;
            n /= 10;
        }
        w
    });

    let mut out = String::new();
    for line in lines {
        let marker = if line.is_target { ">>" } else { "  " };
        let num_str = format!("{:width$}", line.number, width = width as usize);
        let _ = writeln!(out, "{marker} {num_str} | {}", line.text);
    }
    out
}

/// Applies a format spec with source location tokens.
///
/// Supported tokens:
/// - `{source}` or `{source:context}` — source `<file:line>` with context lines
/// - `{file}` — source file path
/// - `{line}` — source line number
/// - `{column}` — source column number
/// - `{function}` — function name
/// - `{module}` — module path
#[must_use]
pub fn resolve_source_token(name: &str, loc: &SourceLocation) -> Option<String> {
    match name {
        "file" => loc.file.clone(),
        "line" => loc.line.map(|l| l.to_string()),
        "column" => loc.column.map(|c| c.to_string()),
        "function" => loc.function.clone(),
        "module" => loc.module.clone(),
        "file_line" => loc.file_line(),
        "file_line_col" => loc.file_line_col(),
        "function_location" => loc.function_location(),
        "filename" => loc.filename().map(str::to_owned),
        _ if name.starts_with("source:") => {
            let context_str = &name[7..];
            let context_lines: u32 = context_str.parse().unwrap_or(2);
            let file = loc.file.as_deref()?;
            let line = loc.line.unwrap_or(1);
            source_context(file, line, context_lines)
                .ok()
                .map(|lines| format_source_context(&lines, None))
        }
        "source" => {
            let file = loc.file.as_deref()?;
            let line = loc.line.unwrap_or(1);
            Some(format!("{file}:{line}"))
        }
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn location_new_is_empty() {
        let loc = SourceLocation::new();
        assert!(!loc.has_file());
        assert!(!loc.has_file_and_line());
        assert_eq!(loc.file_line(), None);
    }

    #[test]
    fn location_builder() {
        let loc = SourceLocation::new()
            .with_file("src/main.rs")
            .with_line(42)
            .with_column(10)
            .with_function("main")
            .with_module("my_crate");

        assert!(loc.has_file());
        assert!(loc.has_file_and_line());
        assert_eq!(loc.file.as_deref(), Some("src/main.rs"));
        assert_eq!(loc.line, Some(42));
        assert_eq!(loc.column, Some(10));
        assert_eq!(loc.function.as_deref(), Some("main"));
        assert_eq!(loc.module.as_deref(), Some("my_crate"));
    }

    #[test]
    fn location_file_line() {
        let loc = SourceLocation::new().with_file("src/lib.rs").with_line(10);
        assert_eq!(loc.file_line(), Some("src/lib.rs:10".to_owned()));
    }

    #[test]
    fn location_file_line_col() {
        let loc = SourceLocation::new()
            .with_file("src/lib.rs")
            .with_line(10)
            .with_column(5);
        assert_eq!(loc.file_line_col(), Some("src/lib.rs:10:5".to_owned()));
    }

    #[test]
    fn location_function_location() {
        let loc = SourceLocation::new()
            .with_file("src/lib.rs")
            .with_line(10)
            .with_function("my_func");
        assert_eq!(
            loc.function_location(),
            Some("my_func (src/lib.rs:10)".to_owned())
        );
    }

    #[test]
    fn location_filename() {
        let loc = SourceLocation::new().with_file("/path/to/src/main.rs");
        assert_eq!(loc.filename(), Some("main.rs"));
    }

    #[test]
    fn location_display() {
        let loc = SourceLocation::new()
            .with_file("src/main.rs")
            .with_line(42)
            .with_function("main");
        assert_eq!(format!("{loc}"), "src/main.rs:42 in main");
    }

    #[test]
    fn location_display_no_function() {
        let loc = SourceLocation::new().with_file("src/main.rs").with_line(42);
        assert_eq!(format!("{loc}"), "src/main.rs:42");
    }

    #[test]
    fn link_format_vscode() {
        let loc = SourceLocation::new()
            .with_file("src/main.rs")
            .with_line(42)
            .with_column(5);
        let link = clickable_link(&loc, LinkFormat::VsCode).unwrap();
        assert!(link.starts_with("vscode://file/"));
        assert!(link.contains("src/main.rs:42:5"));
    }

    #[test]
    fn link_format_jetbrains() {
        let loc = SourceLocation::new().with_file("src/main.rs").with_line(42);
        let link = clickable_link(&loc, LinkFormat::JetBrains).unwrap();
        assert!(link.starts_with("file:///"));
        assert!(link.contains("src/main.rs:42"));
    }

    #[test]
    fn link_format_plain() {
        let loc = SourceLocation::new().with_file("src/main.rs").with_line(42);
        let link = clickable_link(&loc, LinkFormat::Plain).unwrap();
        assert_eq!(link, "src/main.rs:42");
    }

    #[test]
    fn link_format_vim() {
        let loc = SourceLocation::new().with_file("src/main.rs").with_line(42);
        let link = clickable_link(&loc, LinkFormat::Vim).unwrap();
        assert_eq!(link, "+42 src/main.rs");
    }
}

#[test]
fn link_format_hyperlink() {
    let loc = SourceLocation::new().with_file("src/main.rs").with_line(42);
    let link = clickable_link(&loc, LinkFormat::Hyperlink).unwrap();
    assert!(link.contains("\x1b]8;;"));
    assert!(link.contains("src/main.rs:42"));
}

#[test]
fn link_no_file_returns_none() {
    let loc = SourceLocation::new().with_line(42);
    assert!(clickable_link(&loc, LinkFormat::Plain).is_none());
}

#[test]
fn normalize_path_forward_slash() {
    assert_eq!(normalize_path("src\\main.rs"), "src/main.rs");
}

#[test]
fn normalize_path_strip_dot_slash() {
    assert_eq!(normalize_path("./src/main.rs"), "src/main.rs");
}

#[test]
fn normalize_path_already_normalized() {
    assert_eq!(normalize_path("src/main.rs"), "src/main.rs");
}

#[test]
fn source_context_reads_lines() {
    let dir = std::env::temp_dir().join("logly_source_test");
    let _ = std::fs::create_dir_all(&dir);
    let file = dir.join("test.rs");
    std::fs::write(&file, "line1\nline2\nline3\nline4\nline5\n").unwrap();

    let lines = source_context(file.to_str().unwrap(), 3, 1).unwrap();
    assert_eq!(lines.len(), 3);
    assert_eq!(lines[0].number, 2);
    assert_eq!(lines[0].text, "line2");
    assert!(!lines[0].is_target);
    assert_eq!(lines[1].number, 3);
    assert_eq!(lines[1].text, "line3");
    assert!(lines[1].is_target);
    assert_eq!(lines[2].number, 4);
    assert_eq!(lines[2].text, "line4");
    assert!(!lines[2].is_target);

    let _ = std::fs::remove_dir_all(&dir);
}

#[test]
fn source_context_boundary() {
    let dir = std::env::temp_dir().join("logly_source_test2");
    let _ = std::fs::create_dir_all(&dir);
    let file = dir.join("test.rs");
    std::fs::write(&file, "line1\nline2\nline3\n").unwrap();

    // Line 1 with context 2 before: only lines 1-3 should appear
    let lines = source_context(file.to_str().unwrap(), 1, 2).unwrap();
    assert!(lines.len() <= 3);
    assert!(lines.iter().any(|l| l.is_target));

    let _ = std::fs::remove_dir_all(&dir);
}

#[test]
fn format_source_context_output() {
    let lines = vec![
        SourceLine {
            number: 40,
            text: "fn main() {".to_owned(),
            is_target: false,
        },
        SourceLine {
            number: 41,
            text: "    let x = 42;".to_owned(),
            is_target: false,
        },
        SourceLine {
            number: 42,
            text: "    println!(\"{x}\");".to_owned(),
            is_target: true,
        },
        SourceLine {
            number: 43,
            text: "}".to_owned(),
            is_target: false,
        },
    ];

    let output = format_source_context(&lines, None);
    assert!(output.contains(">> 42"));
    assert!(output.contains("   41"));
    assert!(output.contains("fn main()"));
}

#[test]
fn resolve_source_token_file() {
    let loc = SourceLocation::new().with_file("src/main.rs");
    assert_eq!(
        resolve_source_token("file", &loc),
        Some("src/main.rs".to_owned())
    );
}

#[test]
fn resolve_source_token_line() {
    let loc = SourceLocation::new().with_line(42);
    assert_eq!(resolve_source_token("line", &loc), Some("42".to_owned()));
}

#[test]
fn resolve_source_token_file_line() {
    let loc = SourceLocation::new().with_file("src/main.rs").with_line(42);
    assert_eq!(
        resolve_source_token("file_line", &loc),
        Some("src/main.rs:42".to_owned())
    );
}

#[test]
fn resolve_source_token_unknown() {
    let loc = SourceLocation::new();
    assert_eq!(resolve_source_token("unknown", &loc), None);
}

#[test]
fn location_new_defaults() {
    let loc = SourceLocation::new();
    assert_eq!(loc.file, None);
    assert_eq!(loc.line, None);
    assert_eq!(loc.column, None);
    assert_eq!(loc.function, None);
    assert_eq!(loc.module, None);
}

#[test]
fn location_file_only() {
    let loc = SourceLocation::new().with_file("src/lib.rs");
    assert!(loc.has_file());
    assert!(!loc.has_file_and_line());
}

#[test]
fn location_file_line_only_no_col() {
    let loc = SourceLocation::new().with_file("src/lib.rs").with_line(5);
    assert_eq!(loc.file_line_col(), Some("src/lib.rs:5".to_owned()));
}

#[test]
fn location_function_only() {
    let loc = SourceLocation::new().with_function("helper");
    assert_eq!(loc.function_location(), Some("helper".to_owned()));
}

#[test]
fn location_function_no_file() {
    let loc = SourceLocation::new().with_function("helper");
    assert_eq!(loc.function_location(), Some("helper".to_owned()));
}

#[test]
fn location_file_no_line_no_function_display() {
    let loc = SourceLocation::new().with_file("src/main.rs");
    assert_eq!(format!("{loc}"), "src/main.rs");
}

#[test]
fn location_empty_display() {
    let loc = SourceLocation::new();
    assert_eq!(format!("{loc}"), "");
}

#[test]
fn location_filename_with_path() {
    let loc = SourceLocation::new().with_file("deep/nested/path/to/file.txt");
    assert_eq!(loc.filename(), Some("file.txt"));
}

#[test]
fn location_filename_single_component() {
    let loc = SourceLocation::new().with_file("main.rs");
    assert_eq!(loc.filename(), Some("main.rs"));
}

#[test]
fn link_format_sublime() {
    let loc = SourceLocation::new()
        .with_file("src/main.rs")
        .with_line(42)
        .with_column(5);
    let link = clickable_link(&loc, LinkFormat::Sublime).unwrap();
    assert!(link.starts_with("subl://open?url="));
    assert!(link.contains("line=42"));
    assert!(link.contains("column=5"));
}

#[test]
fn link_format_mac_terminal() {
    let loc = SourceLocation::new().with_file("src/main.rs").with_line(42);
    let link = clickable_link(&loc, LinkFormat::MacTerminal).unwrap();
    assert!(link.starts_with("file:///"));
    assert!(link.contains("src/main.rs:42"));
}

#[test]
fn link_format_iterm2() {
    let loc = SourceLocation::new().with_file("src/main.rs").with_line(42);
    let link = clickable_link(&loc, LinkFormat::Iterm2).unwrap();
    assert!(link.starts_with("iterm2://shell?command="));
    assert!(link.contains("src/main.rs"));
}

#[test]
fn link_format_file_uri() {
    let loc = SourceLocation::new()
        .with_file("src/main.rs")
        .with_line(10)
        .with_column(3);
    let link = clickable_link(&loc, LinkFormat::FileUri).unwrap();
    assert!(link.starts_with("file:///"));
    assert!(link.contains("src/main.rs:10:3"));
}

#[test]
fn link_format_hyperlink_contains_escapes() {
    let loc = SourceLocation::new().with_file("src/main.rs").with_line(42);
    let link = clickable_link(&loc, LinkFormat::Hyperlink).unwrap();
    assert!(link.contains("\x1b]8;;"));
    assert!(link.contains("\x1b\\"));
    assert!(link.contains("src/main.rs:42"));
}

#[test]
fn link_format_vscode_contains_vscode_prefix() {
    let loc = SourceLocation::new()
        .with_file("src/lib.rs")
        .with_line(100)
        .with_column(1);
    let link = clickable_link(&loc, LinkFormat::VsCode).unwrap();
    assert!(link.starts_with("vscode://file/"));
    assert!(link.contains("src/lib.rs:100:1"));
}

#[test]
fn link_format_vim_default_line() {
    let loc = SourceLocation::new().with_file("src/main.rs");
    let link = clickable_link(&loc, LinkFormat::Vim).unwrap();
    assert_eq!(link, "+1 src/main.rs");
}

#[test]
fn link_format_emacs_default_col() {
    let loc = SourceLocation::new().with_file("src/main.rs").with_line(5);
    let link = clickable_link(&loc, LinkFormat::Emacs).unwrap();
    assert_eq!(link, "src/main.rs:5:1");
}

#[test]
fn link_format_plain_default_line() {
    let loc = SourceLocation::new().with_file("src/main.rs");
    let link = clickable_link(&loc, LinkFormat::Plain).unwrap();
    assert_eq!(link, "src/main.rs:1");
}

#[test]
fn normalize_path_complex_backslash() {
    assert_eq!(
        normalize_path("C:\\Users\\test\\file.rs"),
        "C:/Users/test/file.rs"
    );
}

#[test]
fn normalize_path_multiple_dot_slash() {
    assert_eq!(normalize_path("././src/main.rs"), "./src/main.rs");
}

#[test]
fn normalize_path_no_prefix() {
    assert_eq!(normalize_path("src/main.rs"), "src/main.rs");
}

#[test]
fn normalize_path_dot_slash_only() {
    assert_eq!(normalize_path("./file.rs"), "file.rs");
}

#[test]
fn source_context_zero_context_lines() {
    let dir = std::env::temp_dir().join("logly_source_test_zero_ctx");
    let _ = std::fs::create_dir_all(&dir);
    let file = dir.join("test.rs");
    std::fs::write(&file, "line1\nline2\nline3\n").unwrap();

    let lines = source_context(file.to_str().unwrap(), 2, 0).unwrap();
    assert_eq!(lines.len(), 1);
    assert_eq!(lines[0].number, 2);
    assert!(lines[0].is_target);

    let _ = std::fs::remove_dir_all(&dir);
}

#[test]
fn source_context_large_context() {
    let dir = std::env::temp_dir().join("logly_source_test_large_ctx");
    let _ = std::fs::create_dir_all(&dir);
    let file = dir.join("test.rs");
    std::fs::write(&file, "line1\nline2\nline3\n").unwrap();

    let lines = source_context(file.to_str().unwrap(), 2, 100).unwrap();
    assert_eq!(lines.len(), 3);
    assert!(lines.iter().any(|l| l.is_target && l.number == 2));

    let _ = std::fs::remove_dir_all(&dir);
}

#[test]
fn source_context_last_line() {
    let dir = std::env::temp_dir().join("logly_source_test_last");
    let _ = std::fs::create_dir_all(&dir);
    let file = dir.join("test.rs");
    std::fs::write(&file, "line1\nline2\nline3\n").unwrap();

    let lines = source_context(file.to_str().unwrap(), 3, 1).unwrap();
    assert_eq!(lines.len(), 2);
    assert!(lines.iter().any(|l| l.is_target && l.number == 3));

    let _ = std::fs::remove_dir_all(&dir);
}

#[test]
fn format_source_context_empty() {
    let output = format_source_context(&[], None);
    assert!(output.is_empty());
}

#[test]
fn format_source_context_custom_gutter() {
    let lines = vec![
        SourceLine {
            number: 1,
            text: "a".to_owned(),
            is_target: false,
        },
        SourceLine {
            number: 2,
            text: "b".to_owned(),
            is_target: true,
        },
    ];
    let output = format_source_context(&lines, Some(5));
    assert!(output.contains(">>     2"));
    assert!(output.contains("      1"));
}

#[test]
fn format_source_context_target_marker() {
    let lines = vec![
        SourceLine {
            number: 10,
            text: "before".to_owned(),
            is_target: false,
        },
        SourceLine {
            number: 11,
            text: "target".to_owned(),
            is_target: true,
        },
        SourceLine {
            number: 12,
            text: "after".to_owned(),
            is_target: false,
        },
    ];
    let output = format_source_context(&lines, None);
    assert!(output.contains(">> 11"));
    assert!(!output.contains(">> 10"));
    assert!(!output.contains(">> 12"));
}

#[test]
fn resolve_source_token_column() {
    let loc = SourceLocation::new().with_column(5);
    assert_eq!(resolve_source_token("column", &loc), Some("5".to_owned()));
}

#[test]
fn resolve_source_token_module() {
    let loc = SourceLocation::new().with_module("my_module");
    assert_eq!(
        resolve_source_token("module", &loc),
        Some("my_module".to_owned())
    );
}

#[test]
fn resolve_source_token_filename() {
    let loc = SourceLocation::new().with_file("/path/to/file.rs");
    assert_eq!(
        resolve_source_token("filename", &loc),
        Some("file.rs".to_owned())
    );
}

#[test]
fn resolve_source_token_function_location() {
    let loc = SourceLocation::new()
        .with_file("src/lib.rs")
        .with_line(10)
        .with_function("my_func");
    assert_eq!(
        resolve_source_token("function_location", &loc),
        Some("my_func (src/lib.rs:10)".to_owned())
    );
}

#[test]
fn resolve_source_token_source() {
    let loc = SourceLocation::new().with_file("src/main.rs").with_line(42);
    assert_eq!(
        resolve_source_token("source", &loc),
        Some("src/main.rs:42".to_owned())
    );
}

#[test]
fn resolve_source_token_source_no_line() {
    let loc = SourceLocation::new().with_file("src/main.rs");
    assert_eq!(
        resolve_source_token("source", &loc),
        Some("src/main.rs:1".to_owned())
    );
}

#[test]
fn resolve_source_token_file_line_col() {
    let loc = SourceLocation::new()
        .with_file("src/lib.rs")
        .with_line(10)
        .with_column(5);
    assert_eq!(
        resolve_source_token("file_line_col", &loc),
        Some("src/lib.rs:10:5".to_owned())
    );
}

#[test]
fn link_format_jetbrains_contains_file_scheme() {
    let loc = SourceLocation::new()
        .with_file("src/main.rs")
        .with_line(42)
        .with_column(7);
    let link = clickable_link(&loc, LinkFormat::JetBrains).unwrap();
    assert!(link.starts_with("file:///"));
    assert!(link.contains("src/main.rs:42:7"));
}

#[test]
fn source_context_nonexistent_file() {
    let result = source_context("/nonexistent/path/file.rs", 1, 1);
    assert!(result.is_err());
}
