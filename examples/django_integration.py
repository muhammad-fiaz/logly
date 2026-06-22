"""Django integration example.

Add to settings.py:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'logly': {
                'class': 'logly.integrations.django.LoglyHandler',
                'level': 'INFO',
            },
        },
        'root': {
            'handlers': ['logly'],
            'level': 'INFO',
        },
    }
    MIDDLEWARE = [
        'logly.integrations.django.LoglyMiddleware',
        # ... other middleware
    ]
"""

from logly import logger
from logly.integrations.django import LoglyHandler

# Demo: use the handler directly
handler = LoglyHandler()
handler.emit(record=None)  # Would emit a logging.LogRecord

logger.info("Django integration example")
logger.complete()
