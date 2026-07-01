---
title: Pydantic
description: Route Pydantic application logs through Logly.
---

# Pydantic

`PydanticLogHandler` routes Python `logging` records through Logly with a `LoglyFormatter`. Integrates seamlessly with Pydantic models and Python's standard logging.

## Installation

This integration requires the `pydantic` package.

::: code-group

```bash [uv]
uv add logly[pydantic]
```

```bash [pip]
pip install "logly[pydantic]"
```

```bash [uv (without extras)]
uv add pydantic
```

```bash [pip (without extras)]
pip install pydantic
```

:::

::: warning Missing Dependency
If `pydantic` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'pydantic'
```
:::

## Usage

```python
import logging
from logly.integrations.pydantic import PydanticLogHandler

logger = logging.getLogger("myapp")
logger.addHandler(PydanticLogHandler())
logger.setLevel(logging.INFO)
```

## Full Example

```python
import logging
from pydantic import BaseModel
from logly.integrations.pydantic import PydanticLogHandler


class User(BaseModel):
    name: str
    age: int


logger = logging.getLogger("myapp")
logger.addHandler(PydanticLogHandler())
logger.setLevel(logging.INFO)

user = User(name="Alice", age=30)
logger.info("User created: %s", user.model_dump())
```
