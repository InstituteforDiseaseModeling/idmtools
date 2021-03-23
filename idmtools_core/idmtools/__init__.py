import sys
from idmtools.core.exceptions import idmtools_error_handler
from idmtools.config.idm_config_parser import IdmConfigParser
__version__ = "1.6.3.0"

# only set exception hook if it has not been overridden
if sys.excepthook == sys.__excepthook__:
    sys.excepthook = idmtools_error_handler
IdmConfigParser.ensure_init()
