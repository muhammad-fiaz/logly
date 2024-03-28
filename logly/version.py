
# version.py
"""
Logly: A ready to go logging utility.

Copyright (c) 2023 Muhammad Fiaz

This file is part of Logly.

Logly is free software: you can redistribute it and/or modify
it under the terms of the MIT License as published by
the Open Source Initiative.

You should have received a copy of the MIT License
along with Logly. If not, see <https://opensource.org/licenses/MIT>.
"""

import importlib.metadata

def get_latest_release_version(package_name):
    """
    Get the latest released version of a Python package.

    Args:
        package_name (str): The name of the Python package.

    Returns:
        str: The latest released version or '0.0.0' if not found.

    """
    try:
        distribution = importlib.metadata.distribution(package_name)
        return distribution.version
    except importlib.metadata.PackageNotFoundError:
        return '0.0.0'

def get_Version(current_version):
    """
    Check if there is a newer version of the package available.

    Args:
        current_version (str): The current version of the package.

    Returns:
        None: Prints a message indicating if a newer version is available.

    """
    package_name = 'logly'
    latest_version = get_latest_release_version(package_name)

    if latest_version > current_version:
        print(f"A newer version ({latest_version}) of logly is available.")
    else:
        pass

