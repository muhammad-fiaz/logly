---
title: Colored Logging - Logly Examples
description: Complete guide to colored logging in Logly with default colors, custom colors, and the new FAIL level.
keywords: python, logging, example, colors, ansi, fail, colored, output, logly
---

# Colored Logging

This example demonstrates Logly's colored logging features, including default color mapping and custom color configuration.

## Default Colored Levels (NEW in v0.1.5)

Logly automatically applies colors to log levels when `color=True`:

```python
from logly import logger

# Colors are automatic! No need to configure
logger.trace("Entering function")           # Cyan
logger.debug("Variable x = 42")             # Blue
logger.info("Server started on port 8000")  # White
logger.success("User created successfully") # Green
logger.warning("Rate limit approaching")    # Yellow
logger.error("Database connection failed")  # Red
logger.critical("System crash imminent")    # Bright Red
logger.fail("Payment authorization failed") # Magenta (NEW)
```

## Default Color Mapping

| Level | Color | ANSI Code | Use Case |
|-------|-------|-----------|----------|
| **TRACE** | Cyan | `36` | Most verbose debugging |
| **DEBUG** | Blue | `34` | Development debugging |
| **INFO** | White | `37` | General information |
| **SUCCESS** | Green | `32` | Successful operations |
| **WARNING** | Yellow | `33` | Warning messages |
| **ERROR** | Red | `31` | Error conditions |
| **CRITICAL** | Bright Red | `91` | Critical failures |
| **FAIL** | Magenta | `35` | Operation failures |

## FAIL Level - Operation Failures

The FAIL level is designed for expected operation failures (vs unexpected errors):

```python
from logly import logger

# Authentication failures
logger.fail("Login failed", 
    user="alice", 
    attempts=3, 
    reason="invalid_password"
)

# Payment failures
logger.fail("Payment declined", 
    transaction_id="txn_123", 
    card_last4="1234",
    reason="insufficient_funds"
)

# Validation failures
logger.fail("Validation failed",
    field="email",
    value="invalid@",
    rule="email_format"
)

# API/Authorization failures
logger.fail("API request denied",
    endpoint="/api/admin",
    status=403,
    reason="insufficient_permissions"
)

# Timeout failures
logger.fail("Operation timeout",
    operation="database_query",
    timeout_seconds=30
)
```

### FAIL vs ERROR

**When to use FAIL:**
- Authentication failures (login, token validation)
- Authorization denials (permission checks)
- Validation failures (form validation, data validation)
- Payment/transaction failures
- Business rule violations
- Operation timeouts
- Expected failure conditions

**When to use ERROR:**
- Unexpected exceptions
- System errors
- Bugs in code
- Infrastructure failures
- Unhandled error conditions

```python
# FAIL - Expected operation failure (user mistake)
logger.fail("Login failed", reason="wrong_password")

# ERROR - Unexpected technical error (system issue)
logger.error("Login system crashed", exception=str(e))
```

## Custom Colors

Override default colors with your own color scheme:

```python
from logly import logger

# Define custom colors using color names
logger.configure(
    color=True,
    level_colors={
        "TRACE": "BRIGHT_CYAN",
        "DEBUG": "BRIGHT_BLUE",
        "INFO": "BRIGHT_WHITE",
        "SUCCESS": "BRIGHT_GREEN",
        "WARNING": "BRIGHT_YELLOW",
        "ERROR": "BRIGHT_RED",
        "CRITICAL": "BRIGHT_MAGENTA",
        "FAIL": "MAGENTA"
    }
)

# Or use ANSI color codes directly
logger.configure(
    color=True,
    level_colors={
        "TRACE": "96",   # Bright Cyan
        "DEBUG": "94",   # Bright Blue
        "INFO": "97",    # Bright White
        "SUCCESS": "92", # Bright Green
        "WARNING": "93", # Bright Yellow
        "ERROR": "91",   # Bright Red
        "CRITICAL": "95",# Bright Magenta
        "FAIL": "35"     # Magenta
    }
)

logger.info("Custom colors applied!")
```

## Available Colors

