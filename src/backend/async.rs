//! # Async Writing Backend
//!
//! This module provides asynchronous buffered writing capabilities for high-performance
//! logging. It uses background threads to write log messages without blocking the main
//! application thread.
//!
//! ## Features
//!
//! - Background thread writing with configurable buffering
//! - Size-based and time-based flushing
//! - Crossbeam channels for efficient inter-thread communication
//! - Automatic thread management and cleanup

use crossbeam_channel::unbounded as channel;
use parking_lot::Mutex;
use std::collections::VecDeque;
use std::io::Write;
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

use crate::config::state;

/// Starts an async writer thread if async writing is enabled and not already running.
///
/// This function spawns a background thread that handles buffered writing to files.
/// The thread uses crossbeam channels for communication and implements intelligent
/// flushing based on buffer size and time intervals.
///
/// # Thread Safety
///
/// This function is thread-safe and ensures only one async writer thread is running
/// at a time for each logger instance.
pub fn start_async_writer_if_needed() {
    // spawn background thread to drain channel and write to file with buffering
    state::with_state(|s| {
        if s.async_write && s.async_sender.is_none() && s.file_writer.is_some() {
            let (tx, rx) = channel::<String>();
            // Clone the Arc to the file writer for the background thread
            let file_writer = s.file_writer.as_ref().unwrap().clone();
            let buffer_size = s.buffer_size;
            let flush_interval = s.flush_interval;
            let max_buffered_lines = s.max_buffered_lines;

            let handle = thread::spawn(move || {
                let mut buffer = String::with_capacity(buffer_size);
                let mut line_queue: VecDeque<String> = VecDeque::new();
                let mut last_flush = Instant::now();

                loop {
                    // Try to receive a line with a timeout for periodic flushing
                    let timeout = Duration::from_millis(flush_interval);
                    match rx.recv_timeout(timeout) {
                        Ok(line) => {
                            let line_len = line.len();

                            // If buffer would exceed buffer_size with this line, flush first
                            if buffer.len() + line_len + 1 >= buffer_size {
                                flush_buffer(&mut buffer, &mut line_queue, &file_writer);
                                last_flush = Instant::now();
                            }

                            // Add line to queue
                            line_queue.push_back(line);

                            // If we've reached max_buffered_lines, flush immediately
                            if line_queue.len() >= max_buffered_lines {
                                flush_buffer(&mut buffer, &mut line_queue, &file_writer);
                                last_flush = Instant::now();
                            }
                        }
                        Err(crossbeam_channel::RecvTimeoutError::Timeout) => {
                            // Timeout reached, flush if we have content or if flush_interval has passed
                            if !line_queue.is_empty()
                                || (!buffer.is_empty()
                                    && last_flush.elapsed()
                                        >= Duration::from_millis(flush_interval))
                            {
                                flush_buffer(&mut buffer, &mut line_queue, &file_writer);
                                last_flush = Instant::now();
                            }
                        }
                        Err(crossbeam_channel::RecvTimeoutError::Disconnected) => {
                            // Channel disconnected, flush remaining content and exit
                            if !line_queue.is_empty() || !buffer.is_empty() {
                                flush_buffer(&mut buffer, &mut line_queue, &file_writer);
                            }
                            break;
                        }
                    }
                }

                fn flush_buffer(
                    buffer: &mut String,
                    line_queue: &mut VecDeque<String>,
                    file_writer: &Arc<Mutex<Box<dyn Write + Send>>>,
                ) {
                    // Build buffer from queued lines
                    while let Some(line) = line_queue.pop_front() {
                        if !buffer.is_empty() {
                            buffer.push('\n');
                        }
                        buffer.push_str(&line);
                    }

                    // Write buffer to file
                    if !buffer.is_empty() {
                        let mut w = file_writer.lock();
                        let _ = write!(&mut **w, "{}", buffer);
                        let _ = w.flush();
                        buffer.clear();
                    }
                }
            });

            s.async_sender = Some(tx);
            s.async_handle = Some(handle);
        }
    });
}

pub fn complete() {
    // drop sender to signal thread to stop, then join
    let handle_opt = state::with_state(|s| {
        // take sender and handle out of state
        let _ = s.async_sender.take();
        s.async_handle.take()
    });
    if let Some(handle) = handle_opt {
        let _ = handle.join();
    }
}
