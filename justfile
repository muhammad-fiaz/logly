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

@install: && develop
  uv sync --frozen --all-extras

@install-release: && develop-release
  uv sync --frozen --all-extras

@lint:
  echo cargo check
  just --justfile {{justfile()}} check
  echo cargo clippy
  just --justfile {{justfile()}} clippy
  echo cargo fmt
  just --justfile {{justfile()}} fmt
  echo mypy
  just --justfile {{justfile()}} mypy
  echo ruff check
  just --justfile {{justfile()}} ruff-check
  echo ruff formatting
  just --justfile {{justfile()}} ruff-format

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
  uv run ruff format logly tests

@test *args="":
  uv run pytest {{args}}