### Standard Colors

| Color Name | Code | Bright Version | Code |
|------------|------|----------------|------|
| `"BLACK"` | `30` | `"BRIGHT_BLACK"` / `"GRAY"` | `90` |
| `"RED"` | `31` | `"BRIGHT_RED"` | `91` |
| `"GREEN"` | `32` | `"BRIGHT_GREEN"` | `92` |
| `"YELLOW"` | `33` | `"BRIGHT_YELLOW"` | `93` |
| `"BLUE"` | `34` | `"BRIGHT_BLUE"` | `94` |
| `"MAGENTA"` | `35` | `"BRIGHT_MAGENTA"` | `95` |
| `"CYAN"` | `36` | `"BRIGHT_CYAN"` | `96` |
| `"WHITE"` | `37` | `"BRIGHT_WHITE"` | `97` |

## Disabling Colors

Disable colors for plain text output:

```python
from logly import logger

# Disable all colors
logger.configure(color=False)

logger.info("No colors")
logger.error("Plain text only")
```

## Per-Level Color Control

Enable colors for specific levels only:

```python
from logly import logger

logger.configure(
    color=True,
    color_levels={
        "INFO": False,    # No color for INFO
        "DEBUG": False,   # No color for DEBUG
        "ERROR": True,    # Color for ERROR
        "CRITICAL": True, # Color for CRITICAL
        "FAIL": True      # Color for FAIL
    }
)

# Only errors and critical messages are colored
logger.info("Plain text")       # No color
logger.error("Colored error")   # Red
logger.fail("Colored failure")  # Magenta
```

## Advanced: Color Callbacks

**Color callbacks** give you complete control over log message coloring and formatting. When a `color_callback` is provided, it takes **full precedence** over built-in colors and `level_colors` configuration.

### Color Callback vs Built-in Colors

| Feature | Built-in Colors | Color Callback |
|---------|----------------|----------------|
| **Setup** | Automatic (v0.1.5+) or `level_colors` dict | Custom function |
| **Flexibility** | Predefined ANSI colors | Any color library or custom ANSI codes |
| **Control** | Per-level color mapping | Full control over text formatting |
| **Precedence** | Lower priority | **Highest priority** (overrides everything) |
| **Use Case** | Simple color schemes | Rich terminal features (bold, underline, gradients) |
| **Libraries** | None needed | Rich, colorama, termcolor, etc. |

### When to Use Color Callbacks

**Use built-in colors (`level_colors`) when:**
- You want simple, clean color mapping
- ANSI colors are sufficient for your needs
- You prefer configuration over code
- You want minimal dependencies

**Use color callbacks when:**
- You need **advanced formatting** (bold, underline, dim, etc.)
- You want to integrate with **Rich**, **colorama**, or other libraries
- You need **conditional coloring** based on message content
- You want **dynamic colors** based on runtime state
- You need **gradient effects** or **custom styling**

### Basic Color Callback Example

```python
from logly import logger

def custom_color(level: str, text: str) -> str:
    """Custom color callback using ANSI codes."""
    colors = {
        "TRACE": "\033[36m",      # Cyan
        "DEBUG": "\033[34m",      # Blue
        "INFO": "\033[37m",       # White
        "SUCCESS": "\033[1;32m",  # Bold Green
        "WARNING": "\033[1;33m",  # Bold Yellow
        "ERROR": "\033[1;31m",    # Bold Red
        "CRITICAL": "\033[1;91m", # Bold Bright Red
        "FAIL": "\033[1;35m",     # Bold Magenta
    }
    reset = "\033[0m"
    
    color = colors.get(level, "")
    return f"{color}{text}{reset}" if color else text

logger.configure(
    color=True,
    color_callback=custom_color  # Takes full control!
)

logger.success("Bold green!")
logger.fail("Bold magenta!")
logger.error("Bold red!")
```

### Integration with Rich Library

Use Rich for **advanced terminal formatting**:

