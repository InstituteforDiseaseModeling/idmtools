"""idmtools core package.

This init installs a system exception hook for idmtools.
It also ensures the configuration is loaded.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import sys
from idmtools.core.exceptions import idmtools_error_handler
from idmtools.config.idm_config_parser import IdmConfigParser   # noqa: F401

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python < 3.8
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("idmtools")  # Use your actual package name
except PackageNotFoundError:
    # Package not installed, use fallback
    __version__ = "0.0.0+unknown"


# only set exception hook if it has not been overridden
if sys.excepthook == sys.__excepthook__:
    sys.excepthook = idmtools_error_handler
