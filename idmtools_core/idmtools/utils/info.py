import sys
from io import BytesIO, SEEK_END, SEEK_SET
from logging import getLogger
from typing import List

logger = getLogger(__name__)


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


class ResponseStream(BytesIO):
    def __init__(self, request_iterator):
        super().__init__()
        self._bytes = BytesIO()
        self._iterator = request_iterator

    def _load_all(self):
        self._bytes.seek(0, SEEK_END)
        for chunk in self._iterator:
            self._bytes.write(chunk)

    def _load_until(self, goal_position):
        current_position = self._bytes.seek(0, SEEK_END)
        while current_position < goal_position:
            try:
                current_position = self._bytes.write(next(self._iterator))
            except StopIteration:
                break

    def tell(self):
        return self._bytes.tell()

    def read(self, size=None):
        left_off_at = self._bytes.tell()
        if size is None:
            self._load_all()
        else:
            goal_position = left_off_at + size
            self._load_until(goal_position)

        self._bytes.seek(left_off_at)
        return self._bytes.read(size)

    def seek(self, position, whence=SEEK_SET):
        if whence == SEEK_END:
            self._load_all()
        else:
            self._bytes.seek(position, whence)
