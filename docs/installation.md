---
title: Installation - Logly Python Logging Library
description: Install Logly logging library for Python. Learn how to install with pip, uv, poetry, or from source with comprehensive setup instructions.
keywords: python, logging, installation, pip, uv, poetry, setup, logly
---

# Installation

## Prerequisites

- **Python**: 3.10 or higher
- **Operating System**: Windows, macOS, or Linux
- **pip**: Latest version recommended

---

## Install from PyPI

The easiest way to install Logly is from PyPI:

=== "pip"

    ```bash
    pip install logly
    ```

=== "uv"

    ```bash
    uv pip install logly
    ```

=== "poetry"

    ```bash
    poetry add logly
    ```

=== "pipenv"

    ```bash
    pipenv install logly
    ```

---

## Verify Installation

After installation, verify that Logly is working correctly:

```python
from logly import logger

logger.info("Logly installed successfully!")
logger.complete()
```

You should see:
```
2025-01-15 10:30:45 | INFO     | Logly installed successfully!
```

---

## Version Information

Check the installed version:

```python
import logly
print(logly.__version__)  # e.g., "0.1.2"
```

**Output:**
```
0.1.2
```

---

## Platform-Specific Installation

### Windows

```powershell
python -m pip install --upgrade pip
pip install logly
```

### macOS

```bash
python3 -m pip install --upgrade pip
pip3 install logly
```

### Linux

```bash
python3 -m pip install --upgrade pip
pip3 install logly
```

---

## Install from Source

For developers or users who want the latest development version:

### Prerequisites for Building

- **Python**: 3.10+
- **Rust**: 1.70+ ([Install Rust](https://rustup.rs/))
- **maturin**: Python package for building Rust extensions

### Build Steps

=== "Clone and Install"

    ```bash
    # Clone repository
    git clone https://github.com/muhammad-fiaz/logly.git
    cd logly

    # Install with uv (recommended)
    uv pip install -e .
    ```

=== "Development Build"

    ```bash
    # Clone repository
    git clone https://github.com/muhammad-fiaz/logly.git
    cd logly

    # Install maturin
    pip install maturin

    # Build in development mode
    maturin develop

    # Run tests
    pytest
    ```

=== "Release Build"

    ```bash
    # Clone repository
    git clone https://github.com/muhammad-fiaz/logly.git
    cd logly

    # Install maturin
    pip install maturin

    # Build wheel
    maturin build --release

    # Install wheel
    pip install target/wheels/logly-*.whl
    ```

---

## Docker Installation

For containerized environments:

### Dockerfile Example

```dockerfile
FROM python:3.12-slim

# Install logly
RUN pip install --no-cache-dir logly

# Copy application
COPY . /app
WORKDIR /app

# Run application
CMD ["python", "app.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    image: python:3.12-slim
    volumes:
      - ./:/app
      - ./logs:/app/logs
    working_dir: /app
    command: >
      sh -c "pip install logly && python app.py"
```

---

## Virtual Environments

It's recommended to use virtual environments:

=== "venv"

    ```bash
    # Create virtual environment
    python -m venv venv

    # Activate (Windows)
    venv\Scripts\activate

    # Activate (Unix/macOS)
    source venv/bin/activate

    # Install logly
    pip install logly
    ```

=== "conda"

    ```bash
    # Create conda environment
    conda create -n myproject python=3.12

    # Activate environment
    conda activate myproject

    # Install logly
    pip install logly
    ```

=== "uv"

    ```bash
    # Create project with uv
    uv init myproject
    cd myproject

    # Add logly
    uv add logly

    # Run application
    uv run python app.py
    ```

---

## Troubleshooting

### Import Error

If you encounter import errors:

```python
ImportError: cannot import name 'logger' from 'logly'
```

**Output:**
```
Traceback (most recent call last):
  File "test.py", line 1, in <module>
    ImportError: cannot import name 'logger' from 'logly'
```

**Solution**: Ensure you're using Python 3.10+:

```bash
python --version  # Should be >= 3.10
pip install --upgrade logly
```

**Output:**
```
Python 3.12.0
Collecting logly
  Downloading logly-0.1.2.tar.gz (15 kB)
Successfully installed logly-0.1.2
```

### Build Errors (Source Installation)

If building from source fails:

1. **Install Rust toolchain**:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Update maturin**:
   ```bash
   pip install --upgrade maturin
   ```

3. **Clean and rebuild**:
   ```bash
   cargo clean
   maturin develop --release
   ```

### Permission Errors

On Unix systems, if you get permission errors:

```bash
# Use --user flag
pip install --user logly

# Or use sudo (not recommended)
sudo pip install logly
```

---

## Upgrade

To upgrade to the latest version:

```bash
pip install --upgrade logly
```

Check release notes: [Changelog](changelog.md)

---

## Uninstall

To remove Logly:

```bash
pip uninstall logly
```

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.10 | 3.11+ |
| RAM | 50 MB | 100 MB+ |
| Disk | 5 MB | 10 MB+ |
| CPU | Any | Multi-core for async |

---

## Next Steps

Now that Logly is installed, check out the [Quick Start Guide](quickstart.md) to start logging!

---

## Need Help?

- 📚 [Quick Start](quickstart.md)
- 🐛 [Report Issues](https://github.com/muhammad-fiaz/logly/issues)
- 💬 [Discussions](https://github.com/muhammad-fiaz/logly/discussions)
