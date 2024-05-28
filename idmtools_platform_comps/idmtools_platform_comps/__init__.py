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
__version__ = "1.7.10"
