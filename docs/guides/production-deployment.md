---
title: Production Deployment Guide - Logly
description: Production deployment guide for Logly Python logging library. Learn monitoring, scaling, security, and maintenance best practices.
keywords: python, logging, guide, production, deployment, monitoring, scaling, security, maintenance, logly
---

# Production Deployment Guide

This guide covers deploying Logly in production environments, including monitoring, scaling, security considerations, and maintenance best practices.

## Pre-Deployment Checklist

### 1. Configuration Review

```python
# Production-ready configuration
logger.configure(
    level=os.getenv("LOG_LEVEL", "WARNING"),
    sinks=[
        # Console for containerized environments
        {
            "type": "console",
            "level": "INFO",
            "format": "{time} | {level} | {message}",
            "colorize": False  # No colors in production
        },
        # Structured file logging
        {
            "type": "file",
            "path": "/var/log/app/app.log",
            "level": "WARNING",
            "format": "{time} | {level} | {file}:{line} | {message}",
            "rotation": "100 MB",
            "retention": "30 days",
            "async": True,
            "buffer_size": 65536
        },
        # Error-only file
        {
            "type": "file",
            "path": "/var/log/app/errors.log",
            "level": "ERROR",
            "format": "{time} | {level} | {message}\n{exception}",
            "rotation": "1 GB",
            "retention": "90 days"
        }
    ]
)
```

### 2. Environment Variables

```bash
# Logging configuration
LOG_LEVEL=WARNING
LOG_FORMAT=json  # or 'text'
LOG_FILE=/var/log/app/app.log

# Performance tuning
LOG_BUFFER_SIZE=65536
LOG_FLUSH_INTERVAL=5000

# Security
LOG_SENSITIVE_MASK=true
```

### 3. Directory Permissions

```bash
# Create log directories
sudo mkdir -p /var/log/app
sudo chown appuser:appgroup /var/log/app
sudo chmod 755 /var/log/app

# For high-security environments
sudo chmod 700 /var/log/app  # Owner only
```

## Monitoring and Observability

### Log Volume Monitoring

```python
from logly import logger
import time
import psutil

class LogMonitor:
    def __init__(self):
        self.log_count = 0
        self.start_time = time.time()

    def log_metrics(self):
        """Log performance metrics periodically"""
        elapsed = time.time() - self.start_time
        rate = self.log_count / elapsed if elapsed > 0 else 0

        logger.info("Log metrics",
                   total_logs=self.log_count,
                   elapsed_seconds=elapsed,
                   logs_per_second=rate,
                   memory_usage=psutil.virtual_memory().percent)

        # Reset counters
        self.log_count = 0
        self.start_time = time.time()

# Usage
monitor = LogMonitor()

# In your logging callback
def monitoring_callback(record):
    monitor.log_count += 1

logger.configure(
    sinks=[
        {"type": "file", "path": "app.log"},
        {"type": "callback", "callback": monitoring_callback}
    ]
)
```

### Health Checks

```python
def log_health_check():
    """Periodic health check logging"""
    import psutil
    import os

    logger.info("Health check",
               pid=os.getpid(),
               cpu_percent=psutil.cpu_percent(),
               memory_percent=psutil.virtual_memory().percent,
               disk_usage=psutil.disk_usage('/').percent,
               log_file_size=os.path.getsize('/var/log/app/app.log') if os.path.exists('/var/log/app/app.log') else 0)

# Run every 5 minutes
import threading
def health_check_loop():
    while True:
        log_health_check()
        time.sleep(300)

threading.Thread(target=health_check_loop, daemon=True).start()
```

### Error Rate Monitoring

```python
class ErrorRateMonitor:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def add_log(self, record):
        """Track error rates"""
        if record.level >= logging.ERROR:
            self.errors.append(time.time())
        elif record.level >= logging.WARNING:
            self.warnings.append(time.time())

        # Clean old entries (keep last hour)
        cutoff = time.time() - 3600
        self.errors = [t for t in self.errors if t > cutoff]
        self.warnings = [t for t in self.warnings if t > cutoff]

    def get_rates(self):
        """Get error rates per minute"""
        now = time.time()
        recent_errors = [t for t in self.errors if now - t < 60]
        recent_warnings = [t for t in self.warnings if now - t < 60]

        return {
            "errors_per_minute": len(recent_errors),
            "warnings_per_minute": len(recent_warnings),
            "total_errors_hour": len(self.errors),
            "total_warnings_hour": len(self.warnings)
        }
```

