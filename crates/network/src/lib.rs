//! Network-based logging sinks.
//!
//! Provides HTTP, TCP, UDP, and syslog sinks for transmitting log records
//! over network protocols.

#![deny(missing_docs)]
#![forbid(unsafe_code)]
#![warn(clippy::all)]
#![warn(clippy::pedantic)]

use error::{LoglyError, LoglyResult};
use levels::LogLevel;
use record::LogRecord;
use serde::Serialize;
use std::collections::BTreeMap;
use std::io::Write;
use std::net::{TcpStream, ToSocketAddrs, UdpSocket};
use std::sync::{Mutex, RwLock};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

/// A JSON-serializable log record for HTTP transmission.
#[derive(Serialize)]
struct JsonLogRecord {
    timestamp: String,
    level: String,
    level_priority: u16,
    message: String,
    name: String,
    file: Option<String>,
    line: Option<u32>,
    function: Option<String>,
    thread_name: Option<String>,
    process_id: u32,
    extra: BTreeMap<String, String>,
    exception: Option<String>,
}

impl From<&LogRecord> for JsonLogRecord {
    fn from(record: &LogRecord) -> Self {
        let timestamp = record
            .timestamp
            .duration_since(UNIX_EPOCH)
            .map_or_else(|_| "0".to_owned(), |d| format!("{}", d.as_secs()));

        Self {
            timestamp,
            level: record.level.name().to_owned(),
            level_priority: record.level.priority(),
            message: record.message.clone(),
            name: record.name.clone(),
            file: record.file.clone(),
            line: record.line,
            function: record.function.clone(),
            thread_name: record.thread_name.clone(),
            process_id: record.process_id,
            extra: record.extra.clone(),
            exception: record.exception.clone(),
        }
    }
}

/// Configuration for the HTTP JSON sink.
#[derive(Clone, Debug)]
pub struct HttpJsonConfig {
    /// The HTTP endpoint URL.
    pub url: String,
    /// HTTP method to use (POST or PUT).
    pub method: HttpMethod,
    /// Optional custom headers.
    pub headers: Vec<(String, String)>,
    /// Request timeout in seconds.
    pub timeout_secs: u64,
}

/// Supported HTTP methods.
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum HttpMethod {
    /// HTTP POST method.
    Post,
    /// HTTP PUT method.
    Put,
}

/// HTTP JSON sink that POSTs log records to an endpoint.
pub struct HttpJsonSink {
    config: RwLock<HttpJsonConfig>,
    agent: ureq::Agent,
}

impl HttpJsonSink {
    /// Creates a new HTTP JSON sink.
    #[must_use]
    pub fn new(config: HttpJsonConfig) -> Self {
        let timeout = config.timeout_secs;
        let agent_config = ureq::Agent::config_builder()
            .timeout_global(Some(Duration::from_secs(timeout)))
            .build();
        let agent = ureq::Agent::new_with_config(agent_config);
        Self {
            config: RwLock::new(config),
            agent,
        }
    }

    /// Sends a log record to the HTTP endpoint.
    ///
    /// # Errors
    ///
    /// Returns an error if the HTTP request fails.
    pub fn send(&self, record: &LogRecord) -> LoglyResult<()> {
        let config = self
            .config
            .read()
            .map_err(|_| LoglyError::Sink("config lock is unavailable".to_owned()))?;

        let json_record = JsonLogRecord::from(record);

        let mut request = match config.method {
            HttpMethod::Post => self.agent.post(&config.url),
            HttpMethod::Put => self.agent.put(&config.url),
        };

        for (key, value) in &config.headers {
            request = request.header(key, value);
        }

        request
            .send_json(&json_record)
            .map_err(|e| LoglyError::Sink(format!("HTTP request failed: {e}")))?;

        Ok(())
    }

    /// Updates the sink configuration.
    ///
    /// # Errors
    ///
    /// Returns an error if the config lock is poisoned.
    pub fn update_config(&self, config: HttpJsonConfig) -> LoglyResult<()> {
        let mut guard = self
            .config
            .write()
            .map_err(|_| LoglyError::Sink("config lock is unavailable".to_owned()))?;
        *guard = config;
        Ok(())
    }

    /// Writes a formatted log line to the HTTP endpoint.
    ///
    /// # Errors
    ///
    /// Returns an error if the HTTP request fails.
    pub fn write(&self, line: &str) -> LoglyResult<()> {
        let config = self
            .config
            .read()
            .map_err(|_| LoglyError::Sink("config lock is unavailable".to_owned()))?;

        let mut request = match config.method {
            HttpMethod::Post => self.agent.post(&config.url),
            HttpMethod::Put => self.agent.put(&config.url),
        };

        for (key, value) in &config.headers {
            request = request.header(key, value);
        }

        let body = serde_json::json!({
            "message": line,
            "timestamp": SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .map_or(0, |d| d.as_secs()),
        });

        request
            .send_json(&body)
            .map_err(|e| LoglyError::Sink(format!("HTTP request failed: {e}")))?;

        Ok(())
    }

