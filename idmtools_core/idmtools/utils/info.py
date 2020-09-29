import urllib

import sys
from logging import getLogger
from typing import List, Optional

logger = getLogger(__name__)


def get_doc_base_url():
    return "https://institutefordiseasemodeling.github.io/idmtools/"


def get_pip_packages_10_to_6():
    """
    Load packages for versions 1.0 to 6 of pip.

    Returns:
        None

    Raises:
        ImportError: If the pip version is different.
    """
    from pip.util import get_installed_distributions
    return get_installed_distributions()


def get_pip_packages_6_to_9():
    """
    Get packages for pip versions 6 through 9.

    Returns:
        None

    Raises:
        ImportError: If the pip version is different.
    """
    from pip.utils import get_installed_distributions
    return get_installed_distributions()


def get_pip_packages_10_to_current():
    """
    Get packages for pip versions 10 to current.

    Returns:
        None

    Raises:
        ImportError: If the pip version is different.
    """
    from pip._internal.utils.misc import get_installed_distributions
    return get_installed_distributions()


def get_packages_from_pip():
    """
    Attempt to load pacakges from pip.

    Returns:
        (List[str]): A list of packages installed.
    """
    load_pip_versions = [get_pip_packages_10_to_current, get_pip_packages_6_to_9, get_pip_packages_10_to_6]
    installed_packages_list = None

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


def get_help_version_url(help_path, url_template: str = 'https://docs.idmod.org/projects/idmtools/en/{version}/', version: Optional[str] = None) -> str:
    """
    Get the help url for a subject based on a version

    Args:
        help_path: Path to config(minus base url). For example, configuration.html
        url_template: Template for URL containing version replacement formatter
        version: Optional version. If not provided, the version of idmtools installed will be used. For development versions, the version will always be nightly

    Returns:
        Path to url
    """
    from idmtools import __version__
    if version is None:
        version = __version__

    if "nightly" in version:
        version = "latest"
    return urllib.parse.urljoin(url_template.format(version=version), help_path)