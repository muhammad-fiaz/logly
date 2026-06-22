# Contributing to Logly

Thank you for your interest in contributing to Logly! This guide will help you get started.

## Prerequisites

- **Rust**: Latest stable (`rustup update stable`)
- **Python**: 3.10+
- **uv**: `pip install uv`
- **maturin**: `cargo install maturin`

## Development Setup

### 1. Fork the Repository

First, fork the [Logly repository](https://github.com/muhammad-fiaz/logly) on GitHub by clicking the **Fork** button.

### 2. Clone Your Fork

```bash
git clone https://github.com/<your-username>/logly.git
cd logly
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/muhammad-fiaz/logly.git
```

### 2. Create Virtual Environment

```bash
uv venv
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Build the Native Extension

```bash
uv run maturin develop
```

### 5. Install Pre-commit Hooks

```bash
uv run pre-commit install
```

## Development Workflow

### Before Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Ensure all checks pass:
   ```bash
   cargo fmt --check
   cargo clippy --workspace --all-targets -- -D warnings
   cargo test --workspace
   ruff check .
   ruff format --check .
   uv run pytest -v
   ```

### Making Changes

1. **Rust code** (in `crates/`):
   - Follow existing code patterns
   - Add tests for new functionality
   - Run `cargo fmt` before committing

2. **Python code** (in `logly/`):
   - Follow existing code patterns
   - Add type hints for new functions
   - Run `ruff format` before committing

3. **Documentation** (in `docs/`):
   - Follow existing patterns
   - Test locally with `uv run mkdocs serve`

### Running Tests

```bash
# Rust tests
cargo test --workspace

# Python tests
uv run pytest -v

# Specific test file
uv run pytest tests/test_logger.py -v

# With coverage
uv run pytest --cov=logly tests/
```

### Linting and Formatting

```bash
# Check Rust formatting
cargo fmt --check

# Fix Rust formatting
cargo fmt

# Check Rust lints
cargo clippy --workspace --all-targets -- -D warnings

# Check Python linting
ruff check .

# Fix Python linting
ruff check --fix .

# Check Python formatting
ruff format --check .

# Fix Python formatting
ruff format .
```

### Building Documentation

```bash
# Serve docs locally
uv run mkdocs serve

# Build docs
uv run mkdocs build
```

## Project Structure

```
logly/
├── crates/              # Rust crates (monorepo)
│   ├── error/          # Error types
│   ├── config/         # Configuration
│   ├── levels/         # Log levels
│   ├── record/         # Log records
│   ├── color/          # ANSI colors
│   ├── format/         # Formatters
│   ├── filter/         # Filters
│   ├── rotate/         # File rotation
│   ├── compress/       # Compression
│   ├── concurrency/    # Background workers
│   ├── schedule/       # Scheduling
│   ├── context/        # Context management
│   ├── sink/           # Sinks
│   └── core/           # Dispatch engine
├── src/                # PyO3 bindings
├── logly/              # Python package
│   ├── logger.py      # Main Logger class
│   ├── models.py      # Pydantic config models
│   ├── exceptions.py  # Exception hierarchy
│   ├── integrations/  # FastAPI, Django, stdlib, Rich, telemetry
│   └── _logly.pyi    # Type stubs
├── tests/              # Python tests
├── examples/           # Usage examples
├── docs/               # Documentation source
└── site/               # Built documentation
```

## Coding Standards

### Rust

- Use `cargo fmt` for consistent formatting
- Use `cargo clippy` for lint checks
- Add `#[cfg(test)] mod tests` for unit tests
- Use `?` for error propagation
- Document public functions with `///` comments

### Python

- Use `ruff` for linting and formatting
- Add type hints for all public functions
- Use `__all__` for public API
- Add docstrings for public classes and functions
- Use `dataclass` or `NamedTuple` for simple data structures

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all checks pass**:
   ```bash
   cargo fmt --check
   cargo clippy --workspace --all-targets -- -D warnings
   cargo test --workspace
   ruff check .
   ruff format --check .
   uv run pytest -v
   ```
4. **Create a pull request** with a clear description
5. **Reference any related issues**

## Reporting Issues

### Bug Reports

- Use the bug report template
- Include steps to reproduce
- Include your environment details

### Feature Requests

- Use the feature request template
- Explain the use case
- Provide examples if possible

### Documentation Issues

- Use the docs issue template
- Specify which page needs updating
- Provide the corrected content if possible

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Questions?

- Open a discussion on GitHub
- Use the help wanted template for specific issues
