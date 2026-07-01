@_default:
  just --list

@lint:
  just --justfile {{justfile()}} check
  just --justfile {{justfile()}} clippy
  just --justfile {{justfile()}} fmt
  just --justfile {{justfile()}} mypy
  just --justfile {{justfile()}} ruff-check
  just --justfile {{justfile()}} ruff-format

@lock:
  uv lock

@lock-upgrade:
  uv lock --upgrade

@develop:
  uv run maturin develop --uv

@develop-release:
  uv run maturin develop -r --uv

@install:
  uv run maturin develop --uv && \
  uv sync --frozen --all-extras

@install-release:
  uv run maturin develop -r --uv && \
  uv sync --frozen --all-extras

@check:
  cargo check --workspace

@clippy:
  cargo clippy --workspace --all-targets -- -D warnings

@fmt:
  cargo fmt --all -- --check

@mypy:
  uv run --group dev mypy logly tests

@ruff-check:
  uv run --group dev ruff check logly tests --fix

@ruff-format:
  uv run --group dev ruff format logly tests

@test *args="":
  cargo test --workspace
  uv run --group dev pytest {{args}}

@build:
  uv run --group dev maturin build

@docs-serve:
  uv run --group dev mkdocs serve

@docs-deploy:
  uv run --group dev mkdocs gh-deploy
