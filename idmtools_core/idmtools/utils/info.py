import sys
from logging import getLogger
from typing import List

logger = getLogger(__name__)


def get_pip_packages_6_to_9():
    from pip.utils import get_installed_distributions
    return get_installed_distributions()


def get_pip_packages_10_to_current():
    from pip._internal.utils.misc import get_installed_distributions
    return get_installed_distributions()


def get_packages_from_pip():
    """
        Attempts to load pacakges from pip
        Returns:
            (List[str]): List of packages installed
        """
    load_pip_versions = [get_pip_packages_10_to_current, get_pip_packages_6_to_9]
    installed_packages_list = []

    for load_pip in load_pip_versions:
        try:
            installed_packages = load_pip()
            installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
            break
        except Exception:
            pass

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
