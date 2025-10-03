---
title: Examples - Logly Python Logging
description: Comprehensive examples for Logly Python logging library. Learn through practical code examples covering all major features.
keywords: python, logging, examples, tutorials, code samples, logly
---

# Examples

Welcome to the Logly examples! This section contains comprehensive, runnable examples that demonstrate all major features of the Logly logging library.


## 📋 Table of Contents

### 🏗️ Getting Started Examples

- **[Basic Console Logging](basic-console.md)** - Start here! Simple console output with colors and formatting
- **[Per-Level Controls](per-level-controls.md)** - Control console output, timestamps, and colors per log level
- **[Template String Formatting](template-strings.md)** - Custom log message formatting with placeholders

### 📁 File & Storage Examples

- **[File Logging with Rotation](file-rotation.md)** - Time-based and size-based log rotation
- **[JSON Logging](json-logging.md)** - Structured JSON output for log analysis
- **[Multi-Sink Setup](multi-sink.md)** - Multiple outputs with independent filtering

### 🔧 Advanced Features

- **[Async Logging](async-logging.md)** - Background writing for high-performance applications
- **[Context Binding](context-binding.md)** - Add persistent context to all log messages
- **[Exception Handling](exception-handling.md)** - Automatic exception logging and traceback capture
- **[Color Callback Styling](color-callback.md)** - Custom color styling with callback functions

## 🚀 Quick Start

Copy and run any example to see Logly in action:

```bash
# Clone the repository
git clone https://github.com/muhammad-fiaz/logly.git
cd logly

# Install dependencies
pip install -e .

# Run an example
python examples/basic_console.py
```

## 💡 Tips for Learning

1. **Start Simple**: Begin with [Basic Console Logging](basic-console.md) to understand the fundamentals
2. **Build Up**: Each example builds on previous concepts
3. **Experiment**: Modify the code and see what happens
4. **Combine Features**: Mix techniques from different examples

## 📚 Related Documentation

- **[Quick Start Guide](../quickstart.md)** - Get up and running in 5 minutes
- **[API Reference](../api-reference/index.md)** - Complete method documentation
- **[Configuration Guide](../guides/configuration.md)** - Advanced configuration options
- **[Production Deployment](../guides/production-deployment.md)** - Production best practices