//! Structured context primitives for `bind()`, `contextualize()`, and `patch()`.
//!
//! This module provides three layers of context that are merged into every
//! log record:
//!
//! 1. **Bound context** ([`BoundContext`]) — Key-value pairs permanently
//!    attached to a logger via `bind()`. Immutable after creation.
//! 2. **Scoped context** ([`ScopedContext`]) — Temporary key-value pairs
//!    active for the current execution scope (e.g., a request handler).
//!    Works across async boundaries.
//! 3. **Patcher chain** ([`PatcherChain`]) — Mutation hooks that modify
//!    the record's extra fields just before dispatch.
//!
//! # Merge Priority
//!
//! When a log record is emitted, contexts are merged in this order:
//!
//! ```text
//! bound → scoped → patchers
//! ```
//!
//! Later sources overwrite earlier ones for duplicate keys.
//!
//! # Examples
//!
//! ```rust
//! use context::{BoundContext, ScopedContext, PatcherChain, merge_contexts};
//!
//! let bound = BoundContext::new()
//!     .with("service", "api")
//!     .with("version", "1.0");
//! let scoped = ScopedContext::new();
//! scoped.set("request_id", "abc-123");
//! let patchers = PatcherChain::new();
//!
//! let extra = merge_contexts(&bound, &scoped, &patchers);
//! assert_eq!(extra.get("service"), Some(&"api".to_owned()));
//! assert_eq!(extra.get("request_id"), Some(&"abc-123".to_owned()));
//! ```

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use std::collections::BTreeMap;
use std::sync::{Arc, Mutex};

/// Immutable key-value pairs permanently attached to a logger.
///
/// Created via `bind()` on a logger view. These fields are merged into
/// every log record the logger emits. Use the builder pattern to
/// construct a `BoundContext`.
///
/// # Examples
///
/// ```rust
/// use context::BoundContext;
///
/// let ctx = BoundContext::new()
///     .with("service", "api")
///     .with("version", "2.1");
/// assert_eq!(ctx.len(), 2);
/// ```
#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct BoundContext {
    values: BTreeMap<String, String>,
}

impl BoundContext {
    /// Creates an empty bound context.
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// Adds or replaces a single key-value pair.
    ///
    /// If the key already exists, the value is overwritten.
    ///
    /// # Arguments
    ///
    /// * `key` — The field name.
    /// * `value` — The field value.
    #[must_use]
    pub fn with(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.values.insert(key.into(), value.into());
        self
    }

    /// Adds or replaces multiple key-value pairs from an iterator.
    #[must_use]
    pub fn with_many<I, K, V>(mut self, iter: I) -> Self
    where
        I: IntoIterator<Item = (K, V)>,
        K: Into<String>,
        V: Into<String>,
    {
        for (key, value) in iter {
            self.values.insert(key.into(), value.into());
        }
        self
    }

    /// Returns a reference to the underlying key-value map.
    #[must_use]
    pub fn values(&self) -> &BTreeMap<String, String> {
        &self.values
    }

    /// Returns the number of key-value pairs in the context.
    #[must_use]
    pub fn len(&self) -> usize {
        self.values.len()
    }

    /// Returns `true` if the context contains no key-value pairs.
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.values.is_empty()
    }

    /// Merges another context into this one, overwriting duplicate keys.
    ///
    /// # Arguments
    ///
    /// * `other` — The context whose values to merge in.
    #[must_use]
    pub fn merge(mut self, other: &BoundContext) -> Self {
        for (key, value) in &other.values {
            self.values.insert(key.clone(), value.clone());
        }
        self
    }
}

/// Thread-safe, temporary key-value storage for the current execution scope.
///
/// Created via `contextualize()`, a `ScopedContext` temporarily binds values
/// that apply to all log calls within a scope. It is safe to use across
/// async boundaries and from multiple threads.
///
/// Scoped values override bound values with the same key.
#[derive(Clone, Debug, Default)]
pub struct ScopedContext {
    values: Arc<Mutex<BTreeMap<String, String>>>,
}