    /// Flushes buffered data (no-op for HTTP).
    pub fn flush(&self) {
        // HTTP requests are immediate; nothing to flush.
    }
}

/// Configuration for the TCP sink.
#[derive(Clone, Debug)]
pub struct TcpConfig {
    /// Hostname or IP address.
    pub host: String,
    /// Port number.
    pub port: u16,
    /// Delimiter between messages (default: newline).
    pub delimiter: String,
}

impl Default for TcpConfig {
    fn default() -> Self {
        Self {
            host: "127.0.0.1".to_owned(),
            port: 514,
            delimiter: "\n".to_owned(),
        }
    }
}

/// TCP sink that sends log messages over a persistent connection.
pub struct TcpSink {
    config: RwLock<TcpConfig>,
    stream: Mutex<Option<TcpStream>>,
}

impl TcpSink {
    /// Creates a new TCP sink.
    #[must_use]
    pub fn new(config: TcpConfig) -> Self {
        Self {
            config: RwLock::new(config),
            stream: Mutex::new(None),
        }
    }

    /// Connects to the TCP server.
    ///
    /// # Errors
    ///
    /// Returns an error if the connection fails.
    pub fn connect(&self) -> LoglyResult<()> {
        let config = self
            .config
            .read()
            .map_err(|_| LoglyError::Sink("config lock is unavailable".to_owned()))?;

        let addr = format!("{}:{}", config.host, config.port);
        let socket_addr = addr
            .to_socket_addrs()
            .map_err(|e| LoglyError::Sink(format!("invalid address: {e}")))?
            .next()
            .ok_or_else(|| LoglyError::Sink("no addresses found".to_owned()))?;

        let stream = TcpStream::connect(socket_addr)
            .map_err(|e| LoglyError::Sink(format!("TCP connect failed: {e}")))?;

        stream
            .set_read_timeout(Some(Duration::from_secs(5)))
            .map_err(|e| LoglyError::Sink(format!("set timeout failed: {e}")))?;
        stream
            .set_write_timeout(Some(Duration::from_secs(5)))
            .map_err(|e| LoglyError::Sink(format!("set timeout failed: {e}")))?;

        let mut guard = self
            .stream
            .lock()
            .map_err(|_| LoglyError::Sink("stream lock is unavailable".to_owned()))?;
        *guard = Some(stream);

        Ok(())
    }

    /// Reconnects to the TCP server.
    ///
    /// # Errors
    ///
    /// Returns an error if reconnection fails.
    pub fn reconnect(&self) -> LoglyResult<()> {
        // Drop old connection
        {
            let mut guard = self
                .stream
                .lock()
                .map_err(|_| LoglyError::Sink("stream lock is unavailable".to_owned()))?;
            *guard = None;
        }
        self.connect()
    }

    /// Sends a log message over TCP.
    ///
    /// # Errors
    ///
    /// Returns an error if sending fails.
    pub fn send(&self, message: &str) -> LoglyResult<()> {
        let config = self
            .config
            .read()
            .map_err(|_| LoglyError::Sink("config lock is unavailable".to_owned()))?;
        let delimiter = config.clone();
        drop(config);

        let mut guard = self
            .stream
            .lock()
            .map_err(|_| LoglyError::Sink("stream lock is unavailable".to_owned()))?;

        if guard.is_none() {
            drop(guard);
            self.connect()?;
            guard = self
                .stream
                .lock()
                .map_err(|_| LoglyError::Sink("stream lock is unavailable".to_owned()))?;
        }

        if let Some(ref mut stream) = *guard {
            let data = format!("{}{}", message, delimiter.delimiter);
            stream
                .write_all(data.as_bytes())
                .map_err(|e| LoglyError::Sink(format!("TCP send failed: {e}")))?;
        }

        Ok(())
    }

    /// Writes a formatted log line over TCP.
    ///
    /// # Errors
    ///
    /// Returns an error if sending fails.
    pub fn write(&self, line: &str) -> LoglyResult<()> {
        self.send(line)
    }

    /// Flushes the TCP stream.
    ///
    /// # Errors
    ///
    /// Returns an error if flushing fails.
    pub fn flush(&self) -> LoglyResult<()> {
        let mut guard = self
            .stream
            .lock()
            .map_err(|_| LoglyError::Sink("stream lock is unavailable".to_owned()))?;

        if let Some(ref mut stream) = *guard {
            stream
                .flush()
                .map_err(|e| LoglyError::Sink(format!("TCP flush failed: {e}")))?;
        }

        Ok(())
    }
}

