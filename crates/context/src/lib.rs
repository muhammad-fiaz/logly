//! Structured context primitives for `bind()`, `contextualize()`, and `patch()`.
//!
//! Provides thread-local and async-context-safe storage for bound key-value
//! fields, scoped context, and record-mutation hooks. Coordinates with the
//! `PyO3` layer on Python's `contextvars` semantics.

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use std::collections::BTreeMap;
use std::sync::{Arc, Mutex};

/// Bound key-value fields for a logger view.
///
/// Created by `bind()` and merged into every record the logger emits.
#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct BoundContext {
    values: BTreeMap<String, String>,
}

impl BoundContext {
    /// Creates an empty context.
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// Adds or replaces a value.
    #[must_use]
    pub fn with(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.values.insert(key.into(), value.into());
        self
    }

    /// Adds or replaces multiple values from an iterator.
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

    /// Returns the bound values.
    #[must_use]
    pub fn values(&self) -> &BTreeMap<String, String> {
        &self.values
    }

    /// Returns the number of bound values.
    #[must_use]
    pub fn len(&self) -> usize {
        self.values.len()
    }

    /// Returns `true` if no values are bound.
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.values.is_empty()
    }

    /// Merges another context into this one, overwriting duplicates.
    #[must_use]
    pub fn merge(mut self, other: &BoundContext) -> Self {
        for (key, value) in &other.values {
            self.values.insert(key.clone(), value.clone());
        }
        self
    }
}

/// Scoped context that is active for the current execution scope.
///
/// Used by `contextualize()` to temporarily bind values that apply to all
/// log calls within the scope, working correctly across async boundaries.
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

    /// Sets a value in the scoped context.
    pub fn set(&self, key: impl Into<String>, value: impl Into<String>) {
        if let Ok(mut values) = self.values.lock() {
            values.insert(key.into(), value.into());
        }
    }

    /// Sets multiple values in the scoped context.
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

    /// Returns a snapshot of the current scoped values.
    #[must_use]
    pub fn snapshot(&self) -> BTreeMap<String, String> {
        self.values
            .lock()
            .map_or_else(|_| BTreeMap::new(), |v| v.clone())
    }

    /// Clears all values from the scoped context.
    pub fn clear(&self) {
        if let Ok(mut values) = self.values.lock() {
            values.clear();
        }
    }
}

/// A record-mutation hook that can modify records before dispatch.
pub type Patcher = Box<dyn Fn(&mut BTreeMap<String, String>) + Send + Sync>;

/// A collection of patchers that are applied in order.
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

    /// Adds a patcher to the chain.
    pub fn add<F>(&self, patcher: F)
    where
        F: Fn(&mut BTreeMap<String, String>) + Send + Sync + 'static,
    {
        if let Ok(mut patchers) = self.patchers.lock() {
            patchers.push(Box::new(patcher));
        }
    }

    /// Applies all patchers to the given extra map.
    pub fn apply(&self, extra: &mut BTreeMap<String, String>) {
        if let Ok(patchers) = self.patchers.lock() {
            for patcher in patchers.iter() {
                patcher(extra);
            }
        }
    }

    /// Returns the number of patchers in the chain.
    #[must_use]
    pub fn len(&self) -> usize {
        self.patchers.lock().map_or(0, |p| p.len())
    }

    /// Returns `true` if no patchers are registered.
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }
}

/// Merges bound context, scoped context, and patcher results into a single
/// extra map for a log record.
///
/// Priority: scoped > bound. Patchers are applied last.
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
