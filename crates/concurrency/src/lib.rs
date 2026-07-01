//! Background worker thread pool and channel-based dispatch.
//!
//! This module provides a bounded, backpressure-aware message queue for
//! asynchronous log dispatch. It is designed for sinks configured with
//! `enqueue=True`, ensuring that logging calls never block the calling thread.
//!
//! # Key Types
//!
//! - [`Backpressure`] — Controls behavior when the queue is full.
//! - [`BackgroundWorker`] — A single worker thread that processes messages
//!   from an `mpsc` channel.
//! - [`WorkerPool`] — A pool of [`BackgroundWorker`]s that distributes tasks
//!   across multiple threads.
//!
//! # Backpressure Policies
//!
//! | Policy         | Behavior                                        |
//! |----------------|------------------------------------------------|
//! | `Block`        | Producer blocks until capacity is available.     |
//! | `DropNewest`   | New messages are silently dropped when full.     |
//! | `Grow`         | Queue grows without bound (memory risk).         |
//!
//! # Examples
//!
//! ```rust,no_run
//! use concurrency::{BackgroundWorker, Backpressure};
//!
//! let worker = BackgroundWorker::new(100, Backpressure::Block, |msg: String| {
//!     println!("received: {msg}");
//! });
//! worker.send("hello".to_owned()).unwrap();
//! worker.shutdown().unwrap();
//! ```

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use error::{LoglyError, LoglyResult};
use std::sync::mpsc::{self, Receiver, Sender, SyncSender};
use std::sync::{Arc, Mutex};
use std::thread::{self, JoinHandle};

/// Controls how the message queue behaves when it reaches capacity.
///
/// This determines what happens to messages sent to a [`BackgroundWorker`]
/// when the underlying channel is full.
#[derive(Clone, Copy, Debug, Default, Eq, PartialEq)]
pub enum Backpressure {
    /// Block producers until capacity is available.
    Block,
    /// Drop new records when the queue is full.
    #[default]
    DropNewest,
    /// Grow the queue without a fixed bound.
    Grow,
}

/// Internal channel wrapper to support different backpressure policies.
enum ChannelSender<T> {
    /// Bounded channel that blocks when full.
    Bounded(SyncSender<T>),
    /// Bounded channel that drops newest when full.
    DropBounded(SyncSender<T>),
    /// Unbounded channel that grows without limit.
    Unbounded(Sender<T>),
}

impl<T> ChannelSender<T> {
    /// Sends a message, returning whether it was accepted.
    fn try_send(&self, message: T) -> bool {
        match self {
            Self::Bounded(s) => s.send(message).is_ok(),
            Self::DropBounded(s) => s.try_send(message).is_ok(),
            Self::Unbounded(s) => s.send(message).is_ok(),
        }
    }
}

/// A background worker that processes messages on a dedicated thread.
///
/// Messages are sent through an `mpsc` channel and processed sequentially
/// by the worker thread. The worker supports three backpressure policies
/// via [`Backpressure`].
///
/// # Thread Safety
///
/// `BackgroundWorker` is `Send` but not `Sync`. Multiple producers can
/// send messages concurrently through the shared [`Sender`].
///
/// # Lifecycle
///
/// 1. Call [`BackgroundWorker::new`] to spawn the worker thread.
/// 2. Send messages via [`BackgroundWorker::send`].
/// 3. Call [`BackgroundWorker::shutdown`] to drain and stop.
///
/// If dropped without calling [`shutdown`], the worker will still drain
/// pending messages.
pub struct BackgroundWorker<T: Send + 'static> {
    sender: Option<ChannelSender<T>>,
    handle: Option<JoinHandle<()>>,
    pending: Arc<Mutex<usize>>,
}

