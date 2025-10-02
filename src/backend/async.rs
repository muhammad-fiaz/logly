use crossbeam_channel::unbounded as channel;
use parking_lot::Mutex;
use std::collections::VecDeque;
use std::io::Write;
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

use crate::config::state;

/// Helper function to flush buffered lines to a file writer.
/// Used by both per-sink and legacy async writers.
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

/// Starts an async writer thread for a specific sink if async writing is enabled and not already running.
///
/// This function spawns a background thread that handles buffered writing to files for a specific sink.
/// The thread uses crossbeam channels for communication and implements intelligent
/// flushing based on buffer size and time intervals.
///
/// # Arguments
/// * `sink_id` - The handler ID of the sink to start async writing for
/// * `file_writer` - The file writer to use for this sink
/// * `buffer_size` - Maximum buffer size in bytes before flushing
/// * `flush_interval` - Time interval in milliseconds for periodic flushing
/// * `max_buffered_lines` - Maximum number of lines to buffer before forcing a flush
///
/// # Thread Safety
///
/// This function is thread-safe and ensures only one async writer thread is running
/// at a time for each sink.
pub fn start_async_writer_for_sink(
    sink_id: usize,
    file_writer: Arc<Mutex<Box<dyn Write + Send>>>,
    buffer_size: usize,
    flush_interval: u64,
    max_buffered_lines: usize,
) {
    state::with_state(|s| {
        // Only start if not already running for this sink
        if !s.async_senders.contains_key(&sink_id) {
            let (tx, rx) = channel::<String>();

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
            });

            s.async_senders.insert(sink_id, tx);
            s.async_handles.push(handle);
        }
    });
}

/// Starts an async writer thread if async writing is enabled and not already running.
/// (Legacy function for backward compatibility)
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
            });

            s.async_sender = Some(tx);
            s.async_handle = Some(handle);
        }
    });
}