/// Configuration for the UDP sink.
#[derive(Clone, Debug)]
pub struct UdpConfig {
    /// Hostname or IP address.
    pub host: String,
    /// Port number.
    pub port: u16,
}

impl Default for UdpConfig {
    fn default() -> Self {
        Self {
            host: "127.0.0.1".to_owned(),
            port: 514,
        }
    }
}

/// UDP sink that sends log messages (fire-and-forget).
pub struct UdpSink {
    config: RwLock<UdpConfig>,
    socket: Mutex<Option<UdpSocket>>,
}

impl UdpSink {
    /// Creates a new UDP sink.
    #[must_use]
    pub fn new(config: UdpConfig) -> Self {
        Self {
            config: RwLock::new(config),
            socket: Mutex::new(None),
        }
    }

    /// Initializes the UDP socket.
    ///
    /// # Errors
    ///
    /// Returns an error if socket creation fails.
    pub fn init(&self) -> LoglyResult<()> {
        let socket = UdpSocket::bind("0.0.0.0:0")
            .map_err(|e| LoglyError::Sink(format!("UDP bind failed: {e}")))?;

        let mut guard = self
            .socket
            .lock()
            .map_err(|_| LoglyError::Sink("socket lock is unavailable".to_owned()))?;
        *guard = Some(socket);

        Ok(())
    }

    /// Sends a log message over UDP.
    ///
    /// # Errors
    ///
    /// Returns an error if sending fails.
    pub fn send(&self, message: &str) -> LoglyResult<()> {
        let config = self
            .config
            .read()
            .map_err(|_| LoglyError::Sink("config lock is unavailable".to_owned()))?;

        let addr = format!("{}:{}", config.host, config.port);
        let socket_addr = addr
            .to_socket_addrs()
            .map_err(|e| LoglyError::Sink(format!("invalid address: {e}")))?
            .next()
            .ok_or_else(|| LoglyError::Sink("no addresses found".to_owned()))?;

        let mut guard = self
            .socket
            .lock()
            .map_err(|_| LoglyError::Sink("socket lock is unavailable".to_owned()))?;

        if guard.is_none() {
            drop(guard);
            self.init()?;
            guard = self
                .socket
                .lock()
                .map_err(|_| LoglyError::Sink("socket lock is unavailable".to_owned()))?;
        }

        if let Some(ref socket) = *guard {
            socket
                .send_to(message.as_bytes(), socket_addr)
                .map_err(|e| LoglyError::Sink(format!("UDP send failed: {e}")))?;
        }

        Ok(())
    }

    /// Writes a formatted log line over UDP.
    ///
    /// # Errors
    ///
    /// Returns an error if sending fails.
    pub fn write(&self, line: &str) -> LoglyResult<()> {
        self.send(line)
    }

    /// Flushes the UDP socket (no-op for UDP).
    pub fn flush(&self) {
        // UDP is fire-and-forget; nothing to flush.
    }
}

/// Syslog facility as defined in RFC 3164/5424.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
#[allow(clippy::module_name_repetitions)]
pub enum SyslogFacility {
    /// Kernel messages.
    Kernel,
    /// User-level messages.
    User,
    /// Mail system.
    Mail,
    /// System daemons.
    Daemon,
    /// Authentication messages.
    Auth,
    /// Syslogd itself.
    Syslog,
    /// Line printer subsystem.
    Lpr,
    /// Network news subsystem.
    News,
    /// UUCP subsystem.
    Uucp,
    /// Clock daemon.
    Cron,
    /// Security/authorization messages.
    AuthPriv,
    /// FTP daemon.
    Ftp,
    /// Local0.
    Local0,
    /// Local1.
    Local1,
    /// Local2.
    Local2,
    /// Local3.
    Local3,
    /// Local4.
    Local4,
    /// Local5.
    Local5,
    /// Local6.
    Local6,
    /// Local7.
    Local7,
}

impl SyslogFacility {
    /// Returns the numeric code for the facility.
    #[must_use]
    pub const fn code(self) -> u32 {
        match self {
            Self::Kernel => 0,
            Self::User => 1,
            Self::Mail => 2,
            Self::Daemon => 3,
            Self::Auth => 4,
            Self::Syslog => 5,
            Self::Lpr => 6,
            Self::News => 7,
            Self::Uucp => 8,
            Self::Cron => 9,
            Self::AuthPriv => 10,
            Self::Ftp => 11,
            Self::Local0 => 16,
            Self::Local1 => 17,
            Self::Local2 => 18,
            Self::Local3 => 19,
            Self::Local4 => 20,
            Self::Local5 => 21,
            Self::Local6 => 22,
            Self::Local7 => 23,
        }
    }
}