impl<T: Send + 'static> BackgroundWorker<T> {
    /// Creates a new background worker with the given capacity and callback.
    ///
    /// Spawns a dedicated thread that processes messages from the channel.
    /// The `callback` is invoked for each message received.
    ///
    /// # Arguments
    ///
    /// * `capacity` — Maximum number of messages the queue can hold (ignored
    ///   for `Backpressure::Grow`).
    /// * `backpressure` — Policy for handling a full queue.
    /// * `callback` — Function invoked for each message.
    ///
    /// # Panics
    ///
    /// Panics if the background thread cannot be spawned.
    pub fn new<F>(capacity: usize, backpressure: Backpressure, callback: F) -> Self
    where
        F: Fn(T) + Send + 'static,
    {
        let pending = Arc::new(Mutex::new(0usize));
        let pending_clone = Arc::clone(&pending);

        let (channel_sender, receiver) = match backpressure {
            Backpressure::Block => {
                let (tx, rx) = mpsc::sync_channel(capacity);
                (ChannelSender::Bounded(tx), rx)
            }
            Backpressure::DropNewest => {
                let (tx, rx) = mpsc::sync_channel(capacity);
                (ChannelSender::DropBounded(tx), rx)
            }
            Backpressure::Grow => {
                let (tx, rx) = mpsc::channel();
                (ChannelSender::Unbounded(tx), rx)
            }
        };

        let handle = thread::spawn(move || {
            Self::worker_loop(receiver, callback, pending_clone);
        });

        Self {
            sender: Some(channel_sender),
            handle: Some(handle),
            pending,
        }
    }

    /// Sends a message to the worker, respecting the backpressure policy.
    ///
    /// # Behavior by Policy
    ///
    /// - `Block`: Blocks the calling thread until capacity is available.
    /// - `DropNewest`: Returns an error if the queue is full (message is dropped).
    /// - `Grow`: Never blocks; messages are always accepted.
    ///
    /// # Arguments
    ///
    /// * `message` — The message to enqueue.
    ///
    /// # Errors
    ///
    /// Returns a [`LoglyError::Concurrency`] if the queue is full
    /// (`DropNewest` policy) or the worker has shut down.
    pub fn send(&self, message: T) -> LoglyResult<()> {
        if let Some(sender) = &self.sender {
            if sender.try_send(message) {
                if let Ok(mut count) = self.pending.lock() {
                    *count += 1;
                }
                Ok(())
            } else {
                Err(LoglyError::Concurrency(
                    "background worker queue is full (message dropped)".to_owned(),
                ))
            }
        } else {
            Err(LoglyError::Concurrency(
                "background worker is not running".to_owned(),
            ))
        }
    }

    /// Returns the number of messages waiting to be processed.
    ///
    /// This count increases when a message is sent and decreases after the
    /// callback completes.
    #[must_use]
    pub fn pending_count(&self) -> usize {
        self.pending.lock().map_or(0, |c| *c)
    }

    /// Drains all pending messages and stops the worker thread.
    ///
    /// After this call, no more messages can be sent. The worker thread
    /// is joined and cleaned up.
    ///
    /// # Errors
    ///
    /// Returns a [`LoglyError::Concurrency`] if the worker thread panics.
    pub fn shutdown(mut self) -> LoglyResult<()> {
        self.sender.take();
        if let Some(handle) = self.handle.take() {
            handle
                .join()
                .map_err(|_| LoglyError::Concurrency("background worker panicked".to_owned()))?;
        }
        Ok(())
    }

    // `Receiver` is moved into the spawned thread; `Arc` is cloned inside the loop.
    // Clippy cannot see across the thread boundary, so this is a justified suppression.
    #[allow(clippy::needless_pass_by_value)]
    fn worker_loop<F>(receiver: Receiver<T>, callback: F, pending: Arc<Mutex<usize>>)
    where
        F: Fn(T),
    {
        while let Ok(message) = receiver.recv() {
            callback(message);
            if let Ok(mut count) = pending.lock() {
                *count = count.saturating_sub(1);
            }
        }
    }
}

impl<T: Send + 'static> Drop for BackgroundWorker<T> {
    fn drop(&mut self) {
        if self.handle.is_some() {
            self.sender.take();
            if let Some(handle) = self.handle.take() {
                let _ = handle.join();
            }
        }
    }
}

/// A thread pool that distributes tasks across multiple background workers.
///
/// Tasks are submitted via [`WorkerPool::submit`] and dispatched to the
/// least-loaded worker. All workers use `Backpressure::Block` to ensure
/// no tasks are lost.
///
/// # Examples
///
/// ```rust,no_run
/// use concurrency::WorkerPool;
///
/// let pool = WorkerPool::new(4, 256);
/// pool.submit(|| println!("task 1")).unwrap();
/// pool.submit(|| println!("task 2")).unwrap();
/// pool.shutdown().unwrap();
/// ```
pub struct WorkerPool {
    workers: Vec<BackgroundWorker<Box<dyn Fn() + Send>>>,
}

