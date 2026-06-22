//! Record filters and level gates.
//!
//! Provides the `Filter` trait, a level-threshold filter, composable filter
//! chains (AND/OR), and support for custom filter callables from Python.

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use levels::LogLevel;
use record::LogRecord;
use std::sync::Arc;

/// Decides whether a record should reach a sink.
pub trait Filter: Send + Sync {
    /// Returns `true` when the record is accepted.
    fn accept(&self, record: &LogRecord) -> bool;
}

/// Filters records below a threshold level.
///
/// # Examples
///
/// ```rust
/// use filter::{Filter, LevelFilter};
/// use levels::LogLevel;
/// use record::LogRecord;
///
/// let filter = LevelFilter::new(LogLevel::new("WARNING", 40, None));
/// let info = LogRecord::builder(LogLevel::new("INFO", 20, None), "msg").build();
/// let warn = LogRecord::builder(LogLevel::new("WARNING", 40, None), "msg").build();
///
/// assert!(!filter.accept(&info));
/// assert!(filter.accept(&warn));
/// ```
#[derive(Clone, Debug)]
pub struct LevelFilter {
    minimum: LogLevel,
}

impl LevelFilter {
    /// Creates a level-threshold filter.
    #[must_use]
    pub const fn new(minimum: LogLevel) -> Self {
        Self { minimum }
    }
}

impl Filter for LevelFilter {
    fn accept(&self, record: &LogRecord) -> bool {
        record.level >= self.minimum
    }
}

/// A composable filter chain that combines multiple filters.
///
/// Supports AND (all must pass) and OR (any must pass) composition.
pub enum FilterChain {
    /// All filters must accept (logical AND).
    All(Vec<Arc<dyn Filter>>),
    /// Any filter must accept (logical OR).
    Any(Vec<Arc<dyn Filter>>),
}

impl std::fmt::Debug for FilterChain {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::All(_) => write!(f, "FilterChain::All({} filters)", 0),
            Self::Any(_) => write!(f, "FilterChain::Any({} filters)", 0),
        }
    }
}

impl Clone for FilterChain {
    fn clone(&self) -> Self {
        match self {
            Self::All(filters) => Self::All(filters.clone()),
            Self::Any(filters) => Self::Any(filters.clone()),
        }
    }
}

impl FilterChain {
    /// Creates an AND chain.
    #[must_use]
    pub fn all(filters: Vec<Arc<dyn Filter>>) -> Self {
        Self::All(filters)
    }

    /// Creates an OR chain.
    #[must_use]
    pub fn any(filters: Vec<Arc<dyn Filter>>) -> Self {
        Self::Any(filters)
    }
}

impl Filter for FilterChain {
    fn accept(&self, record: &LogRecord) -> bool {
        match self {
            Self::All(filters) => filters.iter().all(|f| f.accept(record)),
            Self::Any(filters) => filters.iter().any(|f| f.accept(record)),
        }
    }
}

/// A filter that accepts records whose name starts with a given prefix.
#[derive(Clone, Debug)]
pub struct PrefixFilter {
    prefix: String,
}

impl PrefixFilter {
    /// Creates a prefix filter.
    #[must_use]
    pub fn new(prefix: impl Into<String>) -> Self {
        Self {
            prefix: prefix.into(),
        }
    }
}

impl Filter for PrefixFilter {
    fn accept(&self, record: &LogRecord) -> bool {
        record.name.starts_with(&self.prefix)
    }
}

/// A filter that accepts records containing specific extra key-value pairs.
#[derive(Clone, Debug)]
pub struct ExtraFilter {
    required: std::collections::BTreeMap<String, String>,
}

impl ExtraFilter {
    /// Creates an extra filter that requires all specified key-value pairs.
    #[must_use]
    pub fn new(required: std::collections::BTreeMap<String, String>) -> Self {
        Self { required }
    }
}

impl Filter for ExtraFilter {
    fn accept(&self, record: &LogRecord) -> bool {
        self.required
            .iter()
            .all(|(k, v)| record.extra.get(k) == Some(v))
    }
}

