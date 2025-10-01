# Development Guide

This guide covers development setup, testing, code quality, and contribution guidelines for Logly.

## Development Environment Setup

### Prerequisites

- Python 3.9+
- Rust toolchain (for building the Rust backend)
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/muhammad-fiaz/logly.git
   cd logly
   ```

2. **Install dependencies:**
   ```bash
   # Install Python dependencies with uv
   uv sync --dev

   # Install Rust dependencies
   cargo build
   ```

3. **Verify installation:**
   ```bash
   # Run a quick test
   uv run python -c "import logly; print('Logly installed successfully!')"
   ```

## Testing

Logly maintains comprehensive test coverage with 96%+ code coverage across all functionality.

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage report
uv run pytest --cov=logly --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_logger_features.py

# Run specific test
uv run pytest tests/test_logger_features.py::test_all_log_levels -v
```

### Test Structure

Tests are organized in the `tests/` directory:

- `test_logly.py` - Basic functionality tests
- `test_logger_features.py` - Core logging features
- `test_callbacks_and_templates.py` - Callbacks and template strings
- `test_performance_features.py` - Performance and edge cases

### Writing Tests

When adding new features, ensure comprehensive test coverage:

```python
def test_new_feature(tmp_path):
    """Test description for new feature."""
    # Setup
    logger.add(str(tmp_path / "test.log"))
    logger.configure(level="INFO")

    # Test the feature
    # ... test code ...

    # Assertions
    # ... verify behavior ...

    logger.complete()
```

## Code Quality

Logly maintains a 10.00/10 pylint score and follows strict code quality standards.

### Code Analysis

```bash
# Run pylint on source code
uv run pylint logly/

# Run pylint on tests
uv run pylint tests/

# Run on entire codebase
uv run pylint logly/ tests/
```

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Add comprehensive docstrings for all public functions
- Keep line length under 100 characters (with justified exceptions)
- Use descriptive variable names

### Pre-commit Hooks

Install pre-commit hooks to automatically check code quality:

```bash
pip install pre-commit
pre-commit install
```

## Building and Packaging

### Building the Rust Extension

```bash
# Debug build
cargo build

# Release build
cargo build --release

# Build Python wheel
uv run maturin develop
```

### Building Documentation

```bash
# Build docs locally
uv run mkdocs build

# Serve docs locally for development
uv run mkdocs serve

# Deploy docs (requires proper permissions)
uv run mkdocs gh-deploy
```

## Performance Testing

Logly includes comprehensive benchmarks to ensure performance standards.

### Running Benchmarks

```bash
# File logging benchmark
uv run python bench/benchmark_logging.py

# Concurrency benchmark
uv run python bench/benchmark_concurrency.py

# Latency microbenchmark
uv run python bench/benchmark_latency.py

# Matrix benchmark (comprehensive)
uv run python bench/benchmark_matrix.py
```

### Benchmark Results

Current performance metrics (as of October 2025):

- **File Logging**: ~150,000 messages/second
- **Concurrent Logging**: ~400,000 messages/second (4 threads)
- **Latency**: p50 < 10μs, p95 < 50μs, p99 < 100μs

## Contributing

### Development Workflow

1. **Fork and clone** the repository
2. **Create a feature branch** from `main`
3. **Make changes** following the code quality guidelines
4. **Add tests** for new functionality
5. **Run the full test suite** and ensure all checks pass
6. **Update documentation** if needed
7. **Submit a pull request**

### Pull Request Checklist

- [ ] Tests pass (`uv run pytest`)
- [ ] Code quality checks pass (`uv run pylint logly/ tests/`)
- [ ] Coverage remains at 96%+ (`uv run pytest --cov=logly`)
- [ ] Documentation updated if needed
- [ ] Changelog updated for user-facing changes
- [ ] Commit messages follow conventional format

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Architecture Overview

### Core Components

- **Python API** (`logly/__init__.py`): User-facing logging interface
- **Rust Backend** (`src/`): High-performance logging implementation
- **PyO3 Bindings** (`src/lib.rs`): Python-Rust interop layer

### Key Design Decisions

- **Rust Backend**: Provides memory safety and performance
- **Async by Default**: Non-blocking logging operations
- **Callback System**: Extensible logging pipeline
- **Template Strings**: Efficient string formatting
- **Context Binding**: Structured logging support

## Troubleshooting

### Common Issues

**Import Error**: Ensure the Rust extension is built
```bash
uv run maturin develop
```

**Test Failures**: Check Python and Rust versions
```bash
python --version
cargo --version
```

**Performance Issues**: Run benchmarks to identify bottlenecks
```bash
uv run python bench/benchmark_matrix.py
```

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/muhammad-fiaz/logly/issues)
- **Discussions**: [GitHub Discussions](https://github.com/muhammad-fiaz/logly/discussions)
- **Documentation**: [Logly Docs](https://muhammad-fiaz.github.io/logly/)

## Release Process

For maintainers:

1. Update version in `Cargo.toml` and `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag
4. Build and publish to PyPI
5. Deploy documentation

```bash
# Tag release
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3

# Build and publish
uv run maturin build
uv run twine upload dist/*
```