/// Syslog severity as defined in RFC 3164/5424.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
#[allow(clippy::module_name_repetitions)]
pub enum SyslogSeverity {
    /// Emergency.
    Emergency,
    /// Alert.
    Alert,
    /// Critical.
    Critical,
    /// Error.
    Error,
    /// Warning.
    Warning,
    /// Notice.
    Notice,
    /// Informational.
    Info,
    /// Debug.
    Debug,
}

impl SyslogSeverity {
    /// Returns the numeric code for the severity.
    #[must_use]
    pub const fn code(self) -> u32 {
        match self {
            Self::Emergency => 0,
            Self::Alert => 1,
            Self::Critical => 2,
            Self::Error => 3,
            Self::Warning => 4,
            Self::Notice => 5,
            Self::Info => 6,
            Self::Debug => 7,
        }
    }
}

/// Syslog message format.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum SyslogFormat {
    /// RFC 3164 (BSD) format.
    Rfc3164,
    /// RFC 5424 format.
    Rfc5424,
}

/// Transport protocol for syslog.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum SyslogTransport {
    /// UDP transport.
    Udp,
    /// TCP transport.
    Tcp,
}

/// Configuration for the syslog sink.
#[derive(Clone, Debug)]
pub struct SyslogConfig {
    /// Hostname or IP address of the syslog server.
    pub host: String,
    /// Port number (typically 514).
    pub port: u16,
    /// Syslog facility.
    pub facility: SyslogFacility,
    /// Transport protocol.
    pub transport: SyslogTransport,
    /// Message format.
    pub format: SyslogFormat,
    /// Process name for syslog header.
    pub process_name: String,
}

impl Default for SyslogConfig {
    fn default() -> Self {
        Self {
            host: "127.0.0.1".to_owned(),
            port: 514,
            facility: SyslogFacility::User,
            transport: SyslogTransport::Udp,
            format: SyslogFormat::Rfc3164,
            process_name: "logly".to_owned(),
        }
    }
}

/// Syslog sink that sends messages in RFC 3164 or RFC 5424 format.
pub struct SyslogSink {
    config: RwLock<SyslogConfig>,
    udp_socket: Mutex<Option<UdpSocket>>,
    tcp_stream: Mutex<Option<TcpStream>>,
}

impl SyslogSink {
    /// Creates a new syslog sink.
    #[must_use]
    pub fn new(config: SyslogConfig) -> Self {
        Self {
            config: RwLock::new(config),
            udp_socket: Mutex::new(None),
            tcp_stream: Mutex::new(None),
        }
    }

    /// Maps a log level to syslog severity.
    #[must_use]
    pub fn level_to_severity(level: &LogLevel) -> SyslogSeverity {
        match level.priority() {
            0..=10 => SyslogSeverity::Debug,
            11..=29 => SyslogSeverity::Notice,
            30..=39 => SyslogSeverity::Info,
            40..=49 => SyslogSeverity::Warning,
            50..=54 => SyslogSeverity::Error,
            55..=59 => SyslogSeverity::Critical,
            60..=69 => SyslogSeverity::Alert,
            _ => SyslogSeverity::Emergency,
        }
    }

    /// Initializes the transport.
    ///
    /// # Errors
    ///
    /// Returns an error if transport initialization fails.
    pub fn init(&self) -> LoglyResult<()> {
        let config = self
            .config
            .read()
            .map_err(|_| LoglyError::Sink("config lock is unavailable".to_owned()))?;

        match config.transport {
            SyslogTransport::Udp => {
                let socket = UdpSocket::bind("0.0.0.0:0")
                    .map_err(|e| LoglyError::Sink(format!("UDP bind failed: {e}")))?;
                let mut guard = self
                    .udp_socket
                    .lock()
                    .map_err(|_| LoglyError::Sink("socket lock is unavailable".to_owned()))?;
                *guard = Some(socket);
            }
            SyslogTransport::Tcp => {
                let addr = format!("{}:{}", config.host, config.port);
                let socket_addr = addr
                    .to_socket_addrs()
                    .map_err(|e| LoglyError::Sink(format!("invalid address: {e}")))?
                    .next()
                    .ok_or_else(|| LoglyError::Sink("no addresses found".to_owned()))?;

                let stream = TcpStream::connect(socket_addr)
                    .map_err(|e| LoglyError::Sink(format!("TCP connect failed: {e}")))?;

                let mut guard = self
                    .tcp_stream
                    .lock()
                    .map_err(|_| LoglyError::Sink("stream lock is unavailable".to_owned()))?;
                *guard = Some(stream);
            }
        }

        Ok(())
    }

