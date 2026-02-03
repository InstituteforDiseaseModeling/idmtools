"""
idmtools container platform.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
# flake8: noqa F821
try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python < 3.8
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("idmtools-platform-container")  # Use your actual package name
except PackageNotFoundError:
    # Package not installed, use fallback
    __version__ = "0.0.0+unknown"

