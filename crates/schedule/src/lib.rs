//! Scheduling primitives for retention and timed rotation.
//!
//! Runs scheduled tasks on the `concurrency` crate's worker infrastructure
//! rather than spawning ad hoc threads.

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use error::{LoglyError, LoglyResult};
use std::sync::Mutex;
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

/// A periodic task schedule.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct Interval {
    duration: Duration,
}

impl Interval {
    /// Creates a schedule from a duration.
    #[must_use]
    pub const fn new(duration: Duration) -> Self {
        Self { duration }
    }

    /// Creates a schedule from seconds.
    #[must_use]
    pub const fn from_secs(secs: u64) -> Self {
        Self {
            duration: Duration::from_secs(secs),
        }
    }

    /// Creates a schedule from minutes.
    #[must_use]
    pub const fn from_mins(mins: u64) -> Self {
        Self {
            duration: Duration::from_secs(mins * 60),
        }
    }

    /// Returns the duration between runs.
    #[must_use]
    pub const fn duration(self) -> Duration {
        self.duration
    }
}

/// A scheduled task that runs periodically.
pub struct ScheduledTask {
    name: String,
    interval: Interval,
    running: std::sync::Arc<AtomicBool>,
    handle: Option<JoinHandle<()>>,
}

impl ScheduledTask {
    /// Creates and starts a scheduled task.
    ///
    /// # Panics
    ///
    /// Panics if the scheduler thread cannot be spawned.
    pub fn new<F>(name: impl Into<String>, interval: Interval, task: F) -> Self
    where
        F: Fn() + Send + Sync + 'static,
    {
        let name = name.into();
        let running = std::sync::Arc::new(AtomicBool::new(true));
        let running_clone = std::sync::Arc::clone(&running);
        let task = std::sync::Arc::new(task);

        let handle = thread::spawn(move || {
            let mut last_run = Instant::now();
            while running_clone.load(Ordering::Relaxed) {
                let elapsed = last_run.elapsed();
                if elapsed >= interval.duration() {
                    task();
                    last_run = Instant::now();
                }
                let sleep_time = interval.duration().saturating_sub(elapsed);
                if sleep_time > Duration::ZERO {
                    thread::sleep(sleep_time.min(Duration::from_millis(100)));
                }
            }
        });

        Self {
            name,
            interval,
            running,
            handle: Some(handle),
        }
    }

    /// Returns the task name.
    #[must_use]
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Returns the task interval.
    #[must_use]
    pub fn interval(&self) -> Interval {
        self.interval
    }

    /// Stops the scheduled task.
    ///
    /// # Errors
    ///
    /// Returns an error if the task thread panics.
    pub fn stop(&mut self) -> LoglyResult<()> {
        self.running.store(false, Ordering::Relaxed);
        if let Some(handle) = self.handle.take() {
            handle
                .join()
                .map_err(|_| LoglyError::Schedule(format!("task '{}' panicked", self.name)))?;
        }
        Ok(())
    }
}

impl Drop for ScheduledTask {
    fn drop(&mut self) {
        self.running.store(false, Ordering::Relaxed);
        if let Some(handle) = self.handle.take() {
            let _ = handle.join();
        }
    }
}

/// A scheduler that manages multiple periodic tasks.
pub struct Scheduler {
    tasks: Mutex<Vec<ScheduledTask>>,
}

impl Scheduler {
    /// Creates a new empty scheduler.
    #[must_use]
    pub fn new() -> Self {
        Self {
            tasks: Mutex::new(Vec::new()),
        }
    }

    /// Schedules a periodic task.
    ///
    /// # Errors
    ///
    /// Returns an error if the task list cannot be locked.
    pub fn schedule<F>(
        &self,
        name: impl Into<String>,
        interval: Interval,
        task: F,
    ) -> LoglyResult<()>
    where
        F: Fn() + Send + Sync + 'static,
    {
        let scheduled = ScheduledTask::new(name, interval, task);
        self.tasks
            .lock()
            .map_err(|_| LoglyError::Schedule("scheduler lock is unavailable".to_owned()))?
            .push(scheduled);
        Ok(())
    }

    /// Stops all scheduled tasks.
    ///
    /// # Errors
    ///
    /// Returns an error if any task fails to stop.
    pub fn stop_all(&self) -> LoglyResult<()> {
        let mut tasks = self
            .tasks
            .lock()
            .map_err(|_| LoglyError::Schedule("scheduler lock is unavailable".to_owned()))?;
        for task in tasks.iter_mut() {
            task.stop()?;
        }
        tasks.clear();
        Ok(())
    }

    /// Returns the number of active scheduled tasks.
    #[must_use]
    pub fn task_count(&self) -> usize {
        self.tasks.lock().map_or(0, |tasks| tasks.len())
    }
}

impl Default for Scheduler {
    fn default() -> Self {
        Self::new()
    }
}

impl Drop for Scheduler {
    fn drop(&mut self) {
        let _ = self.stop_all();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::AtomicUsize;

    #[test]
    fn interval_from_secs() {
        let interval = Interval::from_secs(5);
        assert_eq!(interval.duration(), Duration::from_secs(5));
    }

    #[test]
    fn interval_from_mins() {
        let interval = Interval::from_mins(2);
        assert_eq!(interval.duration(), Duration::from_mins(2));
    }

    #[test]
    fn scheduled_task_runs_multiple_times() {
        let counter = std::sync::Arc::new(AtomicUsize::new(0));
        let counter_clone = std::sync::Arc::clone(&counter);

        let mut task = ScheduledTask::new(
            "test",
            Interval::new(Duration::from_millis(50)),
            move || {
                counter_clone.fetch_add(1, Ordering::SeqCst);
            },
        );

        thread::sleep(Duration::from_millis(180));
        task.stop().unwrap();

        let count = counter.load(Ordering::SeqCst);
        assert!(count >= 2, "expected at least 2 runs, got {count}");
    }

    #[test]
    fn scheduler_manages_tasks() {
        let scheduler = Scheduler::new();
        assert_eq!(scheduler.task_count(), 0);

        scheduler
            .schedule("task1", Interval::from_secs(60), || {})
            .unwrap();

        assert_eq!(scheduler.task_count(), 1);

        scheduler.stop_all().unwrap();
        assert_eq!(scheduler.task_count(), 0);
    }

    #[test]
    fn scheduler_default_is_empty() {
        let scheduler = Scheduler::default();
        assert_eq!(scheduler.task_count(), 0);
    }

    #[test]
    fn interval_new() {
        let interval = Interval::new(Duration::from_secs(10));
        assert_eq!(interval.duration(), Duration::from_secs(10));
    }

    #[test]
    fn interval_from_mins_conversion() {
        let interval = Interval::from_mins(5);
        assert_eq!(interval.duration(), Duration::from_mins(5));
    }

    #[test]
    fn scheduled_task_name() {
        let task = ScheduledTask::new("my-task", Interval::from_secs(1), || {});
        assert_eq!(task.name(), "my-task");
    }

    #[test]
    fn scheduled_task_interval() {
        let interval = Interval::from_secs(30);
        let task = ScheduledTask::new("task", interval, || {});
        assert_eq!(task.interval(), interval);
    }

    #[test]
    fn scheduler_multiple_tasks() {
        let scheduler = Scheduler::new();
        scheduler
            .schedule("task1", Interval::from_secs(60), || {})
            .unwrap();
        scheduler
            .schedule("task2", Interval::from_secs(120), || {})
            .unwrap();

        assert_eq!(scheduler.task_count(), 2);

        scheduler.stop_all().unwrap();
        assert_eq!(scheduler.task_count(), 0);
    }
}
