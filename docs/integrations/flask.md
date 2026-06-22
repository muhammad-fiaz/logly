---
title: Flask
description: Handler and request context for Flask applications.
---

# Flask

`init_app()` adds request context, error handling, and configures stdlib logging. `LoglyHandler` routes Flask logs through Logly.

## Installation

This integration requires the `flask` package.

::: code-group

```bash [uv]
uv add logly[flask]
```

```bash [pip]
pip install "logly[flask]"
```

```bash [uv (without extras)]
uv add flask
```

```bash [pip (without extras)]
pip install flask
```

:::

::: warning Missing Dependency
If `flask` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'flask'
```
:::

## Usage

```python
from flask import Flask
from logly.integrations.flask import init_app

app = Flask(__name__)
init_app(app)
```

## Handler Only

```python
from flask import Flask
from logly.integrations.flask import LoglyHandler

app = Flask(__name__)
app.logger.handlers = [LoglyHandler()]
```

## Full Example

```python
from flask import Flask, jsonify
from logly.integrations.flask import init_app
from logly import logger

app = Flask(__name__)
init_app(app)

@app.route("/")
def index():
    logger.info("Index page accessed")
    return jsonify({"message": "Hello World"})

@app.route("/items/<int:item_id>")
def get_item(item_id):
    logger.debug("Fetching item {}", item_id)
    return jsonify({"item_id": item_id})

if __name__ == "__main__":
    app.run(debug=True)
```
