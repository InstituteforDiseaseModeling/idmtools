import sys
from logging import getLogger
from typing import List

logger = getLogger(__name__)


def get_packages_from_pip():
    """
        Attempt to load pacakges from pip.

        Returns:
            (List[str]): A list of packages installed.
        """
    try:

        from pip._internal import get_installed_distributions
        installed_packages = get_installed_distributions()
        installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
    except Exception:
        # try a different version of pip
        try:
            from pip._internal.utils.misc import get_installed_distributions
            installed_packages = get_installed_distributions()
            installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
        except Exception as e:
            logger.exception(e)
            logger.warning("Could not load the packages from pip")
            return None
    return installed_packages_list


def get_packages_list() -> List[str]:
    """
    Return a list of installed packages in the current environment. Currently |IT_s| depends on pip for this 
    functionality and since it is just used for troubleshooting, errors can be ignored.

    Returns:
        (List[str]): A list of packages installed.
    """

    packages = get_packages_from_pip()
    if packages is None:  # fall back to sys modules
        packages = []
        # for name, module in sys.modules:
        modules = list(sys.modules.items())
        for name, mod in modules:
            version = ''
            if hasattr(mod, 'version'):
                version = mod.version
            elif hasattr(mod, '__version__'):
                version = mod.__version__
            packages.append(f'{name}=={version}')
        packages = list(sorted(packages))
    return packages
