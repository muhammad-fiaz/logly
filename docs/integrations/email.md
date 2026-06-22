---
title: Email
description: Send log entries as emails via SMTP.
---

# Email

`EmailHandler` sends log entries as email messages via SMTP. Uses the Python standard library (`smtplib`) - no extra dependencies required.

## Installation

No additional dependencies required. This integration uses Python's standard library.

## Usage

```python
from logly import logger
from logly.integrations.email import EmailHandler

handler = EmailHandler(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    from_addr="alerts@example.com",
    to_addrs=["ops@example.com"],
    username="alerts@example.com",
    password="app-password",
)
logger.add(handler, level="ERROR")
```

## Constructor Args

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `smtp_host` | `str` | `localhost` | SMTP server hostname |
| `smtp_port` | `int` | `25` | SMTP server port |
| `from_addr` | `str` | `""` | Sender email address |
| `to_addrs` | `list[str] \| None` | `None` | List of recipient email addresses |
| `username` | `str \| None` | `None` | SMTP authentication username |
| `password` | `str \| None` | `None` | SMTP authentication password |
| `use_tls` | `bool` | `True` | Whether to use STARTTLS |
| `use_ssl` | `bool` | `False` | Whether to use SSL/TLS from the start |
| `timeout` | `float` | `30.0` | SMTP connection timeout in seconds |
| `subject_prefix` | `str` | `[Logly]` | Prefix added to email subject lines |

## Tips

- Use `use_ssl=True` with port 465 for implicit TLS, or `use_tls=True` with port 587 for STARTTLS.
- Use application-specific passwords (not your main account password) for Gmail and similar providers.
- Restrict this handler to `level="ERROR"` or `level="CRITICAL"` to avoid email fatigue.

## Full Example

```python
from logly import logger
from logly.integrations.email import EmailHandler

handler = EmailHandler(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    from_addr="alerts@myapp.com",
    to_addrs=["oncall@myapp.com", "team-lead@myapp.com"],
    username="alerts@myapp.com",
    password="xxxx-xxxx-xxxx-xxxx",
    use_tls=True,
    subject_prefix="[MyApp Alert]",
)
logger.add(handler, level="CRITICAL")

logger.critical("Payment processing is DOWN", service="payments")
```
