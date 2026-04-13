"""idmtools comps platform.

We try to load the CLI here but if idmtools-cli is not installed, we fail gracefully.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
# flake8: noqa F821
from idmtools_platform_comps.plugin_info import COMPSPlatformSpecification
try: # since cli is not required but we always try to load file, wrap in try except
    from idmtools_platform_comps.comps_cli import CompsCLI
except ImportError:
    pass

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python < 3.8
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("idmtools-platform-comps")  # Use your actual package name
except PackageNotFoundError:
    # Package not installed, use fallback
    __version__ = "0.0.0+unknown"