impl ScopedContext {
    /// Creates an empty scoped context.
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// Sets a single key-value pair in the scoped context.
    ///
    /// If the key already exists, the value is overwritten.
    ///
    /// # Arguments
    ///
    /// * `key` — The field name.
    /// * `value` — The field value.
    pub fn set(&self, key: impl Into<String>, value: impl Into<String>) {
        if let Ok(mut values) = self.values.lock() {
            values.insert(key.into(), value.into());
        }
    }

    /// Sets multiple key-value pairs in the scoped context.
    ///
    /// # Arguments
    ///
    /// * `iter` — An iterator of `(key, value)` pairs.
    pub fn set_many<I, K, V>(&self, iter: I)
    where
        I: IntoIterator<Item = (K, V)>,
        K: Into<String>,
        V: Into<String>,
    {
        if let Ok(mut values) = self.values.lock() {
            for (key, value) in iter {
                values.insert(key.into(), value.into());
            }
        }
    }

    /// Returns a snapshot of all current scoped values.
    ///
    /// The returned map is a clone; subsequent changes to the scoped context
    /// do not affect it.
    #[must_use]
    pub fn snapshot(&self) -> BTreeMap<String, String> {
        self.values
            .lock()
            .map_or_else(|_| BTreeMap::new(), |v| v.clone())
    }

    /// Removes all key-value pairs from the scoped context.
    pub fn clear(&self) {
        if let Ok(mut values) = self.values.lock() {
            values.clear();
        }
    }
}

/// A record-mutation hook that modifies extra fields before dispatch.
///
/// Patcher functions receive a mutable reference to the record's `extra`
/// map and can add, remove, or overwrite fields. Used with
/// [`PatcherChain`].
pub type Patcher = Box<dyn Fn(&mut BTreeMap<String, String>) + Send + Sync>;

/// An ordered collection of [`Patcher`] hooks applied to log records.
///
/// Patchers are invoked in registration order when [`PatcherChain::apply`]
/// is called. The chain is thread-safe and can be shared across threads.
///
/// # Examples
///
/// ```rust
/// use context::PatcherChain;
/// use std::collections::BTreeMap;
///
/// let chain = PatcherChain::new();
/// chain.add(|extra| {
///     extra.insert("host".to_owned(), "web-01".to_owned());
/// });
///
/// let mut extra = BTreeMap::new();
/// chain.apply(&mut extra);
/// assert_eq!(extra.get("host"), Some(&"web-01".to_owned()));
/// ```
pub struct PatcherChain {
    patchers: Arc<Mutex<Vec<Patcher>>>,
}

impl std::fmt::Debug for PatcherChain {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let len = self.len();
        write!(f, "PatcherChain({len} patchers)")
    }
}

impl Clone for PatcherChain {
    fn clone(&self) -> Self {
        Self {
            patchers: Arc::clone(&self.patchers),
        }
    }
}

impl Default for PatcherChain {
    fn default() -> Self {
        Self::new()
    }
}

impl PatcherChain {
    /// Creates an empty patcher chain.
    #[must_use]
    pub fn new() -> Self {
        Self {
            patchers: Arc::new(Mutex::new(Vec::new())),
        }
    }

    /// Registers a new patcher in the chain.
    ///
    /// The patcher is appended to the end and will be called last during
    /// [`PatcherChain::apply`].
    ///
    /// # Arguments
    ///
    /// * `patcher` — A closure that mutates the extra map.
    pub fn add<F>(&self, patcher: F)
    where
        F: Fn(&mut BTreeMap<String, String>) + Send + Sync + 'static,
    {
        if let Ok(mut patchers) = self.patchers.lock() {
            patchers.push(Box::new(patcher));
        }
    }

    /// Applies all registered patchers to the given extra map.
    ///
    /// Patchers are invoked in registration order. Each patcher receives
    /// a mutable reference to `extra` and can modify it freely.
    ///
    /// # Arguments
    ///
    /// * `extra` — The mutable extra map to patch.
    pub fn apply(&self, extra: &mut BTreeMap<String, String>) {
        if let Ok(patchers) = self.patchers.lock() {
            for patcher in patchers.iter() {
                patcher(extra);
            }
        }
    }

