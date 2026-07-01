"""Gunicorn integration example.

Routes Gunicorn access and error logs through Logly using either
the setup function or the LoglyWorker class.
"""

from flask import Flask

from logly import logger
from logly.integrations.gunicorn import setup_gunicorn_logging

app = Flask(__name__)

# Option 1: Call setup directly (e.g. in gunicorn.conf.py)
setup_gunicorn_logging(level="INFO")


@app.route("/")
def index():
    logger.info("Hello from Gunicorn")
    return {"status": "ok"}


# Option 2: Use the LoglyWorker class (preferred)
# In gunicorn.conf.py:
#   from logly.integrations.gunicorn import LoglyWorker
#   worker_class = LoglyWorker

# Run with: gunicorn examples.gunicorn_integration:app -k logly.integrations.gunicorn.LoglyWorker
