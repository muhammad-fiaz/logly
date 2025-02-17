"""
Logly: A ready-to-go logging utility.

Copyright (c) 2025 Muhammad Fiaz

This file is part of Logly.

Logly is free software: you can redistribute it and/or modify
it under the terms of the MIT License as published by
the Open Source Initiative.

You should have received a copy of the MIT License
along with Logly. If not, see <https://opensource.org/licenses/MIT>.
"""

from .logly import Logly, LogMessageConfig, LoglyConfig
from .exception import FilePathNotFoundException, FileAccessError, FileCreationError
from .version import get_version
from .__version__ import __version__

__all__ = [
    "Logly",
    "LogMessageConfig",
    "LoglyConfig",
    "FilePathNotFoundException",
    "FileAccessError",
    "FileCreationError",
    "get_version",
    "__version__"
]