/// A filter that inverts another filter's result.
pub struct NotFilter {
    inner: Arc<dyn Filter>,
}

impl std::fmt::Debug for NotFilter {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "NotFilter(...)")
    }
}

impl Clone for NotFilter {
    fn clone(&self) -> Self {
        Self {
            inner: Arc::clone(&self.inner),
        }
    }
}

impl NotFilter {
    /// Creates a negating filter.
    #[must_use]
    pub fn new(inner: Arc<dyn Filter>) -> Self {
        Self { inner }
    }
}

impl Filter for NotFilter {
    fn accept(&self, record: &LogRecord) -> bool {
        !self.inner.accept(record)
    }
}

/// A filter that always accepts or always rejects.
#[derive(Clone, Debug)]
pub struct ConstFilter {
    accept: bool,
}

impl ConstFilter {
    /// Creates a constant filter.
    #[must_use]
    pub const fn new(accept: bool) -> Self {
        Self { accept }
    }
}

impl Filter for ConstFilter {
    fn accept(&self, _record: &LogRecord) -> bool {
        self.accept
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::BTreeMap;

    fn make_record_at_level(level_name: &str, priority: u16) -> LogRecord {
        LogRecord::builder(LogLevel::new(level_name, priority, None), "msg").build()
    }

    #[test]
    fn level_filter_accepts_above() {
        let filter = LevelFilter::new(LogLevel::new("WARNING", 40, None));
        let info = make_record_at_level("INFO", 20);
        let warn = make_record_at_level("WARNING", 40);
        let error = make_record_at_level("ERROR", 50);

        assert!(!filter.accept(&info));
        assert!(filter.accept(&warn));
        assert!(filter.accept(&error));
    }

    #[test]
    fn filter_chain_all_requires_all() {
        let f1 = Arc::new(LevelFilter::new(LogLevel::new("INFO", 20, None)));
        let f2 = Arc::new(PrefixFilter::new("app"));
        let chain = FilterChain::all(vec![f1, f2]);

        let mut record = make_record_at_level("INFO", 20);
        record.name = "app.core".to_owned();
        assert!(chain.accept(&record));

        record.name = "other".to_owned();
        assert!(!chain.accept(&record));
    }

    #[test]
    fn filter_chain_any_requires_one() {
        let f1 = Arc::new(LevelFilter::new(LogLevel::new("ERROR", 50, None)));
        let f2 = Arc::new(PrefixFilter::new("app"));
        let chain = FilterChain::any(vec![f1, f2]);

        let mut record = make_record_at_level("INFO", 20);
        record.name = "app.core".to_owned();
        assert!(chain.accept(&record)); // prefix matches

        record.name = "other".to_owned();
        assert!(!chain.accept(&record)); // neither matches
    }

    #[test]
    fn prefix_filter() {
        let filter = PrefixFilter::new("app.");
        let mut record = make_record_at_level("INFO", 20);

        record.name = "app.core".to_owned();
        assert!(filter.accept(&record));

        record.name = "other".to_owned();
        assert!(!filter.accept(&record));
    }

    #[test]
    fn extra_filter() {
        let mut required = BTreeMap::new();
        required.insert("service".to_owned(), "api".to_owned());
        let filter = ExtraFilter::new(required);

        let mut record = make_record_at_level("INFO", 20);
        record.extra.insert("service".to_owned(), "api".to_owned());
        assert!(filter.accept(&record));

        record.extra.insert("service".to_owned(), "web".to_owned());
        assert!(!filter.accept(&record));
    }

    #[test]
    fn not_filter_inverts() {
        let inner = Arc::new(ConstFilter::new(true));
        let filter = NotFilter::new(inner);
        let record = make_record_at_level("INFO", 20);
        assert!(!filter.accept(&record));
    }

    #[test]
    fn const_filter() {
        let accept = ConstFilter::new(true);
        let reject = ConstFilter::new(false);
        let record = make_record_at_level("INFO", 20);
        assert!(accept.accept(&record));
        assert!(!reject.accept(&record));
    }
}