pub fn complete() {
    // drop all senders to signal threads to stop, then join all handles
    let handles = state::with_state(|s| {
        // Clear all async senders (this signals threads to stop)
        s.async_senders.clear();
        // Take all async handles
        std::mem::take(&mut s.async_handles)
    });

    // Join all async writer threads
    for handle in handles {
        let _ = handle.join();
    }

    // Also handle legacy async writer for backward compatibility
    let legacy_handle = state::with_state(|s| {
        let _ = s.async_sender.take();
        s.async_handle.take()
    });
    if let Some(handle) = legacy_handle {
        let _ = handle.join();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::state::reset_state;
    use std::io::Write;
    use std::sync::Arc;
    use std::thread;
    use std::time::Duration;

    // A simple test writer that just counts writes
    struct TestWriter {
        write_count: Arc<Mutex<usize>>,
    }

    impl TestWriter {
        fn new() -> Self {
            TestWriter {
                write_count: Arc::new(Mutex::new(0)),
            }
        }

        #[allow(dead_code)]
        fn get_write_count(&self) -> usize {
            *self.write_count.lock()
        }
    }

    impl Write for TestWriter {
        fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
            *self.write_count.lock() += 1;
            Ok(buf.len())
        }

        fn flush(&mut self) -> std::io::Result<()> {
            Ok(())
        }
    }

    #[test]
    fn test_flush_buffer() {
        let mut buffer = String::new();
        let mut line_queue = VecDeque::new();
        line_queue.push_back("line1".to_string());
        line_queue.push_back("line2".to_string());

        let test_writer = TestWriter::new();
        let cursor = Arc::new(Mutex::new(Box::new(test_writer) as Box<dyn Write + Send>));
        flush_buffer(&mut buffer, &mut line_queue, &cursor);

        // Check that buffer was cleared
        assert_eq!(buffer, "");

        // Check that write was called (we can't inspect the data, but we can check the count indirectly)
        // The test writer increments a counter on each write
    }

    #[test]
    fn test_flush_buffer_empty() {
        let mut buffer = String::new();
        let mut line_queue = VecDeque::new();

        let test_writer = TestWriter::new();
        let cursor = Arc::new(Mutex::new(Box::new(test_writer) as Box<dyn Write + Send>));
        flush_buffer(&mut buffer, &mut line_queue, &cursor);

        // Should not write anything - buffer should remain empty
        assert_eq!(buffer, "");
    }

    #[test]
    fn test_start_async_writer_for_sink() {
        reset_state();

        let test_writer = TestWriter::new();
        let cursor = Arc::new(Mutex::new(Box::new(test_writer) as Box<dyn Write + Send>));
        let sink_id = 1;

        // Start async writer
        start_async_writer_for_sink(sink_id, cursor.clone(), 1024, 100, 10);

        // Check that sender was created
        state::with_state_read(|s| {
            assert!(s.async_senders.contains_key(&sink_id));
            assert_eq!(s.async_handles.len(), 1);
        });

        // Send a message
        state::with_state_read(|s| {
            if let Some(sender) = s.async_senders.get(&sink_id) {
                let _ = sender.send("test message".to_string());
            }
        });

        // Wait a bit for async processing
        thread::sleep(Duration::from_millis(200));

        // Stop async writer
        complete();

        // Verify cleanup
        state::with_state_read(|s| {
            assert!(!s.async_senders.contains_key(&sink_id));
            assert!(s.async_handles.is_empty());
        });
    }

    #[test]
    fn test_start_async_writer_if_needed() {
        reset_state();

        let test_writer = TestWriter::new();
        let cursor = Arc::new(Mutex::new(Box::new(test_writer) as Box<dyn Write + Send>));

        // Set up state for legacy async writer
        state::with_state(|s| {
            s.async_write = true;
            s.file_writer = Some(cursor.clone());
            s.buffer_size = 1024;
            s.flush_interval = 100;
            s.max_buffered_lines = 10;
        });

        // Start legacy async writer
        start_async_writer_if_needed();

        // Check that legacy sender was created
        state::with_state_read(|s| {
            assert!(s.async_sender.is_some());
            assert!(s.async_handle.is_some());
        });

        // Send a message via legacy sender
        state::with_state_read(|s| {
            if let Some(sender) = &s.async_sender {
                let _ = sender.send("legacy test".to_string());
            }
        });

        // Wait for processing
        thread::sleep(Duration::from_millis(200));

        // Complete and verify cleanup
        complete();

        state::with_state_read(|s| {
            assert!(s.async_sender.is_none());
            assert!(s.async_handle.is_none());
        });
    }

    #[test]
    fn test_complete_cleans_up() {
        reset_state();

        let test_writer = TestWriter::new();
        let cursor = Arc::new(Mutex::new(Box::new(test_writer) as Box<dyn Write + Send>));

        // Start both types of async writers
        start_async_writer_for_sink(1, cursor.clone(), 1024, 100, 10);

        state::with_state(|s| {
            s.async_write = true;
            s.file_writer = Some(cursor);
        });
        start_async_writer_if_needed();

        // Verify they were started
        state::with_state_read(|s| {
            assert!(!s.async_senders.is_empty());
            assert!(!s.async_handles.is_empty());
            // Note: async_sender might not be created if the conditions aren't met
        });

        // Complete should clean them up
        complete();

        // Give a moment for cleanup
        std::thread::sleep(std::time::Duration::from_millis(50));

        // Verify they were cleaned up
        state::with_state_read(|s| {
            assert!(
                s.async_senders.is_empty(),
                "async_senders not empty: {:?}",
                s.async_senders.keys()
            );
            assert!(s.async_handles.is_empty());
            assert!(s.async_sender.is_none());
            assert!(s.async_handle.is_none());
        });
    }

    #[test]
    fn test_start_async_writer_for_sink_idempotent() {
        reset_state();

        let test_writer = TestWriter::new();
        let cursor = Arc::new(Mutex::new(Box::new(test_writer) as Box<dyn Write + Send>));
        let sink_id = 1;

        // Start async writer twice for same sink
        start_async_writer_for_sink(sink_id, cursor.clone(), 1024, 100, 10);
        start_async_writer_for_sink(sink_id, cursor, 1024, 100, 10);

        // Should still only have one sender and handle
        state::with_state_read(|s| {
            assert_eq!(s.async_senders.len(), 1);
            assert_eq!(s.async_handles.len(), 1);
        });

        complete();
    }
}
