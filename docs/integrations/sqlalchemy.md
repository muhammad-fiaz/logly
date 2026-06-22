---
title: SQLAlchemy
description: Engine event listener for SQLAlchemy query logging.
---

# SQLAlchemy

Routes SQLAlchemy engine and query logs through Logly. `patch_engine()` enables SQL echo on a specific engine.

## Installation

This integration requires the `sqlalchemy` package.

::: code-group

```bash [uv]
uv add logly[sqlalchemy]
```

```bash [pip]
pip install "logly[sqlalchemy]"
```

```bash [uv (without extras)]
uv add sqlalchemy
```

```bash [pip (without extras)]
pip install sqlalchemy
```

:::

::: warning Missing Dependency
If `sqlalchemy` is not installed, you'll see:

```
ModuleNotFoundError: No module named 'sqlalchemy'
```
:::

## Usage

```python
from logly.integrations.sqlalchemy import setup_sqlalchemy_logging
setup_sqlalchemy_logging(level="INFO", echo=True)
```

## Patch Engine

```python
from sqlalchemy import create_engine
from logly.integrations.sqlalchemy import patch_engine

engine = create_engine("sqlite:///db.sqlite3")
patch_engine(engine, level="DEBUG")
```

## Full Example

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
from logly.integrations.sqlalchemy import setup_sqlalchemy_logging

setup_sqlalchemy_logging(level="INFO", echo=True)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

engine = create_engine("sqlite:///db.sqlite3")
Base.metadata.create_all(engine)

with Session(engine) as session:
    user = User(name="Alice")
    session.add(user)
    session.commit()
```