    /// Formats a message in RFC 3164 (BSD) format.
    #[must_use]
    pub fn format_rfc3164(
        facility: SyslogFacility,
        severity: SyslogSeverity,
        process_name: &str,
        message: &str,
    ) -> String {
        let priority = facility.code() * 8 + severity.code();
        let hostname = hostname::get().map_or_else(
            |_| "localhost".to_owned(),
            |h| h.to_string_lossy().into_owned(),
        );

        let now = chrono::Utc::now();
        let timestamp = now.format("%b %d %H:%M:%S").to_string();

        format!(
            "<{priority}>{timestamp} {hostname} {process_name}[{}]: {message}",
            std::process::id()
        )
    }

    /// Formats a message in RFC 5424 format.
    #[must_use]
    pub fn format_rfc5424(
        facility: SyslogFacility,
        severity: SyslogSeverity,
        process_name: &str,
        message: &str,
    ) -> String {
        let priority = facility.code() * 8 + severity.code();
        let hostname = hostname::get().map_or_else(
            |_| "localhost".to_owned(),
            |h| h.to_string_lossy().into_owned(),
        );

        let now = chrono::Utc::now();
        let timestamp = now.format("%Y-%m-%dT%H:%M:%S%.3fZ").to_string();

        format!(
            "<{priority}>1 {timestamp} {hostname} {process_name} {} - - - {message}",
            std::process::id()
        )
    }

    /// Sends a log record via syslog.
    ///
    /// # Errors
    ///
    /// Returns an error if sending fails.
    pub fn send_record(&self, record: &LogRecord) -> LoglyResult<()> {
        let config = self
            .config
            .read()
            .map_err(|_| LoglyError::Sink("config lock is unavailable".to_owned()))?;

        let severity = Self::level_to_severity(&record.level);

        let formatted = match config.format {
            SyslogFormat::Rfc3164 => Self::format_rfc3164(
                config.facility,
                severity,
                &config.process_name,
                &record.message,
            ),
            SyslogFormat::Rfc5424 => Self::format_rfc5424(
                config.facility,
                severity,
                &config.process_name,
                &record.message,
            ),
        };

        match config.transport {
            SyslogTransport::Udp => {
                let addr = format!("{}:{}", config.host, config.port);
                let socket_addr = addr
                    .to_socket_addrs()
                    .map_err(|e| LoglyError::Sink(format!("invalid address: {e}")))?
                    .next()
                    .ok_or_else(|| LoglyError::Sink("no addresses found".to_owned()))?;

                let mut guard = self
                    .udp_socket
                    .lock()
                    .map_err(|_| LoglyError::Sink("socket lock is unavailable".to_owned()))?;

                if guard.is_none() {
                    drop(guard);
                    self.init()?;
                    guard = self
                        .udp_socket
                        .lock()
                        .map_err(|_| LoglyError::Sink("socket lock is unavailable".to_owned()))?;
                }

                if let Some(ref socket) = *guard {
                    socket
                        .send_to(formatted.as_bytes(), socket_addr)
                        .map_err(|e| LoglyError::Sink(format!("syslog UDP send failed: {e}")))?;
                }
            }
            SyslogTransport::Tcp => {
                let mut guard = self
                    .tcp_stream
                    .lock()
                    .map_err(|_| LoglyError::Sink("stream lock is unavailable".to_owned()))?;

                if guard.is_none() {
                    drop(guard);
                    self.init()?;
                    guard = self
                        .tcp_stream
                        .lock()
                        .map_err(|_| LoglyError::Sink("stream lock is unavailable".to_owned()))?;
                }

                if let Some(ref mut stream) = *guard {
                    let data = format!("{formatted}\n");
                    stream
                        .write_all(data.as_bytes())
                        .map_err(|e| LoglyError::Sink(format!("syslog TCP send failed: {e}")))?;
                }
            }
        }

        Ok(())
    }

    /// Writes a formatted log line via syslog.
    ///
    /// # Errors
    ///
    /// Returns an error if sending fails.
    pub fn write(&self, line: &str) -> LoglyResult<()> {
        let config = self
            .config
            .read()
            .map_err(|_| LoglyError::Sink("config lock is unavailable".to_owned()))?;

        let formatted = match config.format {
            SyslogFormat::Rfc3164 => Self::format_rfc3164(
                config.facility,
                SyslogSeverity::Info,
                &config.process_name,
                line,
            ),
            SyslogFormat::Rfc5424 => Self::format_rfc5424(
                config.facility,
                SyslogSeverity::Info,
                &config.process_name,
                line,
            ),
        };
        drop(config);

        self.send_raw(&formatted)
    }

