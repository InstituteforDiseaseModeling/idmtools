"""idmtools core package.

This init installs a system exception hook for idmtools.
It also ensures the configuration is loaded.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import sys
from idmtools.core.exceptions import idmtools_error_handler
from idmtools.config.idm_config_parser import IdmConfigParser   # noqa: F401

__version__ = "1.7.10"

# only set exception hook if it has not been overridden
if sys.excepthook == sys.__excepthook__:
    sys.excepthook = idmtools_error_handler
