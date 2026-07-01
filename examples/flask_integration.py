"""Flask integration example.

Routes all Flask request/response logging through Logly with automatic
request ID, method, path, status code, and timing.
"""

from flask import Flask

from logly import logger
from logly.integrations.flask import init_app

app = Flask(__name__)

# Initialize Logly on the Flask app
# This adds before/after request hooks, error handling,
# and routes Flask/werkzeug logs through Logly
init_app(app)


@app.route("/")
def index():
    logger.info("Root endpoint called")
    return {"message": "Hello World"}


@app.route("/items/<int:item_id>")
def get_item(item_id: int):
    logger.info("Reading item {}", item_id)
    return {"item_id": item_id}


# Run with: flask --app examples.flask_integration run --reload
