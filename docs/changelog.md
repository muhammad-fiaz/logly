---
title: Changelog - Logly Python Logging Library
description: Logly changelog and release notes. See what's new in each version, bug fixes, and feature updates for the Python logging library.
keywords: python, logging, changelog, releases, updates, version, history, logly
---

# Changelog

## Release Notes

For detailed changelogs, release notes, and version history, please refer to the [**GitHub Releases**](https://github.com/muhammad-fiaz/logly/releases) page.

Each release includes:

- ✨ New features and enhancements
- 🐛 Bug fixes and patches
- 📝 Breaking changes (if any)
- 🔧 Performance improvements
- 📚 Documentation updates

[**View All Releases →**](https://github.com/muhammad-fiaz/logly/releases)

---


## Release History

For detailed changelogs of each release, please visit the [GitHub Releases](https://github.com/muhammad-fiaz/logly/releases) page.

---

## Version History

### Versioning Scheme

Logly follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: New features (backwards-compatible)
- **PATCH** version: Bug fixes (backwards-compatible)

### Release Schedule

- **Minor Releases**: Every 1-2 months
- **Patch Releases**: As needed for critical bugs
- **Major Releases**: When breaking changes are necessary

---

## Migration Guides

### From Python `logging`

Logly is largely compatible with Python's standard `logging`, but with performance benefits:

```python
# Before (logging)
import logging
logging.basicConfig(level=logging.INFO)
logging.info("Hello")

# After (logly)
from logly import logger
logger.configure(level="INFO")
logger.add("console")
logger.info("Hello")
```

**Key Differences:**
- ✅ **Explicit sinks**: Must call `logger.add()` to add output targets
- ✅ **Structured logging**: Use kwargs for structured fields
- ✅ **Cleanup required**: Call `logger.complete()` at exit

### From Loguru

Logly API is inspired by Loguru but built for performance:

```python
# Before (loguru)
from loguru import logger
logger.add("file.log", rotation="500 MB")
logger.info("Hello {name}", name="World")

# After (logly)
from logly import logger
logger.add("file.log", rotation="500 MB")
logger.info("Hello {name}", name="World")
```

**Key Differences:**
- ✅ **Must configure**: Call `logger.configure()` before adding sinks
- ✅ **Performance**: 10-100x faster for high-throughput scenarios
- ✅ **Type safety**: Full type hints for IDE support
- ✅ **Rust backend**: Native performance

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](https://github.com/muhammad-fiaz/logly/blob/main/CONTRIBUTING.md) for guidelines.

### Reporting Issues

Found a bug? Have a feature request?

1. **Search existing issues** to avoid duplicates
2. **Open a new issue** with clear description and reproduction steps
3. **Include system info**: OS, Python version, Logly version

### Pull Requests

1. **Fork** the repository
2. **Create branch**: `git checkout -b feature/my-feature`
3. **Make changes** with tests
4. **Run tests**: `uv run pytest`
5. **Submit PR** with clear description

---

## Acknowledgments

### Inspiration

Logly was inspired by:
- [Loguru](https://github.com/Delgan/loguru) - API design and developer experience
- [Tracing](https://github.com/tokio-rs/tracing) - Rust performance patterns
- [Slog](https://github.com/slog-rs/slog) - Structured logging concepts

### Dependencies

Built with:
- [PyO3](https://github.com/PyO3/PyO3) - Rust bindings for Python
- [Tokio](https://github.com/tokio-rs/tokio) - Async runtime
- [Serde](https://github.com/serde-rs/serde) - Serialization

### Community

Thanks to all contributors, issue reporters, and users!

---

## Links

- **Documentation**: [muhammad-fiaz.github.io/logly](https://muhammad-fiaz.github.io/logly/)
- **PyPI**: [pypi.org/project/logly](https://pypi.org/project/logly/)
- **GitHub**: [github.com/muhammad-fiaz/logly](https://github.com/muhammad-fiaz/logly)
- **Issues**: [github.com/muhammad-fiaz/logly/issues](https://github.com/muhammad-fiaz/logly/issues)
- **Discussions**: [github.com/muhammad-fiaz/logly/discussions](https://github.com/muhammad-fiaz/logly/discussions)

---

## Support

### Getting Help

- **Documentation**: Check the [docs](https://muhammad-fiaz.github.io/logly/)
- **API Reference**: See [API docs](https://muhammad-fiaz.github.io/logly/api-reference/)
- **Issues**: Open an [issue](https://github.com/muhammad-fiaz/logly/issues)
- **Discussions**: Ask in [discussions](https://github.com/muhammad-fiaz/logly/discussions)

### Commercial Support

For commercial support, consulting, or custom features:
- **Email**: contact@muhammad-fiaz.com
- **GitHub**: [@muhammad-fiaz](https://github.com/muhammad-fiaz)

---

## License

Logly is released under the [MIT License](https://github.com/muhammad-fiaz/logly/blob/main/LICENSE).

Copyright (c) 2025 Muhammad Fiaz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