    /// Sends a raw formatted syslog message.
    fn send_raw(&self, message: &str) -> LoglyResult<()> {
        let config = self
            .config
            .read()
            .map_err(|_| LoglyError::Sink("config lock is unavailable".to_owned()))?;

        match config.transport {
            SyslogTransport::Udp => {
                let addr = format!("{}:{}", config.host, config.port);
                let socket_addr = addr
                    .to_socket_addrs()
                    .map_err(|e| LoglyError::Sink(format!("invalid address: {e}")))?
                    .next()
                    .ok_or_else(|| LoglyError::Sink("no addresses found".to_owned()))?;

                let mut guard = self
                    .udp_socket
                    .lock()
                    .map_err(|_| LoglyError::Sink("socket lock is unavailable".to_owned()))?;

                if guard.is_none() {
                    drop(guard);
                    self.init()?;
                    guard = self
                        .udp_socket
                        .lock()
                        .map_err(|_| LoglyError::Sink("socket lock is unavailable".to_owned()))?;
                }

                if let Some(ref socket) = *guard {
                    socket
                        .send_to(message.as_bytes(), socket_addr)
                        .map_err(|e| LoglyError::Sink(format!("syslog UDP send failed: {e}")))?;
                }
            }
            SyslogTransport::Tcp => {
                let mut guard = self
                    .tcp_stream
                    .lock()
                    .map_err(|_| LoglyError::Sink("stream lock is unavailable".to_owned()))?;

                if guard.is_none() {
                    drop(guard);
                    self.init()?;
                    guard = self
                        .tcp_stream
                        .lock()
                        .map_err(|_| LoglyError::Sink("stream lock is unavailable".to_owned()))?;
                }

                if let Some(ref mut stream) = *guard {
                    let data = format!("{message}\n");
                    stream
                        .write_all(data.as_bytes())
                        .map_err(|e| LoglyError::Sink(format!("syslog TCP send failed: {e}")))?;
                }
            }
        }

        Ok(())
    }

    /// Flushes the syslog transport.
    ///
    /// # Errors
    ///
    /// Returns an error if flushing fails.
    pub fn flush(&self) -> LoglyResult<()> {
        let config = self
            .config
            .read()
            .map_err(|_| LoglyError::Sink("config lock is unavailable".to_owned()))?;

        if config.transport == SyslogTransport::Tcp {
            let mut guard = self
                .tcp_stream
                .lock()
                .map_err(|_| LoglyError::Sink("stream lock is unavailable".to_owned()))?;

            if let Some(ref mut stream) = *guard {
                stream
                    .flush()
                    .map_err(|e| LoglyError::Sink(format!("syslog flush failed: {e}")))?;
            }
        }

        Ok(())
    }
}

/// A trait for network sinks that accept formatted log lines.
pub trait NetworkSink: Send + Sync {
    /// Writes a formatted log line to the network destination.
    ///
    /// # Errors
    ///
    /// Returns an error if writing fails.
    fn write(&self, line: &str) -> LoglyResult<()>;

    /// Flushes any buffered data.
    ///
    /// # Errors
    ///
    /// Returns an error if flushing fails.
    fn flush(&self) -> LoglyResult<()>;
}

impl NetworkSink for HttpJsonSink {
    fn write(&self, line: &str) -> LoglyResult<()> {
        self.write(line)
    }

    fn flush(&self) -> LoglyResult<()> {
        self.flush();
        Ok(())
    }
}

impl NetworkSink for TcpSink {
    fn write(&self, line: &str) -> LoglyResult<()> {
        self.write(line)
    }

    fn flush(&self) -> LoglyResult<()> {
        self.flush()
    }
}

impl NetworkSink for UdpSink {
    fn write(&self, line: &str) -> LoglyResult<()> {
        self.write(line)
    }

    fn flush(&self) -> LoglyResult<()> {
        self.flush();
        Ok(())
    }
}

impl NetworkSink for SyslogSink {
    fn write(&self, line: &str) -> LoglyResult<()> {
        self.write(line)
    }

