"""idmtools models package.

This package provides some common model tasks like Python, Template Scripts, or Python task.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python < 3.8
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("idmtools-models")  # Use your actual package name
except PackageNotFoundError:
    # Package not installed, use fallback
    __version__ = "0.0.0+unknown"