```python
from logly import logger
from rich.console import Console

console = Console()

def rich_color(level: str, text: str) -> str:
    """Color callback using Rich library."""
    styles = {
        "TRACE": "dim cyan",
        "DEBUG": "blue",
        "INFO": "white",
        "SUCCESS": "bold green",
        "WARNING": "bold yellow",
        "ERROR": "bold red",
        "CRITICAL": "bold white on red",
        "FAIL": "bold magenta",
    }
    
    style = styles.get(level, "white")
    
    # Rich provides advanced formatting
    from io import StringIO
    buffer = StringIO()
    temp_console = Console(file=buffer, force_terminal=True)
    temp_console.print(text, style=style, end="")
    return buffer.getvalue()

logger.configure(
    color=True,
    color_callback=rich_color
)

logger.info("Standard info")
logger.success("✓ Operation completed")
logger.critical("⚠ CRITICAL ALERT")
logger.fail("✗ Payment failed")
```

### Integration with Colorama

Use colorama for **cross-platform color support**:

```python
from logly import logger
from colorama import Fore, Style, init

# Initialize colorama (important for Windows)
init(autoreset=True)

def colorama_color(level: str, text: str) -> str:
    """Color callback using colorama."""
    colors = {
        "TRACE": Fore.CYAN,
        "DEBUG": Fore.BLUE,
        "INFO": Fore.WHITE,
        "SUCCESS": Fore.GREEN + Style.BRIGHT,
        "WARNING": Fore.YELLOW + Style.BRIGHT,
        "ERROR": Fore.RED + Style.BRIGHT,
        "CRITICAL": Fore.RED + Style.BRIGHT,
        "FAIL": Fore.MAGENTA + Style.BRIGHT,
    }
    
    color = colors.get(level, "")
    return f"{color}{text}{Style.RESET_ALL}"

logger.configure(
    color=True,
    color_callback=colorama_color
)

logger.success("Works perfectly on Windows!")
logger.fail("Cross-platform colors")
```

### Integration with Termcolor

Use termcolor for **quick color formatting**:

```python
from logly import logger
from termcolor import colored

def termcolor_callback(level: str, text: str) -> str:
    """Color callback using termcolor."""
    color_map = {
        "TRACE": ("cyan", None),
        "DEBUG": ("blue", None),
        "INFO": ("white", None),
        "SUCCESS": ("green", ["bold"]),
        "WARNING": ("yellow", ["bold"]),
        "ERROR": ("red", ["bold"]),
        "CRITICAL": ("white", ["bold"], "on_red"),
        "FAIL": ("magenta", ["bold"]),
    }
    
    config = color_map.get(level, ("white", None))
    color = config[0]
    attrs = config[1] if len(config) > 1 else None
    on_color = config[2] if len(config) > 2 else None
    
    return colored(text, color, on_color, attrs=attrs)

logger.configure(
    color=True,
    color_callback=termcolor_callback
)

logger.info("Using termcolor")
logger.critical("Critical with background")
```

### Advanced: Conditional Coloring

Apply different colors based on message content:

```python
from logly import logger

def smart_color(level: str, text: str) -> str:
    """Conditional coloring based on content."""
    
    # Base color from level
    base_colors = {
        "ERROR": "\033[31m",     # Red
        "FAIL": "\033[35m",      # Magenta
        "WARNING": "\033[33m",   # Yellow
        "SUCCESS": "\033[32m",   # Green
    }
    
    # Enhanced colors for specific keywords
    if "database" in text.lower():
        color = "\033[1;31m"  # Bold red for database issues
    elif "payment" in text.lower() or "transaction" in text.lower():
        color = "\033[1;35m"  # Bold magenta for payment issues
    elif "timeout" in text.lower():
        color = "\033[1;33m"  # Bold yellow for timeouts
    else:
        color = base_colors.get(level, "\033[37m")
    
    return f"{color}{text}\033[0m"

logger.configure(
    color=True,
    color_callback=smart_color
)

logger.error("Database connection failed")  # Bold red
logger.fail("Payment timeout occurred")     # Bold magenta
logger.warning("API timeout")               # Bold yellow
```

### Color Callback Precedence

**Important:** Color callbacks have **highest precedence**:

