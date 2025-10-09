@_default:
  just --list

@lock:
  uv lock

@lock-upgrade:
  uv lock --upgrade

@develop:
  uv run maturin develop --uv

@develop-release:
  uv run maturin develop -r --uv

@install: develop
  uv sync --frozen --all-extras

@install-release: develop-release
  uv sync --frozen --all-extras

@build:
  cargo build --release

@release:
  uv run maturin build --release

@docs:
  uv run mkdocs build

@docs-serve:
  uv run mkdocs serve

@clean:
  cargo clean
  rm -rf target/
  rm -rf dist/
  rm -rf site/

@lint:
  echo "Running cargo check..."
  just check
  echo "Running cargo clippy..."
  just clippy
  echo "Running cargo fmt check..."
  just fmt
  echo "Running mypy..."
  just mypy
  echo "Running ruff check..."
  just ruff-check
  echo "Running ruff format check..."
  just ruff-format

@check:
  cargo check

@clippy:
  cargo clippy --all-targets

@fmt:
  cargo fmt --all -- --check

@mypy:
  uv run mypy logly tests

@ruff-check:
  uv run ruff check logly tests --fix

@ruff-format:
  uv run ruff format logly tests --check

@test *args="":
  uv run pytest {{args}}

@coverage:
  uv run pytest --cov=logly --cov-report=html --cov-report=term-missing

@ci: lint
  just test
  just build
  just docs

@all: clean install lint test coverage docs
  echo "All checks passed! ✅"
