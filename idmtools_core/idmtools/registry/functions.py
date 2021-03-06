from logging import getLogger, DEBUG

from pluggy import PluginManager
import idmtools.registry.hook_specs as hookspecs
from idmtools.utils.decorators import SingletonMixin

logger = getLogger(__name__)


class FunctionPluginManager(PluginManager, SingletonMixin):
    def __init__(self):
        super(FunctionPluginManager, self).__init__(hookspecs.IDMTOOLS_HOOKS)
        self.add_hookspecs(hookspecs)
        self.load_setuptools_entrypoints(hookspecs.IDMTOOLS_HOOKS.lower())
        if logger.isEnabledFor(DEBUG):
            logger.debug(self.get_plugins())