```python
from logly import logger

def my_callback(level: str, text: str) -> str:
    return f"\033[35m{text}\033[0m"  # Always magenta

logger.configure(
    color=True,
    level_colors={
        "INFO": "BRIGHT_CYAN"  # This will be IGNORED
    },
    color_callback=my_callback  # This takes full control
)

logger.info("This will be MAGENTA, not cyan")  # Callback wins!
```

**Precedence order:**
1. **color_callback** (highest - if provided, overrides everything)
2. **level_colors** (medium - custom color mapping)
3. **Default colors** (lowest - automatic in v0.1.5+)

### Best Practices

**✅ DO:**
- Use callbacks for **advanced formatting** needs
- Use callbacks when integrating **external libraries**
- Use `level_colors` for **simple color schemes**
- Keep callbacks **fast and efficient**
- Handle **exceptions** in your callback (return plain text on error)

**❌ DON'T:**
- Use callbacks for simple color changes (use `level_colors` instead)
- Perform **heavy computation** in callbacks (called for every log message)
- **Block or wait** in callbacks (performance impact)
- Forget to **reset ANSI codes** (causes color bleeding)

## Complete Example

```python
from logly import logger

# Configure with custom colors
logger.configure(
    level="TRACE",
    color=True,
    level_colors={
        "TRACE": "CYAN",
        "DEBUG": "BLUE",
        "INFO": "WHITE",
        "SUCCESS": "BRIGHT_GREEN",
        "WARNING": "BRIGHT_YELLOW",
        "ERROR": "BRIGHT_RED",
        "CRITICAL": "BRIGHT_MAGENTA",
        "FAIL": "MAGENTA"
    }
)

# Application startup
logger.info("Starting application", version="1.0.0")
logger.success("Configuration loaded")

# Simulated operations
logger.trace("Entering authentication flow")
logger.debug("Checking credentials", user="alice")

# Success case
logger.success("User authenticated", user="alice", session_id="sess_123")

# Warning case
logger.warning("Rate limit at 80%", current=80, limit=100)

# Failure case (expected failure)
logger.fail("Payment declined", 
    transaction_id="txn_456",
    reason="insufficient_funds",
    amount=150.00,
    available=75.50
)

# Error case (unexpected error)
try:
    1 / 0
except Exception as e:
    logger.error("Unexpected error", exception=str(e))

# Critical case
logger.critical("Database connection pool exhausted", 
    active=100, 
    max=100,
    queued=50
)

logger.complete()
```

## Expected Output

```
2025-01-15T14:30:00.123456+00:00 [INFO] Starting application | version=1.0.0
2025-01-15T14:30:00.124567+00:00 [SUCCESS] Configuration loaded
2025-01-15T14:30:00.125678+00:00 [TRACE] Entering authentication flow
2025-01-15T14:30:00.126789+00:00 [DEBUG] Checking credentials | user=alice
2025-01-15T14:30:00.127890+00:00 [SUCCESS] User authenticated | user=alice | session_id=sess_123
2025-01-15T14:30:00.128901+00:00 [WARN] Rate limit at 80% | current=80 | limit=100
2025-01-15T14:30:00.129012+00:00 [FAIL] Payment declined | transaction_id=txn_456 | reason=insufficient_funds | amount=150.0 | available=75.5
2025-01-15T14:30:00.130123+00:00 [ERROR] Unexpected error | exception=division by zero
2025-01-15T14:30:00.131234+00:00 [CRITICAL] Database connection pool exhausted | active=100 | max=100 | queued=50
```

Each level will appear in its configured color in your terminal!

## Key Features Demonstrated

- ✅ **Default Colors**: Automatic color mapping for all 8 levels
- ✅ **FAIL Level**: New level for operation failures (v0.1.5)
- ✅ **Custom Colors**: Override defaults with ANSI codes or color names
- ✅ **Color Control**: Per-level enable/disable
- ✅ **Color Callbacks**: Integration with external color libraries
- ✅ **Semantic Logging**: FAIL for expected failures, ERROR for unexpected errors
