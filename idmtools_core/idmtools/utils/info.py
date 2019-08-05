import sys
from logging import getLogger
from typing import List

logger = getLogger(__name__)


def get_packages_from_pip():
    """
        Attempts to load pacakges from pip
        Returns:
            (List[str]): List of packages installed
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
    Returns a list of installed packages in current environment. Currently we depend on pip for this functionality
    and since it is just used for troubleshooting, we can ignore if it errors.

    Returns:
        (List[str]): List of packages installed
    """

    packages = get_packages_from_pip()
    if packages is None:  # fall back to sys modules
        packages = []
        # for name, module in sys.modules:
        for name, mod in sys.modules.items():
            version = ''
            if hasattr(mod, 'version'):
                version = mod.version
            elif hasattr(mod, '__version__'):
                version = mod.__version__
            packages.append(f'{name}=={version}')
        packages = list(sorted(packages))
    return packages