    fn flush(&self) -> LoglyResult<()> {
        self.flush()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn http_json_config_default() {
        let config = HttpJsonConfig {
            url: "http://localhost:8080/logs".to_owned(),
            method: HttpMethod::Post,
            headers: vec![],
            timeout_secs: 30,
        };
        assert_eq!(config.method, HttpMethod::Post);
        assert_eq!(config.timeout_secs, 30);
    }

    #[test]
    fn http_json_sink_creation() {
        let config = HttpJsonConfig {
            url: "http://localhost:8080/logs".to_owned(),
            method: HttpMethod::Post,
            headers: vec![("Authorization".to_owned(), "Bearer token".to_owned())],
            timeout_secs: 10,
        };
        let sink = HttpJsonSink::new(config);
        sink.flush();
    }

    #[test]
    fn tcp_config_default() {
        let config = TcpConfig::default();
        assert_eq!(config.host, "127.0.0.1");
        assert_eq!(config.port, 514);
        assert_eq!(config.delimiter, "\n");
    }

    #[test]
    fn tcp_sink_creation() {
        let config = TcpConfig {
            host: "127.0.0.1".to_owned(),
            port: 9999,
            delimiter: "\n".to_owned(),
        };
        let sink = TcpSink::new(config);
        // Attempt to connect (may fail if no server, that's OK for unit test)
        let _ = sink.connect();
    }

    #[test]
    fn udp_config_default() {
        let config = UdpConfig::default();
        assert_eq!(config.host, "127.0.0.1");
        assert_eq!(config.port, 514);
    }

    #[test]
    fn udp_sink_creation() {
        let config = UdpConfig {
            host: "127.0.0.1".to_owned(),
            port: 9998,
        };
        let sink = UdpSink::new(config);
        let _ = sink.init();
    }

    #[test]
    fn syslog_facility_codes() {
        assert_eq!(SyslogFacility::Kernel.code(), 0);
        assert_eq!(SyslogFacility::User.code(), 1);
        assert_eq!(SyslogFacility::Daemon.code(), 3);
        assert_eq!(SyslogFacility::Local0.code(), 16);
        assert_eq!(SyslogFacility::Local7.code(), 23);
    }

    #[test]
    fn syslog_severity_codes() {
        assert_eq!(SyslogSeverity::Emergency.code(), 0);
        assert_eq!(SyslogSeverity::Alert.code(), 1);
        assert_eq!(SyslogSeverity::Critical.code(), 2);
        assert_eq!(SyslogSeverity::Error.code(), 3);
        assert_eq!(SyslogSeverity::Warning.code(), 4);
        assert_eq!(SyslogSeverity::Notice.code(), 5);
        assert_eq!(SyslogSeverity::Info.code(), 6);
        assert_eq!(SyslogSeverity::Debug.code(), 7);
    }

    #[test]
    fn syslog_level_to_severity_mapping() {
        let debug = LogLevel::new("DEBUG", 10, None);
        let info = LogLevel::new("INFO", 20, None);
        let warning = LogLevel::new("WARNING", 40, None);
        let error = LogLevel::new("ERROR", 50, None);
        let critical = LogLevel::new("CRITICAL", 60, None);
        let fatal = LogLevel::new("FATAL", 70, None);

        assert_eq!(SyslogSink::level_to_severity(&debug), SyslogSeverity::Debug);
        assert_eq!(SyslogSink::level_to_severity(&info), SyslogSeverity::Notice);
        assert_eq!(
            SyslogSink::level_to_severity(&warning),
            SyslogSeverity::Warning
        );
        assert_eq!(SyslogSink::level_to_severity(&error), SyslogSeverity::Error);
        assert_eq!(
            SyslogSink::level_to_severity(&critical),
            SyslogSeverity::Alert
        );
        assert_eq!(
            SyslogSink::level_to_severity(&fatal),
            SyslogSeverity::Emergency
        );
    }

    #[test]
    fn syslog_rfc3164_format() {
        let msg = SyslogSink::format_rfc3164(
            SyslogFacility::User,
            SyslogSeverity::Info,
            "testapp",
            "hello world",
        );
        assert!(msg.contains("hello world"));
        assert!(msg.contains("testapp"));
        assert!(msg.starts_with('<'));
    }

    #[test]
    fn syslog_rfc5424_format() {
        let msg = SyslogSink::format_rfc5424(
            SyslogFacility::Daemon,
            SyslogSeverity::Error,
            "myapp",
            "test message",
        );
        assert!(msg.contains("test message"));
        assert!(msg.contains("myapp"));
        assert!(msg.starts_with('<'));
        assert!(msg.contains("1 "));
    }

    #[test]
    fn syslog_config_default() {
        let config = SyslogConfig::default();
        assert_eq!(config.host, "127.0.0.1");
        assert_eq!(config.port, 514);
        assert_eq!(config.facility, SyslogFacility::User);
        assert_eq!(config.transport, SyslogTransport::Udp);
        assert_eq!(config.format, SyslogFormat::Rfc3164);
    }

    #[test]
    fn syslog_sink_creation() {
        let config = SyslogConfig {
            host: "127.0.0.1".to_owned(),
            port: 514,
            facility: SyslogFacility::Local0,
            transport: SyslogTransport::Udp,
            format: SyslogFormat::Rfc5424,
            process_name: "test".to_owned(),
        };
        let sink = SyslogSink::new(config);
        let _ = sink.init();
    }

    #[test]
    fn json_log_record_from_record() {
        let level = LogLevel::new("INFO", 20, None);
        let record = LogRecord::builder(level, "test message")
            .name("test_logger")
            .build();

        let json = JsonLogRecord::from(&record);
        assert_eq!(json.message, "test message");
        assert_eq!(json.level, "INFO");
        assert_eq!(json.level_priority, 20);
        assert_eq!(json.name, "test_logger");
    }

    #[test]
    fn http_json_sink_write_to_endpoint() {
        let config = HttpJsonConfig {
            url: "http://127.0.0.1:1".to_owned(),
            method: HttpMethod::Post,
            headers: vec![],
            timeout_secs: 2,
        };
        let sink = HttpJsonSink::new(config);
        let result = sink.write("test log line");
        assert!(result.is_err());
    }

    #[test]
    fn tcp_sink_send_without_connection() {
        let config = TcpConfig {
            host: "127.0.0.1".to_owned(),
            port: 19999,
            delimiter: "\n".to_owned(),
        };
        let sink = TcpSink::new(config);
        // Should fail since no server is listening
        let result = sink.write("test message");
        assert!(result.is_err());
    }

    #[test]
    fn udp_sink_send_without_init() {
        let config = UdpConfig {
            host: "127.0.0.1".to_owned(),
            port: 19998,
        };
        let sink = UdpSink::new(config);
        // Should auto-init on first send
        let result = sink.write("test message");
        // May succeed or fail depending on network, but tests the code path
        let _ = result;
    }

    #[test]
    fn syslog_sink_write_without_connection() {
        let config = SyslogConfig {
            host: "127.0.0.1".to_owned(),
            port: 19997,
            facility: SyslogFacility::User,
            transport: SyslogTransport::Udp,
            format: SyslogFormat::Rfc3164,
            process_name: "test".to_owned(),
        };
        let sink = SyslogSink::new(config);
        // Should auto-init on first write
        let result = sink.write("test syslog message");
        let _ = result;
    }

    #[test]
    fn network_sink_trait_implementations() {
        let http_config = HttpJsonConfig {
            url: "http://localhost:8080".to_owned(),
            method: HttpMethod::Post,
            headers: vec![],
            timeout_secs: 5,
        };
        let http_sink = HttpJsonSink::new(http_config);
        let _: &dyn NetworkSink = &http_sink;

        let tcp_config = TcpConfig::default();
        let tcp_sink = TcpSink::new(tcp_config);
        let _: &dyn NetworkSink = &tcp_sink;

        let udp_config = UdpConfig::default();
        let udp_sink = UdpSink::new(udp_config);
        let _: &dyn NetworkSink = &udp_sink;

        let syslog_config = SyslogConfig::default();
        let syslog_sink = SyslogSink::new(syslog_config);
        let _: &dyn NetworkSink = &syslog_sink;
    }

    #[test]
    fn syslog_rfc3164_format_contains_priority() {
        let msg =
            SyslogSink::format_rfc3164(SyslogFacility::User, SyslogSeverity::Info, "app", "msg");
        // User=1, Info=6, priority = 1*8+6 = 14
        assert!(msg.contains("<14>"));
    }

    #[test]
    fn syslog_rfc5424_format_contains_priority() {
        let msg =
            SyslogSink::format_rfc5424(SyslogFacility::Daemon, SyslogSeverity::Error, "app", "msg");
        // Daemon=3, Error=3, priority = 3*8+3 = 27
        assert!(msg.contains("<27>"));
    }

    #[test]
    fn http_method_variants() {
        assert_eq!(HttpMethod::Post, HttpMethod::Post);
        assert_eq!(HttpMethod::Put, HttpMethod::Put);
        assert_ne!(HttpMethod::Post, HttpMethod::Put);
    }

    #[test]
    fn syslog_format_variants() {
        assert_eq!(SyslogFormat::Rfc3164, SyslogFormat::Rfc3164);
        assert_eq!(SyslogFormat::Rfc5424, SyslogFormat::Rfc5424);
        assert_ne!(SyslogFormat::Rfc3164, SyslogFormat::Rfc5424);
    }

    #[test]
    fn syslog_transport_variants() {
        assert_eq!(SyslogTransport::Udp, SyslogTransport::Udp);
        assert_eq!(SyslogTransport::Tcp, SyslogTransport::Tcp);
        assert_ne!(SyslogTransport::Udp, SyslogTransport::Tcp);
    }
}
