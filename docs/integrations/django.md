---
title: Django
description: Handler and middleware for Django applications.
---

# Django

`LoglyHandler` routes Python `logging` records through Logly. `LoglyMiddleware` adds request context (`request_id`, `method`, `path`, `client_ip`) to each request.

## Installation

This integration requires the `django` package.

::: code-group

```bash [uv]
uv add logly[django]
```

```bash [pip]
pip install "logly[django]"
```

```bash [uv (without extras)]
uv add django
```

```bash [pip (without extras)]
pip install django
```

:::

::: warning Missing Dependency
If `django` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'django'
```
:::

## Usage

```python
# settings.py
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "logly": {
            "class": "logly.integrations.django.LoglyHandler",
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["logly"],
        "level": "INFO",
    },
}

MIDDLEWARE = [
    "logly.integrations.django.LoglyMiddleware",
    # ... other middleware
]
```

## Full Example

```python
# settings.py
from pathlib import Path

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {},
    "handlers": {
        "logly": {
            "class": "logly.integrations.django.LoglyHandler",
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["logly"],
        "level": "INFO",
    },
}

MIDDLEWARE = [
    "logly.integrations.django.LoglyMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]
```