    /// Returns the number of registered patchers.
    #[must_use]
    pub fn len(&self) -> usize {
        self.patchers.lock().map_or(0, |p| p.len())
    }

    /// Returns `true` if the chain contains no patchers.
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }
}

/// Merges bound, scoped, and patcher contexts into a single extra map.
///
/// The merge order is:
///
/// 1. Bound context values are inserted first.
/// 2. Scoped context values overwrite bound values with the same key.
/// 3. Patchers are applied last, potentially modifying any field.
///
/// # Arguments
///
/// * `bound` — Permanent key-value pairs from `bind()`.
/// * `scoped` — Temporary key-value pairs from `contextualize()`.
/// * `patchers` — Mutation hooks applied last.
///
/// # Returns
///
/// A merged `BTreeMap<String, String>` ready for the log record.
#[must_use]
pub fn merge_contexts(
    bound: &BoundContext,
    scoped: &ScopedContext,
    patchers: &PatcherChain,
) -> BTreeMap<String, String> {
    let mut extra = BTreeMap::new();
    for (key, value) in bound.values() {
        extra.insert(key.clone(), value.clone());
    }
    for (key, value) in &scoped.snapshot() {
        extra.insert(key.clone(), value.clone());
    }
    patchers.apply(&mut extra);
    extra
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bound_context_builder() {
        let ctx = BoundContext::new()
            .with("service", "api")
            .with("version", "1.0");
        assert_eq!(ctx.len(), 2);
        assert_eq!(ctx.values().get("service"), Some(&"api".to_owned()));
    }

    #[test]
    fn bound_context_merge() {
        let a = BoundContext::new().with("x", "1");
        let b = BoundContext::new().with("y", "2");
        let merged = a.merge(&b);
        assert_eq!(merged.len(), 2);
        assert_eq!(merged.values().get("x"), Some(&"1".to_owned()));
        assert_eq!(merged.values().get("y"), Some(&"2".to_owned()));
    }

    #[test]
    fn bound_context_is_empty() {
        assert!(BoundContext::new().is_empty());
        assert!(!BoundContext::new().with("k", "v").is_empty());
    }

    #[test]
    fn scoped_context_set_and_snapshot() {
        let ctx = ScopedContext::new();
        ctx.set("key", "value");
        let snap = ctx.snapshot();
        assert_eq!(snap.get("key"), Some(&"value".to_owned()));
    }

    #[test]
    fn scoped_context_clear() {
        let ctx = ScopedContext::new();
        ctx.set("key", "value");
        ctx.clear();
        assert!(ctx.snapshot().is_empty());
    }

    #[test]
    fn patcher_chain_applies_in_order() {
        let chain = PatcherChain::new();
        chain.add(|extra| {
            extra.insert("a".to_owned(), "1".to_owned());
        });
        chain.add(|extra| {
            extra.insert("b".to_owned(), "2".to_owned());
        });

        let mut extra = BTreeMap::new();
        chain.apply(&mut extra);
        assert_eq!(extra.get("a"), Some(&"1".to_owned()));
        assert_eq!(extra.get("b"), Some(&"2".to_owned()));
    }

    #[test]
    fn patcher_chain_len() {
        let chain = PatcherChain::new();
        assert!(chain.is_empty());
        chain.add(|_| {});
        assert_eq!(chain.len(), 1);
    }

    #[test]
    fn merge_contexts_priority() {
        let bound = BoundContext::new().with("a", "bound").with("b", "bound");
        let scoped = ScopedContext::new();
        scoped.set("b", "scoped");
        scoped.set("c", "scoped");

        let patchers = PatcherChain::new();
        patchers.add(|extra| {
            extra.insert("d".to_owned(), "patched".to_owned());
        });

        let merged = merge_contexts(&bound, &scoped, &patchers);
        assert_eq!(merged.get("a"), Some(&"bound".to_owned()));
        assert_eq!(merged.get("b"), Some(&"scoped".to_owned()));
        assert_eq!(merged.get("c"), Some(&"scoped".to_owned()));
        assert_eq!(merged.get("d"), Some(&"patched".to_owned()));
    }
}