## Scaling Considerations

### High-Throughput Applications

```python
# Optimized for high throughput
logger.configure(
    sinks=[
        {
            "type": "file",
            "path": "/var/log/app/app.log",
            "async": True,
            "buffer_size": 1048576,  # 1MB buffer
            "flush_interval": 1000,  # Flush every second
            "max_buffered_lines": 10000
        }
    ]
)
```

### Multi-Process Applications

```python
import os

# Use process ID in log files for multi-process apps
process_id = os.getpid()
log_file = f"/var/log/app/app.{process_id}.log"

logger.configure(
    sinks=[
        {
            "type": "file",
            "path": log_file,
            "rotation": "1 GB",
            "retention": "7 days"
        }
    ]
)
```

### Containerized Deployments

```python
# Docker/Kubernetes optimized
logger.configure(
    sinks=[
        # Log to stdout for container log collection
        {
            "type": "console",
            "level": "INFO",
            "format": "{time} | {level} | {message}",
            "colorize": False,
            "stderr": False  # Use stdout
        },
        # Optional: Also log to file inside container
        {
            "type": "file",
            "path": "/app/logs/app.log",
            "level": "DEBUG",
            "rotation": "10 MB"
        }
    ]
)
```

## Security Best Practices

### Sensitive Data Protection

```python
import re
from logly import logger

class SensitiveDataFilter:
    def __init__(self):
        # Patterns for sensitive data
        self.patterns = [
            (re.compile(r'password["\s:=]+([^"\s&]+)'), 'password=***'),
            (re.compile(r'secret["\s:=]+([^"\s&]+)'), 'secret=***'),
            (re.compile(r'token["\s:=]+([^"\s&]+)'), 'token=***'),
            (re.compile(r'api_key["\s:=]+([^"\s&]+)'), 'api_key=***'),
        ]

    def filter_message(self, message: str) -> str:
        """Remove sensitive data from log messages"""
        for pattern, replacement in self.patterns:
            message = pattern.sub(replacement, message)
        return message

filter = SensitiveDataFilter()

def secure_callback(record):
    """Callback that filters sensitive data"""
    record.message = filter.filter_message(record.message)
    # Send to secure logging system

logger.configure(
    sinks=[
        {
            "type": "callback",
            "callback": secure_callback,
            "level": "WARNING"
        }
    ]
)
```

### Log File Permissions

```bash
# Secure log file permissions
sudo touch /var/log/app/app.log
sudo chown root:adm /var/log/app/app.log
sudo chmod 640 /var/log/app/app.log

# For application user access
sudo usermod -a -G adm appuser
```

### Audit Logging

```python
def audit_callback(record):
    """Send security events to audit log"""
    if "security" in getattr(record, 'tags', []):
        # Write to audit trail
        with open('/var/log/audit.log', 'a') as f:
            f.write(f"{record.time} | AUDIT | {record.message}\n")

logger.configure(
    sinks=[
        {"type": "file", "path": "app.log"},
        {"type": "callback", "callback": audit_callback}
    ]
)

# Usage
logger.info("User login", tags=["security"], user_id=123, ip="192.168.1.1")
```

## Maintenance Tasks

### Log Rotation Management

```python
import glob
import os
from datetime import datetime, timedelta

def cleanup_old_logs():
    """Clean up log files older than retention period"""
    log_dir = "/var/log/app"
    retention_days = 30

    cutoff_date = datetime.now() - timedelta(days=retention_days)

    for log_file in glob.glob(f"{log_dir}/*.log*"):
        file_date = datetime.fromtimestamp(os.path.getmtime(log_file))

        if file_date < cutoff_date:
            logger.info("Removing old log file", file=log_file, age_days=(datetime.now() - file_date).days)
            os.remove(log_file)

# Run daily
import schedule
schedule.every().day.do(cleanup_old_logs)
```

### Log Analysis Scripts

