# flake8: noqa F821
from idmtools_platform_comps.plugin_info import COMPSPlatformSpecification
try: # since cli is not required but we always try to load file, wrap in try except
    from idmtools_platform_comps.comps_cli import CompsCLI
except ImportError:
    pass
<<<<<<< HEAD
__version__ = "1.0.0.0"
=======
__version__ = "1.0.0+nightly.0"
>>>>>>> a8289087eb0fc6076ae3f15a013a510ed3939c8f