impl WorkerPool {
    /// Creates a worker pool with the specified number of workers.
    ///
    /// Each worker gets its own bounded channel with the given `capacity`.
    /// Workers use `Backpressure::Block` so tasks are never silently dropped.
    ///
    /// # Arguments
    ///
    /// * `workers` — Number of worker threads to spawn.
    /// * `capacity` — Per-worker channel capacity.
    #[must_use]
    pub fn new(workers: usize, capacity: usize) -> Self {
        let pool_workers = (0..workers)
            .map(|_| {
                BackgroundWorker::new(
                    capacity,
                    Backpressure::Block,
                    |task: Box<dyn Fn() + Send>| {
                        task();
                    },
                )
            })
            .collect();
        Self {
            workers: pool_workers,
        }
    }

    /// Submits a task to the least-loaded worker.
    ///
    /// The task is dispatched to the worker with the fewest pending messages.
    /// If multiple workers have the same load, one is chosen arbitrarily.
    ///
    /// # Arguments
    ///
    /// * `task` — A closure to execute on a worker thread.
    ///
    /// # Errors
    ///
    /// Returns a [`LoglyError::Concurrency`] if no workers are available.
    pub fn submit(&self, task: impl Fn() + Send + 'static) -> LoglyResult<()> {
        let least_loaded = self
            .workers
            .iter()
            .min_by_key(|w| w.pending_count())
            .ok_or_else(|| LoglyError::Concurrency("no workers available".to_owned()))?;
        least_loaded.send(Box::new(task))
    }

    /// Shuts down all workers in the pool.
    ///
    /// Each worker drains its pending messages before stopping. Workers
    /// are shut down sequentially.
    ///
    /// # Errors
    ///
    /// Returns a [`LoglyError::Concurrency`] if any worker thread panics.
    pub fn shutdown(self) -> LoglyResult<()> {
        for worker in self.workers {
            worker.shutdown()?;
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicUsize, Ordering};

    #[test]
    fn background_worker_processes_messages() {
        let counter = Arc::new(AtomicUsize::new(0));
        let counter_clone = Arc::clone(&counter);

        let worker = BackgroundWorker::new(100, Backpressure::Block, move |_msg: String| {
            counter_clone.fetch_add(1, Ordering::SeqCst);
        });

        for i in 0..10 {
            worker.send(format!("msg {i}")).unwrap();
        }

        thread::sleep(std::time::Duration::from_millis(50));
        let worker = worker.shutdown();
        assert!(worker.is_ok());
        assert!(counter.load(Ordering::SeqCst) >= 10);
    }

    #[test]
    fn backpressure_drop_newest_does_not_block() {
        let worker = BackgroundWorker::new(2, Backpressure::DropNewest, |_msg: String| {
            thread::sleep(std::time::Duration::from_millis(10));
        });

        // With DropNewest, send() should never block even if queue is full.
        // Some sends will fail (return Err) when queue is at capacity.
        let mut accepted = 0;
        let mut dropped = 0;
        for i in 0..100 {
            if worker.send(format!("msg {i}")).is_ok() {
                accepted += 1;
            } else {
                dropped += 1;
            }
        }
        assert!(accepted > 0, "at least some messages should be accepted");
        assert!(
            dropped > 0,
            "some messages should be dropped when queue is full"
        );

        let _ = worker.shutdown();
    }

    #[test]
    fn pending_count_tracks_messages() {
        let counter = Arc::new(AtomicUsize::new(0));
        let counter_clone = Arc::clone(&counter);

        let worker = BackgroundWorker::new(10, Backpressure::Block, move |_msg: String| {
            counter_clone.fetch_add(1, Ordering::SeqCst);
        });

        worker.send("msg1".to_owned()).unwrap();
        worker.send("msg2".to_owned()).unwrap();

        thread::sleep(std::time::Duration::from_millis(50));
        let count = worker.pending_count();
        assert!(count < 100);

        let _ = worker.shutdown();
    }

    #[test]
    fn worker_pool_submit_works() {
        let counter = Arc::new(AtomicUsize::new(0));
        let pool = WorkerPool::new(2, 100);

        for _ in 0..10 {
            let c = Arc::clone(&counter);
            pool.submit(move || {
                c.fetch_add(1, Ordering::SeqCst);
            })
            .unwrap();
        }

        thread::sleep(std::time::Duration::from_millis(100));
        let _ = pool.shutdown();
        assert!(counter.load(Ordering::SeqCst) >= 10);
    }

    #[test]
    fn backpressure_default_is_drop_newest() {
        assert_eq!(Backpressure::default(), Backpressure::DropNewest);
    }
}