```python
def analyze_logs():
    """Analyze log files for patterns and issues"""
    import re
    from collections import Counter

    error_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}) .* ERROR .*')
    errors_by_date = Counter()

    with open('/var/log/app/app.log', 'r') as f:
        for line in f:
            match = error_pattern.search(line)
            if match:
                errors_by_date[match.group(1)] += 1

    logger.info("Error analysis", errors_by_date=errors_by_date)

    # Alert if too many errors
    if sum(errors_by_date.values()) > 100:
        logger.warning("High error rate detected", total_errors=sum(errors_by_date.values()))
```

### Backup and Archiving

```python
import shutil
import gzip

def backup_logs():
    """Create compressed backups of log files"""
    log_dir = "/var/log/app"
    backup_dir = "/var/log/backup"

    os.makedirs(backup_dir, exist_ok=True)

    for log_file in glob.glob(f"{log_dir}/*.log"):
        if os.path.getsize(log_file) > 0:  # Only backup non-empty files
            backup_name = f"{os.path.basename(log_file)}.{datetime.now().strftime('%Y%m%d%H%M%S')}.gz"
            backup_path = os.path.join(backup_dir, backup_name)

            with open(log_file, 'rb') as f_in:
                with gzip.open(backup_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            logger.info("Log backup created", original=log_file, backup=backup_path)

# Run weekly
schedule.every().week.do(backup_logs)
```

## Performance Optimization

### Benchmarking Your Setup

```python
import time
from logly import logger

def benchmark_logging(log_count=10000):
    """Benchmark your logging configuration"""
    logger.configure(
        sinks=[{"type": "file", "path": "/tmp/benchmark.log", "async": True}]
    )

    start_time = time.time()

    for i in range(log_count):
        logger.info("Benchmark message", iteration=i)

    end_time = time.time()
    duration = end_time - start_time

    logger.info("Benchmark complete",
               total_logs=log_count,
               duration=duration,
               logs_per_second=log_count/duration)

    return log_count/duration

# Run benchmark
rate = benchmark_logging()
print(f"Logging rate: {rate:.0f} logs/second")
```

### Memory Usage Monitoring

```python
import tracemalloc
import psutil

def monitor_memory_usage():
    """Monitor memory usage during logging"""
    tracemalloc.start()

    # Your logging-intensive code here
    for i in range(100000):
        logger.debug("Memory test message", counter=i)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    logger.info("Memory usage",
               current_mb=current / 1024 / 1024,
               peak_mb=peak / 1024 / 1024,
               system_memory_percent=psutil.virtual_memory().percent)
```

## Troubleshooting Production Issues

### Common Problems

**Logs not rotating?**
```bash
# Check file permissions
ls -la /var/log/app/

# Check disk space
df -h

# Manual rotation test
logger.info("Test rotation message")
```

**Performance degradation?**
```python
# Check async settings
logger.configure(sinks=[{
    "type": "file",
    "path": "app.log",
    "async": True,
    "buffer_size": 131072  # Increase buffer
}])
```

**Missing logs?**
```python
# Add debug logging
import logging
logging.getLogger("logly").setLevel(logging.DEBUG)

# Check sink configuration
logger.info("Configuration test")
```

### Emergency Logging

```python
def emergency_logging_setup():
    """Fallback logging when main config fails"""
    try:
        # Try main configuration
        configure_production_logging()
    except Exception as e:
        # Fallback to basic console logging
        print(f"Logging configuration failed: {e}")
        logger.configure(
            level="ERROR",
            sinks=[{"type": "console"}]
        )
        logger.error("Using emergency logging configuration", error=str(e))
```

## Deployment Checklist

### Pre-Deployment
- [ ] Log directories created with correct permissions
- [ ] Environment variables configured
- [ ] Configuration tested in staging
- [ ] Log rotation and retention tested
- [ ] Monitoring and alerting configured

### Post-Deployment
- [ ] Log files appearing as expected
- [ ] Log levels appropriate for environment
- [ ] No sensitive data in logs
- [ ] Performance meets requirements
- [ ] Monitoring dashboards show data

### Maintenance
- [ ] Regular log analysis
- [ ] Cleanup old log files
- [ ] Monitor disk space usage
- [ ] Review and adjust retention policies
- [ ] Update logging configuration as needed

This guide provides a comprehensive foundation for running Logly in production. Monitor your logs closely and adjust configuration based on your specific requirements and observed behavior.